"""
Infrastructure Models - FASE 12
Cierre de brechas del DBML original.
Con protección 'extend_existing=True' para evitar colisiones en tests.
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime,
    ForeignKey, Text, Numeric, JSON, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.models.usuarios_empresa import CompanyUser

# ==============================================================================
# BLOQUE A: Autenticación y Sesiones
# ==============================================================================

class SocialAuth(Base):
    __tablename__ = "autenticaciones_sociales"
    __table_args__ = (
        UniqueConstraint("proveedor", "proveedor_usuario_id", name="uq_proveedor_usuario_id"),
        {"extend_existing": True}
    )

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    proveedor = Column(String(50), nullable=False)
    proveedor_usuario_id = Column(String(255), nullable=False)
    email_proveedor = Column(String(255), nullable=True)
    nombre_proveedor = Column(String(200), nullable=True)
    avatar_url_proveedor = Column(String(500), nullable=True)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expira_en = Column(DateTime(timezone=True), nullable=True)
    scopes = Column(JSON().with_variant(JSONB, "postgresql"), default=list, nullable=True)
    metadata_proveedor = Column(JSON().with_variant(JSONB, "postgresql"), default=dict, nullable=True)
    verificado = Column(Boolean, default=True, nullable=False)
    es_metodo_principal = Column(Boolean, default=False, nullable=False)
    ultimo_uso = Column(DateTime(timezone=True), nullable=True)
    total_usos = Column(Integer, default=0, nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())
    usuario = relationship("User", backref="social_auths")

class UserSession(Base):
    __tablename__ = "sesiones_usuario"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_sesion = Column(String(500), unique=True, nullable=False, index=True)
    refresh_token = Column(String(500), unique=True, nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    plataforma = Column(String(50), nullable=True)
    navegador = Column(String(100), nullable=True)
    sistema_operativo = Column(String(100), nullable=True)
    dispositivo = Column(String(100), nullable=True)
    pais = Column(String(100), nullable=True)
    ciudad = Column(String(100), nullable=True)
    expira_en = Column(DateTime(timezone=True), nullable=False)
    ultimo_uso = Column(DateTime(timezone=True), server_default=func.now())
    total_requests = Column(Integer, default=0, nullable=False)
    revocado = Column(Boolean, default=False, nullable=False, index=True)
    revocado_en = Column(DateTime(timezone=True), nullable=True)
    razon_revocacion = Column(String(200), nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    usuario = relationship("User", backref="sesiones")

class AuthLog(Base):
    __tablename__ = "logs_autenticacion"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    tipo_evento = Column(String(50), nullable=False, index=True)
    metodo = Column(String(50), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    plataforma = Column(String(50), nullable=True)
    pais = Column(String(100), nullable=True)
    ciudad = Column(String(100), nullable=True)
    exitoso = Column(Boolean, nullable=False)
    razon_fallo = Column(String(200), nullable=True)
    codigo_error = Column(String(50), nullable=True)
    metadata_log = Column(JSON().with_variant(JSONB, "postgresql"), default=dict, nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    usuario = relationship("User", backref="auth_logs")

# ==============================================================================
# BLOQUE B: Seguridad y Sistema
# ==============================================================================

class RateLimit(Base):
    __tablename__ = "rate_limits"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True, index=True)
    tipo_accion = Column(String(50), nullable=False)
    contador = Column(Integer, default=0, nullable=False)
    limite_max = Column(Integer, nullable=False)
    ventana_inicio = Column(DateTime(timezone=True), nullable=False)
    ventana_fin = Column(DateTime(timezone=True), nullable=False, index=True)
    ventana_duracion_segundos = Column(Integer, default=3600, nullable=False)
    bloqueado = Column(Boolean, default=False, nullable=False, index=True)
    bloqueado_hasta = Column(DateTime(timezone=True), nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())
    usuario = relationship("User", backref="rate_limits")

class SystemConfig(Base):
    __tablename__ = "configuracion_sistema"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    clave = Column(String(100), unique=True, nullable=False, index=True)
    valor = Column(Text, nullable=False)
    tipo_dato = Column(String(50), default="string", nullable=False)
    descripcion = Column(Text, nullable=True)
    categoria = Column(String(50), nullable=True, index=True)
    es_publico = Column(Boolean, default=False, nullable=False)
    es_modificable = Column(Boolean, default=True, nullable=False)
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())
    actualizado_por_admin_id = Column(Integer, ForeignKey("admins_dao.id", ondelete="SET NULL"), nullable=True, index=True)
    admin = relationship("AdminDao", backref="configuraciones_modificadas")

# ==============================================================================
# BLOQUE C: Gamificación y Referidos
# ==============================================================================

class Level(Base):
    __tablename__ = "niveles"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    nivel = Column(Integer, unique=True, nullable=False, index=True)
    xp_requerida = Column(Integer, nullable=False, index=True)
    nombre_nivel = Column(String(100), nullable=True)
    descripcion = Column(Text, nullable=True)
    recompensa_xp_bonus = Column(Integer, default=0, nullable=False)
    recompensas_items = Column(JSON().with_variant(JSONB, "postgresql"), default=list, nullable=True)
    recompensas_desbloqueos = Column(JSON().with_variant(JSONB, "postgresql"), default=list, nullable=True)
    icono = Column(String(500), nullable=True)
    color = Column(String(7), nullable=True)
    badge_url = Column(String(500), nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

class Referral(Base):
    __tablename__ = "referidos"
    __table_args__ = (
        UniqueConstraint("usuario_referidor_id", "usuario_referido_id", name="uq_referidor_referido"),
        {"extend_existing": True}
    )

    id = Column(Integer, primary_key=True, index=True)
    usuario_referidor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_referido_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    codigo_referido = Column(String(20), nullable=False)
    recompensa_referidor_xp = Column(Integer, default=500, nullable=False)
    recompensa_referido_xp = Column(Integer, default=200, nullable=False)
    recompensa_adicional = Column(JSON().with_variant(JSONB, "postgresql"), default=dict, nullable=True)
    estado = Column(String(50), default="pendiente", nullable=False, index=True)
    recompensa_reclamada = Column(Boolean, default=False, nullable=False)
    reclamada_en = Column(DateTime(timezone=True), nullable=True)
    requiere_completar_simulacion = Column(Boolean, default=True, nullable=False)
    simulaciones_completadas = Column(Integer, default=0, nullable=False)
    fuente = Column(String(50), nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    referidor = relationship("User", foreign_keys=[usuario_referidor_id], backref="referidos_enviados")
    referido = relationship("User", foreign_keys=[usuario_referido_id], backref="referidos_recibidos")

# ==============================================================================
# BLOQUE D: Tablas Puente
# ==============================================================================

class MentorSimulation(Base):
    __tablename__ = "mentores_simulacion"
    __table_args__ = (
        UniqueConstraint("simulacion_id", "mentor_id", name="uq_simulacion_mentor"),
        {"extend_existing": True}
    )

    id = Column(Integer, primary_key=True, index=True)
    simulacion_id = Column(Integer, ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False, index=True)
    mentor_id = Column(Integer, ForeignKey("mentores_virtuales.id", ondelete="CASCADE"), nullable=False, index=True)
    rol_en_simulacion = Column(String(50), default="mentor_principal", nullable=False)
    descripcion_rol = Column(Text, nullable=True)
    disponible_chat_global = Column(Boolean, default=True, nullable=False)
    orden_presentacion = Column(Integer, default=1, nullable=False)
    mensaje_bienvenida = Column(Text, nullable=True)
    aparece_en_modulos = Column(JSON().with_variant(JSONB, "postgresql"), default=list, nullable=True)
    aparece_en_tareas = Column(JSON().with_variant(JSONB, "postgresql"), default=list, nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    simulacion = relationship("Simulation", backref="mentores_asignados")
    mentor = relationship("VirtualMentor", backref="simulaciones_asignadas")

# ==============================================================================
# BLOQUE E: Auditoría
# ==============================================================================

class AuditSimulation(Base):
    __tablename__ = "auditoria_simulaciones"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    simulacion_id = Column(Integer, ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_empresa_id = Column(Integer, ForeignKey("usuarios_empresa.id", ondelete="SET NULL"), nullable=True, index=True)
    accion = Column(String(50), nullable=False, index=True)
    campos_modificados = Column(JSON().with_variant(JSONB, "postgresql"), default=dict, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    simulacion = relationship("Simulation", backref="auditoria")
    usuario_empresa = relationship(CompanyUser, backref="auditoria_simulaciones", foreign_keys=[usuario_empresa_id])

class AuditCompany(Base):
    __tablename__ = "auditoria_empresas"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    admin_dao_id = Column(Integer, ForeignKey("admins_dao.id", ondelete="SET NULL"), nullable=True, index=True)
    accion = Column(String(50), nullable=False, index=True)
    detalles = Column(Text, nullable=True)
    campos_modificados = Column(JSON().with_variant(JSONB, "postgresql"), default=dict, nullable=True)
    ip_address = Column(String(45), nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    empresa = relationship("Empresa", backref="auditoria")
    admin = relationship("AdminDao", backref="auditoria_empresas")

class AuditUser(Base):
    __tablename__ = "auditoria_usuarios"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    admin_dao_id = Column(Integer, ForeignKey("admins_dao.id", ondelete="SET NULL"), nullable=True, index=True)
    accion = Column(String(50), nullable=False, index=True)
    razon = Column(Text, nullable=True)
    detalles = Column(Text, nullable=True)
    campos_modificados = Column(JSON().with_variant(JSONB, "postgresql"), default=dict, nullable=True)
    ip_address = Column(String(45), nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    usuario = relationship("User", backref="auditoria_usuario")
    admin = relationship("AdminDao", backref="auditoria_usuarios")

