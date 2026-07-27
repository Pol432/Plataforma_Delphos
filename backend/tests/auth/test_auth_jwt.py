"""
AUTH JWT SECURITY TESTS - Fixed for python-jose
"""
import pytest
from fastapi import status
from datetime import datetime, timedelta
from jose import jwt  # FIX: Usar python-jose en lugar de PyJWT
from app.core.security import SECRET_KEY, ALGORITHM


class TestJWTTampering:
    """Test JWT tampering and signature validation"""

    def test_tampered_token_rejected(self, client):
        """Test: Tampered token should be rejected"""
        # 1. Get valid token
        user = {
            "username": "jwtuser",
            "email": "jwt@test.com",
            "password": "Password123!",
            "full_name": "JWT User"
        }
        client.post("/api/v1/users", json=user)
        login_res = client.post("/api/v1/token", data={
            "username": "jwtuser",
            "password": "Password123!"
        })
        token = login_res.json()["access_token"]

        # 2. Tamper with token (modify last character)
        tampered_token = token[:-10] + "HACKED" + token[-4:]
        headers = {"Authorization": f"Bearer {tampered_token}"}

        # 3. Should be rejected
        res = client.get("/api/v1/users/me", headers=headers)
        assert res.status_code == 401

    def test_token_with_wrong_secret(self, client):
        """Test: Token signed with wrong secret should be rejected"""
        fake_secret = "wrong-secret-key"
        payload = {
            "sub": "hacker",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        fake_token = jwt.encode(payload, fake_secret, algorithm="HS256")
        headers = {"Authorization": f"Bearer {fake_token}"}

        res = client.get("/api/v1/users/me", headers=headers)
        assert res.status_code == 401

    def test_token_without_signature(self, client):
        """Test: Unsigned token should be rejected"""
        payload = {"sub": "hacker"}
        
        # python-jose doesn't support algorithm="none", so we manually create invalid token
        # This simulates an attacker trying to bypass signature verification
        import base64
        import json
        
        header = base64.urlsafe_b64encode(json.dumps({"alg": "none"}).encode()).decode().rstrip("=")
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
        unsigned_token = f"{header}.{payload_b64}."
        
        headers = {"Authorization": f"Bearer {unsigned_token}"}
        res = client.get("/api/v1/users/me", headers=headers)
        assert res.status_code == 401


class TestJWTExpiration:
    """Test JWT expiration handling"""

    def test_expired_token_rejected(self, client):
        """Test: Expired token should be rejected"""
        # Create expired token using real SECRET_KEY
        payload = {
            "sub": "expireduser",
            "exp": datetime.utcnow() - timedelta(hours=1)  # Already expired
        }
        expired_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        headers = {"Authorization": f"Bearer {expired_token}"}

        res = client.get("/api/v1/users/me", headers=headers)
        assert res.status_code == 401
