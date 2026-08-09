"""
Learning Path Models
Defines curated learning routes and their required skills.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, Numeric, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, default="General")
    difficulty_level = Column(String(50), nullable=True)
    duration_hours = Column(Numeric(5, 2), default=0.0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    skills = relationship(
        "LearningPathSkill",
        back_populates="learning_path",
        cascade="all, delete-orphan",
        order_by="LearningPathSkill.skill_order"
    )

    def __repr__(self):
        return f"<LearningPath {self.slug}>"


class LearningPathSkill(Base):
    __tablename__ = "learning_path_skills"

    id = Column(Integer, primary_key=True, index=True)
    learning_path_id = Column(
        Integer,
        ForeignKey("learning_paths.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_catalog_id = Column(
        Integer,
        ForeignKey("skills_catalog.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_order = Column(Integer, nullable=False, default=1)
    required_level = Column(Integer, nullable=False, default=1)
    is_core = Column(Boolean, nullable=False, default=True)

    learning_path = relationship("LearningPath", back_populates="skills")
    skill = relationship("SkillCatalog")

    __table_args__ = (
        UniqueConstraint("learning_path_id", "skill_catalog_id", name="uq_learning_path_skill"),
    )

    def __repr__(self):
        return f"<LearningPathSkill path={self.learning_path_id} skill={self.skill_catalog_id}>"
