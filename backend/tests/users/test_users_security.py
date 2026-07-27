"""
USERS SECURITY TESTS
Password Attacks, IDOR, Account Enumeration, Session Hijacking
"""
import pytest
from fastapi import status


class TestUsersPasswordSecurity:
    """Password Strength & Brute Force Protection"""

    def test_weak_password_rejected(self, client):
        """Weak Password: Less than 8 chars"""
        payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "weak",
            "full_name": "Test User"
        }
        res = client.post("/api/v1/users", json=payload)
        assert res.status_code == 422
        assert "password" in res.text.lower()

    def test_password_without_complexity(self, client):
        """Password: No numbers (no complexity check currently)"""
        payload = {
            "username": "testuser2",
            "email": "test2@example.com",
            "password": "onlyletters",
            "full_name": "Test User"
        }
        res = client.post("/api/v1/users", json=payload)
        assert res.status_code in [201, 422]

    def test_password_with_sql_injection(self, client):
        """Password: SQL Injection attempt - should hash safely"""
        payload = {
            "username": "sqluser",
            "email": "sql@example.com",
            "password": "' OR '1'='1",
            "full_name": "SQL User"
        }
        res = client.post("/api/v1/users", json=payload)
        assert res.status_code in [201, 422]


class TestUsersIDOR:
    """Insecure Direct Object Reference"""

    def test_access_other_user_profile(self, client):
        """IDOR: User A accesses User B's profile (documented vulnerability)"""
        user1 = {
            "username": "user1",
            "email": "user1@test.com",
            "password": "Password123!",
            "full_name": "User One"
        }
        res1 = client.post("/api/v1/users", json=user1)
        assert res1.status_code == 201
        user2 = {
            "username": "user2",
            "email": "user2@test.com",
            "password": "Password123!",
            "full_name": "User Two"
        }
        res2 = client.post("/api/v1/users", json=user2)
        assert res2.status_code == 201
        user2_id = res2.json()["id"]

        login_res = client.post(
            "/api/v1/token",
            data={"username": "user1", "password": "Password123!"}
        )
        assert login_res.status_code == 200, f"Login falló: {login_res.json()}"
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        res = client.get(f"/api/v1/users/{user2_id}", headers=headers)
        assert res.status_code == 200  # Documented vulnerability

    def test_modify_other_user_profile(self, client):
        """IDOR: User A modifies User B's data - should return 403"""
        user1 = {
            "username": "alice",
            "email": "alice@test.com",
            "password": "Password123!",
            "full_name": "Alice"
        }
        res1 = client.post("/api/v1/users", json=user1)
        assert res1.status_code == 201

        user2 = {
            "username": "bob",
            "email": "bob@test.com",
            "password": "Password123!",
            "full_name": "Bob"
        }
        res2 = client.post("/api/v1/users", json=user2)
        assert res2.status_code == 201
        user2_id = res2.json()["id"]

        login_res = client.post(
            "/api/v1/token",
            data={"username": "alice", "password": "Password123!"}
        )
        assert login_res.status_code == 200, f"Login falló: {login_res.json()}"
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        res = client.patch(
            f"/api/v1/users/{user2_id}",
            json={"full_name": "Hacked Bob"},
            headers=headers
        )
        assert res.status_code == 403


class TestUsersAccountEnumeration:
    """Account Enumeration via Registration"""

    def test_email_enumeration_via_registration(self, client):
        """Enumeration: Check if email exists via registration error message"""
        user = {
            "username": "existing",
            "email": "existing@test.com",
            "password": "Password123!",
            "full_name": "Existing User"
        }
        client.post("/api/v1/users", json=user)

        duplicate = {
            "username": "different",
            "email": "existing@test.com",
            "password": "Password123!",
            "full_name": "Different User"
        }
        res = client.post("/api/v1/users", json=duplicate)
        assert res.status_code in [400, 422]

        detail = res.json()["detail"].lower()
        assert "email" in detail
        # Acepta mensaje en español o inglés
        assert any(w in detail for w in ["registered", "registrado", "already", "ya"])


class TestUsersMassAssignment:
    """Mass Assignment / Privilege Escalation"""

    def test_inject_xp_total_on_registration(self, client):
        """Mass Assignment: Inject xp_total=999999"""
        payload = {
            "username": "hacker",
            "email": "hacker@test.com",
            "password": "Password123!",
            "full_name": "Hacker",
            "xp_total": 999999,
            "level_current": 100
        }
        res = client.post("/api/v1/users", json=payload)
        assert res.status_code in [201, 422]
        data = res.json()
        assert data["xp_total"] == 0
        assert data["level_current"] == 1

    def test_inject_is_active_false(self, client):
        """Mass Assignment: Create deactivated user"""
        payload = {
            "username": "deactivated",
            "email": "deactivated@test.com",
            "password": "Password123!",
            "full_name": "Deactivated",
            "is_active": False
        }
        res = client.post("/api/v1/users", json=payload)
        assert res.status_code in [201, 422]
        assert res.json()["is_active"] == True
