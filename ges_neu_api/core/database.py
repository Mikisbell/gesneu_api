# ges_neu_api/ges_neu_api/core/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel, create_engine

# Importamos nuestro objeto 'settings' desde el archivo config.py
from .config import settings

# Configuración de la conexión
DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI

# Motor asíncrono (principal para FastAPI)
async_engine = create_async_engine(
    DATABASE_URL,
    echo=settings.APP_DEBUG,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
)

# Motor síncrono (para migraciones y scripts)
sync_database_url = DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")
sync_engine = create_engine(
    sync_database_url,
    echo=settings.APP_DEBUG,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
)

# Configuración de sesiones
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
    expire_on_commit=False,
)

# Base para los modelos SQLAlchemy
Base = declarative_base()

# Configuración para SQLModel
SQLModel.metadata.schema = "public"

async def get_session():
    """
    Proveedor de dependencia para obtener una sesión de base de datos asíncrona.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

def get_sync_session():
    """
    Proveedor de dependencia para obtener una sesión de base de datos síncrona.
    """
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

async def test_connection():
    """Prueba la conexión a la base de datos."""
    try:
        async with AsyncSessionLocal() as session:
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            print("✅ Conexión a base de datos exitosa")
            return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def init_db():
    """
    Inicializa la base de datos creando todas las tablas.
    """
    SQLModel.metadata.create_all(bind=sync_engine)

async def init_async_db():
    """
    Inicializa la base de datos de forma asíncrona.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


"""Módulo para el manejo de transacciones de base de datos."""
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator, Optional, TypeVar, Any, Callable, Type
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from .exceptions import AppException, BusinessRuleError

# Tipo genérico para transacciones
T = TypeVar('T')

@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Obtiene una sesión de base de datos asíncrona."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

@contextmanager
def get_sync_db() -> Generator[Session, None, None]:
    """Obtiene una sesión de base de datos síncrona."""
    db = SyncSessionLocal()
    try:
        yield db
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise e
    finally:
        db.close()

class Transactional:
    """Decorador para manejar transacciones de base de datos."""
    
    @classmethod
    async def execute(
        cls, 
        func: Callable[..., T],
        *args: Any,
        **kwargs: Any
    ) -> T:
        """
        Ejecuta una función dentro de una transacción.
        
        Args:
            func: Función a ejecutar
            *args: Argumentos posicionales para la función
            **kwargs: Argumentos clave para la función
            
        Returns:
            El resultado de la función
            
        Raises:
            BusinessRuleError: Si ocurre un error de negocio
            SQLAlchemyError: Si ocurre un error de base de datos
        """
        async with get_db() as session:
            try:
                # Inyectar la sesión si la función la requiere
                if 'db' in func.__code__.co_varnames:
                    kwargs['db'] = session
                
                result = await func(*args, **kwargs)
                await session.commit()
                return result
                
            except BusinessRuleError:
                await session.rollback()
                raise
                
            except SQLAlchemyError as e:
                await session.rollback()
                # Aquí podrías agregar logging del error
                raise
            
            except Exception as e:
                await session.rollback()
                # Convertir excepciones inesperadas en BusinessRuleError
                raise BusinessRuleError(
                    f"Error inesperado: {str(e)}",
                    code="unexpected_error"
                ) from e

# Ejemplo de uso:
# @Transactional.execute
# async def crear_vehiculo(db: AsyncSession, datos: dict) -> Vehiculo:
#     # Lógica para crear un vehículo
#     vehiculo = Vehiculo(**datos)
#     db.add(vehiculo)
#     await db.flush()
#     return vehiculo
