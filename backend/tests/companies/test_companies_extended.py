"""
Companies Extended Tests - Search, Pagination, Validation
Objetivo: Aumentar cobertura a >200 tests totales
"""
import pytest
import uuid
from fastapi import status


class TestCompaniesSearch:
    """Test search functionality"""

    @pytest.fixture
    def sample_companies(self, client, db_session):
        """Create sample companies for search tests"""
        from app.models.empresa import Empresa
        
        companies = [
            Empresa(
                nombre_empresa="TechCorp Solutions",
                slug="techcorp-solutions",
                industria="Technology",
                pais="Ecuador"
            ),
            Empresa(
                nombre_empresa="FinTech Innovators",
                slug="fintech-innovators",
                industria="Finance",
                pais="Ecuador"
            ),
            Empresa(
                nombre_empresa="Global Tech Partners",
                slug="global-tech-partners",
                industria="Technology",
                pais="Ecuador"
            ),
        ]
        
        for company in companies:
            db_session.add(company)
        
        db_session.commit()
        
        for company in companies:
            db_session.refresh(company)
        
        return companies

    def test_search_case_insensitive(self, client, sample_companies):
        """Test: Search is case insensitive"""
        # Search with lowercase
        res = client.get("/api/v1/empresas/search?q=tech")
        assert res.status_code == 200
        
        results = res.json()
        assert len(results) >= 2  # Should find TechCorp and Global Tech

    def test_search_partial_match(self, client, sample_companies):
        """Test: Search matches partial strings"""
        res = client.get("/api/v1/empresas/search?q=inn")
        assert res.status_code == 200
        
        results = res.json()
        # Should find "FinTech Innovators"
        assert any("Innovators" in c["nombre_empresa"] for c in results)

    def test_search_by_slug(self, client, sample_companies):
        """Test: Search also matches slug"""
        res = client.get("/api/v1/empresas/search?q=fintech")
        assert res.status_code == 200
        
        results = res.json()
        assert len(results) >= 1

    def test_search_limit_respected(self, client, sample_companies):
        """Test: Search respects limit parameter"""
        res = client.get("/api/v1/empresas/search?q=tech&limit=1")
        assert res.status_code == 200
        
        results = res.json()
        assert len(results) <= 1

    def test_search_no_results(self, client, sample_companies):
        """Test: Search returns empty list if no matches"""
        res = client.get("/api/v1/empresas/search?q=nonexistent999")
        assert res.status_code == 200
        assert res.json() == []


class TestCompaniesPagination:
    """Test pagination functionality"""

    @pytest.fixture
    def many_companies(self, client, db_session):
        """Create many companies for pagination tests"""
        from app.models.empresa import Empresa
        
        companies = []
        for i in range(25):
            uid = uuid.uuid4().hex[:8]
            company = Empresa(
                nombre_empresa=f"Company {i:02d} {uid}",
                slug=f"company-{i:02d}-{uid}",
                industria="Tech",
                pais="Ecuador"
            )
            db_session.add(company)
            companies.append(company)
        
        db_session.commit()
        return companies

    def test_pagination_default(self, client, many_companies):
        """Test: Default pagination returns first page"""
        res = client.get("/api/v1/empresas")
        assert res.status_code == 200
        
        results = res.json()
        assert len(results) >= 10  # Should have at least 10 companies

    def test_pagination_skip(self, client, many_companies):
        """Test: Skip parameter works correctly"""
        # Get first page
        res1 = client.get("/api/v1/empresas?skip=0&limit=5")
        page1 = res1.json()
        
        # Get second page
        res2 = client.get("/api/v1/empresas?skip=5&limit=5")
        page2 = res2.json()
        
        # Should be different companies
        page1_ids = {c["id"] for c in page1}
        page2_ids = {c["id"] for c in page2}
        
        assert page1_ids.isdisjoint(page2_ids), "Pages should have different companies"

    def test_pagination_limit(self, client, many_companies):
        """Test: Limit parameter works correctly"""
        res = client.get("/api/v1/empresas?limit=3")
        assert res.status_code == 200
        
        results = res.json()
        assert len(results) == 3


class TestCompaniesValidation:
    """Test field validation"""

    def test_create_empty_name(self, client):
        """Test: Empty name should be rejected"""
        company = {
            "nombre_empresa": "",
            "slug": "empty-name",
            "industria": "Tech",
            "pais": "Ecuador"
        }
        
        res = client.post("/api/v1/empresas", json=company)
        assert res.status_code == 422

    def test_create_missing_required_field(self, client):
        """Test: Missing required field should be rejected"""
        company = {
            "nombre_empresa": "Test Company",
            "slug": "test-company"
            # Missing industria (required)
        }
        
        res = client.post("/api/v1/empresas", json=company)
        assert res.status_code == 422

    def test_create_too_long_name(self, client):
        """Test: Name exceeding max length should be rejected"""
        uid = uuid.uuid4().hex[:8]
        company = {
            "nombre_empresa": "A" * 250,  # Exceeds 200 max
            "slug": f"long-name-{uid}",
            "industria": "Tech",
            "pais": "Ecuador"
        }
        
        res = client.post("/api/v1/empresas", json=company)
        assert res.status_code == 422

    def test_get_nonexistent_id(self, client):
        """Test: Get non-existent company returns 404"""
        res = client.get("/api/v1/empresas/999999")
        assert res.status_code == 404

    def test_get_nonexistent_slug(self, client):
        """Test: Get non-existent slug returns 404"""
        res = client.get("/api/v1/empresas/slug/nonexistent-slug-999")
        assert res.status_code == 404

    def test_update_nonexistent_company(self, client):
        """Test: Update non-existent company returns 404"""
        res = client.put("/api/v1/empresas/999999", json={"pais": "Peru"})
        assert res.status_code == 404

    def test_delete_nonexistent_company(self, client):
        """Test: Delete non-existent company returns 404"""
        res = client.delete("/api/v1/empresas/999999")
        assert res.status_code == 404
