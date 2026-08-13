"""
Seed Learning Paths
Idempotent seeder for curated learning routes and required skills.
"""
from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.catalog import SkillCatalog
from app.models.learning_path import LearningPath, LearningPathSkill

LEARNING_PATH_DATA = [
    {
        "slug": "data-science-essentials",
        "name": "Data Science Essentials",
        "category": "Data Analytics",
        "difficulty_level": "Intermediate",
        "duration_hours": 40.0,
        "description": "Rutas de aprendizaje para desarrolladores que quieren dominar la ciencia de datos desde Python hasta modelos ML.",
        "skills": [
            {"slug": "python", "name": "Python", "category": "technical", "required_level": 2, "is_core": True},
            {"slug": "pandas", "name": "Pandas", "category": "technical", "required_level": 2, "is_core": True},
            {"slug": "sql", "name": "SQL", "category": "technical", "required_level": 2, "is_core": True},
            {"slug": "statistics", "name": "Statistics", "category": "technical", "required_level": 1, "is_core": True},
            {"slug": "data-visualization", "name": "Data Visualization", "category": "technical", "required_level": 1, "is_core": True},
            {"slug": "machine-learning", "name": "Machine Learning", "category": "technical", "required_level": 1, "is_core": False},
            {"slug": "communication", "name": "Communication", "category": "soft", "required_level": 1, "is_core": False},
            {"slug": "problem-solving", "name": "Problem Solving", "category": "soft", "required_level": 1, "is_core": False},
        ],
    },
    {
        "slug": "cloud-engineering-fundamentals",
        "name": "Cloud Engineering Fundamentals",
        "category": "Cloud & DevOps",
        "difficulty_level": "Intermediate",
        "duration_hours": 45.0,
        "description": "Rutas de aprendizaje para ingenieros que quieren construir infraestructura escalable en la nube.",
        "skills": [
            {"slug": "aws", "name": "AWS", "category": "technical", "required_level": 2, "is_core": True},
            {"slug": "docker", "name": "Docker", "category": "tool", "required_level": 2, "is_core": True},
            {"slug": "kubernetes", "name": "Kubernetes", "category": "technical", "required_level": 1, "is_core": True},
            {"slug": "terraform", "name": "Terraform", "category": "tool", "required_level": 1, "is_core": True},
            {"slug": "linux", "name": "Linux", "category": "technical", "required_level": 2, "is_core": True},
            {"slug": "networking", "name": "Networking", "category": "technical", "required_level": 1, "is_core": False},
            {"slug": "security-basics", "name": "Security Basics", "category": "technical", "required_level": 1, "is_core": False},
            {"slug": "monitoring", "name": "Monitoring", "category": "technical", "required_level": 1, "is_core": False},
        ],
    },
    {
        "slug": "ux-product-design-track",
        "name": "UX Product Design Track",
        "category": "Design",
        "difficulty_level": "Beginner",
        "duration_hours": 35.0,
        "description": "Ruta diseñada para perfiles creativos que quieren aprender investigación de UX y diseño de productos.",
        "skills": [
            {"slug": "ux-research", "name": "UX Research", "category": "technical", "required_level": 1, "is_core": True},
            {"slug": "interaction-design", "name": "Interaction Design", "category": "technical", "required_level": 1, "is_core": True},
            {"slug": "prototyping", "name": "Prototyping", "category": "tool", "required_level": 1, "is_core": True},
            {"slug": "user-testing", "name": "User Testing", "category": "technical", "required_level": 1, "is_core": False},
            {"slug": "visual-design", "name": "Visual Design", "category": "technical", "required_level": 1, "is_core": False},
            {"slug": "accessibility", "name": "Accessibility", "category": "technical", "required_level": 1, "is_core": False},
            {"slug": "storytelling", "name": "Storytelling", "category": "soft", "required_level": 1, "is_core": False},
            {"slug": "collaboration", "name": "Collaboration", "category": "soft", "required_level": 1, "is_core": False},
        ],
    },
]


def get_or_create_skill(db: Session, skill_data: Dict) -> SkillCatalog:
    skill = db.query(SkillCatalog).filter(SkillCatalog.slug == skill_data["slug"]).first()
    if skill:
        skill.name = skill_data["name"]
        skill.category = skill_data["category"]
        skill.description = skill_data.get("description") or skill.description
        skill.market_demand = skill_data.get("market_demand", skill.market_demand)
        skill.trend = skill_data.get("trend", skill.trend)
        skill.avg_salary_impact = skill_data.get("avg_salary_impact", skill.avg_salary_impact)
        db.add(skill)
        db.commit()
        db.refresh(skill)
        return skill

    skill = SkillCatalog(
        name=skill_data["name"],
        slug=skill_data["slug"],
        category=skill_data["category"],
        description=skill_data.get("description"),
        market_demand=skill_data.get("market_demand", "medium"),
        trend=skill_data.get("trend", "stable"),
        avg_salary_impact=skill_data.get("avg_salary_impact"),
        is_active=True,
    )
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


def seed_learning_paths(db: Session) -> None:
    """
    Seed the curated learning path definitions and required skills.
    Idempotent: updates existing paths and creates missing skills.
    """
    for path_data in LEARNING_PATH_DATA:
        path = db.query(LearningPath).filter(LearningPath.slug == path_data["slug"]).first()
        if not path:
            path = LearningPath(
                name=path_data["name"],
                slug=path_data["slug"],
                description=path_data.get("description"),
                category=path_data["category"],
                difficulty_level=path_data.get("difficulty_level"),
                duration_hours=path_data.get("duration_hours", 0.0),
                is_active=True,
            )
            db.add(path)
            db.commit()
            db.refresh(path)
        else:
            path.name = path_data["name"]
            path.description = path_data.get("description")
            path.category = path_data["category"]
            path.difficulty_level = path_data.get("difficulty_level")
            path.duration_hours = path_data.get("duration_hours", 0.0)
            path.is_active = True
            db.add(path)
            db.commit()
            db.refresh(path)

        existing_skill_links = {
            (link.skill_catalog_id): link
            for link in db.query(LearningPathSkill).filter(LearningPathSkill.learning_path_id == path.id).all()
        }

        seen_skill_ids = set()
        for order, skill_info in enumerate(path_data["skills"], start=1):
            skill = get_or_create_skill(db, skill_info)
            seen_skill_ids.add(skill.id)
            link = existing_skill_links.get(skill.id)
            if not link:
                link = LearningPathSkill(
                    learning_path_id=path.id,
                    skill_catalog_id=skill.id,
                    skill_order=order,
                    required_level=skill_info.get("required_level", 1),
                    is_core=skill_info.get("is_core", True),
                )
                db.add(link)
            else:
                link.skill_order = order
                link.required_level = skill_info.get("required_level", 1)
                link.is_core = skill_info.get("is_core", True)
                db.add(link)
            db.commit()

        stale_links = [
            link for skill_id, link in existing_skill_links.items()
            if skill_id not in seen_skill_ids
        ]
        for stale in stale_links:
            db.delete(stale)
        if stale_links:
            db.commit()


def main() -> None:
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        seed_learning_paths(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
