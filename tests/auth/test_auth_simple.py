"""
Simple auth tests using the working async pattern from conftest.py
"""
import pytest
import pytest_asyncio
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from ges_neu_api.core.config import settings


class TestAuthSimple:
    """Simple auth tests to verify basic functionality."""
    
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials returns 401."""
        response = await client.post(
            f"{settings.API_V1_STR}/auth/login",
            data={"username": "nonexistent", "password": "wrongpassword"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    async def test_me_endpoint_unauthenticated(self, client: AsyncClient):
        """Test accessing /me endpoint without authentication returns 401."""
        response = await client.get(f"{settings.API_V1_STR}/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    async def test_me_endpoint_authenticated(self, client: AsyncClient, get_auth_headers):
        """Test accessing /me endpoint with authentication returns user data."""
        response = await client.get(
            f"{settings.API_V1_STR}/auth/me",
            headers=get_auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        user_data = response.json()
        assert "email" in user_data
        assert "id" in user_data
