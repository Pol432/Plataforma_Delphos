"""
Gamification Schemas - Pydantic V2
Validación para modelos de Fase 9
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal


# ============================================
# PROGRESO Y ECONOMÍA
# ============================================

class UserModuleOut(BaseModel):
    """Schema de salida para progreso en módulos"""
    id: int
    user_id: int
    module_id: int
    estado: str
    porcentaje_completado: Decimal = Field(ge=0, le=100)
    tiempo_dedicado_minutos: int = Field(ge=0)
    fecha_inicio: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TaskSkillCreate(BaseModel):
    """Schema para crear asociación tarea-skill"""
    task_id: int
    skill_id: int
    xp_ganado: int = Field(default=10, ge=0)
    peso: Decimal = Field(default=1.0, ge=0, le=2.0)


class TaskSkillOut(BaseModel):
    """Schema de salida para habilidades de tarea"""
    id: int
    task_id: int
    skill_id: int
    xp_ganado: int
    peso: Decimal
    
    model_config = ConfigDict(from_attributes=True)


class XPTransactionCreate(BaseModel):
    """Schema para crear transacción XP"""
    user_id: int
    cantidad_xp: int  # Puede ser negativo
    tipo_fuente: str = Field(pattern="^(tarea|logro|mision|bonus|penalizacion)$")
    fuente_id: Optional[int] = None
    descripcion: str = Field(min_length=1, max_length=500)


class XPTransactionOut(BaseModel):
    """Schema de salida para transacciones XP"""
    id: int
    user_id: int
    cantidad_xp: int
    tipo_fuente: str
    descripcion: str
    xp_anterior: int
    xp_nuevo: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# GAMIFICACIÓN
# ============================================

class AchievementCreate(BaseModel):
    """Schema para crear logro"""
    titulo: str = Field(min_length=1, max_length=200)
    descripcion: str = Field(min_length=1)
    tipo_logro: str = Field(pattern="^(bronce|plata|oro|platino)$")
    recompensa_xp: int = Field(default=0, ge=0)


class AchievementOut(BaseModel):
    """Schema de salida para logros"""
    id: int
    titulo: str
    descripcion: str
    tipo_logro: str
    recompensa_xp: int
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)


class UserAchievementOut(BaseModel):
    """Schema de salida para logros de usuario"""
    id: int
    user_id: int
    logro_id: int
    desbloqueado: bool
    fecha_desbloqueo: datetime
    
    model_config = ConfigDict(from_attributes=True)


class MissionCreate(BaseModel):
    """Schema para crear misión"""
    titulo: str = Field(min_length=1, max_length=200)
    descripcion: str = Field(min_length=1)
    objetivo_tipo: str = Field(min_length=1, max_length=100)
    objetivo_cantidad: int = Field(ge=1)
    recompensa_xp: int = Field(default=0, ge=0)


class MissionOut(BaseModel):
    """Schema de salida para misiones"""
    id: int
    titulo: str
    descripcion: str
    objetivo_tipo: str
    objetivo_cantidad: int
    recompensa_xp: int
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)


class UserMissionOut(BaseModel):
    """Schema de salida para progreso en misiones"""
    id: int
    user_id: int
    mision_id: int
    progreso_actual: int
    estado: str
    fecha_inicio: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================
# MENTORES IA
# ============================================

class VirtualMentorCreate(BaseModel):
    """Schema para crear mentor virtual"""
    empresa_id: int
    nombre: str = Field(min_length=1, max_length=200)
    personalidad: str = Field(default="profesional")
    prompt_sistema: str = Field(min_length=1)
    modelo_ia: str = Field(default="gpt-4")


class VirtualMentorOut(BaseModel):
    """Schema de salida para mentores virtuales"""
    id: int
    empresa_id: int
    nombre: str
    personalidad: str
    modelo_ia: str
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)


class MentorMessageCreate(BaseModel):
    """Schema para crear mensaje de mentor"""
    conversacion_id: int
    rol: str = Field(pattern="^(user|assistant|system)$")
    contenido: str = Field(min_length=1)


class MentorMessageOut(BaseModel):
    """Schema de salida para mensajes de mentor"""
    id: int
    conversacion_id: int
    rol: str
    contenido: str
    tokens_usados: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class OracleMessageCreate(BaseModel):
    """Schema para crear mensaje de oráculo"""
    sesion_id: int
    rol: str = Field(pattern="^(user|assistant|system)$")
    contenido: str = Field(min_length=1)


class OracleMessageOut(BaseModel):
    """Schema de salida para mensajes de oráculo"""
    id: int
    sesion_id: int
    rol: str
    contenido: str
    tokens_usados: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
