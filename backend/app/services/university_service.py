from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.university_repository import UniversityRepository
from app.models.university import University
from app.schemas.university import UniversityCreate, UniversityUpdate

class UniversityService:
    def __init__(self, db: Session):
        self.repo = UniversityRepository(db)
        self.db = db

    def create_university(self, uni_data: UniversityCreate) -> University:
        if uni_data.dominio and "." not in uni_data.dominio:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El dominio debe ser válido (ej. edu.ec)"
            )

        if self.repo.get_by_slug(uni_data.slug):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El slug ya existe"
            )
            
        if self.repo.get_by_name(uni_data.nombre):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de la universidad ya existe"
            )

        return self.repo.create(uni_data)

    def get_university(self, uni_id: int) -> University:
        uni = self.repo.get(uni_id)
        if not uni:
            raise HTTPException(status_code=404, detail="Universidad no encontrada")
        return uni

    def list_universities(self, skip: int = 0, limit: int = 100) -> List[University]:
        return self.repo.get_multi(skip, limit)

    def search_universities(self, query: str) -> List[University]:
        return self.repo.search_by_name(query)
