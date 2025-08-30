"""Integration tests for the catalogos router endpoints."""
import pytest
from uuid import uuid4
from fastapi import status
from httpx import AsyncClient

from ges_neu_api.modules.catalogos import models, schemas

# Test data
TEST_FABRICANTE_ID = uuid4()
TEST_ITEM_ID = uuid4()

# --- Helper functions ---

def get_admin_auth_headers():
    """Return headers with admin authentication."""
    return {"X-User-Id": str(uuid4()), "X-User-Role": "admin"}

def get_user_auth_headers():
    """Return headers with regular user authentication."""
    return {"X-User-Id": str(uuid4()), "X-User-Role": "user"}

# --- Test cases ---

class TestFabricantesEndpoints:
    """Test cases for the /fabricantes/ endpoints."""
    
    async def test_create_fabricante_as_admin(self, client: AsyncClient):
        """Test creating a fabricante as an admin user."""
        # Arrange
        fabricante_data = {
            "nombre": "Test Fabricante",
            "descripcion": "Test Description",
            "activo": True
        }
        
        # Act
        response = await client.post(
            "/catalogos/fabricantes/",
            json=fabricante_data,
            headers=get_admin_auth_headers()
        )
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["nombre"] == fabricante_data["nombre"]
        assert "id" in data
    
    async def test_create_fabricante_as_regular_user_fails(self, client: AsyncClient):
        """Test that regular users cannot create fabricantes."""
        # Arrange
        fabricante_data = {
            "nombre": "Test Fabricante",
            "descripcion": "Test Description",
            "activo": True
        }
        
        # Act
        response = await client.post(
            "/catalogos/fabricantes/",
            json=fabricante_data,
            headers=get_user_auth_headers()
        )
        
        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    async def test_get_fabricante_by_id(self, client: AsyncClient, db_session):
        """Test getting a fabricante by ID."""
        # Arrange - create a test fabricante
        fabricante = models.Fabricante(
            id=TEST_FABRICANTE_ID,
            nombre="Test Fabricante",
            descripcion="Test Description",
            activo=True,
            creado_por=uuid4()
        )
        db_session.add(fabricante)
        await db_session.commit()
        
        # Act
        response = await client.get(
            f"/catalogos/fabricantes/{TEST_FABRICANTE_ID}",
            headers=get_user_auth_headers()
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(TEST_FABRICANTE_ID)
        assert data["nombre"] == "Test Fabricante"
    
    async def test_update_fabricante(self, client: AsyncClient, db_session):
        """Test updating a fabricante."""
        # Arrange - create a test fabricante
        fabricante = models.Fabricante(
            id=TEST_FABRICANTE_ID,
            nombre="Old Name",
            descripcion="Old Description",
            activo=True,
            creado_por=uuid4()
        )
        db_session.add(fabricante)
        await db_session.commit()
        
        update_data = {
            "nombre": "Updated Name",
            "descripcion": "Updated Description"
        }
        
        # Act
        response = await client.put(
            f"/catalogos/fabricantes/{TEST_FABRICANTE_ID}",
            json=update_data,
            headers=get_admin_auth_headers()
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["nombre"] == "Updated Name"
        assert data["descripcion"] == "Updated Description"
    
    async def test_delete_fabricante(self, client: AsyncClient, db_session):
        """Test deleting a fabricante."""
        # Arrange - create a test fabricante
        fabricante = models.Fabricante(
            id=TEST_FABRICANTE_ID,
            nombre="Test Fabricante",
            descripcion="Test Description",
            activo=True,
            creado_por=uuid4()
        )
        db_session.add(fabricante)
        await db_session.commit()
        
        # Act
        response = await client.delete(
            f"/catalogos/fabricantes/{TEST_FABRICANTE_ID}",
            headers=get_admin_auth_headers()
        )
        
        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify the fabricante was deleted
        result = await db_session.get(models.Fabricante, TEST_FABRICANTE_ID)
        assert result is None


