# tests/conftest.py
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport

# --- Importaciones Corregidas ---
from sqlmodel.ext.asyncio.session import AsyncSession  # <--- Importar de SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

# Importar tu aplicación FastAPI y la dependencia real
from main import app
from database import get_session as get_real_session

# Fixture para el cliente HTTP asíncrono
@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Proporciona un cliente HTTP asíncrono para interactuar con la app."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

# Fixture para la sesión de BD en memoria (Usando AsyncSession de SQLModel)
@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Proporciona una sesión de base de datos de prueba en memoria (SQLModel)."""
    DATABASE_URL_TEST = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(DATABASE_URL_TEST, echo=False) # No echo en tests

    # Crear tablas antes de la sesión
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Crear fábrica y sesión de SQLModel
    async_session_factory = sessionmaker(
        bind=engine,
        class_=AsyncSession,  # <--- Usa la AsyncSession importada de SQLModel
        expire_on_commit=False,
    )
    async with async_session_factory() as session:
        yield session # Esta sesión tendrá .exec()

    # Opcional: Limpiar después (aunque scope=function aísla)
    # async with engine.begin() as conn:
    #    await conn.run_sync(SQLModel.metadata.drop_all)
    # await engine.dispose()

# Fixture para sobrescribir la dependencia get_session globalmente para los tests
@pytest_asyncio.fixture(scope="function", autouse=True)
def override_get_session_dependency(db_session: AsyncSession):
    """Sobrescribe la dependencia get_session para usar la sesión de prueba."""
    async def _override_get_session():
        # Entrega la sesión del fixture db_session (que es una sesión SQLModel)
        yield db_session

    # Aplica la sobrescritura en la app de FastAPI
    app.dependency_overrides[get_real_session] = _override_get_session
    # Permite que la prueba se ejecute
    yield
    # Limpia la sobrescritura después de que la prueba termina
    app.dependency_overrides.pop(get_real_session, None)