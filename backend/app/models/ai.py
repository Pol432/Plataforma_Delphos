from app.db.base import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class RecomendacionIA(Base):
    __tablename__ = "recomendaciones_ia"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    simulacion_id = Column(Integer, ForeignKey("simulations.id"), index=True, nullable=False)
    
    engagement_probability = Column(Numeric(5, 4), nullable=False)
    razon_principal = Column(String(200), nullable=True)
    
    fue_clickeado = Column(Boolean, default=False)
    fue_iniciado = Column(Boolean, default=False)
    
    generado_en = Column(DateTime(timezone=True), server_default=func.now())
