from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class SimulationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    slug: str = Field(..., min_length=1, max_length=300)
    short_description: str = Field(..., min_length=1, max_length=500)
    full_description: Optional[str] = None

    company_id: int
    category_id: int

    difficulty_level: str = Field(default="intermediate")
    estimated_hours: Optional[Decimal] = None
    xp_reward: int = Field(default=500, ge=0)

    # Scheduling (Inglés)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    total_spots: int = Field(default=0)

    state: str = Field(default="draft")

class SimulationCreate(SimulationBase):
    pass

class SimulationUpdate(BaseModel):
    title: Optional[str] = None
    state: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class SimulationOut(SimulationBase):
    id: int
    available_spots: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
