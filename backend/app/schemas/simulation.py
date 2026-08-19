"""
Simulation Schemas - Complete hierarchy validation
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict, Literal
from datetime import datetime


# =============================================================================
# SIMULATION SCHEMAS
# =============================================================================

class SimulationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    slug: str = Field(..., min_length=1, max_length=300)
    short_description: str = Field(..., min_length=1)  # CRITICAL: Required
    company_id: int
    category_id: int
    lore_context: Optional[str] = None
    scaffolding_phase: Optional[Literal['Guided','Intermediate','Final Challenge']] = Field(default='Guided')
    real_world_constraints: Optional[List[str]] = Field(default_factory=list)
    immediate_feedback: Optional[Dict[str, object]] = Field(default_factory=dict)
    skills_metrics_weights: Optional[Dict[str, float]] = Field(default_factory=dict)


class SimulationCreate(SimulationBase):
    state: str = Field(default="draft", pattern="^(draft|published|archived)$")
    difficulty_level: Optional[str] = None


class SimulationUpdate(BaseModel):
    title: Optional[str] = None
    short_description: str = Field(..., min_length=1)
    state: Optional[str] = None
    difficulty_level: Optional[str] = None


class SimulationOut(SimulationBase):
    id: int
    state: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# MODULE SCHEMAS
# =============================================================================

class ModuleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    simulation_id: int
    order: int = Field(..., ge=1)


class ModuleCreate(ModuleBase):
    description: Optional[str] = None


class ModuleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = Field(None, ge=1)


class ModuleOut(ModuleBase):
    id: int
    description: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# TASK SCHEMAS
# =============================================================================

#: Tipos de tarea aceptados. El patrón anterior —(video|quiz|pdf|text|code)— no
#: incluía `submission`, que es el DEFAULT del propio modelo
#: (`models/simulations.py:96`), así que `GET /api/v1/tasks` reventaba con
#: ResponseValidationError (500) en cuanto la tabla tenía una fila normal: la
#: validación de RESPUESTA rechazaba datos que el backend mismo había escrito.
#:
#: Se añaden los dos que existen en la base y faltaban —`submission` (24 filas) e
#: `interactive` (12)— y se conservan los cinco originales aunque hoy sólo se
#: usen `video` y `text`: quitarlos rompería a quien ya cree tareas con ellos.
#:
#: Va como tupla y no como regex suelto para que sea la única lista, la
#: compartan TaskBase y TaskUpdate, y añadir un tipo sea tocar un sitio.
TASK_TYPES = ("submission", "interactive", "video", "quiz", "pdf", "text", "code")

TaskType = Literal[TASK_TYPES]  # type: ignore[valid-type]


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    module_id: int
    order: int = Field(..., ge=1)
    task_type: TaskType
    lore_context: Optional[str] = None
    scaffolding_phase: Optional[Literal['Guided','Intermediate','Final Challenge']] = Field(default='Guided')
    real_world_constraints: Optional[List[str]] = Field(default_factory=list)
    immediate_feedback: Optional[Dict[str, object]] = Field(default_factory=dict)
    skills_metrics_weights: Optional[Dict[str, float]] = Field(default_factory=dict)


class TaskCreate(TaskBase):
    description: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = Field(None, ge=1)
    # Antes era `Optional[str]` sin validar: se podía PATCHear un `task_type`
    # arbitrario que luego hacía fallar la lectura. Misma lista que TaskBase.
    task_type: Optional[TaskType] = None


class TaskOut(TaskBase):
    id: int
    description: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# RESOURCE SCHEMAS
# =============================================================================

class ResourceBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    url: str = Field(..., min_length=1, max_length=500)
    task_id: int



    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

class ResourceCreate(ResourceBase):
    resource_type: Optional[str] = "file"


class ResourceUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    resource_type: Optional[str] = None


class ResourceOut(ResourceBase):
    id: int
    resource_type: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
