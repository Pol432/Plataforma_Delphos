"""
Simulation Schemas - Complete hierarchy validation
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime


# =============================================================================
# SIMULATION SCHEMAS
# =============================================================================

class SimulationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    slug: str = Field(..., min_length=1, max_length=300)
    short_description: str = Field(..., min_length=1)  # CRITICAL: Required
    company_id: int
    category_id: int


class SimulationCreate(SimulationBase):
    state: str = Field(default="draft", pattern="^(draft|published|archived)$")
    difficulty_level: Optional[str] = None


class SimulationUpdate(BaseModel):
    title: Optional[str] = None
    short_description: str = Field(..., min_length=1)
    state: Optional[str] = None
    difficulty_level: Optional[str] = None


class SimulationOut(SimulationBase):
    id: int
    state: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# MODULE SCHEMAS
# =============================================================================

class ModuleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    simulation_id: int
    order: int = Field(..., ge=1)


class ModuleCreate(ModuleBase):
    description: Optional[str] = None


class ModuleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = Field(None, ge=1)


class ModuleOut(ModuleBase):
    id: int
    description: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# TASK SCHEMAS
# =============================================================================

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    module_id: int
    order: int = Field(..., ge=1)
    task_type: str = Field(..., pattern="^(video|quiz|pdf|text|code)$")


class TaskCreate(TaskBase):
    description: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = Field(None, ge=1)
    task_type: Optional[str] = None


class TaskOut(TaskBase):
    id: int
    description: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# RESOURCE SCHEMAS
# =============================================================================

class ResourceBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    url: str = Field(..., min_length=1, max_length=500)
    task_id: int



    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

class ResourceCreate(ResourceBase):
    resource_type: Optional[str] = "file"


class ResourceUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    resource_type: Optional[str] = None


class ResourceOut(ResourceBase):
    id: int
    resource_type: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
