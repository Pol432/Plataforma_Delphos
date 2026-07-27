"""
User Progress Models
Track user progress through simulations
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class ProgressStatus(str, enum.Enum):
    """Progress status enum"""
    NOT_STARTED = "not_started"
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class UserSimulationProgress(Base):
    """
    User progress through simulations
    Tracks completion, scores, and time spent
    """
    __tablename__ = "user_simulation_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"), nullable=False, index=True)
    
    # Progress tracking
    status = Column(
        SQLEnum(ProgressStatus),
        nullable=False,
        default=ProgressStatus.NOT_STARTED,
        index=True
    )
    
    # Scores
    score = Column(Numeric(5, 2), default=0.0, comment="0-100 score")
    completion_percentage = Column(Numeric(5, 2), default=0.0)
    
    # Time tracking
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    last_activity_at = Column(DateTime(timezone=True))
    total_time_minutes = Column(Integer, default=0)
    
    # Metadata
    current_module_id = Column(Integer, ForeignKey("simulation_modules.id"), nullable=True)
    current_task_id = Column(Integer, ForeignKey("module_tasks.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="simulation_progress")
    simulation = relationship("Simulation", backref="user_progress")
    current_module = relationship("SimulationModule", foreign_keys=[current_module_id])
    current_task = relationship("ModuleTask", foreign_keys=[current_task_id])
    
    def __repr__(self):
        return f"<UserSimulationProgress user={self.user_id} sim={self.simulation_id} status={self.status}>"
