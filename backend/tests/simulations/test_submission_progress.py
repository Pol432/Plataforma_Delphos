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
