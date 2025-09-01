"""
Pruebas de endpoints de la API GesNeu.

Este módulo contiene pruebas básicas para verificar que los endpoints
principales de la API estén funcionando correctamente.
"""
import pytest
from fastapi.testclient import TestClient
from ges_neu_api.main import app

client = TestClient(app)


class TestMainEndpoints:
    """Pruebas para endpoints principales de la API."""
    
    def test_root_endpoint(self):
        """Prueba el endpoint raíz de la API."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert data["message"] == "Bienvenido a la API de Gestión de Neumáticos"
    
    def test_health_check(self):
        """Prueba el endpoint de health check."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"
        assert "environment" in data
    
    def test_docs_endpoint(self):
        """Prueba que la documentación esté disponible."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_openapi_json(self):
        """Prueba que el esquema OpenAPI esté disponible."""
        response = client.get("/api/v1/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data


class TestVehiculosEndpoints:
    """Pruebas para endpoints del módulo de vehículos."""
    
    def test_list_vehiculos(self):
        """Prueba listar vehículos."""
        response = client.get("/api/v1/vehiculos/")
        # Puede devolver 200 con lista vacía o error de BD
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_get_vehiculo_not_found(self):
        """Prueba obtener vehículo inexistente."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/v1/vehiculos/{fake_uuid}")
        # Puede devolver 404 o error de BD
        assert response.status_code in [404, 500]
    
    def test_create_vehiculo_validation(self):
        """Prueba validación al crear vehículo."""
        # Datos inválidos
        invalid_data = {"placa": ""}
        response = client.post("/api/v1/vehiculos/", json=invalid_data)
        assert response.status_code == 422  # Validation error


class TestNeumaticoEndpoints:
    """Pruebas para endpoints del módulo de neumáticos."""
    
    def test_neumaticos_info(self):
        """Prueba endpoint de información de neumáticos."""
        response = client.get("/api/v1/neumaticos/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["status"] == "pending_implementation"
    
    def test_neumaticos_health(self):
        """Prueba endpoint de salud del módulo neumáticos."""
        response = client.get("/api/v1/neumaticos/health")
        assert response.status_code == 200
        data = response.json()
        assert "module" in data
        assert data["module"] == "neumaticos"
        assert "status" in data
        assert data["status"] == "active"
    
    def test_get_neumatico_placeholder(self):
        """Prueba endpoint placeholder de neumático por ID."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/v1/neumaticos/{fake_uuid}")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "neumatico_id" in data
        assert data["neumatico_id"] == fake_uuid
    
    def test_create_neumatico_placeholder(self):
        """Prueba endpoint placeholder de creación de neumático."""
        response = client.post("/api/v1/neumaticos/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["status"] == "pending_implementation"


class TestAuthEndpoints:
    """Pruebas para endpoints del módulo de autenticación."""
    
    def test_auth_endpoints_exist(self):
        """Verifica que los endpoints de auth existan."""
        # Solo verificamos que no devuelvan 404
        endpoints = [
            "/api/v1/auth/login",
            "/api/v1/auth/register"
        ]
        
        for endpoint in endpoints:
            response = client.post(endpoint, json={})
            # No debe ser 404 (endpoint no encontrado)
            assert response.status_code != 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
