"""
Content Seed Script
Creates a full realistic Simulation with Modules, Tasks, and Resources.
Usage: python -m app.db.seeds_content
"""
import logging
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.simulations import (
    Simulation, SimulationModule, ModuleTask, 
    TaskResource, ModelAnswer
)
from app.models.empresa import Empresa
from app.models.catalog import ContentCategory

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_full_simulation(db: Session):
    logger.info("--- Sembrando Simulación Completa ---")

    # 1. Asegurar Empresa (The Content Creator)
    company = db.query(Empresa).filter(Empresa.slug == "tech-global").first()
    if not company:
        company = Empresa(
            nombre_empresa="Tech Global Corp", industria="Tecnología", ciudad="San Francisco",
            slug="tech-global",
            tipo_empresa="real_internacional",
            pais="USA",
            descripcion_corta="Leading innovation in software solutions."
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        logger.info(f"Empresa creada: {company.nombre_empresa}")

    # 2. Asegurar Categoría
    category = db.query(ContentCategory).filter(ContentCategory.slug == "software-engineering").first()
    if not category:
        category = ContentCategory(
            name="Software Engineering",
            slug="software-engineering",
            description="Development, Architecture, and DevOps"
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        logger.info(f"Categoría creada: {category.name}")

    # 3. Crear la Simulación (Si no existe)
    sim_slug = "backend-engineering-virtual-experience"
    simulation = db.query(Simulation).filter(Simulation.slug == sim_slug).first()
    
    if simulation:
        logger.info("⚠️ La simulación ya existe. Saltando creación.")
        return

    simulation = Simulation(
        title="Backend Engineering Virtual Experience",
        slug=sim_slug,
        short_description="Work as a backend engineer designing scalable APIs.",
        full_description="In this simulation, you will join the Tech Global team to rebuild their legacy payment system. You will learn about API design, Database locking strategies, and Security.",
        company_id=company.id,
        category_id=category.id,
        difficulty_level="advanced",
        estimated_hours=4.5,
        state="published",
        is_premium=False
    )
    db.add(simulation)
    db.commit()
    db.refresh(simulation)
    logger.info(f"Simulación creada: {simulation.title}")

    # --- MÓDULO 1: API Design ---
    mod1 = SimulationModule(
        simulation_id=simulation.id,
        title="Module 1: Interface Design & REST APIs",
        description="Learn how to design clean RESTful interfaces.",
        order=1,
        estimated_hours=2.0
    )
    db.add(mod1)
    db.commit()
    db.refresh(mod1)

    # Tarea 1.1: Video Intro
    task1 = ModuleTask(
        module_id=mod1.id,
        title="Briefing: The Payment Gateway Issue",
        description="Listen to the CTO explain the current bottlenecks.",
        order=1,
        task_type="video",
        instructor_name="Sarah Connor",
        instructor_role="CTO",
        estimated_minutes=10
    )
    db.add(task1)
    
    # Tarea 1.2: Submission
    task2 = ModuleTask(
        module_id=mod1.id,
        title="Design the Payment Endpoint",
        description="Create a YAML specification for the POST /payments endpoint.",
        order=2,
        task_type="submission",
        estimated_minutes=45
    )
    db.add(task2)
    db.commit()
    db.refresh(task2)

    # Recursos Tarea 1.2
    res1 = TaskResource(
        task_id=task2.id,
        name="Current_API_Docs.pdf",
        url="https://example.com/docs.pdf",
        resource_type="pdf"
    )
    db.add(res1)

    # Respuesta Modelo Tarea 1.2
    ans1 = ModelAnswer(
        task_id=task2.id,
        description="Here is the ideal OpenAPI 3.0 spec for the endpoint.",
        key_learnings=["Idempotency keys are crucial", "Use proper HTTP status codes"]
    )
    db.add(ans1)

    # --- MÓDULO 2: Database Optimization ---
    mod2 = SimulationModule(
        simulation_id=simulation.id,
        title="Module 2: Database Locking & Concurrency",
        description="Prevent double-spending using pessimistic locking.",
        order=2,
        estimated_hours=2.5
    )
    db.add(mod2)
    db.commit()
    db.refresh(mod2)

    # Tarea 2.1: Quiz
    task3 = ModuleTask(
        module_id=mod2.id,
        title="Knowledge Check: ACID Properties",
        description="Verify your understanding of database transactions.",
        order=1,
        task_type="quiz",
        estimated_minutes=15
    )
    db.add(task3)

    db.commit()
    logger.info("✅ Contenido generado: 1 Simulación, 2 Módulos, 3 Tareas.")

def main():
    db = SessionLocal()
    try:
        create_full_simulation(db)
    except Exception as e:
        logger.error(f"❌ Error sembrando contenido: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
