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
    # Categorías presentes en el catálogo del oráculo (simulation_catalog.csv)
    DESIGN = "Design"
    EDUCATION = "Education"
    FINANCE = "Finance"
    LEGAL = "Legal"
    OTHER = "Other"

class DifficultyLevel(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"
    # Niveles reales del dataset de entrenamiento (dataset_metadata.json)
    LOWER_INTERMEDIATE = "Lower-Intermediate"
    UPPER_INTERMEDIATE = "Upper-Intermediate"

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
    
    @field_validator('user_skill_ids', mode='before')
    @classmethod
    def validate_skill_ids(cls, v):
        if v is None:
            return []
        if not isinstance(v, list):
            raise TypeError("user_skill_ids must be a list of positive integers")

        cleaned = []
        seen = set()
        for item in v:
            if item is None:
                continue
            try:
                skill_id = int(item)
            except (TypeError, ValueError):
                raise ValueError("All skill IDs must be integers")
            if skill_id <= 0:
                raise ValueError("All skill IDs must be positive integers")
            if skill_id not in seen:
                seen.add(skill_id)
                cleaned.append(skill_id)
        return cleaned

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
    
    @field_validator('simulation_skill_ids', mode='before')
    @classmethod
    def validate_simulation_skills(cls, v):
        if v is None:
            return []
        if not isinstance(v, list):
            raise TypeError("simulation_skill_ids must be a list of positive integers")

        cleaned = []
        seen = set()
        for item in v:
            if item is None:
                continue
            try:
                skill_id = int(item)
            except (TypeError, ValueError):
                raise ValueError("All simulation skill IDs must be integers")
            if skill_id <= 0:
                raise ValueError("All simulation skill IDs must be positive")
            if skill_id not in seen:
                seen.add(skill_id)
                cleaned.append(skill_id)
        return cleaned
    
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


# --- ORACLE ENDPOINT SCHEMAS ---
class OracleProfileInput(BaseModel):
    """
    Perfil que el cliente envía a /oracle/recommend.

    Los skills van como nombres o slugs ("Python", "ux_research") y se resuelven
    contra el catálogo del oráculo; los IDs de la tabla `skills` del backend no
    corresponden al vocabulario del modelo.
    """
    skills: List[str] = Field(default_factory=list, max_length=100)
    education_level: EducationLevel = EducationLevel.BACHELOR
    field_of_study: str = Field(default="General", min_length=1, max_length=200)

    analytical_score: int = Field(50, ge=0, le=100)
    creative_score: int = Field(50, ge=0, le=100)
    social_score: int = Field(50, ge=0, le=100)
    linguistic_score: int = Field(50, ge=0, le=100)
    hands_on_score: int = Field(50, ge=0, le=100)

    top_n: int = Field(5, ge=1, le=64, description="Cuántas recomendaciones devolver")

    @field_validator('skills')
    @classmethod
    def sanitize_skills(cls, v: List[str]) -> List[str]:
        cleaned = [s.strip() for s in v if s and s.strip()]
        if len(cleaned) != len(set(s.lower() for s in cleaned)):
            # Deduplicar preservando orden
            seen, out = set(), []
            for s in cleaned:
                if s.lower() not in seen:
                    seen.add(s.lower())
                    out.append(s)
            return out
        return cleaned

    model_config = ConfigDict(str_strip_whitespace=True)


class LearningPathItem(BaseModel):
    path_id: int
    name: str
    slug: str
    category: str
    difficulty_level: Optional[str] = None
    duration_hours: float
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    relevance_score: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class RecommendationItem(BaseModel):
    simulation_id: str
    title: str
    base_career: Optional[str] = None
    categoria: str
    nivel_dificultad: str
    duracion_horas: float
    matched_skills: List[str] = []
    scores: MatchingOutput

    model_config = ConfigDict(from_attributes=True)


class FullProfileResponse(BaseModel):
    user_id: int
    engine: str = Field(..., description="Motor usado: 'heuristic_bridge_v1' o 'wide_and_deep'")
    catalog_size: int
    resolved_skill_ids: List[int] = []
    unresolved_skills: List[str] = Field(
        default=[], description="Skills enviados que no existen en el catálogo del oráculo"
    )
    recommendations: List[RecommendationItem]
    learning_paths: List[LearningPathItem]

    model_config = ConfigDict(from_attributes=True)


class RecommendationResponse(BaseModel):
    """
    Respuesta de /oracle/recommend.

    Procedencia de los números
    --------------------------
    Dos motores intervienen y NO hacen lo mismo, así que un único campo `engine`
    no alcanzaba para decir de dónde sale cada cosa:

    * `scored_by` — quién calculó los valores de `recommendations[].scores`.
    * `ranked_by` — quién decidió el ORDEN de `recommendations`.

    Que `ranked_by` sea 'wide_and_deep' NO significa que los números vengan del
    modelo: vienen de `scored_by`. Ambos campos son de nivel respuesta porque
    describen la lista entera — todos los items se puntúan con el mismo motor y
    el orden es una propiedad de la lista, no de un item.
    """
    user_id: int

    #: Alias histórico de `ranked_by`: mismo valor, mismo significado de siempre
    #: (el motor que ORDENÓ). Se mantiene intacto para no romper a quien ya lo
    #: lea; en código nuevo preferir `ranked_by`/`scored_by`, que distinguen
    #: cuál de las dos cosas hizo cada motor.
    engine: str = Field(..., description="Motor usado: 'heuristic_bridge_v1' o 'wide_and_deep'")
    scored_by: str = Field(
        ...,
        description=(
            "Motor que produjo los valores de `recommendations[].scores` "
            "(engagement_probability, confidence_interval, etc.). Hoy siempre "
            "'heuristic_bridge_v1': la probabilidad cruda del Wide&Deep no se "
            "publica porque su calibración está sin resolver."
        ),
    )
    ranked_by: str = Field(
        ...,
        description=(
            "Motor que decidió el orden de `recommendations`: 'wide_and_deep', "
            "o 'heuristic_bridge_v1' si hubo fallback. Mismo valor que `engine`."
        ),
    )
    catalog_size: int
    resolved_skill_ids: List[int] = []
    unresolved_skills: List[str] = Field(
        default=[], description="Skills enviados que no existen en el catálogo del oráculo"
    )
    recommendations: List[RecommendationItem]

    model_config = ConfigDict(from_attributes=True)
