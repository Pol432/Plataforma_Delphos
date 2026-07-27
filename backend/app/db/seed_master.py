import sys, os, logging
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.session import SessionLocal
from app.models.catalog import ContentCategory, SkillCatalog
from app.models.simulations import Simulation, SimulationModule, ModuleTask
from app.models.user import User
from app.models.empresa import Empresa
from app.models.oracle import Archetype
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def get_or_create(db, model, unique_field, unique_value, **kwargs):
    filter_kwargs = {unique_field: unique_value}
    instance = db.query(model).filter_by(**filter_kwargs).first()
    if instance: return instance
    instance = model(**filter_kwargs, **kwargs)
    try:
        db.add(instance); db.commit(); db.refresh(instance)
        return instance
    except IntegrityError:
        db.rollback()
        if "title" in kwargs: return db.query(model).filter_by(title=kwargs["title"]).first()
        return None

def seed_master(db):
    logger.info("==================================================")
    logger.info("🌌 EJECUTANDO SEEDER MAESTRO (DATOS + MVP + HIPER)")
    logger.info("==================================================")

    # 1. USUARIOS
    users_data = [
        {"u": "alexander.lopez", "e": "alexander.lopez@delphos.com", "n": "Alexander L.", "xp": 14500, "lvl": 12, "streak": 45},
        {"u": "diego.m", "e": "diego.m@delphos.com", "n": "Diego M.", "xp": 19500, "lvl": 15, "streak": 60},
        {"u": "luis.t", "e": "luis.t@delphos.com", "n": "Luis T.", "xp": 34000, "lvl": 20, "streak": 120},
        {"u": "maria.perez", "e": "maria.perez@delphos.com", "n": "Maria P.", "xp": 8200, "lvl": 7, "streak": 12},
        {"u": "carlos.r", "e": "carlos.r@delphos.com", "n": "Carlos R.", "xp": 12100, "lvl": 10, "streak": 30}
    ]
    pass_hash = get_password_hash("Campus2026!")
    for u in users_data:
        user = db.query(User).filter(User.email == u["e"]).first()
        if not user:
            user = User(username=u["u"], email=u["e"], full_name=u["n"], hashed_password=pass_hash, is_active=True)
            db.add(user)
        user.xp_total = u["xp"]; user.level_current = u["lvl"]; user.streak_days = u["streak"]
        db.commit()
    logger.info("✅ Usuarios veteranos listos.")

    # 2. CATEGORÍAS Y HABILIDADES
    cats = [
        ("ia", "Inteligencia Artificial"), ("dev", "Desarrollo de Software"), ("cloud", "Cloud & DevOps"),
        ("data", "Data Analytics"), ("cyber", "Ciberseguridad"), ("design", "UX/UI Design"), ("negocios", "Negocios")
    ]
    cats_db = {}
    for slug, name in cats:
        c = get_or_create(db, ContentCategory, "slug", slug, name=name, description=f"Módulo de {name}", is_active=True)
        if c: cats_db[slug] = c.id

    skills = [("python", "Python", "technical"), ("react", "React", "technical"), ("aws", "AWS", "technical"), ("figma", "Figma", "tool")]
    for slug, name, cat in skills:
        get_or_create(db, SkillCatalog, "slug", slug, name=name, category=cat, is_active=True)

    # 3. MISIONES (CORTAS Y LARGAS)
    default_company = get_or_create(db, Empresa, 'nombre_empresa', 'Delphos Academy', slug='delphos-academy', tipo_empresa='educacion', industria='Tecnología', pais='Global', esta_activo=True)
    missions = [
        ("bootcamp-ai", "Especialización: AI & LLMs", "ia", "advanced", 40.0),
        ("arquitecto-aws", "Certificación AWS", "cloud", "advanced", 60.0),
        ("microservicios", "Migración a Microservicios", "dev", "intermediate", 15.0),
        ("design-system", "Creación de Design System", "design", "advanced", 25.0)
    ]
    for slug, title, cat_slug, diff, horas in missions:
        if cat_slug not in cats_db: continue
        sim = get_or_create(db, Simulation, "slug", slug, title=title, short_description=title, full_description="Contenido profundo.", category_id=cats_db[cat_slug], company_id=default_company.id, difficulty_level=diff, estimated_hours=horas, state="published", is_premium=True)
        if not sim: continue
        
        # Módulos y tareas
        if not db.query(SimulationModule).filter_by(simulation_id=sim.id).first():
            for i in range(1, 4):
                mod = SimulationModule(simulation_id=sim.id, title=f"Módulo {i}", order=i, estimated_hours=horas/3)
                db.add(mod); db.commit(); db.refresh(mod)
                db.add_all([
                    ModuleTask(module_id=mod.id, title="Video Clase", order=1, task_type="video", estimated_minutes=30),
                    ModuleTask(module_id=mod.id, title="Laboratorio", order=2, task_type="interactive", estimated_minutes=60)
                ])
                db.commit()
    logger.info("✅ Catálogo de misiones hiper-realistas poblado.")

    # 4. COMUNIDAD (ESTILO REDDIT)
    try:
        db.execute(text("CREATE TABLE IF NOT EXISTS community_channels (id SERIAL PRIMARY KEY, name VARCHAR(100) UNIQUE, category VARCHAR(100))"))
        db.execute(text("CREATE TABLE IF NOT EXISTS community_messages (id SERIAL PRIMARY KEY, channel_id INTEGER, user_email VARCHAR(100), content TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"))
        db.commit()

        for n, c in [("general", "general"), ("entrevistas-tech", "networking"), ("ofertas-laborales", "networking")]:
            db.execute(text("INSERT INTO community_channels (name, category) VALUES (:n, :c) ON CONFLICT DO NOTHING"), {"n": n, "c": c})
        db.commit()

        cid = db.execute(text("SELECT id FROM community_channels WHERE name = 'entrevistas-tech'")).fetchone()
        if cid:
            db.execute(text("DELETE FROM community_messages WHERE channel_id = :cid"), {"cid": cid[0]})
            mensajes = [
                ("carlos.r@delphos.com", "¿Alguien ha hecho la técnica para Mercado Libre?"),
                ("luis.t@delphos.com", "Sí, enfócate en Árboles y Grafos. ¡Éxitos!")
            ]
            for email, msg in mensajes:
                db.execute(text("INSERT INTO community_messages (channel_id, user_email, content) VALUES (:cid, :e, :m)"), {"cid": cid[0], "e": email, "m": msg})
            db.commit()
        logger.info("✅ Foros y chats creados.")
    except Exception as e:
        logger.warning(f"Error en BD de comunidad: {e}")
        db.rollback()

    logger.info("==================================================")
    logger.info("🚀 BASE DE DATOS MAESTRA TOTALMENTE CONFIGURADA")
    logger.info("==================================================")

if __name__ == "__main__":
    db = SessionLocal()
    try: seed_master(db)
    finally: db.close()
