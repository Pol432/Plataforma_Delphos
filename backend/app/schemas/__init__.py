"""
Schemas Package
"""
from app.schemas.user import UserCreate, UserOut
from app.schemas.catalog import (
    RegionOut, ProvinceOut, CityOut,
    IndustryOut, ContentCategoryOut, SkillCatalogOut,
    RegionCreate, ProvinceCreate, CityCreate,
    IndustryCreate, ContentCategoryCreate, SkillCatalogCreate
)

__all__ = [
    # User
    "UserCreate",
    "UserOut",
    # Catalogs - Read
    "RegionOut",
    "ProvinceOut",
    "CityOut",
    "IndustryOut",
    "ContentCategoryOut",
    "SkillCatalogOut",
    # Catalogs - Create
    "RegionCreate",
    "ProvinceCreate",
    "CityCreate",
    "IndustryCreate",
    "ContentCategoryCreate",
    "SkillCatalogCreate",
]
