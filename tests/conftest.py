"""Test configuration and fixtures."""
import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from fastapi import Depends
from ges_neu_api.core.config import Settings
from ges_neu_api.core.database import Base, get_db
from ges_neu_api.main import app
from tests.auth.factories import UsuarioFactory
# Import test models for SQLite compatibility
from ges_neu_api.core.test_models import Usuario, Rol, Permiso, UsuariosRoles, RolesPermisos


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    # Configuración mejorada para evitar warnings de event loop
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    
    yield loop
    
    # Clean shutdown mejorado
    try:
        # Cancelar todas las tareas pendientes
        pending = asyncio.all_tasks(loop)
        if pending:
            for task in pending:
                task.cancel()
            # Esperar a que las tareas canceladas terminen
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
    except Exception:
        pass
    finally:
        # Cerrar el loop de forma segura
        try:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.run_until_complete(loop.shutdown_default_executor())
        except Exception:
            pass
        finally:
            if not loop.is_closed():
                loop.close()
            asyncio.set_event_loop(None)


@pytest_asyncio.fixture(scope="function")
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Database engine fixture using SQLite for tests."""
    from sqlalchemy.pool import StaticPool
    settings = Settings()
    
    # Use SQLite in-memory database for tests
    engine = create_async_engine(
        settings.TEST_SQLALCHEMY_DATABASE_URI,
        echo=False,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
        },
    )
    
    # Create all tables using test metadata (SQLite compatible)
    from ges_neu_api.core.test_models import test_metadata
    async with engine.begin() as conn:
        await conn.run_sync(test_metadata.create_all)
    
    try:
        yield engine
    finally:
        # Proper async cleanup
        try:
            await engine.dispose()
        except Exception as e:
            print(f"Warning: Error during engine cleanup: {e}")


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Database session fixture with proper cleanup."""
    # Create session factory
    session_factory = async_sessionmaker(
        bind=db_engine,
        expire_on_commit=False,
        autoflush=True,
        autocommit=False
    )
    
    session = session_factory()
    
    try:
        yield session
    finally:
        # Clean shutdown
        try:
            await session.rollback()
            await session.close()
        except Exception as e:
            print(f"Warning: Error during session cleanup: {e}")


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client that overrides the database dependency."""
    
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    # Override auth service to use test models
    from tests.auth.test_service import TestAuthService
    from ges_neu_api.modules.auth.router import get_auth_service
    from ges_neu_api.core.database import get_session
    
    def override_get_auth_service(db: AsyncSession = Depends(get_session)) -> TestAuthService:
        return TestAuthService(db)

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_auth_service] = override_get_auth_service
    
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), 
            base_url="http://test",
            timeout=30.0
        ) as async_client:
            yield async_client
    finally:
        # Clean up dependency overrides
        if get_session in app.dependency_overrides:
            del app.dependency_overrides[get_session]
        if get_auth_service in app.dependency_overrides:
            del app.dependency_overrides[get_auth_service]


@pytest.fixture(scope="function")
def sync_client(db_session: AsyncSession) -> Generator[TestClient, None, None]:
    """Create a synchronous test client."""
    from ges_neu_api.core.database import get_session
    
    def override_get_session() -> Generator[AsyncSession, None, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    del app.dependency_overrides[get_session]

# --- User and Auth Fixtures ---

@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> Usuario:
    """Fixture to create a standard test user."""
    return await UsuarioFactory.create(
        db=db_session,
        activo=True
    )

@pytest_asyncio.fixture(scope="function")
async def superuser(db_session: AsyncSession) -> Usuario:
    """Fixture to create a superuser."""
    return await UsuarioFactory.create(
        db=db_session,
        activo=True
    )


@pytest_asyncio.fixture(scope="function")
async def get_auth_headers(client: AsyncClient, db_session: AsyncSession) -> dict:
    """Fixture to get authentication headers for a test user."""
    password = "testpassword"
    
    # Create user with unique values using factory defaults - only valid PostgreSQL schema fields
    user = await UsuarioFactory.create(
        db=db_session,
        password=password,
        activo=True
    )
    
    print(f"DEBUG: Created user with email: {user.email}, id: {user.id}")

    login_data = {
        "username": user.email,
        "password": password,
    }

    response = await client.post("/api/v1/auth/login", data=login_data)
    print(f"DEBUG: Login response status: {response.status_code}, body: {response.text}")
    assert response.status_code == 200, f"Failed to log in: {response.text}"
    
    token_data = response.json()
    return {"Authorization": f"Bearer {token_data['access_token']}"}