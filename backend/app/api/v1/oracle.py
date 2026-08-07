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

Nota: este router NO es el cuestionario vocacional (app/models/oracle.py); ese
sigue sin exponerse.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from app.schemas.ml import (
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
        "skill_vocabulary_size": len(catalog.skill_name_by_id),
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

    return {
        "count": len(catalog.skill_name_by_id),
        "skills": [
            {"skill_id": sid, "name": name}
            for sid, name in sorted(catalog.skill_name_by_id.items())
        ],
    }


@router.post("/recommend", response_model=RecommendationResponse)
def recommend_simulations(
    profile: OracleProfileInput,
    current_user=Depends(get_current_user),
):
    """
    Puntúa las 64 simulaciones del catálogo contra el perfil y devuelve el top-N.

    Los `scores` de cada item los produce siempre el heurístico. El orden lo
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
        engine=engine,
        catalog_size=len(catalog.simulations),
        resolved_skill_ids=resolved_ids,
        unresolved_skills=unresolved,
        recommendations=scored[: profile.top_n],
    )
