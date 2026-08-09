from datetime import datetime

from app.db.session import SessionLocal
from app.models.user_progress import UserSimulationProgress, ProgressStatus
from app.models.progress import UserSkill
from app.models.skill import Skill
from app.models.catalog import SkillCatalog
from app.models.simulations import Simulation
from app.models.user import User


def main():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == 4).first()
        if user is None:
            raise RuntimeError("User id=4 not found")

        simulation = db.query(Simulation).filter(Simulation.id == 4).first()
        if simulation is None:
            raise RuntimeError("Simulation id=4 not found")

        progress = db.query(UserSimulationProgress).filter(
            UserSimulationProgress.user_id == 4,
            UserSimulationProgress.simulation_id == 4,
        ).first()

        if progress is None:
            progress = UserSimulationProgress(
                user_id=4,
                simulation_id=4,
                status=ProgressStatus.COMPLETED,
                score=95.0,
                completion_percentage=100.0,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                last_activity_at=datetime.utcnow(),
                total_time_minutes=120,
            )
            db.add(progress)
        else:
            progress.status = ProgressStatus.COMPLETED
            progress.score = 95.0
            progress.completion_percentage = 100.0
            progress.completed_at = datetime.utcnow()
            progress.last_activity_at = datetime.utcnow()
            progress.total_time_minutes = 120

        skill_catalog_names = ["Python", "SQL", "Communication"]
        for name in skill_catalog_names:
            catalog_skill = db.query(SkillCatalog).filter(SkillCatalog.name == name).first()
            if catalog_skill is None:
                continue

            skill = db.query(Skill).filter(Skill.name == name).first()
            if skill is None:
                skill = Skill(
                    name=name,
                    category=catalog_skill.category,
                    catalog_skill_id=catalog_skill.id,
                )
                db.add(skill)
                db.flush()
            else:
                skill.catalog_skill_id = catalog_skill.id
                skill.category = catalog_skill.category

            user_skill = db.query(UserSkill).filter(
                UserSkill.user_id == 4,
                UserSkill.skill_id == skill.id,
            ).first()
            if user_skill is None:
                user_skill = UserSkill(
                    user_id=4,
                    skill_id=skill.id,
                    xp_total=1200,
                    nivel=3,
                )
                db.add(user_skill)
            else:
                user_skill.xp_total = 1200
                user_skill.nivel = 3

        db.commit()
        print("Injection completed successfully")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
