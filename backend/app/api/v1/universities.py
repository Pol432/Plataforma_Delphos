from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.university_service import UniversityService
from app.schemas.university import UniversityCreate, UniversityOut

router = APIRouter()

@router.post("", response_model=UniversityOut, status_code=status.HTTP_201_CREATED)
def create_university(uni_data: UniversityCreate, db: Session = Depends(get_db)):
    """Crear nueva universidad"""
    service = UniversityService(db)
    return service.create_university(uni_data)

@router.get("", response_model=List[UniversityOut])
def list_universities(
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1, le=100), 
    db: Session = Depends(get_db)
):
    """Listar universidades"""
    service = UniversityService(db)
    return service.list_universities(skip, limit)

@router.get("/search", response_model=List[UniversityOut])
def search_universities(q: str = Query(..., min_length=2), db: Session = Depends(get_db)):
    """Buscar universidades por nombre"""
    service = UniversityService(db)
    return service.search_universities(q)

@router.get("/{uni_id}", response_model=UniversityOut)
def get_university(uni_id: int, db: Session = Depends(get_db)):
    """Obtener universidad por ID"""
    service = UniversityService(db)
    return service.get_university(uni_id)
