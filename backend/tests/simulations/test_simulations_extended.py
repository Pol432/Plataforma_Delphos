"""
Simulations Extended Tests - Relationships, Integrity
FIXED: Syntax errors resolved & Clean FK handling
"""
import pytest
import uuid
from sqlalchemy.exc import IntegrityError

class TestSimulationCompanyRelationship:
    """Test simulation-company relationship"""

    def test_create_simulation_for_existing_company(self, client, db_session):
        from app.models.empresa import Empresa
        from app.models.catalog import ContentCategory
        from app.models.simulations import Simulation

        # Create company & category
        uid = uuid.uuid4().hex[:8]
        company = Empresa(
            nombre_empresa=f"Sim Co {uid}",
            slug=f"sim-co-{uid}",
            industria="Tech",
            pais="Ecuador"
        )
        category = ContentCategory(
            name=f"Cat {uid}",
            slug=f"cat-{uid}"
        )
        db_session.add_all([company, category])
        db_session.commit()
        db_session.refresh(company)
        db_session.refresh(category)

        # Create valid sim
        sim = Simulation(
            company_id=company.id,
            category_id=category.id,
            title=f"Test Sim {uid}",
            slug=f"test-sim-{uid}",
            short_description="Desc",
            state="draft"
        )
        db_session.add(sim)
        db_session.commit()
        assert sim.id is not None

    def test_create_simulation_nonexistent_company(self, db_session):
        """Test: Creating simulation for non-existent company should fail"""
        from app.models.simulations import Simulation
        from app.models.catalog import ContentCategory

        # Create category first
        uid = uuid.uuid4().hex[:8]
        category = ContentCategory(
            name=f"Cat2 {uid}",
            slug=f"cat2-{uid}"
        )
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        # Try to create simulation with non-existent company_id
        sim = Simulation(
            company_id=999999,
            category_id=category.id,
            title="Invalid Sim",
            slug=f"invalid-sim-{uid}",
            short_description="Should fail",
            state="draft"
        )
        db_session.add(sim)

        # CRITICAL FIX: Clean syntax for exception handling
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()

    def test_delete_company_with_simulations(self, db_session):
        from app.models.empresa import Empresa
        from app.models.simulations import Simulation
        from app.models.catalog import ContentCategory
        
        uid = uuid.uuid4().hex[:8]
        company = Empresa(nombre_empresa=f"Del {uid}", slug=f"del-{uid}", industria="T", pais="E")
        category = ContentCategory(name=f"Cat3 {uid}", slug=f"cat3-{uid}")
        db_session.add_all([company, category])
        db_session.commit()
        db_session.refresh(company)
        db_session.refresh(category)

        sim = Simulation(
            company_id=company.id,
            category_id=category.id,
            title=f"Sim Del {uid}",
            slug=f"sim-del-{uid}",
            short_description="Desc",
            state="published"
        )
        db_session.add(sim)
        db_session.commit()

        # Soft delete
        company.esta_activo = False
        db_session.commit()
        
        # Sim should still exist
        db_session.refresh(sim)
        assert sim.id is not None


class TestSimulationStates:
    def test_create_draft_simulation(self, db_session):
        from app.models.empresa import Empresa
        from app.models.catalog import ContentCategory
        from app.models.simulations import Simulation
        
        uid = uuid.uuid4().hex[:8]
        company = Empresa(nombre_empresa=f"Drft {uid}", slug=f"drft-{uid}", industria="T", pais="E")
        category = ContentCategory(name=f"Cat4 {uid}", slug=f"cat4-{uid}")
        db_session.add_all([company, category])
        db_session.commit()
        db_session.refresh(company)
        db_session.refresh(category)

        sim = Simulation(
            company_id=company.id,
            category_id=category.id,
            title=f"Draft {uid}",
            slug=f"draft-{uid}",
            short_description="Desc",
            state="draft"
        )
        db_session.add(sim)
        db_session.commit()
        assert sim.state == "draft"

    def test_publish_simulation(self, db_session):
        from app.models.empresa import Empresa
        from app.models.catalog import ContentCategory
        from app.models.simulations import Simulation
        
        uid = uuid.uuid4().hex[:8]
        company = Empresa(nombre_empresa=f"Pub {uid}", slug=f"pub-{uid}", industria="T", pais="E")
        category = ContentCategory(name=f"Cat5 {uid}", slug=f"cat5-{uid}")
        db_session.add_all([company, category])
        db_session.commit()
        db_session.refresh(company)
        db_session.refresh(category)

        sim = Simulation(
            company_id=company.id,
            category_id=category.id,
            title=f"Pub {uid}",
            slug=f"pub-{uid}",
            short_description="Desc",
            state="draft"
        )
        db_session.add(sim)
        db_session.commit()
        
        sim.state = "published"
        db_session.commit()
        assert sim.state == "published"
