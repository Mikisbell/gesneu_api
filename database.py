# database.py
import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

# Cargar variables de entorno desde el archivo .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("No se encontró la variable de entorno DATABASE_URL")

# motor de base de datos asíncrono
# echo=True es útil para debug, muestra las consultas SQL ejecutadas
# echo=False para producción
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Fábrica de sesiones asíncronas
AsyncSessionFactory = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# Dependencia de FastAPI para obtener una sesión de BD
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Generador de sesión de base de datos asíncrona para dependencias de FastAPI."""
    async with AsyncSessionFactory() as session:
        yield session

# Función para inicializar la BD (crear tablas - Opcional si ya existen)
# async def init_db():
#     async with engine.begin() as conn:
#         # await conn.run_sync(SQLModel.metadata.drop_all) # Cuidado: Borra tablas existentes
#         await conn.run_sync(SQLModel.metadata.create_all)