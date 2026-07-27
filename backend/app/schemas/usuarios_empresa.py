"""
Company Users Schemas
Pydantic models for company user validation
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


# ============================================
# BASE SCHEMAS
# ============================================

class CompanyUserBase(BaseModel):
    """Base schema for company user"""
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=200)
    position: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role: str = Field(default='viewer', pattern='^(owner|admin|editor|viewer)$')


class CompanyUserPermissions(BaseModel):
    """Permissions schema"""
    can_create_simulations: bool = False
    can_edit_simulations: bool = False
    can_publish_simulations: bool = False
    can_archive_simulations: bool = False
    can_view_candidates: bool = False
    can_contact_candidates: bool = False
    can_export_data: bool = False
    can_manage_users: bool = False
    can_view_billing: bool = False


# ============================================
# CREATE SCHEMAS
# ============================================

class CompanyUserCreate(CompanyUserBase):
    """Schema for creating company user"""
    company_id: int
    password: str = Field(..., min_length=8, max_length=100)
    
    # Optional permissions
    can_create_simulations: bool = False
    can_edit_simulations: bool = False
    can_publish_simulations: bool = False
    can_archive_simulations: bool = False
    can_view_candidates: bool = False
    can_contact_candidates: bool = False
    can_export_data: bool = False
    can_manage_users: bool = False
    can_view_billing: bool = False


class CompanyUserInvite(BaseModel):
    """Schema for inviting user to company"""
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=200)
    role: str = Field(default='viewer', pattern='^(admin|editor|viewer)$')
    position: Optional[str] = Field(None, max_length=100)


# ============================================
# UPDATE SCHEMAS
# ============================================

class CompanyUserUpdate(BaseModel):
    """Schema for updating company user"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    position: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    avatar_url: Optional[str] = Field(None, max_length=500)
    role: Optional[str] = Field(None, pattern='^(owner|admin|editor|viewer)$')
    
    # Permissions
    can_create_simulations: Optional[bool] = None
    can_edit_simulations: Optional[bool] = None
    can_publish_simulations: Optional[bool] = None
    can_archive_simulations: Optional[bool] = None
    can_view_candidates: Optional[bool] = None
    can_contact_candidates: Optional[bool] = None
    can_export_data: Optional[bool] = None
    can_manage_users: Optional[bool] = None
    can_view_billing: Optional[bool] = None
    
    is_active: Optional[bool] = None


# ============================================
# RESPONSE SCHEMAS
# ============================================

class CompanyUserOut(CompanyUserBase):
    """Schema for company user response"""
    id: int
    company_id: int
    avatar_url: Optional[str] = None
    
    # Permissions
    can_create_simulations: bool
    can_edit_simulations: bool
    can_publish_simulations: bool
    can_archive_simulations: bool
    can_view_candidates: bool
    can_contact_candidates: bool
    can_export_data: bool
    can_manage_users: bool
    can_view_billing: bool
    
    # Verification
    email_verified: bool
    email_verified_at: Optional[datetime] = None
    
    # Activity
    last_access: Optional[datetime] = None
    total_accesses: int
    
    # Status
    is_active: bool
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class CompanyUserWithCompany(CompanyUserOut):
    """Company user with company details"""
    company_name: str = Field(..., description="Name of the company")
    company_slug: str = Field(..., description="Company slug")


class CompanyUserList(BaseModel):
    """List of company users"""
    total: int
    users: list[CompanyUserOut]
