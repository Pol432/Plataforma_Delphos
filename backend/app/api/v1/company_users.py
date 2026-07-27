"""
Company Users API Endpoints
CRUD operations for company users with role-based access
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from passlib.context import CryptContext

from app.db.session import get_db
from app.models.usuarios_empresa import CompanyUser
from app.models.empresa import Empresa
from app.schemas.usuarios_empresa import (
    CompanyUserCreate, CompanyUserUpdate, CompanyUserOut,
    CompanyUserInvite, CompanyUserList
)

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================
# HELPER FUNCTIONS
# ============================================

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)


def verify_company_exists(company_id: int, db: Session) -> Empresa:
    """Verify company exists"""
    company = db.query(Empresa).filter(Empresa.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id {company_id} not found"
        )
    return company


# ============================================
# ENDPOINTS
# ============================================

@router.get("/companies/{company_id}/users", response_model=CompanyUserList)
def list_company_users(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
    db: Session = Depends(get_db)
):
    """
    List all users of a company
    
    - **company_id**: Company ID
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **include_inactive**: Include inactive users
    """
    # Verify company exists
    verify_company_exists(company_id, db)
    
    # Build query
    query = db.query(CompanyUser).filter(CompanyUser.company_id == company_id)
    
    if not include_inactive:
        query = query.filter(CompanyUser.is_active == True)
    
    # Get total count
    total = query.count()
    
    # Get users
    users = query.offset(skip).limit(limit).all()
    
    return CompanyUserList(total=total, users=users)


@router.post("/companies/{company_id}/users", response_model=CompanyUserOut, status_code=status.HTTP_201_CREATED)
def create_company_user(
    company_id: int,
    user_data: CompanyUserCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new company user
    
    - **company_id**: Company ID
    - **user_data**: User data including email, password, role, and permissions
    """
    # Verify company exists
    verify_company_exists(company_id, db)
    
    # Check if email already exists
    existing_user = db.query(CompanyUser).filter(
        CompanyUser.email == user_data.email
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user
    user_dict = user_data.model_dump(exclude={'password'})
    user_dict['company_id'] = company_id
    user_dict['password_hash'] = hashed_password
    
    db_user = CompanyUser(**user_dict)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.get("/companies/{company_id}/users/{user_id}", response_model=CompanyUserOut)
def get_company_user(
    company_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get specific company user
    
    - **company_id**: Company ID
    - **user_id**: User ID
    """
    user = db.query(CompanyUser).filter(
        CompanyUser.id == user_id,
        CompanyUser.company_id == company_id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.patch("/companies/{company_id}/users/{user_id}", response_model=CompanyUserOut)
def update_company_user(
    company_id: int,
    user_id: int,
    user_data: CompanyUserUpdate,
    db: Session = Depends(get_db)
):
    """
    Update company user
    
    - **company_id**: Company ID
    - **user_id**: User ID
    - **user_data**: Fields to update
    """
    user = db.query(CompanyUser).filter(
        CompanyUser.id == user_id,
        CompanyUser.company_id == company_id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    update_data = user_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/companies/{company_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company_user(
    company_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Deactivate company user (soft delete)
    
    - **company_id**: Company ID
    - **user_id**: User ID
    """
    user = db.query(CompanyUser).filter(
        CompanyUser.id == user_id,
        CompanyUser.company_id == company_id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Soft delete
    user.is_active = False
    
    db.commit()
    
    return None


@router.get("/companies/{company_id}/users/role/{role}", response_model=List[CompanyUserOut])
def get_users_by_role(
    company_id: int,
    role: str,
    db: Session = Depends(get_db)
):
    """
    Get all users with specific role
    
    - **company_id**: Company ID
    - **role**: Role (owner, admin, editor, viewer)
    """
    if role not in ['owner', 'admin', 'editor', 'viewer']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be: owner, admin, editor, or viewer"
        )
    
    users = db.query(CompanyUser).filter(
        CompanyUser.company_id == company_id,
        CompanyUser.role == role,
        CompanyUser.is_active == True
    ).all()
    
    return users
