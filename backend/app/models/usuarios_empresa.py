"""
Modelo de Relación Usuario-Empresa (M2M con metadatos)
Permite asignar usuarios a empresas con roles y permisos
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from app.db.base import Base


class RoleType(str, Enum):
    """Roles disponibles en una empresa"""
    OWNER = "owner"           # Dueño (todos los permisos)
    ADMIN = "admin"           # Administrador
    EDITOR = "editor"         # Editor de contenido
    VIEWER = "viewer"         # Solo lectura


class Permission(str, Enum):
    """Permisos granulares"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    MANAGE_USERS = "manage_users"
    MANAGE_SIMULATIONS = "manage_simulations"


class UsuarioEmpresa(Base):
    """
    Tabla de asociación Usuario-Empresa con metadata
    Equivalente a "Company Users" en Forage/edX
    """
    __tablename__ = "usuarios_empresa"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False, index=True)
    
    # Rol y Permisos
    role = Column(String(50), nullable=False, default=RoleType.VIEWER.value)
    permissions = Column(JSON, nullable=False, default=list)  # Lista de permisos
    
    # Estado
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones ORM
    user = relationship("User", backref="company_memberships")
    empresa = relationship("Empresa", backref="user_memberships")
    
    def __repr__(self):
        return f"<UsuarioEmpresa user_id={self.user_id} empresa_id={self.empresa_id} role={self.role}>"
    
    # Constraint único: un usuario solo puede tener un rol por empresa
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )

# Alias para compatibilidad con imports en inglés
CompanyUser = UsuarioEmpresa
