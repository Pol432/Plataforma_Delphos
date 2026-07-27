"""
Catalog Schemas - Pydantic models for API validation
Based on class diagram MÓDULO 0
Updated for Pydantic V2 (ConfigDict)
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


# ============================================
# REGION SCHEMAS
# ============================================

class RegionBase(BaseModel):
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=10)
    description: Optional[str] = None
    map_color: Optional[str] = Field(None, max_length=7)
    order: int = 1


class RegionCreate(RegionBase):
    pass


class RegionOut(RegionBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================
# PROVINCE SCHEMAS
# ============================================

class ProvinceBase(BaseModel):
    region_id: int
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=10)
    capital: Optional[str] = Field(None, max_length=100)
    population: Optional[int] = None


class ProvinceCreate(ProvinceBase):
    pass


class ProvinceOut(ProvinceBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================
# CITY SCHEMAS
# ============================================

class CityBase(BaseModel):
    province_id: int
    name: str = Field(..., max_length=100)
    is_capital: bool = False
    population: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class CityCreate(CityBase):
    pass


class CityOut(CityBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================
# INDUSTRY SCHEMAS
# ============================================

class IndustryBase(BaseModel):
    name: str = Field(..., max_length=100)
    slug: str = Field(..., max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=255)
    color: Optional[str] = Field(None, max_length=7)
    parent_industry_id: Optional[int] = None
    level: int = 1
    order: int = 999


class IndustryCreate(IndustryBase):
    pass


class IndustryOut(IndustryBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================
# CONTENT CATEGORY SCHEMAS
# ============================================

class ContentCategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    slug: str = Field(..., max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=255)
    color: Optional[str] = Field(None, max_length=7)
    parent_category_id: Optional[int] = None
    level: int = 1
    order: int = 999


class ContentCategoryCreate(ContentCategoryBase):
    pass


class ContentCategoryOut(ContentCategoryBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================
# SKILL CATALOG SCHEMAS
# ============================================

class SkillCatalogBase(BaseModel):
    name: str = Field(..., max_length=150)
    slug: str = Field(..., max_length=150)
    category: str = Field(..., max_length=50, description="technical, soft, language, tool")
    description: Optional[str] = None
    icon_url: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(None, max_length=7)
    parent_skill_id: Optional[int] = None
    taxonomy_level: int = 1
    market_demand: str = Field(default='medium', max_length=20)
    trend: str = Field(default='stable', max_length=20)
    avg_salary_impact: Optional[float] = None
    linkedin_skill_id: Optional[str] = Field(None, max_length=100)
    coursera_skill_id: Optional[str] = Field(None, max_length=100)


class SkillCatalogCreate(SkillCatalogBase):
    pass


class SkillCatalogOut(SkillCatalogBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
