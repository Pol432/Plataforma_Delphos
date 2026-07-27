"""
Schemas Pydantic - FASE 11: Enterprise
Social, Notificaciones, Soporte, Monetización y Seguridad
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


# ==============================================================================
# BLOQUE A: Feed Social
# ==============================================================================

class FeedPostCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    contenido: str = Field(..., min_length=1)
    imagen_url: Optional[str] = Field(None, max_length=500)

class FeedPostOut(BaseModel):
    id: int
    user_id: int
    contenido: str
    imagen_url: Optional[str] = None
    esta_activo: bool
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class PostLikeCreate(BaseModel):
    post_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)

class PostLikeOut(BaseModel):
    id: int
    post_id: int
    user_id: int
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class PostCommentCreate(BaseModel):
    post_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)
    contenido: str = Field(..., min_length=1)

class PostCommentOut(BaseModel):
    id: int
    post_id: int
    user_id: int
    contenido: str
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class SavedPostCreate(BaseModel):
    post_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)

class SavedPostOut(BaseModel):
    id: int
    post_id: int
    user_id: int
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# BLOQUE B: Notificaciones
# ==============================================================================

class NotificationCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    titulo: str = Field(..., min_length=1, max_length=200)
    mensaje: str = Field(..., min_length=1)
    tipo: str = Field(default="sistema", pattern="^(sistema|social|simulacion)$")
    link_accion: Optional[str] = Field(None, max_length=500)

class NotificationOut(BaseModel):
    id: int
    user_id: int
    titulo: str
    mensaje: str
    tipo: str
    leida: bool
    link_accion: Optional[str] = None
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class NotificationPreferenceCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    email_marketing: bool = True
    email_alertas: bool = True
    push_social: bool = True

class NotificationPreferenceOut(BaseModel):
    id: int
    user_id: int
    email_marketing: bool
    email_alertas: bool
    push_social: bool
    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# BLOQUE C: Soporte y Feedback
# ==============================================================================

class SupportTicketCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    asunto: str = Field(..., min_length=3, max_length=300)
    descripcion: str = Field(..., min_length=10)
    prioridad: str = Field(default="media", pattern="^(baja|media|alta|critica)$")

class SupportTicketOut(BaseModel):
    id: int
    user_id: int
    asunto: str
    descripcion: str
    estado: str
    prioridad: str
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class TicketMessageCreate(BaseModel):
    ticket_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)
    mensaje: str = Field(..., min_length=1)
    es_staff: bool = False

class TicketMessageOut(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    mensaje: str
    es_staff: bool
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class GeneralFeedbackCreate(BaseModel):
    user_id: Optional[int] = Field(None, gt=0)
    tipo: str = Field(default="idea", pattern="^(bug|idea)$")
    mensaje: str = Field(..., min_length=5)
    calificacion: Optional[int] = Field(None, ge=1, le=5)

class GeneralFeedbackOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    tipo: str
    mensaje: str
    calificacion: Optional[int] = None
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# BLOQUE D: Monetización y Seguridad
# ==============================================================================

class SubscriptionPlanCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    precio_mensual: Decimal = Field(..., ge=0)
    caracteristicas: Optional[Dict[str, Any]] = None

class SubscriptionPlanOut(BaseModel):
    id: int
    nombre: str
    precio_mensual: Decimal
    es_activo: bool
    caracteristicas: Optional[Dict[str, Any]] = None
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class UserSubscriptionCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    plan_id: int = Field(..., gt=0)
    estado: str = Field(default="activa", pattern="^(activa|cancelada|vencida|trial)$")
    metodo_pago: Optional[str] = Field(None, max_length=100)

class UserSubscriptionOut(BaseModel):
    id: int
    user_id: int
    plan_id: int
    estado: str
    metodo_pago: Optional[str] = None
    fecha_fin: Optional[datetime] = None
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class PaymentTransactionCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    plan_id: int = Field(..., gt=0)
    monto: Decimal = Field(..., gt=0)
    estado: str = Field(default="pendiente", pattern="^(pendiente|completado|fallido|reembolsado)$")
    id_transaccion_pasarela: Optional[str] = Field(None, max_length=255)

class PaymentTransactionOut(BaseModel):
    id: int
    user_id: int
    plan_id: int
    monto: Decimal
    estado: str
    id_transaccion_pasarela: Optional[str] = None
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class AdminDaoCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    rol: str = Field(default="moderador", pattern="^(superadmin|moderador)$")

class AdminDaoOut(BaseModel):
    id: int
    user_id: int
    rol: str
    esta_activo: bool
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)


class FraudAttemptCreate(BaseModel):
    user_id: Optional[int] = Field(None, gt=0)
    ip_address: str = Field(..., min_length=7, max_length=45)
    tipo_intento: str = Field(..., min_length=3, max_length=100)
    descripcion: Optional[str] = None

class FraudAttemptOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    ip_address: str
    tipo_intento: str
    descripcion: Optional[str] = None
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)
