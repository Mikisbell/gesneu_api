"""Tests for the Alertas router."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from ges_neu_api.modules.auth.models import Usuario

pytestmark = pytest.mark.asyncio


async def test_get_alertas_unauthenticated(client: AsyncClient):
    """Test that unauthenticated users cannot access the alertas endpoint."""
    response = await client.get("/api/v1/alertas/")
    assert response.status_code == 401


async def test_get_alertas_pendientes_authenticated(client: AsyncClient, get_auth_headers: dict[str, str]):
    """
    Test fetching pending alertas for an authenticated user.
    """
    response = await client.get("/api/v1/alertas/", headers=get_auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
