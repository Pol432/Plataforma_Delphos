from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any
from datetime import datetime
from decimal import Decimal

class EnrollmentCreate(BaseModel):
    simulation_id: int = Field(..., gt=0)

class TaskSubmission(BaseModel):
    task_id: int = Field(..., gt=0)
    respuesta_texto: Optional[str] = Field(None, max_length=10000)

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
    simulation_id: int
    estado: str
    porcentaje_completado: Decimal
    tiempo_total_minutos: int
    inscrito_en: datetime
    model_config = ConfigDict(from_attributes=True)
