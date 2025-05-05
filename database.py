# database.py
# --- CÓDIGO CORREGIDO Y CONSOLIDADO ---

import os # os sigue siendo útil para otras cosas si es necesario
from typing import AsyncGenerator

# --- Quitar imports redundantes ---
# from dotenv import load_dotenv # Ya no se usa aquí
# from sqlmodel import Session # Import no usado (era para sesión síncrona?)

# --- Imports necesarios ---
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel # Necesario para init_db

# --- Importar la configuración centralizada ---
from core.config import settings # <-- IMPORTANTE: Usar la instancia de settings

# --- Usar la URL de la base de datos desde settings ---
# Ya no se necesita leer desde os.getenv aquí
DATABASE_URL_FROM_SETTINGS = settings.DATABASE_URL
if not DATABASE_URL_FROM_SETTINGS:
    # Fallback o error si la URL no está definida en la configuración central
    # Podrías poner un valor por defecto aquí para pruebas locales si quieres,
    # pero es mejor asegurarse que esté en .env o variables de entorno.
    print("ADVERTENCIA: DATABASE_URL no encontrada en settings. Usando SQLite local por defecto.")
    DATABASE_URL_FROM_SETTINGS = "sqlite+aiosqlite:///./local_fallback.db"
    # Alternativamente, lanzar un error:
    # raise ValueError("DATABASE_URL no está configurada en las variables de entorno o .env")

# --- Crear el motor asíncrono ---
# connect_args solo es necesario para SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL_FROM_SETTINGS.startswith("sqlite") else {}

# Usar la URL de settings para crear el engine
engine = create_async_engine(
    DATABASE_URL_FROM_SETTINGS,
    echo=False, # Poner True para debug de SQL
    future=True,
    connect_args=connect_args
)

# --- Crear una factoría de sesión asíncrona ---
# (Sin cambios aquí)
AsyncSessionFactory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# --- Función para obtener una sesión asíncrona ---
# (Sin cambios aquí - Asumiendo que este es el 'get_session' que usan tus endpoints)
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    # print("DEBUG: Abriendo sesión asíncrona...") # Debug
    async with AsyncSessionFactory() as session:
        # print("DEBUG: Sesión asíncrona obtenida, yielding...") # Debug
        try:
            yield session
            # print("DEBUG: Sesión asíncrona yield terminado.") # Debug
        except Exception as e:
             print(f"ERROR en sesión: {e}. Haciendo rollback...")
             await session.rollback()
             raise # Re-lanzar la excepción para que FastAPI la maneje
        finally:
            # print("DEBUG: Cerrando sesión asíncrona.") # Debug
             # No es necesario cerrar explícitamente con el context manager 'async with'
             pass


# --- Función de inicialización (Opcional) ---
# (Sin cambios aquí)
async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
        print("Base de datos inicializada (tablas creadas si no existían).")

# --- Código comentado para sesión síncrona (lo dejamos comentado) ---
# from sqlalchemy import create_engine
# ...