# database.py
import os
from typing import AsyncGenerator

# --- Importaciones Corregidas ---
from sqlmodel.ext.asyncio.session import AsyncSession  # <--- Importar de SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel # Asegurar que SQLModel esté importado para metadata

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "GesNeu API"
    DATABASE_URL: str
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

settings = Settings()

# Motor asíncrono (sin cambios)
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Considera False en producción
    future=True,
)

# --- Fabrica de sesiones (Usa AsyncSession de SQLModel) ---
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,  # <--- Usa la AsyncSession importada de SQLModel
    expire_on_commit=False,
)

# Dependencia para FastAPI (Inyectará sesión SQLModel)
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Proporciona una sesión de base de datos asíncrona (SQLModel) por request"""
    async with AsyncSessionLocal() as session:
        yield session

# Inicializar tablas (sin cambios, pero depende de que los modelos importen SQLModel)
async def init_db():
    """Crea las tablas definidas en los modelos en la base de datos"""
    async with engine.begin() as conn:
        # SQLModel necesita ser importado en los archivos de tus modelos
        await conn.run_sync(SQLModel.metadata.create_all)