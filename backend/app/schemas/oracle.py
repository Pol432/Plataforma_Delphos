from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

class OptionOut(BaseModel):
    id: int
    texto_opcion: str
    orden: int
    model_config = ConfigDict(from_attributes=True)

class QuestionOut(BaseModel):
    id: int
    pregunta: str
    categoria: str
    opciones: List[OptionOut] = []
    model_config = ConfigDict(from_attributes=True)

class AnswerCreate(BaseModel):
    pregunta_id: int = Field(..., gt=0)
    opcion_id: int = Field(..., gt=0)
    tiempo_respuesta_segundos: Optional[int] = Field(None, ge=0)

class SessionOut(BaseModel):
    id: int
    usuario_id: int
    estado: str
    paso_actual: int
    iniciado_en: datetime
    model_config = ConfigDict(from_attributes=True)
