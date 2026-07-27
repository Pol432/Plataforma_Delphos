from app.db.base import Base
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, UniqueConstraint, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# ==============================================================================
# FASE 8: Telemetría y Pipeline B2B Original
# ==============================================================================
class Candidate(Base):
    """Pipeline de reclutamiento (ATS) para empresas."""
    __tablename__ = "candidatos_empresa"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    origen = Column(String(50), nullable=False)
    simulacion_origen_id = Column(Integer, ForeignKey("simulations.id", ondelete="SET NULL"), nullable=True)
    estado_candidato = Column(String(50), default="nuevo", nullable=False, index=True)
    puntuacion_total = Column(Integer, nullable=True)
    notas_internas = Column(Text, nullable=True)
    etiquetas = Column(JSON().with_variant(JSONB, 'postgresql'), nullable=True)
    contactado = Column(Boolean, default=False)
    fecha_contacto = Column(DateTime(timezone=True), nullable=True)
    fecha_agregado = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint('empresa_id', 'usuario_id', name='uq_empresa_candidato'),)

class UserEvent(Base):
    """Telemetría y Clickstream."""
    __tablename__ = "eventos_usuario"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    evento = Column(String(100), nullable=False, index=True)
    categoria = Column(String(50), nullable=False, index=True)
    referencia_id = Column(Integer, nullable=True)
    referencia_tipo = Column(String(50), nullable=True)
    metadata_evento = Column(JSON().with_variant(JSONB, 'postgresql'), nullable=True)
    sesion_id = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)
    plataforma = Column(String(50), nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), index=True)

# ==============================================================================
# FASE 10 - Bloque B: CRM Recruiter y Analítica B2B
# ==============================================================================
class CandidateEvent(Base):
    __tablename__ = "eventos_candidato"

    id = Column(Integer, primary_key=True, index=True)
    candidato_empresa_id = Column(Integer, ForeignKey("candidatos_empresa.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo_evento = Column(String(100), nullable=False)
    detalles = Column(Text, nullable=True)
    metadata_evento = Column(JSON().with_variant(JSONB, 'postgresql'), default=dict, nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # IMPORTANTE: Eliminamos el backref="eventos" y usamos back_populates si es necesario, 
    # o simplemente no lo declaramos para evitar choques.

class SimulationAnalytics(Base):
    __tablename__ = "analitica_simulacion"

    id = Column(Integer, primary_key=True, index=True)
    simulacion_id = Column(Integer, ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    periodo_tipo = Column(String(50), default="mensual", nullable=False)
    total_inscritos = Column(Integer, default=0, nullable=False)
    tasa_completado = Column(Float, default=0.0, nullable=False)
    nps_score = Column(Float, nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

class SimulationCohort(Base):
    __tablename__ = "cohortes_simulacion"

    id = Column(Integer, primary_key=True, index=True)
    simulacion_id = Column(Integer, ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False, index=True)
    nombre_cohorte = Column(String(200), nullable=False)
    tasa_retencion_dia_7 = Column(Float, default=0.0, nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

class ConversionFunnel(Base):
    __tablename__ = "embudo_conversion"

    id = Column(Integer, primary_key=True, index=True)
    simulacion_id = Column(Integer, ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False, index=True)
    paso_1_nombre = Column(String(100), nullable=False)
    paso_1_usuarios = Column(Integer, default=0, nullable=False)
    tasa_conversion_total = Column(Float, default=0.0, nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
