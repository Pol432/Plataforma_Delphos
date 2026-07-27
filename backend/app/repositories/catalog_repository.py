from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.catalog import Industry, SkillCatalog, Region, Province, City


class CatalogRepository(BaseRepository):
    """Repositorio para gestión de catálogos del sistema"""
    
    # ==================== INDUSTRIES ====================
    def get_all_industries(self, db: Session, active_only: bool = True) -> List[Industry]:
        """Obtener todas las industrias"""
        query = db.query(Industry)
        if active_only:
            query = query.filter(Industry.is_active == True)
        return query.order_by(Industry.name).all()
    
    def get_industry_by_id(self, db: Session, industry_id: int) -> Optional[Industry]:
        return db.query(Industry).filter(Industry.id == industry_id).first()
    
    def get_industry_by_slug(self, db: Session, slug: str) -> Optional[Industry]:
        return db.query(Industry).filter(Industry.slug == slug).first()
    
    # ==================== SKILLS ====================
    def get_all_skills(self, db: Session, active_only: bool = True) -> List[SkillCatalog]:
        query = db.query(SkillCatalog)
        if active_only:
            query = query.filter(SkillCatalog.is_active == True)
        return query.order_by(SkillCatalog.name).all()
    
    def get_skills_by_category(self, db: Session, category: str) -> List[SkillCatalog]:
        return db.query(SkillCatalog).filter(
            SkillCatalog.category == category,
            SkillCatalog.is_active == True
        ).all()
    
    def get_skill_by_id(self, db: Session, skill_id: int) -> Optional[SkillCatalog]:
        return db.query(SkillCatalog).filter(SkillCatalog.id == skill_id).first()
    
    # ==================== REGIONS ====================
    def get_all_regions(self, db: Session, active_only: bool = True) -> List[Region]:
        query = db.query(Region)
        if active_only:
            query = query.filter(Region.is_active == True)
        return query.order_by(Region.name).all()
    
    def get_region_by_id(self, db: Session, region_id: int) -> Optional[Region]:
        return db.query(Region).filter(Region.id == region_id).first()
    
    # ==================== PROVINCES ====================
    def get_provinces_by_region(self, db: Session, region_id: int) -> List[Province]:
        return db.query(Province).filter(
            Province.region_id == region_id,
            Province.is_active == True
        ).all()
    
    def get_province_by_id(self, db: Session, province_id: int) -> Optional[Province]:
        return db.query(Province).filter(Province.id == province_id).first()
    
    # ==================== CITIES ====================
    def get_cities_by_province(self, db: Session, province_id: int) -> List[City]:
        return db.query(City).filter(
            City.province_id == province_id, # CORREGIDO: province_id (Inglés)
            City.is_active == True # CORREGIDO: is_active (Inglés)
        ).all()
    
    def get_city_by_id(self, db: Session, city_id: int) -> Optional[City]:
        return db.query(City).filter(City.id == city_id).first()
