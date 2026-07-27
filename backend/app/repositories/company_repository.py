from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.repositories.base_repository import BaseRepository
from app.models.empresa import Empresa as Company


class CompanyRepository(BaseRepository[Company, None, None]): # Tipos genéricos opcionales
    """Repositorio para gestión de empresas"""
    
    def __init__(self, db: Session):
        super().__init__(Company, db)
    
    def get_by_slug(self, slug: str) -> Optional[Company]:
        return self.db.query(Company).filter(Company.slug == slug).first()
    
    def get_by_name(self, name: str) -> Optional[Company]:
        return self.db.query(Company).filter(Company.nombre_empresa == name).first()
    
    def search_by_name(self, query: str, limit: int = 10) -> List[Company]:
        search_pattern = f"%{query}%"
        return self.db.query(Company).filter(
            Company.nombre_empresa.ilike(search_pattern)
        ).limit(limit).all()
    
    def get_by_industry(self, industry: str, skip: int = 0, limit: int = 100) -> List[Company]:
        return self.db.query(Company).filter(
            Company.industria == industry,
            Company.esta_activo == True
        ).offset(skip).limit(limit).all()
    
    def get_partners(self, skip: int = 0, limit: int = 100) -> List[Company]:
        return self.db.query(Company).filter(
            Company.es_partner_activo == True,
            Company.esta_activo == True
        ).offset(skip).limit(limit).all()
    
    def get_top_rated(self, limit: int = 10) -> List[Company]:
        return self.db.query(Company).filter(
            Company.esta_activo == True
        ).order_by(Company.calificacion_promedio.desc()).limit(limit).all()
    
    def count_by_industry(self, industry: str) -> int:
        return self.db.query(func.count(Company.id)).filter(
            Company.industria == industry,
            Company.esta_activo == True
        ).scalar()
