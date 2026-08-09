"""
Oracle Router — recomendación de simulaciones.

Dos motores detrás de la misma interfaz. El contrato del endpoint no cambia,
solo el valor de `engine`:

* El puente heurístico (`RecommendationService`) produce SIEMPRE los valores de
  `scores` que viajan en la respuesta.
* El Wide&Deep entrenado, cuando está disponible, decide sólo el ORDEN de la
  lista. Su probabilidad cruda no se publica: la calibración está sin resolver
  (ver `app/services/oracle_engine.py`).

Si el modelo no carga, falla, o devuelve scores degenerados, se cae al
heurístico y `engine` lo refleja.

Cómo se lee mal `engine`
------------------------
`engine: "wide_and_deep"` significa "el modelo ORDENÓ esta lista", NO "estos
números salieron del modelo". Los números son siempre del heurístico. Es una
confusión fácil y ya se ha dado: al narrar una demo o al leer el JSON, no
atribuir `engagement_probability` ni `confidence_interval` al Wide&Deep.

`confidence_interval` merece mención aparte: lo rellena el heurístico como una
banda fija de +/-0.1 alrededor de su propio score (ancho constante 0.2, punto
medio igual a la probabilidad). No es una estimación de incertidumbre de nadie
— ni del modelo, que deja el campo en None a propósito.

Nota: este router NO es el cuestionario vocacional (app/models/oracle.py); ese
sigue sin exponerse.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from slugify import slugify

from app.api.deps import get_current_user, get_db
from app.models.learning_path import LearningPath
from app.schemas.ml import (
    FullProfileResponse,
    LearningPathItem,
    MatchingInput,
    OracleProfileInput,
    RecommendationItem,
    RecommendationResponse,
    UserFeaturesInput,
)
from app.services import oracle_engine
from app.services.oracle_catalog import get_catalog
from app.services.recommendation_service import RecommendationService

router = APIRouter()

#: Se conserva el nombre por compatibilidad con lo que ya importaba este módulo.
ENGINE_NAME = oracle_engine.ENGINE_HEURISTIC

_service = RecommendationService()


@router.get("/catalog")
def get_simulation_catalog(current_user=Depends(get_current_user)):
    """Catálogo de simulaciones disponible para recomendar."""
    try:
        catalog = get_catalog()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    return {
        "count": len(catalog.simulations),
        "skill_vocabulary_size": len(catalog.skill_name_by_id) + len(catalog.alias_skill_ids),
        "simulations": [
            {
                "simulation_id": sim.simulation_id,
                "title": catalog.title_for(sim.simulation_id),
                "base_career": catalog.career_for(sim.simulation_id),
                "categoria": sim.simulation_categoria.value,
                "nivel_dificultad": sim.simulation_nivel_dificultad.value,
                "duracion_horas": sim.simulation_duracion_horas,
            }
            for sim in catalog.simulations
        ],
    }


@router.get("/skills")
def get_skill_vocabulary(current_user=Depends(get_current_user)):
    """Vocabulario de skills que entiende el oráculo (para que el cliente lo use)."""
    try:
        catalog = get_catalog()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    # Los nombres OOV se publican con el ID de su equivalente entrenado, así
    # que hay IDs repetidos: "Figma" y "Adobe Creative Suite" son el mismo 39.
    # Es lo que de verdad devuelve `resolve_skill_names`, y omitirlos dejaría al
    # cliente sin poder ofrecer 16 skills que el oráculo entiende igual.
    vocabulary = [
        {"skill_id": sid, "name": name}
        for sid, name in catalog.skill_name_by_id.items()
    ] + [
        {"skill_id": sid, "name": name}
        for name, sid in catalog.alias_skill_ids.items()
    ]
    vocabulary.sort(key=lambda entry: (entry["skill_id"], entry["name"]))

    return {"count": len(vocabulary), "skills": vocabulary}


@router.post("/recommend", response_model=RecommendationResponse)
def recommend_simulations(
    profile: OracleProfileInput,
    current_user=Depends(get_current_user),
):
    """
    Puntúa las 64 simulaciones del catálogo contra el perfil y devuelve el top-N.

    Los `scores` de cada item —incluido `confidence_interval`— los produce
    siempre el heurístico, cualquiera que sea el motor que ordene. El orden lo
    decide el Wide&Deep si está disponible; si no, la probabilidad heurística.
    """
    try:
        catalog = get_catalog()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    resolved_ids = catalog.resolve_skill_names(profile.skills)
    unresolved = catalog.unresolved_skill_names(profile.skills)

    user_features = UserFeaturesInput(
        user_skill_ids=resolved_ids,
        education_level=profile.education_level,
        field_of_study=profile.field_of_study,
        analytical_score=profile.analytical_score,
        creative_score=profile.creative_score,
        social_score=profile.social_score,
        linguistic_score=profile.linguistic_score,
        hands_on_score=profile.hands_on_score,
    )

    scored: List[RecommendationItem] = []
    user_skill_set = set(resolved_ids)

    # Un MatchingInput por simulación, en orden de catálogo. La misma lista
    # alimenta al heurístico (que llena `scores`) y al modelo (que ordena), así
    # que los índices de `model_ranking()` indexan directamente `scored`.
    matching_inputs = [
        MatchingInput(user_features=user_features, simulation_features=sim)
        for sim in catalog.simulations
    ]

    for sim, matching_input in zip(catalog.simulations, matching_inputs):
        # calculate_skill_overlap levanta ValueError si ambas listas están vacías;
        # las simulaciones siempre traen >=1 skill, así que solo aplica al perfil.
        result = _service.predict(matching_input)

        matched = [
            catalog.skill_name_by_id[sid]
            for sid in sorted(user_skill_set & set(sim.simulation_skill_ids))
        ]

        scored.append(
            RecommendationItem(
                simulation_id=sim.simulation_id,
                title=catalog.title_for(sim.simulation_id),
                base_career=catalog.career_for(sim.simulation_id),
                categoria=sim.simulation_categoria.value,
                nivel_dificultad=sim.simulation_nivel_dificultad.value,
                duracion_horas=sim.simulation_duracion_horas,
                matched_skills=matched,
                scores=result,
            )
        )

    order = oracle_engine.model_ranking(matching_inputs)
    if order is not None:
        engine = oracle_engine.ENGINE_WIDEDEEP
        scored = [scored[i] for i in order]
    else:
        engine = oracle_engine.ENGINE_HEURISTIC
        scored.sort(key=lambda item: item.scores.engagement_probability, reverse=True)

    return RecommendationResponse(
        user_id=current_user.id,
        # `engine` se mantiene tal cual estaba: el motor que ordenó. `ranked_by`
        # es su alias explícito y sale de la MISMA variable, así que los dos
        # reflejan siempre el mismo camino de fallback; no hay semántica nueva.
        engine=engine,
        ranked_by=engine,
        # Los `scores` los llena `_service.predict()` en el bucle de arriba, sin
        # excepción y sin depender del motor que ordene. Es constante a
        # propósito: refleja el estado real, no una condición.
        scored_by=oracle_engine.ENGINE_HEURISTIC,
        catalog_size=len(catalog.simulations),
        resolved_skill_ids=resolved_ids,
        unresolved_skills=unresolved,
        recommendations=scored[: profile.top_n],
    )


@router.post("/full_profile", response_model=FullProfileResponse)
def full_profile(
    profile: OracleProfileInput,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Devuelve recomendaciones de simulaciones y rutas de aprendizaje sugeridas
    para el perfil completo del usuario.
    """
    try:
        catalog = get_catalog()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    resolved_ids = catalog.resolve_skill_names(profile.skills)
    unresolved = catalog.unresolved_skill_names(profile.skills)

    user_features = UserFeaturesInput(
        user_skill_ids=resolved_ids,
        education_level=profile.education_level,
        field_of_study=profile.field_of_study,
        analytical_score=profile.analytical_score,
        creative_score=profile.creative_score,
        social_score=profile.social_score,
        linguistic_score=profile.linguistic_score,
        hands_on_score=profile.hands_on_score,
    )

    scored: List[RecommendationItem] = []
    user_skill_set = set(resolved_ids)
    user_skill_slugs = {slugify(skill) for skill in profile.skills if skill and skill.strip()}

    for sim in catalog.simulations:
        result = _service.predict(MatchingInput(user_features=user_features, simulation_features=sim))

        matched = [
            catalog.skill_name_by_id[sid]
            for sid in sorted(user_skill_set & set(sim.simulation_skill_ids))
        ]

        scored.append(
            RecommendationItem(
                simulation_id=sim.simulation_id,
                title=catalog.title_for(sim.simulation_id),
                base_career=catalog.career_for(sim.simulation_id),
                categoria=sim.simulation_categoria.value,
                nivel_dificultad=sim.simulation_nivel_dificultad.value,
                duracion_horas=sim.simulation_duracion_horas,
                matched_skills=matched,
                scores=result,
            )
        )

    scored.sort(key=lambda item: item.scores.engagement_probability, reverse=True)

    learning_paths = []
    for path in db.query(LearningPath).filter(LearningPath.is_active == True).all():
        path_skill_names = [skill.skill.name for skill in path.skills]
        if not path_skill_names:
            continue

        matched_skills = [
            name for name in path_skill_names
            if slugify(name) in user_skill_slugs
        ]
        missing_skills = [
            name for name in path_skill_names
            if slugify(name) not in user_skill_slugs
        ]
        relevance = round(len(matched_skills) / len(path_skill_names), 4) if path_skill_names else 0.0

        learning_paths.append(
            LearningPathItem(
                path_id=path.id,
                name=path.name,
                slug=path.slug,
                category=path.category,
                difficulty_level=path.difficulty_level,
                duration_hours=float(path.duration_hours or 0.0),
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                relevance_score=relevance,
            )
        )

    learning_paths.sort(key=lambda item: item.relevance_score, reverse=True)

    return FullProfileResponse(
        user_id=current_user.id,
        # Este endpoint no llama a `oracle_engine`: puntúa con el heurístico y
        # ordena por esa misma probabilidad. Así que los tres campos son el
        # heurístico, y `ranked_by` no es condicional como en /recommend —
        # reflejarlo con la lógica de allí sería copiar una selección de motor
        # que aquí no existe.
        engine=ENGINE_NAME,
        scored_by=ENGINE_NAME,
        ranked_by=ENGINE_NAME,
        catalog_size=len(catalog.simulations),
        resolved_skill_ids=resolved_ids,
        unresolved_skills=unresolved,
        recommendations=scored[: profile.top_n],
        learning_paths=learning_paths[:5],
    )
