from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class UniversityBase(BaseModel):
    nombre: str
    slug: str
    dominio: Optional[str] = None
    tipo: str = "Privada"
    pais: str = "Ecuador"
    ciudad: Optional[str] = None
    direccion: Optional[str] = None
    es_partner: bool = False

class UniversityCreate(UniversityBase):
    pass

class UniversityUpdate(BaseModel):
    nombre: Optional[str] = None
    dominio: Optional[str] = None
    es_partner: Optional[bool] = None
    esta_activo: Optional[bool] = None

class UniversityOut(UniversityBase):
    id: int
    esta_activo: bool
    creado_en: datetime
    actualizado_en: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
