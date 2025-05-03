# tests/conftest.py
import pytest
import pytest_asyncio
import os
from typing import AsyncGenerator, Generator, AsyncIterator # Mantener AsyncIterator
from sqlalchemy.sql import text # Para verificación

from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
# Quitar NullPool por ahora para probar la configuración por defecto
# from sqlalchemy.pool import NullPool

# Importar tu aplicación FastAPI y la dependencia real
from main import app
from database import get_session as get_real_session

# --- Model Imports (Asegúrate que estén todos) ---
# (Mantener la lista completa de tus imports aquí)
print("--- [conftest.py] Importando modelos... ---")
try:
    from models.usuario import Usuario
    from models.tipo_vehiculo import TipoVehiculo
    from models.vehiculo import Vehiculo
    from models.proveedor import Proveedor
    from models.fabricante import FabricanteNeumatico
    from models.modelo import ModeloNeumatico
    from models.motivo_desecho import MotivoDesecho
    from models.posicion_neumatico import PosicionNeumatico
    from models.configuracion_eje import ConfiguracionEje
    from models.neumatico import Neumatico
    from models.evento_neumatico import EventoNeumatico
    from models.almacen import Almacen
    from models.parametro_inventario import ParametroInventario
    from models.alerta import Alerta
    # from models.registro_odometro import RegistroOdometro # Si existe
    print("--- [conftest.py] Modelos importados OK ---")
except ImportError as e:
    print(f"--- [conftest.py] ¡¡ERROR CRÍTICO IMPORTANDO MODELOS!!: {e} ---")
    raise e
# ----------------------------------------------------


# --- Fixtures para SQLite (v7 - Simplificada y Unificada) ---

@pytest_asyncio.fixture(scope="function")
async def sqlite_session() -> AsyncIterator[AsyncSession]:
    """Proporciona una sesión SQLite en memoria y asegura creación de tablas."""
    print("\n--- [sqlite_session fixture v7] Iniciando ---")
    DATABASE_URL_TEST = "sqlite+aiosqlite:///:memory:"
    # Crear engine sin NullPool para probar
    engine_test = create_async_engine(DATABASE_URL_TEST, echo=False)

    # Crear tablas ANTES de crear la fábrica de sesiones
    try:
        async with engine_test.begin() as conn:
            print("[sqlite_session fixture v7] Ejecutando run_sync(SQLModel.metadata.create_all)...")
            # print(f"[DEBUG] Metadata Tables: {list(SQLModel.metadata.tables.keys())}") # Opcional
            await conn.run_sync(SQLModel.metadata.create_all)
            print("[sqlite_session fixture v7] create_all completado.")
        # La transacción se commitea al salir del 'begin()'

        # Verificar existencia tabla 'usuarios' después de crearla
        async with engine_test.connect() as conn_check:
             result = await conn_check.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios';"))
             if not result.scalar_one_or_none():
                 pytest.fail("Fallo crítico: Tabla 'usuarios' no existe DESPUÉS de create_all.")
             print("[sqlite_session fixture v7] Tabla 'usuarios' verificada OK.")

    except Exception as e_create:
         print(f"[sqlite_session fixture v7] ¡¡ERROR durante create_all!!: {e_create}")
         await engine_test.dispose() # Limpiar engine si falla la creación
         raise e_create

    # Crear la fábrica de sesiones y la sesión
    AsyncSessionFactory = sessionmaker(
        bind=engine_test, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    async with AsyncSessionFactory() as session:
        print("[sqlite_session fixture v7] Yielding session (expire_on_commit=True)...")
        yield session
        print("[sqlite_session fixture v7] Session yield terminado.")
        # Limpieza dentro de la sesión (opcional, pero bueno para aislamiento)
        # await session.rollback() # Podría ser útil si las pruebas dejan datos

    print("[sqlite_session fixture v7] Eliminando engine...")
    await engine_test.dispose()
    print("[sqlite_session fixture v7] Fixture finalizada.")


# Fixture 'db_session' sigue siendo el alias para las pruebas existentes
@pytest_asyncio.fixture(scope="function")
async def db_session(sqlite_session: AsyncSession) -> AsyncIterator[AsyncSession]: # Usar AsyncIterator por Pylance
     """Fixture por defecto que usa la sesión SQLite."""
     yield sqlite_session


# --- Fixtures para PostgreSQL de Integración (Sin cambios) ---

DATABASE_TEST_URL = os.getenv("DATABASE_TEST_URL_HOST", "postgresql+asyncpg://test_user:test_password@localhost:5433/test_db")

@pytest_asyncio.fixture(scope="session")
async def postgres_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Crea el engine de SQLAlchemy para la BD de prueba PostgreSQL."""
    if not os.getenv("DATABASE_TEST_URL_HOST"):
         pytest.skip("DATABASE_TEST_URL_HOST no definida. Omitiendo pruebas de integración.")
    print("\n--- [Fixture postgres_engine] Creando engine PostgreSQL ---")
    engine = create_async_engine(DATABASE_TEST_URL, echo=False, future=True)
    yield engine
    print("\n--- [Fixture postgres_engine] Eliminando engine PostgreSQL ---")
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def postgres_session(postgres_engine: AsyncEngine) -> AsyncIterator[AsyncSession]: # Usar AsyncIterator por Pylance
    """Proporciona una sesión de base de datos PostgreSQL para pruebas de integración."""
    async_session_factory = sessionmaker(
        bind=postgres_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_factory() as session:
        yield session


# --- Fixture de Cliente HTTP (Sin cambios) ---

@pytest_asyncio.fixture(scope="function")
async def client(sqlite_session: AsyncSession) -> AsyncIterator[AsyncClient]: # Usar AsyncIterator por Pylance
    """Cliente HTTP asíncrono estándar usando la sesión SQLite."""
    async def _override_get_session():
        # Esta sesión viene de la fixture sqlite_session ya configurada
        yield sqlite_session

    original_dependency = app.dependency_overrides.get(get_real_session)
    app.dependency_overrides[get_real_session] = _override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    # Restaurar dependencia
    app.dependency_overrides.pop(get_real_session, None)
    if original_dependency:
        app.dependency_overrides[get_real_session] = original_dependency


@pytest_asyncio.fixture(scope="function")
async def integration_client(postgres_session: AsyncSession) -> AsyncIterator[AsyncClient]: # Usar AsyncIterator por Pylance
    """Cliente HTTP asíncrono para pruebas de integración usando la sesión PostgreSQL."""
    async def _override_get_session_integration():
        yield postgres_session

    original_dependency = app.dependency_overrides.get(get_real_session)
    app.dependency_overrides[get_real_session] = _override_get_session_integration
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    # Restaurar dependencia
    app.dependency_overrides.pop(get_real_session, None)
    if original_dependency:
        app.dependency_overrides[get_real_session] = original_dependency