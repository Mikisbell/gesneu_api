# ges_neu_api/ges_neu_api/core/database.py

from typing import (
    AsyncGenerator,
    Generator,
    TypeVar,
    Any,
    Callable,
    Awaitable,
    cast,
    overload,
    ParamSpec,
)
import inspect
import asyncio
import logging

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, create_engine

# Importamos nuestro objeto 'settings' desde el archivo config.py
from .config import settings

# Configuración de la conexión
DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI

async_engine: AsyncEngine | None = None
sync_engine: Engine | None = None
AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None
SyncSessionLocal: sessionmaker | None = None

def get_async_engine() -> AsyncEngine:
    global async_engine
    if async_engine is None:
        async_engine = create_async_engine(
            DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_recycle=3600,
            # Configuración para manejar fallos temporales de DNS
            pool_timeout=30,
            pool_reset_on_return='commit',
            connect_args={
                "server_settings": {
                    "application_name": "gesneu_api",
                    "jit": "off"
                },
                # Configuración específica para asyncpg
                "command_timeout": 60,
            }
        )
    return async_engine

def get_sync_engine() -> Engine:
    global sync_engine
    if sync_engine is None:
        sync_database_url = DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")
        sync_engine = create_engine(
            sync_database_url,
            echo=settings.app_debug,
            pool_pre_ping=True,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
        )
    return sync_engine

def get_async_session_local() -> async_sessionmaker[AsyncSession]:
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        AsyncSessionLocal = async_sessionmaker(
            bind=get_async_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return AsyncSessionLocal

def get_sync_session_local() -> sessionmaker:
    global SyncSessionLocal
    if SyncSessionLocal is None:
        SyncSessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_sync_engine(),
            expire_on_commit=False,
        )
    return SyncSessionLocal

# Base para los modelos SQLAlchemy
Base = declarative_base()

# Configuración para SQLModel - Sin esquema para compatibilidad SQLite/PostgreSQL
# SQLModel.metadata.schema = "public"  # Comentado para permitir configuración por modelo

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Proveedor de dependencia para obtener una sesión de base de datos asíncrona.
    """
    session_local: async_sessionmaker[AsyncSession] = get_async_session_local()
    async with session_local() as session:
        try:
            yield session
        finally:
            await session.close()

def get_sync_session() -> Generator[Session, None, None]:
    """
    Proveedor de dependencia para obtener una sesión de base de datos síncrona.
    """
    session_local: sessionmaker = get_sync_session_local()
    db: Session = session_local()
    try:
        yield db
    finally:
        db.close()

async def test_connection() -> bool:
    """Prueba la conexión a la base de datos."""
    try:
        session_local: async_sessionmaker[AsyncSession] = get_async_session_local()
        async with session_local() as session:
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            print("✅ Conexión a base de datos exitosa")
            return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

async def wait_for_db(max_attempts: int = 10, initial_delay: float = 0.5) -> None:
    """
    Espera de forma robusta a que la base de datos esté disponible.

    Usa reintentos con backoff exponencial. No modifica el esquema ni crea tablas.
    """
    logger = logging.getLogger(__name__)
    delay = initial_delay
    for attempt in range(1, max_attempts + 1):
        try:
            ok = await test_connection()
            if ok:
                logger.info("Conexión a BD verificada correctamente")
                return
        except Exception as e:
            logger.warning(f"Intento {attempt}/{max_attempts} de conectar a BD falló: {e}")

        logger.info(f"Reintentando conexión a BD en {delay:.1f}s...")
        await asyncio.sleep(delay)
        delay = min(delay * 2, 10.0)

    # Si llega aquí, no se pudo verificar la conexión
    raise RuntimeError("No fue posible verificar la conexión a la base de datos tras varios intentos")

def init_db() -> None:
    """
    Inicializa la base de datos creando todas las tablas.
    """
    engine = get_sync_engine()
    SQLModel.metadata.create_all(bind=engine)

async def init_async_db() -> None:
    """
    Inicializa la base de datos de forma asíncrona.
    """
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


"""Módulo para el manejo de transacciones de base de datos."""
from contextlib import asynccontextmanager, contextmanager
from sqlalchemy.exc import SQLAlchemyError

from .exceptions import AppException, BusinessRuleError

# Tipo genérico para transacciones
T = TypeVar('T')
P = ParamSpec("P")

@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Obtiene una sesión de base de datos asíncrona."""
    session_local: async_sessionmaker[AsyncSession] = get_async_session_local()
    async with session_local() as session:
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
    session_local: sessionmaker = get_sync_session_local()
    db: Session = session_local()
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
    
    # Sobrecargas para ayudar a MyPy a inferir correctamente el retorno
    @overload
    @classmethod
    async def execute(
        cls,
        func: Callable[P, Awaitable[T]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T: ...

    @overload
    @classmethod
    async def execute(
        cls,
        func: Callable[P, T],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T: ...

    @classmethod
    async def execute(
        cls,
        func: Callable[P, Awaitable[T]] | Callable[P, T],
        *args: P.args,
        **kwargs: P.kwargs,
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
                # Preparar kwargs sin romper la información de tipos de ParamSpec
                call_kwargs: dict[str, Any] = dict(kwargs)  # copia segura para inyección
                # Inyectar la sesión si la función la requiere
                if 'db' in func.__code__.co_varnames:
                    call_kwargs['db'] = session

                # Ejecutar según sea función async o sync manteniendo tipos
                result: T
                if inspect.iscoroutinefunction(func):
                    result = await cast(Callable[P, Awaitable[T]], func)(
                        *args, **cast(Any, call_kwargs)
                    )
                else:
                    result = cast(Callable[P, T], func)(
                        *args, **cast(Any, call_kwargs)
                    )
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
