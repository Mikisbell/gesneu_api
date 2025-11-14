"""
Versión mínima de la API para diagnóstico.
"""
import os
import sys
from fastapi import FastAPI

# Crear la aplicación FastAPI mínima
app = FastAPI(
    title="GesNeu API - Debug",
    description="Versión mínima para diagnóstico",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Ruta raíz mínima."""
    return {"message": "GesNeu API Debug - Funcionando"}

@app.get("/health")
async def health():
    """Health check mínimo."""
    return {"status": "ok", "mode": "minimal"}

@app.get("/debug")
async def debug():
    """Debug de variables de entorno."""
    return {
        "status": "debug_minimal_ok",
        "has_database_url": bool(os.getenv("DATABASE_URL")),
        "has_jwt_secret": bool(os.getenv("JWT_SECRET_KEY")),
        "has_app_secret": bool(os.getenv("APP_SECRET_KEY")),
        "python_version": sys.version,
        "env_vars_count": len(os.environ),
        "working": True
    }

@app.get("/env")
async def env_check():
    """Verificar variables específicas."""
    return {
        "DATABASE_URL": "SET" if os.getenv("DATABASE_URL") else "NOT_SET",
        "JWT_SECRET_KEY": "SET" if os.getenv("JWT_SECRET_KEY") else "NOT_SET", 
        "APP_SECRET_KEY": "SET" if os.getenv("APP_SECRET_KEY") else "NOT_SET",
        "APP_ENV": os.getenv("APP_ENV", "NOT_SET"),
        "DB_HOST": os.getenv("DB_HOST", "NOT_SET")
    }
