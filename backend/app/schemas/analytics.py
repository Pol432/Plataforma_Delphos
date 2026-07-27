from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime

# === SCHEMAS DE TELEMETRÍA ===
class UserEventCreate(BaseModel):
    evento: str = Field(..., max_length=100)
    categoria: str = Field(..., max_length=50)
    referencia_id: Optional[int] = None
    referencia_tipo: Optional[str] = None
    metadata_evento: Optional[Dict[str, Any]] = Field(default_factory=dict)
    sesion_id: Optional[str] = None
    plataforma: Optional[str] = None

class UserEventOut(UserEventCreate):
    id: int
    usuario_id: Optional[int]
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)

# === SCHEMAS B2B ATS ===
class CandidateUpdate(BaseModel):
    estado_candidato: Optional[str] = Field(None, max_length=50)
    puntuacion_total: Optional[int] = Field(None, ge=0, le=100)
    notas_internas: Optional[str] = None
    etiquetas: Optional[List[str]] = None
    contactado: Optional[bool] = None

class CandidateOut(BaseModel):
    id: int
    empresa_id: int
    usuario_id: int
    origen: str
    estado_candidato: str
    puntuacion_total: Optional[int]
    contactado: bool
    fecha_agregado: datetime
    model_config = ConfigDict(from_attributes=True)
