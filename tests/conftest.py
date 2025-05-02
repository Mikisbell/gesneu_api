# tests/conftest.py
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel, select # Añadir select si usas helpers aquí

# --- Importaciones Corregidas ---
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
# --- Has añadido SQLModel y select ---


# Importar tu aplicación FastAPI y la dependencia real
from main import app
from database import get_session as get_real_session

# --- ¡¡ASEGÚRATE DE TENER ESTAS IMPORTACIONES DE MODELOS!! ---
# (Mantener estas importaciones como las tienes)
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
# from models.registro_odometro import RegistroOdometro
# -------------------------------------------------------------

# Fixture para el cliente HTTP asíncrono
# --- CORRECCIÓN AQUÍ ---
@pytest_asyncio.fixture(scope="function") # <-- CAMBIADO DE "session" A "function"
async def client() -> AsyncGenerator[AsyncClient, None]:
# ---------------------
    """Proporciona un cliente HTTP asíncrono para interactuar con la app."""
    # Usar un transporte específico para evitar conflictos de loop entre httpx y pytest-asyncio
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

# Fixture para la sesión de BD en memoria (Usando AsyncSession de SQLModel)
@pytest_asyncio.fixture(scope="function") # <-- Ya estaba como function, lo cual es correcto
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Proporciona una sesión de base de datos de prueba en memoria (SQLModel)."""
    DATABASE_URL_TEST = "sqlite+aiosqlite:///:memory:"
    # El engine se crea por función, lo cual es bueno para aislamiento
    engine = create_async_engine(DATABASE_URL_TEST, echo=False)

    # Los modelos ya están importados arriba...
    async with engine.begin() as conn:
        # --- DEBUGGING: Imprimir tablas conocidas ANTES de create_all ---
        # print("\n--- Tablas conocidas por SQLModel.metadata ANTES de create_all: ---")
        # print(list(SQLModel.metadata.tables.keys()))
        # print("--- Fin Tablas Conocidas ---")
        # -----------------------------------------------------------------
        try:
            # Esta línea ahora DEBERÍA funcionar gracias a los imports
            await conn.run_sync(SQLModel.metadata.create_all)
            # print("--- SQLModel.metadata.create_all ejecutado SIN ERRORES ---") # Mensaje de éxito
        except Exception as e:
            print(f"--- ERROR durante SQLModel.metadata.create_all: {e} ---") # Imprimir error si aún ocurre
            raise # Re-lanzar la excepción para que pytest la muestre

    # Crear fábrica y sesión de SQLModel por función
    async_session_factory = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session_factory() as session:
        yield session
    # Limpiar el engine después de la prueba si es necesario (opcional con :memory:)
    # await engine.dispose()


# Fixture para sobrescribir la dependencia get_session
@pytest_asyncio.fixture(scope="function", autouse=True) # <-- Ya estaba como function, correcto
def override_get_session_dependency(db_session: AsyncSession):
    """Sobrescribe la dependencia get_session para usar la sesión de prueba."""
    async def _override_get_session():
        yield db_session
    # Guardar la dependencia original si existe
    original_dependency = app.dependency_overrides.get(get_real_session)
    app.dependency_overrides[get_real_session] = _override_get_session
    yield
    # Restaurar la dependencia original o eliminar la sobrescritura
    if original_dependency:
        app.dependency_overrides[get_real_session] = original_dependency
    else:
        app.dependency_overrides.pop(get_real_session, None)