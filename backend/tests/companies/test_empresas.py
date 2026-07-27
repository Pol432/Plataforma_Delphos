import pytest
from fastapi import status

@pytest.fixture
def empresa_data(valid_company_data):
    """Usar datos válidos globales de conftest"""
    return valid_company_data

@pytest.fixture
def empresa_creada(client, empresa_data, db_session):
    """Empresa creada y persistida en DB"""
    response = client.post("/api/v1/empresas", json=empresa_data)
    assert response.status_code == status.HTTP_201_CREATED
    
    # Forzar commit de la sesión de test
    db_session.commit()
    
    return response.json()

class TestCrearEmpresa:
    def test_crear_empresa_exitosamente(self, client, empresa_data):
        response = client.post("/api/v1/empresas", json=empresa_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["nombre_empresa"] == empresa_data["nombre_empresa"]
        assert "id" in data

    def test_crear_duplicado(self, client, empresa_creada):
        # Intentar crear empresa con mismo nombre
        empresa_duplicada = {
            "nombre_empresa": empresa_creada["nombre_empresa"],
            "slug": "otro-slug-diferente",
            "tipo_empresa": "real_nacional",
            "industria": "Finanzas",
            "pais": "Ecuador"
        }
        response = client.post("/api/v1/empresas", json=empresa_duplicada)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

class TestLeerEmpresas:
    def test_listar_empresas(self, client, empresa_creada, db_session):
        # Asegurar que la empresa esté en DB
        db_session.commit()
        
        response = client.get("/api/v1/empresas")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1

    def test_obtener_uno(self, client, empresa_creada):
        empresa_id = empresa_creada["id"]
        response = client.get(f"/api/v1/empresas/{empresa_id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == empresa_id

class TestActualizar:
    def test_update_nombre(self, client, empresa_creada):
        empresa_id = empresa_creada["id"]
        update_data = {"nombre_empresa": "Nombre Actualizado"}
        response = client.put(f"/api/v1/empresas/{empresa_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["nombre_empresa"] == "Nombre Actualizado"

class TestEliminar:
    def test_delete(self, client, empresa_creada):
        empresa_id = empresa_creada["id"]
        del_response = client.delete(f"/api/v1/empresas/{empresa_id}")
        assert del_response.status_code == status.HTTP_204_NO_CONTENT
        
        get_response = client.get(f"/api/v1/empresas/{empresa_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
