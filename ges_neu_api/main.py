"""
Punto de entrada principal de la API de Gestión de Neumáticos.

Este módulo configura e inicia la aplicación FastAPI, integrando todos los componentes
como autenticación, rutas, manejo de errores, documentación y monitoreo.
"""
import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import settings
from .core.contracts import validate_implementation
from .core.docs import setup_documentation
from .core.exceptions import global_exception_handler
from .core.logging_config import get_logger, setup_structured_logging
from .core.monitoring import setup_monitoring

# Configurar logging
logger = get_logger(__name__)

# Importar rutas de los módulos
from .auth.router import router as auth_router
from .catalogos.router import router as catalogos_router
from .vehiculos.router import router as vehiculos_router
from .neumaticos.router import router as neumaticos_router

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
    
    # Aquí podrías inicializar conexiones a bases de datos, etc.
    
    yield  # La aplicación está en ejecución
    
    # Código que se ejecuta al cerrar la aplicación
    logger.info("Cerrando la aplicación...")
    # Aquí podrías cerrar conexiones, liberar recursos, etc.

# Crear la aplicación FastAPI
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url=None,  # Deshabilitar docs por defecto (los configuraremos manualmente)
    redoc_url=None,  # Deshabilitar redoc por defecto (los configuraremos manualmente)
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar manejador global de excepciones
app.add_exception_handler(Exception, global_exception_handler)

# Configurar documentación
setup_documentation(app)

# Configurar monitoreo
setup_monitoring(app, service_name="ges-neu-api")

# Incluir rutas de la API
API_PREFIX = "/api/v1"

# Rutas de autenticación
app.include_router(
    auth_router,
    prefix=f"{API_PREFIX}/auth",
    tags=["Autenticación"],
)

# Rutas de catálogos
app.include_router(
    catalogos_router,
    prefix=f"{API_PREFIX}/catalogos",
    tags=["Catálogos"],
)

# Rutas de vehículos
app.include_router(
    vehiculos_router,
    prefix=f"{API_PREFIX}/vehiculos",
    tags=["Vehículos"],
)

# Rutas de neumáticos
app.include_router(
    neumaticos_router,
    prefix=f"{API_PREFIX}/neumaticos",
    tags=["Neumáticos"],
)

# Ruta de bienvenida
@app.get("/", include_in_schema=False)
async def root() -> Dict[str, str]:
    """Ruta raíz que devuelve un mensaje de bienvenida."""
    return {
        "message": "Bienvenido a la API de Gestión de Neumáticos",
        "docs": "/docs",
        "redoc": "/redoc",
        "version": APP_VERSION,
    }

# Ruta de verificación de salud
@app.get("/health", include_in_schema=False)
async def health_check() -> Dict[str, str]:
    """Endpoint de verificación de salud de la API."""
    return {"status": "ok"}

# Middleware para registrar solicitudes
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para registrar información de las solicitudes HTTP."""
    logger.info(
        f"Solicitud recibida: {request.method} {request.url}",
        extra={
            "method": request.method,
            "url": str(request.url),
            "client": request.client.host if request.client else "unknown",
        },
    )
    
    try:
        response = await call_next(request)
        logger.info(
            f"Respuesta enviada: {response.status_code}",
            extra={"status_code": response.status_code},
        )
        return response
    except Exception as e:
        logger.error(
            f"Error en la solicitud: {str(e)}",
            exc_info=True,
            extra={
                "method": request.method,
                "url": str(request.url),
                "error": str(e),
            },
        )
        raise

# Configuración para ejecutar con Uvicorn
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "ges_neu_api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=1,
    )
