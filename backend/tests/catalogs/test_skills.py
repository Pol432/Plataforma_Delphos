"""
Skills Tests - FIXED VERSION
Auth fixture with robust password validation
"""
import pytest
import uuid


class TestSkillsCRUD:
    """Test Skills CRUD operations"""
    
    @pytest.fixture
    def auth_headers(self, client):
        """Create user and return auth headers"""
        uid = uuid.uuid4().hex[:6]
        
        # CRITICAL FIX: Password must be >= 8 chars (see app/schemas/user.py)
        user_data = {
            "username": f"u_{uid}",
            "email": f"e_{uid}@test.com",
            "password": "Password123!",  # FIXED: Was "Pwd" (too short)
            "full_name": "Tester"
        }
        
        # Step 1: Register
        reg = client.post("/api/v1/register", json=user_data)
        
        # CRITICAL: Assert registration success before continuing
        if reg.status_code != 201:
            print(f"\n❌ REGISTRATION FAILED: {reg.status_code}")
            print(f"Response: {reg.text}")
            pytest.fail(f"Registration failed: {reg.status_code} - {reg.text}")
        
        assert reg.status_code == 201, f"Registration failed: {reg.status_code} - {reg.text}"
        print(f"✓ User registered: {user_data['username']}")
        
        # Step 2: Login
        login = client.post("/api/v1/token", data={
            "username": user_data["username"],
            "password": user_data["password"]
        })
        
        # CRITICAL: Assert login success before accessing token
        if login.status_code != 200:
            print(f"\n❌ LOGIN FAILED: {login.status_code}")
            print(f"Response: {login.text}")
            pytest.fail(f"Login failed: {login.status_code} - {login.text}")
        
        assert login.status_code == 200, f"Login failed: {login.status_code} - {login.text}"
        
        token = login.json()["access_token"]
        print(f"✓ Token obtained: {token[:20]}...")
        
        return {"Authorization": f"Bearer {token}"}
    
    def test_create_skill(self, client, auth_headers):
        """Test: Create new skill"""
        uid = uuid.uuid4().hex[:6]
        payload = {
            "name": f"Skill {uid}",
            "description": "Test skill description",
            "category": "technical"
        }
        
        res = client.post("/api/v1/skills", json=payload, headers=auth_headers)
        
        # Expect 201 Created
        assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"
        
        data = res.json()
        assert data["name"] == f"Skill {uid}"
        assert data["category"] == "technical"
        assert data["is_active"] == True
    
    def test_list_skills(self, client, auth_headers):
        """Test: List skills (public endpoint)"""
        res = client.get("/api/v1/skills")
        
        # Public endpoint, no auth required
        assert res.status_code == 200
        assert isinstance(res.json(), list)
    
    def test_create_duplicate_skill_rejected(self, client, auth_headers):
        """Test: Duplicate skill name rejected"""
        uid = uuid.uuid4().hex[:6]
        skill_data = {
            "name": f"Unique Skill {uid}",
            "category": "technical"
        }
        
        # Create first
        res1 = client.post("/api/v1/skills", json=skill_data, headers=auth_headers)
        assert res1.status_code == 201
        
        # Try duplicate
        res2 = client.post("/api/v1/skills", json=skill_data, headers=auth_headers)
        assert res2.status_code == 400
        assert "already exists" in res2.json()["detail"].lower()
    
    def test_get_skill_by_id(self, client, auth_headers):
        """Test: Get skill by ID"""
        uid = uuid.uuid4().hex[:6]
        skill_data = {
            "name": f"Test Skill {uid}",
            "category": "technical"
        }
        
        # Create
        res = client.post("/api/v1/skills", json=skill_data, headers=auth_headers)
        assert res.status_code == 201
        skill_id = res.json()["id"]
        
        # Get by ID
        res = client.get(f"/api/v1/skills/{skill_id}")
        assert res.status_code == 200
        assert res.json()["name"] == f"Test Skill {uid}"
    
    def test_update_skill(self, client, auth_headers):
        """Test: Update skill using PUT"""
        uid = uuid.uuid4().hex[:6]
        
        # Create
        res = client.post("/api/v1/skills", json={
            "name": f"Old Name {uid}",
            "category": "tool"
        }, headers=auth_headers)
        assert res.status_code == 201
        skill_id = res.json()["id"]
        
        # Update
        update_data = {
            "name": f"New Name {uid}",
            "description": "Updated description"
        }
        
        res = client.put(f"/api/v1/skills/{skill_id}", json=update_data, headers=auth_headers)
        assert res.status_code == 200
        
        data = res.json()
        assert data["name"] == f"New Name {uid}"
        assert "Updated" in data["description"]
    
    def test_delete_skill(self, client, auth_headers):
        """Test: Soft delete skill"""
        uid = uuid.uuid4().hex[:6]
        
        # Create
        res = client.post("/api/v1/skills", json={
            "name": f"To Delete {uid}",
            "category": "technical"
        }, headers=auth_headers)
        assert res.status_code == 201
        skill_id = res.json()["id"]
        
        # Delete
        res = client.delete(f"/api/v1/skills/{skill_id}", headers=auth_headers)
        assert res.status_code == 204
        
        # Verify not in active list
        res = client.get("/api/v1/skills")
        skill_ids = [s["id"] for s in res.json()]
        assert skill_id not in skill_ids


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
