from app.db.base import Base
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, UniqueConstraint, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Archetype(Base):
    __tablename__ = "arquetipos_psicologicos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    descripcion = Column(Text, nullable=False)
    color_hex = Column(String(7), nullable=True)

    # Umbrales mínimos para clasificar en este arquetipo (skills dinámicos)
    min_skills = Column(JSON().with_variant(JSONB, 'postgresql'), default=dict, nullable=True)

    esta_activo = Column(Boolean, default=True)

class OracleQuestion(Base):
    __tablename__ = "preguntas_oraculo"

    id = Column(Integer, primary_key=True, index=True)
    pregunta = Column(Text, nullable=False)
    categoria = Column(String(50), nullable=False)
    orden = Column(Integer, nullable=False)
    dificultad = Column(Integer, default=1)
    esta_activo = Column(Boolean, default=True)

class QuestionOption(Base):
    __tablename__ = "opciones_respuesta"

    id = Column(Integer, primary_key=True, index=True)
    pregunta_id = Column(Integer, ForeignKey("preguntas_oraculo.id", ondelete="CASCADE"), nullable=False)
    texto_opcion = Column(Text, nullable=False)
    orden = Column(Integer, default=1)

    # Mapeo dinámico de skills: {"planificacion_proyectos": 25, "gestion_tiempo": 20}
    skill_mapping = Column(JSON().with_variant(JSONB, 'postgresql'), default=dict, nullable=True)

    explicacion = Column(Text, nullable=True)

    pregunta = relationship("OracleQuestion", backref="opciones")

class OracleSession(Base):
    __tablename__ = "sesiones_oraculo"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    estado = Column(String(50), default="iniciada", nullable=False) # iniciada, en_progreso, completada
    paso_actual = Column(Integer, default=1)

    # Acumulador dinámico de skills inferidos durante la sesión
    inferred_skills = Column(JSON().with_variant(JSONB, 'postgresql'), default=dict, nullable=True)

    arquetipo_resultante_id = Column(Integer, ForeignKey("arquetipos_psicologicos.id"), nullable=True)

    iniciado_en = Column(DateTime(timezone=True), server_default=func.now())
    completado_en = Column(DateTime(timezone=True), nullable=True)

    arquetipo = relationship("Archetype")

class UserOracleAnswer(Base):
    __tablename__ = "respuestas_usuario_oraculo"

    id = Column(Integer, primary_key=True, index=True)
    sesion_id = Column(Integer, ForeignKey("sesiones_oraculo.id", ondelete="CASCADE"), nullable=False)
    pregunta_id = Column(Integer, ForeignKey("preguntas_oraculo.id", ondelete="CASCADE"), nullable=False)
    opcion_id = Column(Integer, ForeignKey("opciones_respuesta.id", ondelete="CASCADE"), nullable=False)
    tiempo_respuesta_segundos = Column(Integer, nullable=True)

    __table_args__ = (UniqueConstraint('sesion_id', 'pregunta_id', name='uq_sesion_pregunta'),)
