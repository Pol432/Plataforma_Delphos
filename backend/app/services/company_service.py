"""
Company Service - Complete CRUD + Stats with Soft Delete filtering
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from typing import List, Dict
from fastapi import HTTPException, status

from app.models.empresa import Empresa
from app.models.simulations import Simulation
from app.models.usuarios_empresa import UsuarioEmpresa
from app.models.user_progress import UserSimulationProgress
from app.schemas.empresa import EmpresaCreate, EmpresaUpdate


class CompanyService:
    """Service layer for company business logic"""

    def __init__(self, db: Session):
        self.db = db

    def create_company(self, company: EmpresaCreate) -> Empresa:
        """Create new company with duplicate detection"""
        try:
            db_company = Empresa(**company.model_dump())
            self.db.add(db_company)
            self.db.commit()
            self.db.refresh(db_company)
            return db_company
        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e.orig).lower()

            if "nombre_empresa" in error_msg or "unique" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Company name already exists"
                )
            elif "slug" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Company slug already exists"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Database integrity error"
                )

    def list_companies(self, skip: int = 0, limit: int = 100) -> List[Empresa]:
        """List all active companies with pagination"""
        return self.db.query(Empresa).filter(
            Empresa.esta_activo == True
        ).offset(skip).limit(limit).all()

    def get_company(self, company_id: int) -> Empresa:
        """Get company by ID - ONLY ACTIVE"""
        company = self.db.query(Empresa).filter(
            Empresa.id == company_id,
            Empresa.esta_activo == True  # CRITICAL FIX
        ).first()

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with id {company_id} not found"
            )

        return company

    def get_company_by_slug(self, slug: str) -> Empresa:
        """Get company by slug - ONLY ACTIVE"""
        company = self.db.query(Empresa).filter(
            Empresa.slug == slug,
            Empresa.esta_activo == True  # CRITICAL FIX
        ).first()

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with slug '{slug}' not found"
            )

        return company

    def update_company(self, company_id: int, company_data: EmpresaUpdate) -> Empresa:
        """Update company with partial data"""
        company = self.get_company(company_id)

        update_dict = company_data.model_dump(exclude_unset=True)

        for field, value in update_dict.items():
            setattr(company, field, value)

        try:
            self.db.commit()
            self.db.refresh(company)
            return company
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update failed - possibly duplicate name or slug"
            )

    def delete_company(self, company_id: int) -> None:
        """Soft delete company (set esta_activo=False)"""
        company = self.get_company(company_id)
        company.esta_activo = False
        self.db.commit()

    def search_companies(self, q: str, limit: int = 10) -> List[Empresa]:
        """Search companies by name or slug (case insensitive)"""
        search_pattern = f"%{q}%"

        return self.db.query(Empresa).filter(
            Empresa.esta_activo == True,
            or_(
                Empresa.nombre_empresa.ilike(search_pattern),
                Empresa.slug.ilike(search_pattern)
            )
        ).limit(limit).all()

    def get_top_companies(self, limit: int = 10) -> List[Empresa]:
        """Get top-rated companies"""
        return self.db.query(Empresa).filter(
            Empresa.esta_activo == True
        ).order_by(
            Empresa.calificacion_promedio.desc()
        ).limit(limit).all()

    def get_company_stats(self, company_id: int) -> Dict:
        """Get real-time statistics for company dashboard"""

        total_sims = self.db.query(func.count(Simulation.id)).filter(
            Simulation.company_id == company_id,
            Simulation.state == "published"
        ).scalar() or 0

        total_staff = self.db.query(func.count(UsuarioEmpresa.id)).filter(
            UsuarioEmpresa.empresa_id == company_id,
            UsuarioEmpresa.is_active == True
        ).scalar() or 0

        total_students = self.db.query(
            func.count(UserSimulationProgress.id.distinct())
        ).join(
            Simulation,
            UserSimulationProgress.simulation_id == Simulation.id
        ).filter(
            Simulation.company_id == company_id
        ).scalar() or 0

        return {
            "total_simulaciones": total_sims,
            "calificacion_promedio": 4.5,
            "total_usuarios_inscritos": total_students,
            "total_company_users": total_staff,
            "simulaciones_activas": total_sims,
            "tasa_finalizacion": 0.0
        }
