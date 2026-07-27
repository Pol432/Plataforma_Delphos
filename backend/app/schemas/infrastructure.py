"""
Schemas Pydantic - FASE 12: Infrastructure
Auth, Sesiones, Seguridad, Sistema, Gamificación, Referidos, Puentes, Auditoría
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal


# ==============================================================================
# BLOQUE A: Autenticación y Sesiones
# ==============================================================================

class SocialAuthCreate(BaseModel):
    usuario_id: int = Field(..., gt=0)
    proveedor: str = Field(..., pattern="^(google|linkedin|github|microsoft|apple)$")
    proveedor_usuario_id: str = Field(..., min_length=1, max_length=255)
    email_proveedor: Optional[str] = Field(None, max_length=255)
    nombre_proveedor: Optional[str] = Field(None, max_length=200)
    avatar_url_proveedor: Optional[str] = Field(None, max_length=500)

class SocialAuthOut(SocialAuthCreate):
    id: int
    verificado: bool
    es_metodo_principal: bool
    total_usos: int
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class UserSessionCreate(BaseModel):
    usuario_id: int = Field(..., gt=0)
    token_sesion: str = Field(..., min_length=10, max_length=500)
    expira_en: datetime
    ip_address: Optional[str] = Field(None, max_length=45)
    plataforma: Optional[str] = Field(None, pattern="^(web|ios|android|desktop)$")

class UserSessionOut(UserSessionCreate):
    id: int
    revocado: bool
    total_requests: int
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class AuthLogCreate(BaseModel):
    usuario_id: Optional[int] = Field(None, gt=0)
    tipo_evento: str = Field(..., min_length=3, max_length=50)
    metodo: Optional[str] = Field(None, max_length=50)
    ip_address: Optional[str] = Field(None, max_length=45)
    exitoso: bool
    razon_fallo: Optional[str] = Field(None, max_length=200)

class AuthLogOut(AuthLogCreate):
    id: int
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# BLOQUE B: Seguridad y Sistema
# ==============================================================================

class RateLimitCreate(BaseModel):
    usuario_id: Optional[int] = Field(None, gt=0)
    ip_address: Optional[str] = Field(None, max_length=45)
    tipo_accion: str = Field(..., min_length=3, max_length=50)
    limite_max: int = Field(..., gt=0)
    ventana_inicio: datetime
    ventana_fin: datetime
    ventana_duracion_segundos: int = Field(default=3600, gt=0)

class RateLimitOut(RateLimitCreate):
    id: int
    contador: int
    bloqueado: bool
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class SystemConfigCreate(BaseModel):
    clave: str = Field(..., min_length=2, max_length=100)
    valor: str = Field(..., min_length=1)
    tipo_dato: str = Field(
        default="string",
        pattern="^(string|integer|decimal|boolean|json)$"
    )
    descripcion: Optional[str] = None
    categoria: Optional[str] = Field(None, max_length=50)
    es_publico: bool = False
    es_modificable: bool = True

class SystemConfigOut(SystemConfigCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# BLOQUE C: Gamificación y Referidos
# ==============================================================================

class LevelCreate(BaseModel):
    nivel: int = Field(..., ge=1)
    xp_requerida: int = Field(..., ge=0)
    nombre_nivel: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = None
    recompensa_xp_bonus: int = Field(default=0, ge=0)

class LevelOut(LevelCreate):
    id: int
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class ReferralCreate(BaseModel):
    usuario_referidor_id: int = Field(..., gt=0)
    usuario_referido_id: int = Field(..., gt=0)
    codigo_referido: str = Field(..., min_length=3, max_length=20)
    fuente: Optional[str] = Field(None, max_length=50)

class ReferralOut(ReferralCreate):
    id: int
    estado: str
    recompensa_referidor_xp: int
    recompensa_referido_xp: int
    recompensa_reclamada: bool
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# BLOQUE D: Tablas Puente
# ==============================================================================

class MentorSimulationCreate(BaseModel):
    simulacion_id: int = Field(..., gt=0)
    mentor_id: int = Field(..., gt=0)
    rol_en_simulacion: str = Field(
        default="mentor_principal",
        pattern="^(mentor_principal|supervisor|colega|experto_invitado)$"
    )
    disponible_chat_global: bool = True
    orden_presentacion: int = Field(default=1, ge=1)
    mensaje_bienvenida: Optional[str] = None

class MentorSimulationOut(MentorSimulationCreate):
    id: int
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class SimulationSkillCreate(BaseModel):
    simulacion_id: int = Field(..., gt=0)
    habilidad_id: int = Field(..., gt=0)
    xp_ganado: int = Field(default=50, ge=0)
    peso: Decimal = Field(default=Decimal("1.0"), ge=0, le=2)
    es_habilidad_principal: bool = False

class SimulationSkillOut(SimulationSkillCreate):
    id: int
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# BLOQUE E: Auditoría
# ==============================================================================

class AuditSimulationCreate(BaseModel):
    simulacion_id: int = Field(..., gt=0)
    usuario_empresa_id: Optional[int] = Field(None, gt=0)
    accion: str = Field(..., min_length=3, max_length=50)
    campos_modificados: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = Field(None, max_length=45)

class AuditSimulationOut(AuditSimulationCreate):
    id: int
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class AuditCompanyCreate(BaseModel):
    empresa_id: int = Field(..., gt=0)
    admin_dao_id: Optional[int] = Field(None, gt=0)
    accion: str = Field(..., min_length=3, max_length=50)
    detalles: Optional[str] = None
    campos_modificados: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = Field(None, max_length=45)

class AuditCompanyOut(AuditCompanyCreate):
    id: int
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class AuditUserCreate(BaseModel):
    usuario_id: int = Field(..., gt=0)
    admin_dao_id: Optional[int] = Field(None, gt=0)
    accion: str = Field(..., min_length=3, max_length=50)
    razon: Optional[str] = None
    detalles: Optional[str] = None
    campos_modificados: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = Field(None, max_length=45)

class AuditUserOut(AuditUserCreate):
    id: int
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)
