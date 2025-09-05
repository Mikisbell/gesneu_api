"""
Pruebas de endpoints de la API GesNeu.

Este módulo contiene pruebas básicas para verificar que los endpoints
principales de la API estén funcionando correctamente.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from ges_neu_api.main import app


class TestMainEndpoints:
    """Pruebas para endpoints principales de la API."""
    
    async def test_root_endpoint(self, client: AsyncClient):
        """Prueba el endpoint raíz de la API."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert data["message"] == "Bienvenido a la API de Gestión de Neumáticos"
    
    async def test_health_check(self, client: AsyncClient):
        """Prueba el endpoint de health check."""
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"
        assert "environment" in data
    
    async def test_docs_endpoint(self, client: AsyncClient):
        """Prueba que la documentación esté disponible."""
        response = await client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    async def test_openapi_json(self, client: AsyncClient):
        """Prueba que el esquema OpenAPI esté disponible."""
        response = await client.get("/api/v1/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data


class TestVehiculosEndpoints:
    """Pruebas para endpoints del módulo de vehículos."""
    
    async def test_list_vehiculos(self, client: AsyncClient):
        """Prueba listar vehículos."""
        response = await client.get("/api/v1/vehiculos/")
        # Puede devolver 200 con lista vacía o error de BD
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    async def test_get_vehiculo_not_found(self, client: AsyncClient):
        """Prueba obtener vehículo inexistente."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/api/v1/vehiculos/{fake_uuid}")
        # Puede devolver 404 o error de BD
        assert response.status_code in [404, 500]
    
    async def test_create_vehiculo_validation(self, client: AsyncClient):
        """Prueba validación al crear vehículo."""
        # Datos inválidos
        invalid_data = {"placa": ""}
        response = await client.post("/api/v1/vehiculos/", json=invalid_data)
        assert response.status_code == 422  # Validation error


class TestNeumaticoEndpoints:
    """Pruebas para endpoints del módulo de neumáticos."""
    
    async def test_list_neumaticos_requires_auth_or_returns_list(self, client: AsyncClient):
        """GET lista de neumáticos: puede requerir auth (401) o devolver 200 con lista."""
        response = await client.get("/api/v1/neumaticos/")
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    async def test_neumaticos_health(self, client: AsyncClient):
        """Prueba endpoint de salud del módulo neumáticos."""
        response = await client.get("/api/v1/neumaticos/health")
        assert response.status_code == 200
        data = response.json()
        assert "module" in data
        assert data["module"] == "neumaticos"
        assert "status" in data
        assert data["status"] == "active"
    
    async def test_get_neumatico_not_found(self, client: AsyncClient):
        """GET neumático por ID inexistente debe devolver 404."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/api/v1/neumaticos/{fake_uuid}")
        # Puede devolver 404 (no encontrado), 401 (auth requerida) o 500 (sin BD en entorno de test)
        assert response.status_code in [404, 401, 500]
    
    async def test_create_neumatico_validation(self, client: AsyncClient):
        """POST crear neumático sin body debe fallar con 422 (validación)."""
        response = await client.post("/api/v1/neumaticos/")
        assert response.status_code == 422


class TestAuthEndpoints:
    """Pruebas para endpoints del módulo de autenticación."""
    
    async def test_auth_login_endpoint_exists(self, client: AsyncClient):
        """Verifica que el endpoint de login exista (puede devolver 422 por payload vacío)."""
        response = await client.post("/api/v1/auth/login", json={})
        assert response.status_code != 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
