"""
UNIVERSITIES SHIELD SUITE
Coverage: CRUD, Domain Validation, Duplicates, SQL Injection
"""
import pytest
from fastapi import status

class TestUniversitiesShield:
    
    @pytest.fixture
    def base_uni(self):
        import uuid
        return {
            "nombre": f"Universidad Test {uuid.uuid4()}",
            "slug": f"uni-test-{uuid.uuid4()}",
            "dominio": "shield.edu.ec",
            "tipo": "Privada",
            "pais": "Ecuador",
            "ciudad": "Quito",
            "direccion": "Av. Testing 123",
            "es_partner": True
        }

    def test_create_university(self, client, base_uni):
        # FIX: Slash final
        res = client.post("/api/v1/universities/", json=base_uni)
        assert res.status_code == 201

    def test_read_universities(self, client):
        # FIX: Slash final
        res = client.get("/api/v1/universities/")
        assert res.status_code == 200

    def test_create_uni_invalid_domain(self, client, base_uni):
        payload = base_uni.copy()
        payload["dominio"] = "not-a-domain"
        res = client.post("/api/v1/universities/", json=payload)
        assert res.status_code == 422

    def test_create_uni_duplicate_slug(self, client, base_uni):
        client.post("/api/v1/universities/", json=base_uni)
        res = client.post("/api/v1/universities/", json=base_uni)
        assert res.status_code == 400 

    def test_sec_sqli_search(self, client):
        res = client.get("/api/v1/universities/search?q=admin' OR '1'='1")
        assert res.status_code == 200
    
    def test_sec_xss_name(self, client, base_uni):
        payload = base_uni.copy()
        payload["nombre"] = "<script>alert('hacked')</script>"
        res = client.post("/api/v1/universities/", json=payload)
        assert res.status_code in [201, 422] 
