"""
Oracle Router — recomendación de simulaciones.

Puente heurístico (`RecommendationService`) sobre el catálogo real del oráculo.
El Wide&Deep entrenado entra después detrás de esta misma interfaz: el contrato
del endpoint no cambia, solo el valor de `engine`.

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
from app.services.oracle_catalog import get_catalog
from app.services.recommendation_service import RecommendationService

router = APIRouter()

ENGINE_NAME = "heuristic_bridge_v1"

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
    Puntúa las 64 simulaciones del catálogo contra el perfil y devuelve el top-N
    ordenado por probabilidad de engagement.
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

    for sim in catalog.simulations:
        # calculate_skill_overlap levanta ValueError si ambas listas están vacías;
        # las simulaciones siempre traen >=1 skill, así que solo aplica al perfil.
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

    return RecommendationResponse(
        user_id=current_user.id,
        engine=ENGINE_NAME,
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
        engine=ENGINE_NAME,
        catalog_size=len(catalog.simulations),
        resolved_skill_ids=resolved_ids,
        unresolved_skills=unresolved,
        recommendations=scored[: profile.top_n],
        learning_paths=learning_paths[:5],
    )
