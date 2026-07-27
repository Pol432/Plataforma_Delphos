from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    nombre_empresa = Column(String(150), unique=True, index=True, nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    tipo_empresa = Column(String(50), default="real_nacional")
    industria = Column(String(100), nullable=False)
    pais = Column(String(50), nullable=False)
    ciudad = Column(String(50))
    descripcion_corta = Column(String(255))
    tipo_partnership = Column(String(50), default="basico")
    
    es_partner_activo = Column(Boolean, default=False)
    verificado = Column(Boolean, default=False)
    esta_activo = Column(Boolean, default=True) # Soft delete
    
    calificacion_promedio = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Propiedades calculadas (Mocks para tests)
    @property
    def total_simulaciones(self):
        return 0 # TODO: Implementar count real
        
    @property
    def total_usuarios_inscritos(self):
        return 0 # TODO: Implementar count real
