from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.repositories.catalog_repository import CatalogRepository
from app.models.catalog import Industry, SkillCatalog, Region, Province, City


class CatalogService:
    """Servicio de lógica de negocio para catálogos"""
    
    def __init__(self, db: Session):
        self.repo = CatalogRepository(Industry, db) # Hack para inicializar BaseRepo
        self.db = db
    
    def get_all_industries(self, db: Session) -> List[Industry]:
        return self.repo.get_all_industries(db, active_only=True)
    
    def validate_industry(self, db: Session, industry_name: str) -> bool:
        # Validamos por nombre porque Company usa string "industria"
        industries = self.get_all_industries(db)
        return any(i.name == industry_name for i in industries)
    
    def get_all_skills(self, db: Session) -> List[SkillCatalog]:
        return self.repo.get_all_skills(db, active_only=True)
    
    def get_all_regions(self, db: Session) -> List[Region]:
        return self.repo.get_all_regions(db, active_only=True)
    
    def get_provinces_by_region(self, db: Session, region_id: int) -> List[Province]:
        return self.repo.get_provinces_by_region(db, region_id)
    
    def get_cities_by_province(self, db: Session, province_id: int) -> List[City]:
        return self.repo.get_cities_by_province(db, province_id)
    
    def validate_location(self, db: Session, city_id: int, province_id: int) -> bool:
        city = self.repo.get_city_by_id(db, city_id)
        if not city or not city.is_active: return False
        if city.province_id != province_id: return False
        return True
