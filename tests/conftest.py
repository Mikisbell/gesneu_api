# tests/conftest.py
import uuid # Importar el módulo uuid
from datetime import datetime, date # Importar datetime y date
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
from core.config import settings # <--- AÑADE ESTA LÍNEA

# Importar tu aplicación FastAPI y la dependencia real
from main import app # <-- Asegúrate que app se importa correctamente
from core.dependencies import get_session as get_real_session # Importar desde core.dependencies

# --- Model Imports (Asegúrate que estén todos) ---
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
    import sqlite3 # Importar sqlite3 para las banderas de detección de tipos
    import json # Para serializar/deserializar UUIDs como strings JSON

    # --- Adaptadores para aiosqlite ---
    def _adapt_uuid(val):
        """Adapter for UUID to string."""
        return str(val)

    def _convert_uuid(val):
        """Converter for string to UUID."""
        if val is not None:
            return uuid.UUID(val)
        return None

    def _adapt_datetime(val):
        """Adapter for datetime to ISO 8601 string."""
        return val.isoformat() if val is not None else None

    def _convert_datetime(val):
        """Converter for ISO 8601 string to datetime."""
        if val is not None:
            # Asegurarse de manejar posibles zonas horarias si se almacenan
            return datetime.fromisoformat(val)
        return None

    def _adapt_date(val):
        """Adapter for date to ISO 8601 string."""
        return val.isoformat() if val is not None else None

    def _convert_date(val):
        """Converter for ISO 8601 string to date."""
        if val is not None:
            return date.fromisoformat(val)
        return None

    # Registrar adaptadores y convertidores
    sqlite3.register_adapter(uuid.UUID, _adapt_uuid)
    sqlite3.register_converter("UUID", _convert_uuid) # Usar el nombre del tipo de columna
    sqlite3.register_adapter(datetime, _adapt_datetime)
    sqlite3.register_converter("TIMESTAMP", _convert_datetime) # Usar el nombre del tipo de columna
    sqlite3.register_adapter(date, _adapt_date)
    sqlite3.register_converter("DATE", _convert_date) # Usar el nombre del tipo de columna
    # --- Fin Adaptadores ---

    DATABASE_URL_TEST = "sqlite+aiosqlite:///:memory:"
    # Eliminar detect_types de connect_args ya que usamos adaptadores/convertidores
    engine_test = create_async_engine(
        DATABASE_URL_TEST,
        echo=False,
        connect_args={"check_same_thread": False} # Mantener solo check_same_thread
    )

    try:
        async with engine_test.begin() as conn:
            print("[sqlite_session fixture v7] Ejecutando run_sync(SQLModel.metadata.create_all)...")
            await conn.run_sync(SQLModel.metadata.create_all)
            print("[sqlite_session fixture v7] create_all completado.")

        async with engine_test.connect() as conn_check:
             result = await conn_check.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios';"))
             if not result.scalar_one_or_none():
                 pytest.fail("Fallo crítico: Tabla 'usuarios' no existe DESPUÉS de create_all.")
             print("[sqlite_session fixture v7] Tabla 'usuarios' verificada OK.")

    except Exception as e_create:
         print(f"[sqlite_session fixture v7] ¡¡ERROR durante create_all!!: {e_create}")
         await engine_test.dispose()
         raise e_create

    AsyncSessionFactory = sessionmaker(
        bind=engine_test,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with AsyncSessionFactory() as session:
        print("[sqlite_session fixture v7] Yielding session...")
        yield session
        print("[sqlite_session fixture v7] Session yield terminado.")

    print("[sqlite_session fixture v7] Eliminando engine...")
    await engine_test.dispose()
    print("[sqlite_session fixture v7] Fixture finalizada.")


@pytest_asyncio.fixture(scope="function")
async def db_session(sqlite_session: AsyncSession) -> AsyncIterator[AsyncSession]:
     """Fixture por defecto que usa la sesión SQLite."""
     yield sqlite_session


# --- Fixtures para PostgreSQL de Integración (Sin cambios) ---
DATABASE_TEST_URL = os.getenv("DATABASE_TEST_URL_HOST", "postgresql+asyncpg://test_user:test_password@localhost:5433/test_db")

@pytest_asyncio.fixture(scope="function")
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
async def postgres_session(postgres_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Proporciona una sesión de base de datos PostgreSQL para pruebas de integración."""
    async_session_factory = sessionmaker(
        bind=postgres_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_factory() as session:
        yield session


# --- Fixture de Cliente HTTP (CON DEBUG DE RUTAS) ---
@pytest_asyncio.fixture(scope="function")
async def client(sqlite_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    """Cliente HTTP asíncrono estándar usando la sesión SQLite."""
    async def _override_get_session():
        yield sqlite_session

    original_dependency = app.dependency_overrides.get(get_real_session)
    app.dependency_overrides[get_real_session] = _override_get_session

    # --- DEBUG: Imprimir rutas registradas en la app ---
    print("\n--- [client fixture] Rutas registradas en la app FastAPI: ---")
    for route in app.routes:
        # Intentar obtener métodos y path de diferentes tipos de rutas
        if hasattr(route, "path") and hasattr(route, "methods"):
            print(f"Path: {route.path}, Methods: {route.methods}")
        elif hasattr(route, "path"): # Para Mounts, etc.
             print(f"Path (Mount/Other): {route.path}")
        else:
             print(f"Route Type: {type(route)}") # Si no tiene path/methods
    print("--- [client fixture] Fin de rutas registradas ---\n")
    # --- FIN DEBUG ---

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    # Restaurar dependencia
    app.dependency_overrides.pop(get_real_session, None)
    if original_dependency:
        app.dependency_overrides[get_real_session] = original_dependency


@pytest_asyncio.fixture(scope="function")
async def integration_client(postgres_session: AsyncSession) -> AsyncIterator[AsyncClient]:
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
