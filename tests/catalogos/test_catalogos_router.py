"""Integration tests for the catalogos router endpoints."""
import pytest
from uuid import uuid4
from fastapi import status
from httpx import AsyncClient

from ges_neu_api.modules.catalogos import models, schemas

# Test data
TEST_PROVEEDOR_ID = uuid4()
TEST_ALMACEN_ID = uuid4()

# --- Helper functions ---

def get_admin_auth_headers():
    """Return headers with admin authentication."""
    return {"X-User-Id": str(uuid4()), "X-User-Role": "admin"}

def get_user_auth_headers():
    """Return headers with regular user authentication."""
    return {"X-User-Id": str(uuid4()), "X-User-Role": "user"}

# --- Test cases ---

class TestProveedoresEndpoints:
    """Test cases for the /proveedores/ endpoints."""
    
    async def test_create_proveedor_as_admin(self, client: AsyncClient):
        """Test creating a proveedor as an admin user."""
        # Arrange
        proveedor_data = {
            "nombre": "Test Proveedor",
            "tipo": "DISTRIBUIDOR",
            "contacto_principal": "Juan Pérez",
            "telefono": "987654321",
            "email": "test@proveedor.com",
            "activo": True
        }
        
        # Act
        response = await client.post(
            "/api/v1/catalogos/proveedores/",
            json=proveedor_data,
            headers=get_admin_auth_headers()
        )
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["nombre"] == proveedor_data["nombre"]
        assert "id" in data
    
    async def test_get_proveedores_list(self, client: AsyncClient, db_session):
        """Test getting list of proveedores."""
        # Arrange - create test proveedores
        proveedor1 = models.Proveedor(
            nombre="Proveedor 1",
            tipo="DISTRIBUIDOR",
            contacto_principal="Juan Pérez",
            telefono="987654321",
            email="proveedor1@test.com",
            activo=True
        )
        proveedor2 = models.Proveedor(
            nombre="Proveedor 2", 
            tipo="FABRICANTE",
            contacto_principal="María García",
            telefono="987654322",
            email="proveedor2@test.com",
            activo=True
        )
        db_session.add(proveedor1)
        db_session.add(proveedor2)
        await db_session.commit()
        
        # Act
        response = await client.get(
            "/api/v1/catalogos/proveedores/",
            headers=get_user_auth_headers()
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 2
        assert any(p["nombre"] == "Proveedor 1" for p in data)
        assert any(p["nombre"] == "Proveedor 2" for p in data)

class TestAlmacenesEndpoints:
    """Test cases for the /almacenes/ endpoints."""
    
    async def test_create_almacen_as_admin(self, client: AsyncClient):
        """Test creating an almacen as an admin user."""
        # Arrange
        almacen_data = {
            "nombre": "Almacén Central",
            "codigo": "ALM001",
            "ubicacion": "Zona Industrial Norte",
            "capacidad_maxima": 1000,
            "activo": True
        }
        
        # Act
        response = await client.post(
            "/api/v1/catalogos/almacenes/",
            json=almacen_data,
            headers=get_admin_auth_headers()
        )
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["nombre"] == almacen_data["nombre"]
        assert data["codigo"] == almacen_data["codigo"]
        assert "id" in data


