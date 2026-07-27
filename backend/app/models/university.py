from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class University(Base):
    """Modelo de Universidades (Nombre en Inglés para coincidir con init)"""
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), unique=True, nullable=False, index=True)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    dominio = Column(String(100), nullable=True) 
    
    tipo = Column(String(50), default="Privada")
    pais = Column(String(100), default="Ecuador")
    ciudad = Column(String(100))
    direccion = Column(String(300))
    
    # Estado
    es_partner = Column(Boolean, default=False)
    esta_activo = Column(Boolean, default=True)
    
    # Timestamps
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    careers = relationship("Career", back_populates="university")

    def __repr__(self):
        return f"<University {self.nombre}>"

class Career(Base):
    """Modelo de Carreras (Restaurado)"""
    __tablename__ = "careers"

    id = Column(Integer, primary_key=True, index=True)
    university_id = Column(Integer, ForeignKey("universities.id"))
    nombre = Column(String(200), nullable=False)
    codigo = Column(String(50))
    
    university = relationship("University", back_populates="careers")
