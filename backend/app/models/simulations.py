"""
Simulation Models (Core Content)
Hierarchical structure: Simulation -> Modules -> Tasks -> Resources
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Simulation(Base):
    """
    SimulaciÃ³n principal (Hybrid: On-Demand + Live Events)
    """
    __tablename__ = "simulations"
    # --- CAMPO IA ---
    industria_principal_id = Column(Integer, nullable=True, index=True, comment='Desnormalizado para IA')


    id = Column(Integer, primary_key=True, index=True)

    # Relationships
    company_id = Column(Integer, ForeignKey("empresas.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("content_categories.id"), nullable=False, index=True)

    # Info
    title = Column(String(300), nullable=False)
    slug = Column(String(300), unique=True, nullable=False, index=True)
    short_description = Column(String(500), nullable=False)
    full_description = Column(Text)

    # Media
    intro_video_url = Column(String(500))
    thumbnail_url = Column(String(500))
    banner_url = Column(String(500))

    # --- NUEVOS CAMPOS (Hybrid Model) ---
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    total_spots = Column(Integer, default=0, comment="0 means unlimited")
    available_spots = Column(Integer, default=0)
    # ------------------------------------

    # Difficulty & Gamification
    difficulty_level = Column(String(50), default='intermediate', comment="beginner, intermediate, advanced")
    estimated_hours = Column(Numeric(5, 2))
    xp_reward = Column(Integer, default=500)

    # Configuration
    languages = Column(JSON, default=['es']) 
    is_premium = Column(Boolean, default=False)
    has_certificate = Column(Boolean, default=True)
    
    # Status
    state = Column(String(50), default='draft', index=True, comment="draft, published, archived")
    published_at = Column(DateTime(timezone=True))
    
    # Standard Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # ORM Relationships
    company = relationship("Empresa", backref="simulations")
    category = relationship("ContentCategory", backref="simulations")
    modules = relationship("SimulationModule", back_populates="simulation", cascade="all, delete-orphan", order_by="SimulationModule.order")


class SimulationModule(Base):
    __tablename__ = "simulation_modules"
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    order = Column(Integer, nullable=False)
    intro_video_url = Column(String(500))
    estimated_hours = Column(Numeric(4, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    simulation = relationship("Simulation", back_populates="modules")
    tasks = relationship("ModuleTask", back_populates="module", cascade="all, delete-orphan", order_by="ModuleTask.order")

class ModuleTask(Base):
    __tablename__ = "module_tasks"
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("simulation_modules.id"), nullable=False, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    order = Column(Integer, nullable=False)
    task_type = Column(String(50), nullable=False, default='submission')
    
    # Instructor details preserved
    instructor_name = Column(String(150))
    instructor_role = Column(String(150))
    instructor_video_url = Column(String(500))
    
    estimated_minutes = Column(Integer)
    xp_reward = Column(Integer, default=50)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    module = relationship("SimulationModule", back_populates="tasks")
    resources = relationship("TaskResource", back_populates="task", cascade="all, delete-orphan")
    model_answer = relationship("ModelAnswer", uselist=False, back_populates="task", cascade="all, delete-orphan")

class TaskResource(Base):
    @property
    def title(self):
        return self.name

    __tablename__ = "task_resources"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("module_tasks.id"), nullable=False, index=True)
    name = Column(String(300), nullable=False)
    resource_type = Column(String(50), default='file')
    url = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    task = relationship("ModuleTask", back_populates="resources")

class ModelAnswer(Base):
    __tablename__ = "model_answers"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("module_tasks.id"), nullable=False, unique=True)
    description = Column(Text)
    video_explanation_url = Column(String(500))
    resource_url = Column(String(500))
    key_learnings = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    task = relationship("ModuleTask", back_populates="model_answer")
