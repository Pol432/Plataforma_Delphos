"""
Catalog Models - Complete MÓDULO 0: CATÁLOGOS Y NORMALIZACIÓN
Based on class diagram - PostgreSQL target
Version: English naming (Region, Province, City, Industry, etc.)
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


# ============================================
# GEOGRAPHIC CATALOGS (Ecuador)
# ============================================

class Region(Base):
    """Regiones del Ecuador: Costa, Sierra, Amazonía, Insular"""
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    code = Column(String(10), unique=True, nullable=False, index=True)
    description = Column(Text)
    map_color = Column(String(7), comment="Hex color for maps")
    order = Column(Integer, default=1)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    provinces = relationship("Province", back_populates="region")
    
    def __repr__(self):
        return f"<Region {self.name}>"


class Province(Base):
    """Provincias del Ecuador (24 provincias)"""
    __tablename__ = "provinces"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    code = Column(String(10), unique=True, nullable=False, index=True, comment="INEC Code")
    capital = Column(String(100))
    population = Column(Integer)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    region = relationship("Region", back_populates="provinces")
    cities = relationship("City", back_populates="province")
    
    def __repr__(self):
        return f"<Province {self.name}>"


class City(Base):
    """Ciudades del Ecuador"""
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    province_id = Column(Integer, ForeignKey("provinces.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    is_capital = Column(Boolean, default=False)
    population = Column(Integer)
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    province = relationship("Province", back_populates="cities")
    
    def __repr__(self):
        return f"<City {self.name}>"


# ============================================
# INDUSTRY CATALOG (Hierarchical)
# ============================================

class Industry(Base):
    """
    Industrias con jerarquía
    Example: Technology → Software → Frontend
    """
    __tablename__ = "industries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    icon = Column(String(255))
    color = Column(String(7), comment="Hex color")
    
    # Hierarchy
    parent_industry_id = Column(Integer, ForeignKey("industries.id"), nullable=True, index=True)
    level = Column(Integer, default=1, comment="1: Parent, 2: Child, 3: Grandchild")
    
    is_active = Column(Boolean, default=True)
    order = Column(Integer, default=999)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    parent = relationship("Industry", remote_side=[id], backref="children")
    
    def __repr__(self):
        return f"<Industry {self.name}>"


# ============================================
# CONTENT CATEGORY CATALOG (Hierarchical)
# ============================================

class ContentCategory(Base):
    """
    Categorías de contenido educativo
    Example: STEM, Business, Health, Arts
    """
    __tablename__ = "content_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    icon = Column(String(255))
    color = Column(String(7))
    
    # Hierarchy
    parent_category_id = Column(Integer, ForeignKey("content_categories.id"), nullable=True, index=True)
    level = Column(Integer, default=1)
    order = Column(Integer, default=999)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    parent = relationship("ContentCategory", remote_side=[id], backref="children")
    
    def __repr__(self):
        return f"<ContentCategory {self.name}>"


# ============================================
# SKILLS CATALOG (Hierarchical with Market Data)
# ============================================

class SkillCatalog(Base):
    """
    Catálogo de habilidades con datos de mercado
    Example: Python, Leadership, Advanced Excel
    """
    __tablename__ = "skills_catalog"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, nullable=False, index=True)
    slug = Column(String(150), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True, 
                     comment="technical, soft, language, tool")
    
    description = Column(Text)
    icon_url = Column(String(500))
    color = Column(String(7))
    
    # Hierarchy
    parent_skill_id = Column(Integer, ForeignKey("skills_catalog.id"), nullable=True, index=True)
    taxonomy_level = Column(Integer, default=1, 
                           comment="Programming → Python → Django")
    
    # Market Intelligence
    market_demand = Column(String(20), default='medium', 
                          comment="high, medium, low")
    trend = Column(String(20), default='stable', 
                  comment="growing, stable, declining")
    avg_salary_impact = Column(Numeric(5, 2), 
                              comment="Salary multiplier estimate")
    
    # External IDs (for integrations)
    linkedin_skill_id = Column(String(100))
    coursera_skill_id = Column(String(100))
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    parent = relationship("SkillCatalog", remote_side=[id], backref="children")
    
    def __repr__(self):
        return f"<Skill {self.name} ({self.category})>"
