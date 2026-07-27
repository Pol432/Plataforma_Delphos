from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.schemas.empresa import EmpresaCreate, EmpresaUpdate, EmpresaOut
from app.services.company_service import CompanyService

router = APIRouter()

# NOTA: No instanciamos CompanyService aquí globalmente porque necesita 'db'

@router.post("", response_model=EmpresaOut, status_code=status.HTTP_201_CREATED)
def create_company(company_data: EmpresaCreate, db: Session = Depends(get_db)):
    """Crear nueva empresa"""
    # Instanciamos el servicio con la DB de este request
    service = CompanyService(db)
    
    # Security: Filtrar 'verificado' para evitar mass assignment
    # Aunque el schema ya lo bloquea, doble seguridad no daña
    data_dict = company_data.model_dump()
    data_dict.pop("verificado", None) 
    
    return service.create_company(EmpresaCreate(**data_dict))

@router.get("", response_model=List[EmpresaOut])
def list_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Listar empresas"""
    service = CompanyService(db)
    return service.list_companies(skip=skip, limit=limit)

@router.get("/search", response_model=List[EmpresaOut])
def search_companies(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Buscar empresas por nombre"""
    service = CompanyService(db)
    return service.search_companies(q, limit)

@router.get("/top", response_model=List[EmpresaOut])
def get_top_companies(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Obtener empresas mejor calificadas"""
    service = CompanyService(db)
    return service.get_top_companies(limit)

@router.get("/{company_id}", response_model=EmpresaOut)
def get_company(company_id: int, db: Session = Depends(get_db)):
    """Obtener empresa por ID"""
    service = CompanyService(db)
    return service.get_company(company_id)

@router.get("/slug/{slug}", response_model=EmpresaOut)
def get_company_by_slug(slug: str, db: Session = Depends(get_db)):
    """Obtener empresa por slug"""
    service = CompanyService(db)
    return service.get_company_by_slug(slug)

@router.put("/{company_id}", response_model=EmpresaOut)
def update_company(
    company_id: int,
    company_data: EmpresaUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar empresa"""
    service = CompanyService(db)
    return service.update_company(company_id, company_data)

@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(company_id: int, db: Session = Depends(get_db)):
    """Eliminar empresa (soft delete)"""
    service = CompanyService(db)
    service.delete_company(company_id)
    return None

@router.get("/{company_id}/stats")
def get_company_stats(company_id: int, db: Session = Depends(get_db)):
    """Obtener estadísticas de empresa"""
    service = CompanyService(db)
    return service.get_company_stats(company_id)
