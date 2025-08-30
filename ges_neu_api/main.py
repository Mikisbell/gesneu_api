"""
Punto de entrada principal de la API de Gestión de Neumáticos.

Este módulo configura e inicia la aplicación FastAPI, integrando todos los componentes
como autenticación, rutas, manejo de errores, documentación y monitoreo.
"""
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Core imports - Usando rutas absolutas
from .core.config import settings
from .core.exceptions import global_exception_handler
from .core.logging_config import get_logger, setup_structured_logging
from .core.monitoring import setup_monitoring, setup_metrics

# Module imports - Usando rutas absolutas
from .modules.auth.router import router as auth_router
from .modules.catalogos.router import router as catalogos_router
from .modules.vehiculos.router import router as vehiculos_router
from .modules.neumaticos.router import router as neumaticos_router

# Configuración de logging
logger = get_logger(__name__)

# Configuración de la aplicación
APP_TITLE = "API de Gestión de Neumáticos"
APP_DESCRIPTION = "API para la gestión integral de neumáticos y vehículos"
APP_VERSION = "1.0.0"

# Configuración de CORS
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Frontend local
    "http://localhost:8000",  # API local
    "https://tu-dominio.com", # Dominio de producción
]

# Configuración del ciclo de vida de la aplicación
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja eventos de inicio y cierre de la aplicación."""
    # Código que se ejecuta al iniciar la aplicación
    logger.info("Iniciando la aplicación...")
    
    # Configurar logging estructurado
    setup_structured_logging()
    
    # Configurar monitoreo (sin métricas, que ya se configuran antes)
    setup_monitoring(app, service_name=settings.PROJECT_NAME)
    
    yield
    
    # Código que se ejecuta al cerrar la aplicación
    logger.info("Cerrando la aplicación...")

# Crear la aplicación FastAPI
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar Métricas de Prometheus
setup_metrics(app)

# Manejar excepciones globales
app.add_exception_handler(HTTPException, global_exception_handler)

# Incluir rutas
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Autenticación"])
app.include_router(catalogos_router, prefix=f"{settings.API_V1_STR}/catalogos", tags=["Catálogos"])
app.include_router(vehiculos_router, prefix=f"{settings.API_V1_STR}/vehiculos", tags=["Vehículos"])
app.include_router(neumaticos_router, prefix=f"{settings.API_V1_STR}/neumaticos", tags=["Neumáticos"])

@app.get("/")
async def root():
    """Ruta raíz que devuelve un mensaje de bienvenida."""
    return {
        "message": "Bienvenido a la API de Gestión de Neumáticos",
        "version": APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get(f"{settings.API_V1_STR}/health")
async def health_check():
    """Endpoint de verificación de salud de la API."""
    return {"status": "ok", "environment": settings.APP_ENV}

# Middleware para registrar solicitudes
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para registrar información de las solicitudes HTTP."""
    logger.info(
        "Solicitud recibida",
        extra={
            "props": {
                "method": request.method,
                "url": str(request.url),
                "client": request.client.host if request.client else "unknown",
            }
        }
    )
    
    try:
        response = await call_next(request)
        logger.info(
            "Respuesta enviada",
            extra={
                "props": {
                    "method": request.method,
                    "url": str(request.url),
                    "status_code": response.status_code,
                }
            }
        )
        return response
    except Exception as e:
        logger.error(
            "Error al procesar la solicitud",
            extra={
                "props": {
                    "method": request.method,
                    "url": str(request.url),
                    "error": str(e),
                }
            },
            exc_info=True,
        )
        raise

# Configuración para ejecutar con Uvicorn
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "ges_neu_api.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.APP_DEBUG,
        workers=settings.WORKERS,
    )