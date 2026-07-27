"""
Tests for Catalog Models
Complete coverage for MÓDULO 0
"""
import pytest
from app.models.catalog import (
    Region, Province, City,
    Industry, ContentCategory, SkillCatalog
)


def test_create_region(db_session):
    """Test: Create region"""
    region = Region(
        name="Costa",
        code="COS",
        description="Región costera del Ecuador",
        map_color="#0066CC"
    )
    db_session.add(region)
    db_session.commit()
    db_session.refresh(region)
    
    assert region.id is not None
    assert region.name == "Costa"
    assert region.code == "COS"
    assert region.is_active is True
    print(f"✓ Region created: {region.name}")


def test_create_province(db_session):
    """Test: Create province with region"""
    # Create region first
    region = Region(name="Costa", code="COS")
    db_session.add(region)
    db_session.commit()
    
    # Create province
    province = Province(
        region_id=region.id,
        name="Guayas",
        code="GUA",
        capital="Guayaquil",
        population=4000000
    )
    db_session.add(province)
    db_session.commit()
    db_session.refresh(province)
    
    assert province.id is not None
    assert province.region_id == region.id
    assert province.name == "Guayas"
    print(f"✓ Province created: {province.name}")


def test_create_city(db_session):
    """Test: Create city with province"""
    # Create region and province
    region = Region(name="Costa", code="COS")
    db_session.add(region)
    db_session.commit()
    
    province = Province(region_id=region.id, name="Guayas", code="GUA")
    db_session.add(province)
    db_session.commit()
    
    # Create city
    city = City(
        province_id=province.id,
        name="Guayaquil",
        is_capital=True,
        population=2700000,
        latitude=-2.1894,
        longitude=-79.8837
    )
    db_session.add(city)
    db_session.commit()
    db_session.refresh(city)
    
    assert city.id is not None
    assert city.province_id == province.id
    assert city.is_capital is True
    print(f"✓ City created: {city.name}")


def test_create_industry(db_session):
    """Test: Create industry"""
    industry = Industry(
        name="Technology",
        slug="technology",
        description="Tech industry",
        color="#00FF00",
        level=1
    )
    db_session.add(industry)
    db_session.commit()
    db_session.refresh(industry)
    
    assert industry.id is not None
    assert industry.name == "Technology"
    assert industry.slug == "technology"
    print(f"✓ Industry created: {industry.name}")


def test_create_hierarchical_industry(db_session):
    """Test: Create industry hierarchy"""
    # Parent
    parent = Industry(name="Technology", slug="technology", level=1)
    db_session.add(parent)
    db_session.commit()
    
    # Child
    child = Industry(
        name="Software",
        slug="software",
        parent_industry_id=parent.id,
        level=2
    )
    db_session.add(child)
    db_session.commit()
    db_session.refresh(child)
    
    assert child.parent_industry_id == parent.id
    assert child.level == 2
    print(f"✓ Hierarchical industry: {parent.name} → {child.name}")


def test_create_content_category(db_session):
    """Test: Create content category"""
    category = ContentCategory(
        name="STEM",
        slug="stem",
        description="Science, Technology, Engineering, Math",
        color="#FF5733"
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    
    assert category.id is not None
    assert category.name == "STEM"
    print(f"✓ Content category created: {category.name}")


def test_create_skill(db_session):
    """Test: Create skill with market data"""
    skill = SkillCatalog(
        name="Python",
        slug="python",
        category="technical",
        description="Python programming language",
        market_demand="high",
        trend="growing",
        avg_salary_impact=1.5
    )
    db_session.add(skill)
    db_session.commit()
    db_session.refresh(skill)
    
    assert skill.id is not None
    assert skill.name == "Python"
    assert skill.category == "technical"
    assert skill.market_demand == "high"
    print(f"✓ Skill created: {skill.name} (demand: {skill.market_demand})")


def test_query_active_regions(db_session):
    """Test: Query only active regions"""
    # Create active and inactive
    active = Region(name="Costa", code="COS", is_active=True)
    inactive = Region(name="Test", code="TST", is_active=False)
    
    db_session.add_all([active, inactive])
    db_session.commit()
    
    # Query active only
    active_regions = db_session.query(Region).filter(Region.is_active == True).all()
    
    assert len(active_regions) == 1
    assert active_regions[0].name == "Costa"
    print(f"✓ Active regions query works: {len(active_regions)} found")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
