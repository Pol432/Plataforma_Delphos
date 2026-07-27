from app.db.base import Base
from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class UserSimulation(Base):
    __tablename__ = "simulaciones_usuario"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    estado = Column(String(50), default="inscrito", nullable=False, index=True)
    porcentaje_completado = Column(Numeric(5, 2), default=0.0, nullable=False)
    
    inscrito_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completado_en = Column(DateTime(timezone=True), nullable=True)
    ultima_actividad = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    tiempo_total_minutos = Column(Integer, default=0)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'simulation_id', name='uq_user_simulation'),
        Index('ix_user_simulation_estado', 'user_id', 'estado'),
    )

class UserTask(Base):
    __tablename__ = "tareas_usuario"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("module_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    
    estado = Column(String(50), default="pendiente", nullable=False, index=True)
    respuesta_texto = Column(Text, nullable=True)
    calificacion_obtenida = Column(Numeric(5, 2), nullable=True)
    calificacion_maxima = Column(Numeric(5, 2), default=100.0)
    
    iniciada_en = Column(DateTime(timezone=True), nullable=True)
    completada_en = Column(DateTime(timezone=True), nullable=True)
    intentos = Column(Integer, default=1)
    
    __table_args__ = (UniqueConstraint('user_id', 'task_id', name='uq_user_task'),)

class SimulationSkill(Base):
    __tablename__ = "habilidades_simulacion"

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    
    peso = Column(Numeric(3, 2), default=1.0, nullable=False)
    es_requerida = Column(Boolean, default=False)
    
    __table_args__ = (UniqueConstraint('simulation_id', 'skill_id', name='uq_simulation_skill'),)

class UserSkill(Base):
    __tablename__ = "habilidades_usuario"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    
    xp_total = Column(Integer, default=0, nullable=False)
    nivel = Column(Integer, default=1, nullable=False)
    
    __table_args__ = (UniqueConstraint('user_id', 'skill_id', name='uq_user_skill'),)
    
    @property
    def porcentaje_nivel_actual(self):
        xp_nivel_actual = (self.nivel ** 2) * 100
        xp_siguiente_nivel = ((self.nivel + 1) ** 2) * 100
        xp_en_nivel = self.xp_total - xp_nivel_actual
        xp_necesario = xp_siguiente_nivel - xp_nivel_actual
        return float(min(100, max(0, (xp_en_nivel / xp_necesario) * 100))) if xp_necesario > 0 else 0.0
