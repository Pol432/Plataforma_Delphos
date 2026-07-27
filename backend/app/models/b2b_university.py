"""
B2B University Models - FASE 10
Bloque A: Ecosistema Universitario
Tablas nuevas — NO modifica university.py existente.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class AcademicProgram(Base):
    __tablename__ = "programas_academicos"

    id = Column(Integer, primary_key=True, index=True)
    universidad_id = Column(Integer, ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    nombre_programa = Column(String(200), nullable=False)
    tipo_programa = Column(String(50), default="pregrado", nullable=False, comment="pregrado, posgrado")
    total_creditos = Column(Integer, default=0, nullable=False)
    esta_activo = Column(Boolean, default=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    universidad = relationship("University", backref="programas_academicos")

class UniversityStudent(Base):
    __tablename__ = "estudiantes_universitarios"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    universidad_id = Column(Integer, ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    programa_id = Column(Integer, ForeignKey("programas_academicos.id", ondelete="SET NULL"), nullable=True, index=True)
    matricula = Column(String(100), nullable=True)
    estado_estudiante = Column(String(50), default="activo", nullable=False, comment="activo, egresado, retirado")
    email_institucional = Column(String(255), nullable=True, index=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("User", backref="estudiantes_universitarios")
    universidad = relationship("University", backref="estudiantes_universitarios")
    programa = relationship("AcademicProgram", backref="estudiantes")

class ProgramSimulation(Base):
    __tablename__ = "simulaciones_programas"

    id = Column(Integer, primary_key=True, index=True)
    simulacion_id = Column(Integer, ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False, index=True)
    programa_id = Column(Integer, ForeignKey("programas_academicos.id", ondelete="CASCADE"), nullable=False, index=True)
    es_obligatoria = Column(Boolean, default=False, nullable=False)
    semestre_sugerido = Column(Integer, nullable=True, comment="1 al 10")
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    simulacion = relationship("Simulation", backref="simulaciones_programas")
    programa = relationship("AcademicProgram", backref="simulaciones_programas")

class UniversityReport(Base):
    __tablename__ = "reporte_universidad"

    id = Column(Integer, primary_key=True, index=True)
    universidad_id = Column(Integer, ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    programa_id = Column(Integer, ForeignKey("programas_academicos.id", ondelete="SET NULL"), nullable=True, index=True)
    periodo = Column(String(50), nullable=False, comment="ej: 2025-I, 2025-II")
    total_estudiantes = Column(Integer, default=0, nullable=False)
    tasa_aprobacion = Column(Float, default=0.0, nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    universidad = relationship("University", backref="reportes")
    programa = relationship("AcademicProgram", backref="reportes")
