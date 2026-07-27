from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class SkillBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None
    category: str = Field(default="technical", pattern="^(technical|soft|language|tool)$")

class SkillCreate(SkillBase):
    catalog_skill_id: Optional[int] = None

class SkillUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

class SkillOut(SkillBase):
    id: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
