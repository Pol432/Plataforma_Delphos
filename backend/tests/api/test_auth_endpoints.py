"""
Auth & Users Endpoints Tests
Comprehensive test suite for authentication and user management
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.main import app
from app.api.deps import get_db


# ============================================================================
# TEST DATABASE SETUP
# ============================================================================

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def test_db():
    """Create fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    """FastAPI test client"""
    return TestClient(app)


# ============================================================================
# TEST DATA
# ============================================================================

VALID_USER_DATA = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User",
    "phone": "+593987654321",
    "gender": "male",
    "city_id": 1
}

VALID_USER_DATA_2 = {
    "username": "anotheruser",
    "email": "another@example.com",
    "password": "AnotherPass456!",
    "full_name": "Another User"
}


# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

class TestAuthentication:
    """Test suite for auth endpoints"""
    
    def test_register_user_success(self, client):
        """POST /api/v1/register - Successful registration"""
        response = client.post("/api/v1/register", json=VALID_USER_DATA)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == VALID_USER_DATA["username"]
        assert data["email"] == VALID_USER_DATA["email"]
        assert "hashed_password" not in data
        assert "password" not in data
        assert data["is_active"] is True
        assert data["xp_total"] == 0
        assert data["level_current"] == 1
    
    def test_register_duplicate_email(self, client):
        """POST /api/v1/register - Reject duplicate email"""
        client.post("/api/v1/register", json=VALID_USER_DATA)
        
        duplicate_data = VALID_USER_DATA.copy()
        duplicate_data["username"] = "different_username"
        
        response = client.post("/api/v1/register", json=duplicate_data)
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()
    
    def test_register_duplicate_username(self, client):
        """POST /api/v1/register - Reject duplicate username"""
        client.post("/api/v1/register", json=VALID_USER_DATA)
        
        duplicate_data = VALID_USER_DATA.copy()
        duplicate_data["email"] = "different@example.com"
        
        response = client.post("/api/v1/register", json=duplicate_data)
        assert response.status_code == 400
        assert "username" in response.json()["detail"].lower()
    
    def test_login_success(self, client):
        """POST /api/v1/token - Successful login"""
        client.post("/api/v1/register", json=VALID_USER_DATA)
        
        response = client.post(
            "/api/v1/token",
            data={
                "username": VALID_USER_DATA["username"],
                "password": VALID_USER_DATA["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 20
    
    def test_login_with_email(self, client):
        """POST /api/v1/token - Login with email instead of username"""
        client.post("/api/v1/register", json=VALID_USER_DATA)
        
        response = client.post(
            "/api/v1/token",
            data={
                "username": VALID_USER_DATA["email"],  # Use email
                "password": VALID_USER_DATA["password"]
            }
        )
        
        assert response.status_code == 200
    
    def test_login_wrong_password(self, client):
        """POST /api/v1/token - Reject wrong password"""
        client.post("/api/v1/register", json=VALID_USER_DATA)
        
        response = client.post(
            "/api/v1/token",
            data={
                "username": VALID_USER_DATA["username"],
                "password": "WrongPassword123!"
            }
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, client):
        """POST /api/v1/token - Reject nonexistent user"""
        response = client.post(
            "/api/v1/token",
            data={
                "username": "nonexistent",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401


# ============================================================================
# PROTECTED ROUTES TESTS
# ============================================================================

class TestProtectedRoutes:
    """Test authentication requirements"""
    
    def test_get_me_without_token(self, client):
        """GET /api/v1/users/me - Reject unauthenticated request"""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401
    
    def test_get_me_with_invalid_token(self, client):
        """GET /api/v1/users/me - Reject invalid token"""
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        assert response.status_code == 401
    
    def test_get_me_success(self, client):
        """GET /api/v1/users/me - Return authenticated user"""
        # Register and login
        client.post("/api/v1/register", json=VALID_USER_DATA)
        login_response = client.post(
            "/api/v1/token",
            data={
                "username": VALID_USER_DATA["username"],
                "password": VALID_USER_DATA["password"]
            }
        )
        token = login_response.json()["access_token"]
        
        # Get profile
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == VALID_USER_DATA["username"]
        assert data["email"] == VALID_USER_DATA["email"]


# ============================================================================
# USER CRUD TESTS
# ============================================================================

class TestUserCRUD:
    """Test user CRUD operations"""
    
    def test_update_my_profile(self, client):
        """PUT /api/v1/users/me - Update own profile"""
        # Register and login
        client.post("/api/v1/register", json=VALID_USER_DATA)
        login_response = client.post(
            "/api/v1/token",
            data={
                "username": VALID_USER_DATA["username"],
                "password": VALID_USER_DATA["password"]
            }
        )
        token = login_response.json()["access_token"]
        
        # Update profile
        update_data = {
            "full_name": "Updated Name",
            "phone": "+593999888777"
        }
        response = client.put(
            "/api/v1/users/me",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["phone"] == "+593999888777"
    
    def test_cannot_update_other_user(self, client):
        """PUT /api/v1/users/{id} - Prevent updating other users"""
        # Create two users
        client.post("/api/v1/register", json=VALID_USER_DATA)
        client.post("/api/v1/register", json=VALID_USER_DATA_2)
        
        # Login as first user
        login_response = client.post(
            "/api/v1/token",
            data={
                "username": VALID_USER_DATA["username"],
                "password": VALID_USER_DATA["password"]
            }
        )
        token = login_response.json()["access_token"]
        
        # Try to update second user (ID 2)
        response = client.put(
            "/api/v1/users/2",
            json={"full_name": "Hacked Name"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
    
    def test_list_users_requires_auth(self, client):
        """GET /api/v1/users - Require authentication"""
        response = client.get("/api/v1/users")
        assert response.status_code == 401
    
    def test_list_users_success(self, client):
        """GET /api/v1/users - List users when authenticated"""
        client.post("/api/v1/register", json=VALID_USER_DATA)
        login_response = client.post(
            "/api/v1/token",
            data={
                "username": VALID_USER_DATA["username"],
                "password": VALID_USER_DATA["password"]
            }
        )
        token = login_response.json()["access_token"]
        
        response = client.get(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1


# ============================================================================
# EDGE CASES & SECURITY TESTS
# ============================================================================

class TestSecurityEdgeCases:
    """Test security edge cases"""
    
    def test_register_weak_password(self, client):
        """POST /api/v1/register - Reject weak password"""
        weak_data = VALID_USER_DATA.copy()
        weak_data["password"] = "123"  # Too short
        
        response = client.post("/api/v1/register", json=weak_data)
        assert response.status_code == 422
    
    def test_register_invalid_email(self, client):
        """POST /api/v1/register - Reject invalid email format"""
        invalid_data = VALID_USER_DATA.copy()
        invalid_data["email"] = "not-an-email"
        
        response = client.post("/api/v1/register", json=invalid_data)
        assert response.status_code == 422
    
    def test_token_expiration_format(self, client):
        """POST /api/v1/token - Token has proper JWT structure"""
        client.post("/api/v1/register", json=VALID_USER_DATA)
        response = client.post(
            "/api/v1/token",
            data={
                "username": VALID_USER_DATA["username"],
                "password": VALID_USER_DATA["password"]
            }
        )
        
        token = response.json()["access_token"]
        # JWT format: header.payload.signature
        parts = token.split(".")
        assert len(parts) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
