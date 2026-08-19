from app.services.simulation_service import SimulationService
from app.schemas.ml import OracleProfileInput


def test_calculate_submission_score_returns_high_score_for_matching_answers():
    service = SimulationService(db=None)

    score = service.calculate_submission_score(
        "Analizo los datos y propongo mejoras claras",
        "Analizo los datos y propongo mejoras claras",
    )

    assert score == 100.0


def test_build_oracle_profile_from_results_uses_completed_task_skills():
    service = SimulationService(db=None)

    profile = service.build_oracle_profile_from_results(
        user_id=7,
        simulation_id=3,
        completed_tasks=[
            {"task_id": 1, "score": 90.0, "skills": ["analytical", "problem_solving"]},
            {"task_id": 2, "score": 85.0, "skills": ["leadership", "communication"]},
        ],
        current_user_fields={"field_of_study": "Computer Science"},
    )

    assert isinstance(profile, OracleProfileInput)
    assert "analytical" in profile.skills
    assert profile.analytical_score >= 80
    assert profile.social_score >= 50


def test_finish_recommendation_uses_heuristic_not_the_model():
    """El cierre de simulación NO debe ordenar con el Wide&Deep.

    El modelo está saturado: entre 26 y 37 de las 64 simulaciones reciben
    probabilidad 0.0 exacta y las de arriba se separan por ~5 diezmilésimas, así
    que con perfiles de finanzas o ingeniería de datos el orden sale casi igual
    que con un perfil vacío. `finish_simulation` pide el heurístico
    explícitamente vía `use_model=False`.

    Se comprueba sobre `recommend_for_profile`, que es el punto exacto que
    invoca el servicio. Sólo se afirma el caso `use_model=False`: el otro
    depende de que el checkpoint esté disponible, que no se garantiza en tests.
    """
    from app.api.v1.oracle import recommend_for_profile
    from app.services import oracle_engine

    profile = OracleProfileInput(
        skills=["Python", "SQL"],
        education_level="Bachelor's",
        field_of_study="Data Science",
        top_n=5,
    )

    response = recommend_for_profile(profile, user_id=1, use_model=False)

    assert response.engine == oracle_engine.ENGINE_HEURISTIC
    assert response.ranked_by == oracle_engine.ENGINE_HEURISTIC
    # `scored_by` era heurístico desde antes y debe seguir igual: el cambio es
    # de quién ORDENA, no de quién puntúa.
    assert response.scored_by == oracle_engine.ENGINE_HEURISTIC

    # Y ordena de verdad por la probabilidad heurística, que es lo que hace que
    # el resultado refleje el solapamiento real de skills.
    probs = [item.scores.engagement_probability for item in response.recommendations]
    assert probs == sorted(probs, reverse=True)


def test_finish_simulation_asks_for_the_heuristic_engine():
    """El servicio pasa `use_model=False`; que no se revierta sin querer."""
    import inspect

    from app.services import simulation_service

    source = inspect.getsource(simulation_service.SimulationService.finish_simulation)
    assert "use_model=False" in source
    assert "recommend_simulations" not in source
