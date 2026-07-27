"""
User Model (Unified)
Represents the end-user (Student/Talent).
Combines basic auth and all extended profile data.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Numeric, Date, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    # --- CAMPOS IA ---
    nivel_educativo = Column(String(100), nullable=True)
    campo_estudio = Column(String(150), nullable=True)
    nombre_institucion = Column(String(200), nullable=True)
    inferred_skills = Column(JSON().with_variant(JSONB, 'postgresql'), default=dict, nullable=True)
    origen_datos = Column(String(50), default='organic')

    id = Column(Integer, primary_key=True, index=True)

    # Auth Basic
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # Profile Data
    full_name = Column(String(200), nullable=False)
    phone = Column(String(20))
    gender = Column(String(20))
    birth_date = Column(Date)

    # Location
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True)
    province_id = Column(Integer, ForeignKey("provinces.id"), nullable=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)

    # Gamification Stats
    xp_total = Column(Integer, default=0, nullable=False)
    xp_validated = Column(Integer, default=0)
    level_current = Column(Integer, default=1)
    streak_days = Column(Integer, default=0)

    # Preferences
    avatar_url = Column(String(500))
    preferred_lang = Column(String(5), default="es")
    timezone = Column(String(50), default="America/Guayaquil")

    # Verification & Security
    email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    region = relationship("Region")
    province = relationship("Province")
    city = relationship("City")

    def __repr__(self):
        return f"<User {self.username}>"
