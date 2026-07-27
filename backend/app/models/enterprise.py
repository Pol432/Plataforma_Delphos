"""
Enterprise Models - FASE 11
Bloque A: Feed Social
Bloque B: Notificaciones
Bloque C: Soporte y Feedback
Bloque D: Monetización y Seguridad
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime,
    ForeignKey, Text, Numeric, JSON, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

# BLOQUE A: Feed Social (Comunidad)
class FeedPost(Base):
    __tablename__ = "publicaciones_feed"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    contenido = Column(Text, nullable=False)
    imagen_url = Column(String(500), nullable=True)
    esta_activo = Column(Boolean, default=True, nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())
    autor = relationship("User", backref="feed_posts")
    likes = relationship("PostLike", back_populates="post", cascade="all, delete-orphan")
    comentarios = relationship("PostComment", back_populates="post", cascade="all, delete-orphan")
    guardados = relationship("SavedPost", back_populates="post", cascade="all, delete-orphan")

class PostLike(Base):
    __tablename__ = "publicaciones_likes"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("publicaciones_feed.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    post = relationship("FeedPost", back_populates="likes")
    usuario = relationship("User", backref="post_likes")
    __table_args__ = (UniqueConstraint("post_id", "user_id", name="uq_like_post_usuario"),)

class PostComment(Base):
    __tablename__ = "publicaciones_comentarios"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("publicaciones_feed.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    contenido = Column(Text, nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())
    post = relationship("FeedPost", back_populates="comentarios")
    autor = relationship("User", backref="comentarios_feed")

class SavedPost(Base):
    __tablename__ = "publicaciones_guardadas"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("publicaciones_feed.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    post = relationship("FeedPost", back_populates="guardados")
    usuario = relationship("User", backref="posts_guardados")
    __table_args__ = (UniqueConstraint("post_id", "user_id", name="uq_guardado_post_usuario"),)

# BLOQUE B: Notificaciones
class Notification(Base):
    __tablename__ = "notificaciones"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    titulo = Column(String(200), nullable=False)
    mensaje = Column(Text, nullable=False)
    tipo = Column(String(50), nullable=False, default="sistema")
    leida = Column(Boolean, default=False, nullable=False, index=True)
    link_accion = Column(String(500), nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    usuario = relationship("User", backref="notificaciones")

class NotificationPreference(Base):
    __tablename__ = "preferencias_notificaciones"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    email_marketing = Column(Boolean, default=True, nullable=False)
    email_alertas = Column(Boolean, default=True, nullable=False)
    push_social = Column(Boolean, default=True, nullable=False)
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())
    usuario = relationship("User", backref="preferencias_notificaciones")

# BLOQUE C: Soporte y Feedback
class SupportTicket(Base):
    __tablename__ = "tickets_soporte"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    asunto = Column(String(300), nullable=False)
    descripcion = Column(Text, nullable=False)
    estado = Column(String(50), default="abierto", nullable=False, index=True)
    prioridad = Column(String(50), default="media", nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())
    usuario = relationship("User", backref="tickets_soporte")
    mensajes = relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan")

class TicketMessage(Base):
    __tablename__ = "mensajes_ticket"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets_soporte.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    mensaje = Column(Text, nullable=False)
    es_staff = Column(Boolean, default=False, nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    ticket = relationship("SupportTicket", back_populates="mensajes")
    autor = relationship("User", backref="mensajes_ticket")

class GeneralFeedback(Base):
    __tablename__ = "feedback_general"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    tipo = Column(String(50), nullable=False, default="idea")
    mensaje = Column(Text, nullable=False)
    calificacion = Column(Integer, nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    usuario = relationship("User", backref="feedbacks_generales")

# BLOQUE D: Monetización y Seguridad
class SubscriptionPlan(Base):
    __tablename__ = "planes_suscripcion"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False, index=True)
    precio_mensual = Column(Numeric(10, 2), nullable=False, default=0.00)
    es_activo = Column(Boolean, default=True, nullable=False)
    caracteristicas = Column(JSON().with_variant(JSONB, "postgresql"), default=dict, nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())
    suscripciones = relationship("UserSubscription", back_populates="plan")
    transacciones = relationship("PaymentTransaction", back_populates="plan")

class UserSubscription(Base):
    __tablename__ = "suscripciones_usuario"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("planes_suscripcion.id", ondelete="RESTRICT"), nullable=False, index=True)
    estado = Column(String(50), default="activa", nullable=False, index=True)
    fecha_fin = Column(DateTime(timezone=True), nullable=True)
    metodo_pago = Column(String(100), nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())
    usuario = relationship("User", backref="suscripciones")
    plan = relationship("SubscriptionPlan", back_populates="suscripciones")

class PaymentTransaction(Base):
    __tablename__ = "transacciones_pago"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("planes_suscripcion.id", ondelete="RESTRICT"), nullable=False, index=True)
    monto = Column(Numeric(10, 2), nullable=False)
    estado = Column(String(50), default="pendiente", nullable=False, index=True)
    id_transaccion_pasarela = Column(String(255), nullable=True, unique=True, index=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    usuario = relationship("User", backref="transacciones_pago")
    plan = relationship("SubscriptionPlan", back_populates="transacciones")

class AdminDao(Base):
    __tablename__ = "admins_dao"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    rol = Column(String(50), nullable=False, default="moderador")
    esta_activo = Column(Boolean, default=True, nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    usuario = relationship("User", backref="admin_dao")

class FraudAttempt(Base):
    __tablename__ = "intentos_fraudulentos"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    ip_address = Column(String(45), nullable=False, index=True)
    tipo_intento = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    usuario = relationship("User", backref="intentos_fraudulentos")
