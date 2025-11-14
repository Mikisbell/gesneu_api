"""
Punto de entrada principal de la API de Gestión de Neumáticos.

Este módulo configura e inicia la aplicación FastAPI, integrando todos los componentes
como autenticación, rutas, manejo de errores, documentación y monitoreo.
"""
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, AsyncGenerator, Callable, Awaitable, TypeVar, cast
from starlette.middleware.base import RequestResponseEndpoint

from fastapi import FastAPI, HTTPException, Request, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Core imports - Usando rutas absolutas
from .core.config import settings
from .core.exceptions import global_exception_handler
from .core.logging_config import get_logger, setup_structured_logging
from logging import Logger
from .core.monitoring import setup_monitoring, setup_metrics
from .core.database import wait_for_db

# Module imports - Usando rutas absolutas
from .modules.auth.router import router as auth_router
from .modules.vehiculos.router import router as vehiculos_router
from .modules.neumaticos.router import router as neumaticos_router
from .modules.catalogos.router import router as catalogos_router
from .modules.inventario.router import router as inventario_router
from .modules.eventos.router import router as eventos_router
from .modules.garantias.router import router as garantias_router
from .modules.alertas.router import router as alertas_router
from .modules.bitacoras.router import router as bitacoras_router
from .modules.sistema.router import router as sistema_router
from .modules.ml.router import router as ml_router

# Configuración de logging
logger: Logger = get_logger(__name__)

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
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Maneja eventos de inicio y cierre de la aplicación."""
    # Código que se ejecuta al iniciar la aplicación
    logger.info("Iniciando la aplicación...")
    
    # Configurar logging estructurado
    setup_structured_logging()
    
    # Esperar robustamente a que la base de datos esté lista (reintentos con backoff)
    # await wait_for_db()  # Temporalmente deshabilitado para debug

    # Configurar monitoreo (sin métricas, que ya se configuran antes)
    setup_monitoring(app, service_name=settings.project_name)
    
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
    openapi_url=f"{settings.api_v1_str}/openapi.json"
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
app.include_router(auth_router, prefix=f"{settings.api_v1_str}/auth", tags=["auth"])
app.include_router(catalogos_router, prefix=f"{settings.api_v1_str}/catalogos", tags=["catalogos"])
app.include_router(vehiculos_router, prefix=f"{settings.api_v1_str}/vehiculos", tags=["vehiculos"])
app.include_router(neumaticos_router, prefix=f"{settings.api_v1_str}/neumaticos", tags=["neumaticos"])
app.include_router(inventario_router, prefix=f"{settings.api_v1_str}/inventario", tags=["inventario"])
app.include_router(eventos_router, prefix=f"{settings.api_v1_str}/eventos", tags=["eventos"])
app.include_router(garantias_router, prefix=f"{settings.api_v1_str}/garantias", tags=["garantias"])
app.include_router(alertas_router, prefix=f"{settings.api_v1_str}/alertas", tags=["alertas"])
app.include_router(bitacoras_router, prefix=f"{settings.api_v1_str}/bitacoras", tags=["bitacoras"])
app.include_router(sistema_router, prefix=f"{settings.api_v1_str}/sistema", tags=["sistema"])
app.include_router(ml_router, prefix=f"{settings.api_v1_str}", tags=["ml"])

@app.get("/")
async def root() -> dict[str, Any]:
    """Ruta raíz que devuelve un mensaje de bienvenida."""
    return {
        "message": "Bienvenido a la API de Gestión de Neumáticos",
        "version": APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Endpoint de verificación de salud de la API."""
    return {"status": "ok", "environment": settings.app_env}

@app.get("/debug")
async def debug_check() -> dict[str, Any]:
    """Endpoint de debug sin dependencias de BD."""
    import os
    return {
        "status": "debug_ok",
        "environment": settings.app_env,
        "has_db_url": bool(os.getenv("DATABASE_URL")),
        "has_jwt_key": bool(os.getenv("JWT_SECRET_KEY")),
        "has_app_key": bool(os.getenv("APP_SECRET_KEY")),
        "python_version": sys.version,
        "settings_loaded": True
    }

@app.get(f"{settings.api_v1_str}/health")
async def health_check_v1() -> dict[str, Any]:
    """Endpoint de verificación de salud de la API v1."""
    return {"status": "ok", "environment": settings.app_env, "version": APP_VERSION}

# Middleware para registrar solicitudes
# Para evitar el warning de mypy por decoradores no tipados, tipamos el decorador explícitamente
_F = TypeVar("_F", bound=Callable[..., Any])
middleware_http = cast(Callable[[_F], _F], app.middleware("http"))

@middleware_http
async def log_requests(
    request: Request,
    call_next: RequestResponseEndpoint,
) -> Response:
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
        response: Response = await call_next(request)
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
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.app_debug,
        workers=settings.workers,
    )