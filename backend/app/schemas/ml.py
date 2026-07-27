"""
ML/Matching Schemas
Pydantic V2 models with strict validation for AI/ML pipeline.
Includes security sanitization and boundary checks.
"""
from pydantic import (
    BaseModel, 
    Field, 
    field_validator, 
    ConfigDict,
    ValidationError
)
from typing import List, Optional, Literal
from enum import Enum

# --- ENUMS (Type Safety) ---
class EducationLevel(str, Enum):
    HIGH_SCHOOL = "High School"
    ASSOCIATE = "Associate's"
    BACHELOR = "Bachelor's"
    MASTER = "Master's"
    DOCTORATE = "Doctorate"
    BOOTCAMP = "Bootcamp"

class SimulationCategory(str, Enum):
    STEM = "STEM"
    BUSINESS = "Business"
    HEALTH = "Health"
    ARTS = "Arts"
    LAW = "Law"

class DifficultyLevel(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"

# --- CORE SCHEMAS ---
class UserFeaturesInput(BaseModel):
    """
    User features for ML matching.
    Security: All scores bounded 0-100.
    """
    user_skill_ids: List[int] = Field(..., min_length=0, max_length=100)
    education_level: EducationLevel
    field_of_study: str = Field(..., min_length=1, max_length=200)
    
    # Psychometric scores (0-100)
    analytical_score: int = Field(..., ge=0, le=100)
    creative_score: int = Field(..., ge=0, le=100)
    social_score: int = Field(..., ge=0, le=100)
    linguistic_score: int = Field(..., ge=0, le=100)
    hands_on_score: int = Field(..., ge=0, le=100)
    
    @field_validator('user_skill_ids')
    @classmethod
    def validate_skill_ids(cls, v: List[int]) -> List[int]:
        if any(skill_id <= 0 for skill_id in v):
            raise ValueError("All skill IDs must be positive integers")
        return list(set(v)) # Deduplicate
    
    @field_validator('field_of_study')
    @classmethod
    def sanitize_field_of_study(cls, v: str) -> str:
        """Sanitize against XSS/SQL injection"""
        import re
        # Remove HTML tags and dangerous characters
        cleaned = re.sub(r'<[^>]+>', '', v)
        cleaned = re.sub(r'[;\'"\\]', '', cleaned)
        if not cleaned or cleaned.isspace():
            raise ValueError("field_of_study cannot be empty after sanitization")
        return cleaned.strip()
    
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

class SimulationFeaturesInput(BaseModel):
    """
    Simulation features for ML matching.
    Security: Strict validation on all numeric fields.
    """
    simulation_id: str = Field(..., min_length=1, max_length=100)
    simulation_categoria: SimulationCategory
    simulation_nivel_dificultad: DifficultyLevel
    simulation_duracion_horas: float = Field(..., gt=0, le=1000)
    simulation_industria: str = Field(..., min_length=1, max_length=200)
    simulation_skill_ids: List[int] = Field(..., min_length=1, max_length=50)
    
    @field_validator('simulation_skill_ids')
    @classmethod
    def validate_simulation_skills(cls, v: List[int]) -> List[int]:
        if any(skill_id <= 0 for skill_id in v):
            raise ValueError("All simulation skill IDs must be positive")
        return list(set(v))
    
    @field_validator('simulation_id')
    @classmethod
    def sanitize_simulation_id(cls, v: str) -> str:
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("simulation_id contains invalid characters")
        return v
    
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

class MatchingInput(BaseModel):
    user_features: UserFeaturesInput
    simulation_features: SimulationFeaturesInput
    model_config = ConfigDict(from_attributes=True)

class MatchingOutput(BaseModel):
    label: Literal[0, 1] = Field(..., description="Binary prediction (0=No Match, 1=Match)")
    engagement_probability: float = Field(..., ge=0.0, le=1.0)
    skill_overlap_score: float = Field(..., ge=0.0, le=1.0)
    difficulty_match_score: float = Field(..., ge=0.0, le=1.0)
    confidence_interval: Optional[tuple[float, float]] = None
    
    model_config = ConfigDict(from_attributes=True)
