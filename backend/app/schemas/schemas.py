from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from typing import Literal

class UserCreateWithLocation(BaseModel):
    """Esquema para crear un usuario extendido con ubicación y gamificación"""
    username: str
    email: EmailStr
    password: str
    full_name: str
    disabled: bool = False
    city_id: Optional[int] = None
    province_id: Optional[int] = None
    region_id: Optional[int] = None
    birth_date: Optional[datetime] = None
    gender: Optional[Literal["masculino", "femenino", "otro", "prefiero_no_decir"]] = None
    accepts_terms: bool
    accepts_privacy: bool
    current_level: int = 1  # Nivel inicial
    xp_total: int = 0  # Puntos totales de experiencia
    streak_days: int = 0  # Días de racha

class UserBase(BaseModel):
    """Campos base de usuario (compartidos entre crear y leer)"""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = False

class UserOut(UserBase):
    """Esquema para leer un usuario (con ID y nuevos campos de gamificación)"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    current_level: int
    xp_total: int
    streak_days: int
    avatar_url: Optional[str] = None
    preferred_theme: Optional[str] = None
    preferred_lang: Optional[str] = None

    class Config:
        from_attributes = True  # Permite leer desde objetos SQLAlchemy

class UserInDB(UserOut):
    """Usuario con contraseña hasheada (solo para uso interno)"""
    hashed_password: str
    
    class Config:
        from_attributes = True
