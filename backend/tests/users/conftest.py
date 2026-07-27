"""
Fixtures específicos para tests de usuarios.
Soluciona el problema de scope de DB entre fixtures auth_header y client.
"""
import pytest


@pytest.fixture
def registered_user(client):
    """
    Crea un usuario via HTTP y retorna sus datos + credenciales.
    Usa el mismo 'client' (y por ende la misma db_session) que el test.
    """
    payload = {
        "username": "shield_user",
        "email": "shield@test.com",
        "password": "ShieldPassword123!",
        "full_name": "Shield Operative",
        "gender": "masculino",
        "phone": "+5939999999"
    }
    res = client.post("/api/v1/users", json=payload)
    assert res.status_code == 201, f"Registro falló: {res.json()}"
    return {**res.json(), "password": payload["password"], "username": payload["username"]}


@pytest.fixture
def auth_token(client, registered_user):
    """
    Genera un token JWT para el usuario registrado.
    GARANTÍA: el usuario existe en la MISMA db_session que usa get_current_user.
    """
    login_res = client.post(
        "/api/v1/token",
        data={
            "username": registered_user["username"],
            "password": registered_user["password"]
        }
    )
    assert login_res.status_code == 200, f"Login falló: {login_res.json()}"
    return login_res.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    """Headers de autenticación listos para usar en requests."""
    return {"Authorization": f"Bearer {auth_token}"}
