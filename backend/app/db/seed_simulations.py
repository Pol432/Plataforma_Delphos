import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
from slugify import slugify

from app.db.session import SessionLocal
from app.db.simulation_data import SIMULATION_DATA
from app.models.simulations import (
    Simulation,
    SimulationModule,
    ModuleTask,
    TaskResource,
    ModelAnswer,
)
from app.models.empresa import Empresa
from app.models.catalog import ContentCategory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_or_create_company(db: Session, company_name: str) -> Empresa:
    """Gets a company by name or creates it if it doesn't exist."""
    company = db.query(Empresa).filter(Empresa.nombre_empresa == company_name).first()
    if not company:
        logger.info(f"Company '{company_name}' not found, creating it.")
        company = Empresa(
            nombre_empresa=company_name,
            slug=slugify(company_name),
            industria="Default", # Provide default values
            pais="Default",
            descripcion_corta=f"Empresa de la simulación {company_name}"
        )
        db.add(company)
        db.flush() # Flush to get the ID for the current transaction
    return company

def get_or_create_category(db: Session, category_name: str) -> ContentCategory:
    """Gets a content category by name or creates it if it doesn't exist."""
    category = db.query(ContentCategory).filter(ContentCategory.name == category_name).first()
    if not category:
        logger.info(f"Category '{category_name}' not found, creating it.")
        category = ContentCategory(
            name=category_name,
            slug=slugify(category_name),
            description=f"Categoría para {category_name}"
        )
        db.add(category)
        db.flush() # Flush to get the ID for the current transaction
    return category

def seed_simulations(db: Session) -> None:
    """
    Populates the database with simulation data from SIMULATION_DATA.
    """
    logger.info("Starting simulation seeding process...")

    try:
        # Get existing simulation slugs to prevent duplicates
        existing_slugs = db.execute(select(Simulation.slug)).scalars().all()
        existing_slugs_set = set(existing_slugs)

        for sim_data in SIMULATION_DATA:
            simulation_details = sim_data["simulation"].copy()
            simulation_slug = simulation_details["slug"]

            if simulation_slug in existing_slugs_set:
                logger.info(f"Simulation with slug '{simulation_slug}' already exists. Skipping.")
                continue

            logger.info(f"Processing simulation: '{simulation_details['title']}'")

            # Get or create parent entities
            company = get_or_create_company(db, simulation_details.pop("company_name"))
            category = get_or_create_category(db, simulation_details.pop("category_name"))

            # Assign IDs
            simulation_details["company_id"] = company.id
            simulation_details["category_id"] = category.id
            
            # Create Simulation instance
            new_simulation = Simulation(**simulation_details)

            # Create Modules, Tasks, Resources, and ModelAnswers
            for module_data in sim_data.get("modules", []):
                module_details = module_data["module"]
                new_module = SimulationModule(**module_details)

                for task_data in module_data.get("tasks", []):
                    task_details = task_data["task"]
                    new_task = ModuleTask(**task_details)

                    for resource_details in task_data.get("resources", []):
                        new_resource = TaskResource(**resource_details)
                        new_task.resources.append(new_resource)

                    if "model_answer" in task_data:
                        model_answer_details = task_data["model_answer"]
                        new_model_answer = ModelAnswer(**model_answer_details)
                        new_task.model_answer = new_model_answer
                    
                    new_module.tasks.append(new_task)
                
                new_simulation.modules.append(new_module)

            db.add(new_simulation)
            existing_slugs_set.add(simulation_slug)

        db.commit()
        logger.info("Successfully committed all data to the database.")
    except Exception as e:
        logger.error(f"An error occurred during seeding: {e}")
        db.rollback()
        raise

def main() -> None:
    """
    Main function to run the seeder.
    """
    logger.info("Initializing database session for seeding.")
    db = SessionLocal()
    try:
        seed_simulations(db)
    finally:
        db.close()
    logger.info("Seeding process finished.")

if __name__ == "__main__":
    main()
