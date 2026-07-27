from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class EnrollmentCreate(BaseModel):
    simulation_id: int = Field(..., gt=0)

class TaskSubmission(BaseModel):
    task_id: int = Field(..., gt=0)
    respuesta_texto: Optional[str] = Field(None, max_length=10000)

class UserProgressOut(BaseModel):
    simulation_id: int
    estado: str
    porcentaje_completado: Decimal
    tiempo_total_minutos: int
    inscrito_en: datetime
    model_config = ConfigDict(from_attributes=True)
