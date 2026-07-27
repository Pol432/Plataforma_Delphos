"""
Database Seeder
Load initial data from JSON files (IDEMPOTENT)
"""
import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.models.catalog import Industry, SkillCatalog
from app.db.session import get_db

DATA_DIR = Path(__file__).parent / "data"


def load_industries(db: Session):
    """
    Load industries from JSON file
    Idempotent: checks if exists before creating
    """
    json_file = DATA_DIR / "industries.json"
    
    if not json_file.exists():
        print(f"⚠ File not found: {json_file}")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        industries_data = json.load(f)
    
    created = 0
    skipped = 0
    
    # First pass: create parent industries
    for item in industries_data:
        if item.get('level', 1) == 1:  # Parent industries
            # Check if exists
            existing = db.query(Industry).filter(Industry.slug == item['slug']).first()
            if existing:
                skipped += 1
                continue
            
            industry = Industry(
                name=item['name'],
                slug=item['slug'],
                description=item.get('description'),
                color=item.get('color'),
                level=item.get('level', 1),
                order=item.get('order', 999)
            )
            db.add(industry)
            created += 1
    
    db.commit()
    
    # Second pass: create child industries
    for item in industries_data:
        if item.get('level', 1) > 1:  # Child industries
            # Check if exists
            existing = db.query(Industry).filter(Industry.slug == item['slug']).first()
            if existing:
                skipped += 1
                continue
            
            # Find parent
            parent = None
            if 'parent_slug' in item:
                parent = db.query(Industry).filter(Industry.slug == item['parent_slug']).first()
            
            industry = Industry(
                name=item['name'],
                slug=item['slug'],
                description=item.get('description'),
                color=item.get('color'),
                level=item.get('level', 1),
                parent_industry_id=parent.id if parent else None,
                order=item.get('order', 999)
            )
            db.add(industry)
            created += 1
    
    db.commit()
    
    print(f"✓ Industries: {created} created, {skipped} already existed")


def load_skills(db: Session):
    """
    Load skills from JSON file
    Idempotent: checks if exists before creating
    """
    json_file = DATA_DIR / "skills.json"
    
    if not json_file.exists():
        print(f"⚠ File not found: {json_file}")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        skills_data = json.load(f)
    
    created = 0
    skipped = 0
    
    # First pass: create parent skills
    for item in skills_data:
        if 'parent_slug' not in item:  # Parent skills
            # Check if exists
            existing = db.query(SkillCatalog).filter(SkillCatalog.slug == item['slug']).first()
            if existing:
                skipped += 1
                continue
            
            skill = SkillCatalog(
                name=item['name'],
                slug=item['slug'],
                category=item['category'],
                description=item.get('description'),
                market_demand=item.get('market_demand', 'medium'),
                trend=item.get('trend', 'stable'),
                avg_salary_impact=item.get('avg_salary_impact'),
                icon_url=item.get('icon_url'),
                color=item.get('color')
            )
            db.add(skill)
            created += 1
    
    db.commit()
    
    # Second pass: create child skills
    for item in skills_data:
        if 'parent_slug' in item:  # Child skills
            # Check if exists
            existing = db.query(SkillCatalog).filter(SkillCatalog.slug == item['slug']).first()
            if existing:
                skipped += 1
                continue
            
            # Find parent
            parent = db.query(SkillCatalog).filter(SkillCatalog.slug == item['parent_slug']).first()
            
            skill = SkillCatalog(
                name=item['name'],
                slug=item['slug'],
                category=item['category'],
                description=item.get('description'),
                market_demand=item.get('market_demand', 'medium'),
                trend=item.get('trend', 'stable'),
                avg_salary_impact=item.get('avg_salary_impact'),
                parent_skill_id=parent.id if parent else None,
                taxonomy_level=2 if parent else 1,
                icon_url=item.get('icon_url'),
                color=item.get('color')
            )
            db.add(skill)
            created += 1
    
    db.commit()
    
    print(f"✓ Skills: {created} created, {skipped} already existed")


def seed_all():
    """
    Run all seeders
    """
    print("\n" + "="*50)
    print("DATABASE SEEDER")
    print("="*50 + "\n")
    
    db = next(get_db())
    
    try:
        load_industries(db)
        load_skills(db)
        
        print("\n✅ Seeding completed successfully\n")
    except Exception as e:
        print(f"\n✗ Seeding failed: {e}\n")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()
