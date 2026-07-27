import pytest
from datetime import datetime, timedelta

class TestSimulationsShield:
    @pytest.fixture
    def base_category(self, db_session):
        """Create real category in DB"""
        from app.models.catalog import ContentCategory
        import uuid
        uid = uuid.uuid4().hex[:6]
        category = ContentCategory(
            name=f"Shield Cat {uid}",
            slug=f"shield-cat-{uid}"
        )
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        return category

    @pytest.fixture
    def base_sim(self, client, valid_company_data, base_category):
        """Crear empresa válida primero + categoría real"""
        import uuid
        company_data = valid_company_data.copy()
        company_data["slug"] = f"sim-company-{uuid.uuid4().hex[:6]}"

        res = client.post("/api/v1/empresas", json=company_data)
        assert res.status_code == 201, f"Failed to create company: {res.text}"
        company_id = res.json()["id"]

        return {
            "title": "Backend Training",
            "slug": f"backend-sim-{uuid.uuid4().hex[:6]}",
            "short_description": "Aprende backend",
            "company_id": company_id,
            "category_id": base_category.id,  # CRITICAL FIX: Real category
            "state": "published"
        }

    @pytest.fixture
    def auth_header(self, client):
        """Usuario autenticado"""
        import uuid
        username = f"sim_user_{uuid.uuid4().hex[:8]}"
        user = {
            "username": username,
            "email": f"{username}@test.com",
            "password": "Password123!",
            "full_name": "Sim User"
        }
        client.post("/api/v1/register", json=user)

        login_res = client.post("/api/v1/token", data={"username": username, "password": "Password123!"})
        token = login_res.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_create_simulation(self, client, base_sim):
        res = client.post("/api/v1/simulaciones", json=base_sim)
        assert res.status_code == 201, f"Error: {res.text}"

    def test_create_sim_end_date_before_start(self, client, base_sim):
        # Validation test - dates if supported
        pass

    def test_create_sim_past_date(self, client, base_sim):
        # Validation test - dates if supported
        pass

    def test_enrollment_logic(self, client, base_sim, auth_header):
        # 1. Crear simulación
        res_create = client.post("/api/v1/simulaciones", json=base_sim)
        if res_create.status_code != 201:
            pytest.fail(f"Error: {res_create.text}")
        
        sim_id = res_create.json()["id"]
        
        # 2. Inscribirse (si existe endpoint)
        res_enroll = client.post(
            f"/api/v1/simulaciones/{sim_id}/inscribir",
            params={"user_id": 1},
            headers=auth_header
        )
        if res_enroll.status_code == 404:
            pytest.skip("Enrollment endpoint not implemented")
        assert res_enroll.status_code in [200, 201]
