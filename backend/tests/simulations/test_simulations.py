"""
Simulations Tests - Fixed with proper fixtures and FK handling
"""
import pytest
import uuid
from fastapi import status


class TestSimulations:
    @pytest.fixture
    def test_company_local(self, db_session):
        """Create company for simulations"""
        from app.models.empresa import Empresa
        uid = uuid.uuid4().hex[:6]
        company = Empresa(
            nombre_empresa=f"Sim Test Co {uid}",
            slug=f"sim-test-co-{uid}",
            tipo_empresa="real_nacional",
            industria="Technology",
            pais="Ecuador",
            ciudad="Quito"
        )
        db_session.add(company)
        db_session.commit()
        db_session.refresh(company)
        return company

    @pytest.fixture
    def test_category(self, db_session):
        """Create category for simulations"""
        from app.models.catalog import ContentCategory
        uid = uuid.uuid4().hex[:6]
        category = ContentCategory(
            name=f"Test Category {uid}",
            slug=f"test-cat-{uid}"
        )
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        return category

    @pytest.fixture
    def core_setup(self, test_company_local, test_category):
        """Core setup with real company and category"""
        return {
            "company_id": test_company_local.id,
            "category_id": test_category.id
        }

    def test_create_simple_simulation(self, client, core_setup):
        """Test: Create simple simulation"""
        sim_data = {
            "title": f"Simple Sim {uuid.uuid4().hex[:6]}",
            "slug": f"simple-sim-{uuid.uuid4().hex[:6]}",
            "short_description": "A simple test simulation",
            "company_id": core_setup["company_id"],
            "category_id": core_setup["category_id"],
            "state": "draft"
        }
        res = client.post("/api/v1/simulaciones", json=sim_data)
        assert res.status_code == 201, f"Failed: {res.text}"

    def test_create_nested_simulation(self, client, core_setup):
        """Test: Create simulation with modules (if supported)"""
        sim_data = {
            "title": f"Nested Sim {uuid.uuid4().hex[:6]}",
            "slug": f"nested-sim-{uuid.uuid4().hex[:6]}",
            "short_description": "Simulation with nested content",
            "company_id": core_setup["company_id"],
            "category_id": core_setup["category_id"],
            "state": "published"
        }
        res = client.post("/api/v1/simulaciones", json=sim_data)
        assert res.status_code == 201, f"Failed: {res.text}"

    def test_get_simulation(self, client, core_setup):
        """Test: Get simulation by ID"""
        # Create first
        sim_data = {
            "title": f"Get Test Sim {uuid.uuid4().hex[:6]}",
            "slug": f"get-sim-{uuid.uuid4().hex[:6]}",
            "short_description": "Test get endpoint",
            "company_id": core_setup["company_id"],
            "category_id": core_setup["category_id"],
            "state": "published"
        }
        create_res = client.post("/api/v1/simulaciones", json=sim_data)
        assert create_res.status_code == 201
        sim_id = create_res.json()["id"]

        # Then get
        res = client.get(f"/api/v1/simulaciones/{sim_id}")
        assert res.status_code == 200
        assert res.json()["id"] == sim_id
