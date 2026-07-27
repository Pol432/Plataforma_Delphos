"""
Skill Model
Extends SkillCatalog with user-specific skills
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Skill(Base):
    """
    User's acquired skills (linked to catalog)
    Simpler model for direct user skills
    """
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Link to catalog (optional - can be freeform too)
    catalog_skill_id = Column(Integer, ForeignKey("skills_catalog.id"), nullable=True, index=True)
    
    # Core fields
    name = Column(String(150), unique=True, nullable=False, index=True)
    description = Column(Text)
    category = Column(String(50), nullable=False, default='technical',
                     comment="technical, soft, language, tool")
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    catalog_skill = relationship("SkillCatalog", backref="derived_skills")
    
    def __repr__(self):
        return f"<Skill {self.name}>"
