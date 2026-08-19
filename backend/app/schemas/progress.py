from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any
from datetime import datetime
from decimal import Decimal
from app.models.user_progress import ProgressStatus

class EnrollmentCreate(BaseModel):
    simulation_id: int = Field(..., gt=0)
    # El endpoint ya exige que coincida con el usuario del token, así que es
    # redundante; se acepta porque el frontend lo manda y leerlo sin declararlo
    # reventaba con AttributeError (500).
    user_id: Optional[int] = Field(None, gt=0)

class TaskSubmission(BaseModel):
    task_id: int = Field(..., gt=0)
    respuesta_texto: Optional[str] = Field(None, max_length=10000)

class ProgressUpdate(BaseModel):
    """Campos actualizables de un registro de progreso.

    Antes el PATCH usaba `TaskSubmission`, que exige `task_id` y no tiene
    `status`: el payload del frontend daba 422 y, de haber pasado, la lectura de
    `progress_data.status` habría dado AttributeError.
    """
    status: Optional[ProgressStatus] = None
    completion_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    score: Optional[Decimal] = Field(None, ge=0, le=100)
    total_time_minutes: Optional[int] = Field(None, ge=0)

class SubmissionPayload(BaseModel):
    respuesta_texto: Optional[str] = Field(None, max_length=10000)
    response: Optional[str] = Field(None, max_length=10000)
    user_answer: Optional[str] = Field(None, max_length=10000)

class SubmissionResultOut(BaseModel):
    task_id: int
    score: float
    passed: bool
    status: str
    model_answer_available: bool

class FinishSimulationPayload(BaseModel):
    skills: Optional[List[str]] = Field(default_factory=list)
    field_of_study: Optional[str] = None
    analytical_score: Optional[int] = Field(default=None, ge=0, le=100)
    creative_score: Optional[int] = Field(default=None, ge=0, le=100)
    social_score: Optional[int] = Field(default=None, ge=0, le=100)
    linguistic_score: Optional[int] = Field(default=None, ge=0, le=100)
    hands_on_score: Optional[int] = Field(default=None, ge=0, le=100)

class UserProgressOut(BaseModel):
    """Salida de los endpoints de `/progress`.

    Los nombres siguen a `app.models.user_progress.UserSimulationProgress`, que
    es el modelo que usa ese router. Antes declaraba los campos en español de
    `app.models.progress.UserSimulation` —otro modelo, otra tabla—, así que
    ningún registro serializaba.
    """
    id: int
    user_id: int
    simulation_id: int
    status: ProgressStatus
    score: Optional[Decimal] = None
    completion_percentage: Optional[Decimal] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_time_minutes: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)
