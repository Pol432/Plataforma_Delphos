"""
User Progress Tests - Complete Version with Required Fields
"""
import pytest
from app.models.user_progress import ProgressStatus


@pytest.fixture
def progress_seed_data(db_session):
    """Create test data for progress tracking with ALL required fields"""
    from app.models.user import User
    from app.models.empresa import Empresa
    from app.models.catalog import ContentCategory
    from app.models.simulations import Simulation
    from app.services.user_service import UserService

    service = UserService(db_session)

    # Create user
    user = User(
        username="progress_user",
        email="progress@test.com",
        hashed_password=service.hash_password("Password123!"),
        full_name="Progress User"
    )
    db_session.add(user)

    # Create company
    company = Empresa(
        nombre_empresa="Progress Test Co",
        slug="progress-test-co",
        industria="Tech",
        pais="Ecuador"
    )
    db_session.add(company)

    # Create category
    category = ContentCategory(name="Progress Cat", slug="progress-cat")
    db_session.add(category)
    
    db_session.commit()
    db_session.refresh(user)
    db_session.refresh(company)
    db_session.refresh(category)

    # CRITICAL: Simulation MUST have short_description
    simulation = Simulation(
        company_id=company.id,
        category_id=category.id,
        title="Progress Test Simulation",
        slug="progress-test-sim",
        short_description="Simulation for testing user progress tracking",  # REQUIRED
        state="published"
    )
    db_session.add(simulation)
    db_session.commit()
    db_session.refresh(simulation)

    return {
        "user_id": user.id,
        "simulation_id": simulation.id
    }


class TestUserProgress:
    """Test user progress tracking"""

    def test_create_progress(self, db_session, progress_seed_data):
        """Test: Create new user progress entry"""
        from app.models.user_progress import UserSimulationProgress

        progress = UserSimulationProgress(
            user_id=progress_seed_data["user_id"],
            simulation_id=progress_seed_data["simulation_id"],
            status=ProgressStatus.STARTED
        )
        db_session.add(progress)
        db_session.commit()
        db_session.refresh(progress)

        assert progress.id is not None
        assert progress.status == ProgressStatus.STARTED

    def test_update_progress_status(self, db_session, progress_seed_data):
        """Test: Update progress status"""
        from app.models.user_progress import UserSimulationProgress

        progress = UserSimulationProgress(
            user_id=progress_seed_data["user_id"],
            simulation_id=progress_seed_data["simulation_id"],
            status=ProgressStatus.STARTED
        )
        db_session.add(progress)
        db_session.commit()

        # Update status
        progress.status = ProgressStatus.COMPLETED
        db_session.commit()
        db_session.refresh(progress)

        assert progress.status == ProgressStatus.COMPLETED
