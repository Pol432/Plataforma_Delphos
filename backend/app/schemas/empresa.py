from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class EmpresaBase(BaseModel):
    nombre_empresa: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=300)
    tipo_empresa: str = "real_nacional"
    industria: str
    pais: str = "Ecuador"
    ciudad: Optional[str] = None
    descripcion_corta: Optional[str] = None

class EmpresaCreate(EmpresaBase):
    """Schema para crear - verificado NO permitido"""
    pass

class EmpresaUpdate(BaseModel):
    nombre_empresa: Optional[str] = Field(None, max_length=200)
    descripcion_corta: Optional[str] = None
    pais: Optional[str] = None
    ciudad: Optional[str] = None
    esta_activo: Optional[bool] = None

class EmpresaOut(EmpresaBase):
    id: int
    verificado: bool = False
    es_partner_activo: bool = False
    tipo_partnership: str = "basico"
    total_simulaciones: int = 0
    total_usuarios_inscritos: int = 0
    
    # FIX: float limpio, sin Decimal ni strings raros
    calificacion_promedio: float = 0.0
    
    esta_activo: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
