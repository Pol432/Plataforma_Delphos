from typing import Optional, List
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.university import University

class UniversityRepository(BaseRepository[University, None, None]):
    def __init__(self, db: Session):
        super().__init__(University, db)
    
    def get_by_slug(self, slug: str) -> Optional[University]:
        return self.db.query(University).filter(University.slug == slug).first()
    
    def get_by_name(self, nombre: str) -> Optional[University]:
        return self.db.query(University).filter(University.nombre == nombre).first()
    
    def search_by_name(self, query: str) -> List[University]:
        return self.db.query(University).filter(
            University.nombre.ilike(f"%{query}%"),
            University.esta_activo == True
        ).all()
