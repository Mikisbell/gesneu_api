"""Test configuration and fixtures."""
import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from core.database import Base, get_db
from ges_neu_api.main import app
from tests.factories import UsuarioFactory
from modules.auth.models.usuario import Usuario

# 1. Start PostgreSQL container for the test session
@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    """Start a PostgreSQL container for testing."""
    with PostgresContainer("postgres:15-alpine") as container:
        yield container

@pytest.fixture(scope="session")
def db_url(postgres_container: PostgresContainer) -> str:
    """Get the database connection URL from the container."""
    # Replace 'postgresql' with 'postgresql+asyncpg' for async SQLAlchemy
    return postgres_container.get_connection_url().replace(
        "postgresql://", "postgresql+asyncpg://"
    )

# 2. Create database engine once per session
@pytest_asyncio.fixture(scope="session")
async def db_engine(db_url: str) -> AsyncGenerator[AsyncEngine, None]:
    """Create and configure the SQLAlchemy async engine."""
    engine = create_async_engine(db_url, echo=False)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    await engine.dispose()

# 3. Create a database connection for each test
@pytest_asyncio.fixture(scope="function")
async def db_connection(
    db_engine: AsyncEngine
) -> AsyncGenerator[AsyncConnection, None]:
    """Create a database connection for each test."""
    async with db_engine.connect() as connection:
        # Begin a nested transaction
        transaction = await connection.begin()
        
        try:
            yield connection
        finally:
            # Always roll back the transaction
            await transaction.rollback()

# 4. Create a database session for each test
@pytest_asyncio.fixture(scope="function")
async def db_session(
    db_connection: AsyncConnection
) -> AsyncGenerator[AsyncSession, None]:
    """Create a database session with automatic rollback after each test."""
    session_maker = async_sessionmaker(
        bind=db_connection,
        expire_on_commit=False,
        autoflush=False
    )
    
    async with session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

# 5. Event loop for async tests
@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

# --- User and Client Fixtures ---

@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> Usuario:
    """Create a test user."""
    return await UsuarioFactory.create(
        db_session,
        email="test@example.com",
        nombre="Test",
        apellido="User",
        activo=True
    )

@pytest_asyncio.fixture(scope="function")
async def admin_user(db_session: AsyncSession) -> Usuario:
    """Create an admin user."""
    return await UsuarioFactory.create(
        db_session,
        email="admin@example.com",
        nombre="Admin",
        apellido="User",
        activo=True
    )

@pytest_asyncio.fixture(scope="function")
async def client(
    db_session: AsyncSession
) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client that overrides the database dependency."""
    # Override the get_db dependency
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        try:
            yield db_session
        finally:
            await db_session.close()
    
    # Apply the override
    app.dependency_overrides[get_db] = override_get_db
    
    # Create and yield the test client
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        yield async_client
    
    # Clean up
    del app.dependency_overrides[get_db]

@pytest.fixture(scope="function")
def sync_client() -> TestClient:
    """Create a synchronous test client."""
    return TestClient(app)