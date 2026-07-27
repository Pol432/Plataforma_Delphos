"""
ML Engine Tests - SHIELD Level
Aggressive boundary, security, and performance tests for matching algorithm.
"""
import pytest
from pydantic import ValidationError
from app.schemas.ml import (
    UserFeaturesInput, SimulationFeaturesInput, MatchingInput, 
    EducationLevel, SimulationCategory, DifficultyLevel
)
from app.services.recommendation_service import RecommendationService

@pytest.fixture
def service():
    return RecommendationService()

@pytest.fixture
def base_user():
    return UserFeaturesInput(
        user_skill_ids=[1, 5, 12, 23],
        education_level=EducationLevel.BACHELOR,
        field_of_study="Computer Science",
        analytical_score=85, creative_score=45, social_score=50,
        linguistic_score=55, hands_on_score=70
    )

@pytest.fixture
def base_sim():
    return SimulationFeaturesInput(
        simulation_id="sim_1",
        simulation_categoria=SimulationCategory.STEM,
        simulation_nivel_dificultad=DifficultyLevel.INTERMEDIATE,
        simulation_duracion_horas=8.5,
        simulation_industria="Tech",
        simulation_skill_ids=[1, 5, 8]
    )

# --- 1. BOUNDARY TESTS ---
def test_score_above_100_rejected(base_user):
    with pytest.raises(ValidationError):
        base_user.analytical_score = 101 # Invalid
        UserFeaturesInput(**base_user.model_dump())

def test_score_negative_rejected(base_user):
    with pytest.raises(ValidationError):
        base_user.analytical_score = -1 # Invalid
        UserFeaturesInput(**base_user.model_dump())

def test_negative_duration_rejected(base_sim):
    with pytest.raises(ValidationError):
        base_sim.simulation_duracion_horas = -5.0
        SimulationFeaturesInput(**base_sim.model_dump())

# --- 2. DATA INTEGRITY ---
def test_empty_user_skills_allowed(base_user):
    """Users (newbies) can have 0 skills"""
    base_user.user_skill_ids = []
    inp = UserFeaturesInput(**base_user.model_dump())
    assert inp.user_skill_ids == []

def test_empty_sim_skills_rejected(base_sim):
    """Simulations MUST have required skills"""
    with pytest.raises(ValidationError):
        base_sim.simulation_skill_ids = []
        SimulationFeaturesInput(**base_sim.model_dump())

def test_duplicate_skills_deduped(base_user):
    base_user.user_skill_ids = [1, 1, 2, 2, 3]
    inp = UserFeaturesInput(**base_user.model_dump())
    assert inp.user_skill_ids == [1, 2, 3]

# --- 3. BUSINESS LOGIC ---
def test_perfect_skill_match(service, base_user, base_sim):
    # Make skills identical
    base_user.user_skill_ids = [1, 5, 8]
    base_sim.simulation_skill_ids = [1, 5, 8]
    
    match_input = MatchingInput(user_features=base_user, simulation_features=base_sim)
    result = service.predict(match_input)
    
    assert result.skill_overlap_score == 1.0
    assert result.engagement_probability > 0.6
    assert result.label == 1

def test_zero_match(service, base_user, base_sim):
    base_user.user_skill_ids = [99, 100] # Disjoint
    base_sim.simulation_skill_ids = [1, 2]
    
    match_input = MatchingInput(user_features=base_user, simulation_features=base_sim)
    result = service.predict(match_input)
    
    assert result.skill_overlap_score == 0.0
    # Probabilidad bajará drásticamente
    assert result.engagement_probability < 0.5

# --- 4. SECURITY & FUZZING ---
def test_sql_injection_sanitization():
    malicious = "CS'; DROP TABLE users; --"
    user = UserFeaturesInput(
        user_skill_ids=[1], education_level="Bachelor's",
        field_of_study=malicious, # Should be sanitized
        analytical_score=50, creative_score=50, social_score=50,
        linguistic_score=50, hands_on_score=50
    )
    # Check that dangerous chars are gone
    assert ";" not in user.field_of_study
    assert "'" not in user.field_of_study
    assert "DROP TABLE users" in user.field_of_study # Text stays, syntax breaks

def test_xss_simulation_id_rejected():
    with pytest.raises(ValidationError):
        SimulationFeaturesInput(
            simulation_id="<script>alert(1)</script>", # Invalid chars
            simulation_categoria="STEM",
            simulation_nivel_dificultad="Beginner",
            simulation_duracion_horas=1,
            simulation_industria="Tech",
            simulation_skill_ids=[1]
        )

# --- 5. PERFORMANCE ---
def test_large_array_performance(service, base_user, base_sim):
    import time
    # User: Max 100 skills (Allowed by Schema)
    base_user.user_skill_ids = list(range(1, 101))
    
    # Simulation: Max 50 skills (Allowed by Schema)
    # Before it failed because we tried 100, but schema limits to 50
    base_sim.simulation_skill_ids = list(range(1, 51))
    
    match_input = MatchingInput(user_features=base_user, simulation_features=base_sim)
    
    start = time.time()
    service.predict(match_input)
    duration = time.time() - start
    
    assert duration < 0.1 # Should be extremely fast (<100ms)
