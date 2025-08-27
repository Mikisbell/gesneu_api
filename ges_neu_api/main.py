# ges_neu_api/main.py

from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

# Configuración
from ges_neu_api.core.config import settings
from ges_neu_api.core.database import init_db
from ges_neu_api.core.exceptions import ErrorResponse

# Importar módulo de monitoreo
from ges_neu_api.core.monitoring import setup_monitoring, monitor_performance
import logging

# Importar modelos para asegurar que las relaciones se resuelvan correctamente
# Esto debe estar antes de cualquier importación que use los modelos
from ges_neu_api.neumaticos import models as neumaticos_models  # noqa: F401

# Importar routers
from ges_neu_api.auth import router as auth_router
from ges_neu_api.catalogos.router import router as catalogos_router

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="""
        # API de Gestión de Neumáticos (GES_NEU)
        
        Bienvenido a la documentación de la API de GES_NEU. Este sistema permite gestionar:
        
        - Vehículos y sus configuraciones
        - Neumáticos y su ciclo de vida
        - Reportes y métricas
        
        ## Autenticación
        La mayoría de los endpoints requieren autenticación mediante JWT.
        
        ## Códigos de estado
        - 200: Operación exitosa
        - 400: Error en la solicitud
        - 401: No autorizado
        - 403: Prohibido
        - 404: Recurso no encontrado
        - 422: Error de validación
        - 500: Error interno del servidor
        
        ## Convenciones
        - Fechas en formato ISO 8601 (YYYY-MM-DD)
        - UUIDs para identificadores únicos
        """,
        routes=app.routes,
    )
    
    # Personalizar esquema OpenAPI
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    # Agregar respuestas de error globales
    for path in openapi_schema.get("paths", {}).values():
        for method in path.values():
            for response in method.get("responses", {}).values():
                if "application/json" in response.get("content", {}):
                    response["content"]["application/json"]["schema"] = {
                        "$ref": "#/components/schemas/ErrorResponse"
                    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para el sistema GES_NEU - Gestión de Neumáticos",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=None,  # Deshabilitar docs por defecto
    redoc_url=None,  # Deshabilitar redoc por defecto
    contact={
        "name": "Soporte Técnico",
        "email": "soporte@gesneu.com",
    },
    license_info={
        "name": "Licencia Propietaria",
        "url": "https://gesneu.com/licencia",
    },
)

# Configurar el esquema OpenAPI personalizado
app.openapi = custom_openapi

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar monitoreo
setup_monitoring(app)

# Incluir esquema de respuesta de error
app.include_schema(ErrorResponse)

# Rutas personalizadas para la documentación
@app.get(f"{settings.API_V1_STR}/docs", include_in_schema=False)
async def get_swagger_documentation():
    return get_swagger_ui_html(
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        title=f"{settings.PROJECT_NAME} - Swagger UI",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )

@app.get(f"{settings.API_V1_STR}/redoc", include_in_schema=False)
async def get_redoc_documentation():
    return get_redoc_html(
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        title=f"{settings.PROJECT_NAME} - ReDoc",
        redoc_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )

# Incluimos los routers con etiquetas y descripciones
app.include_router(
    auth_router.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["Autenticación"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
    },
)

app.include_router(
    catalogos_router,
    prefix=f"{settings.API_V1_STR}/catalogos",
    tags=["Catálogos"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
    },
)

# Evento de inicio para inicializar la base de datos
@app.on_event("startup")
async def startup_event():
    await init_db()

# Ruta raíz con documentación mejorada
@app.get(
    "/",
    response_model=dict,
    summary="Bienvenida",
    description="""
    ## Bienvenido a la API de GES_NEU
    
    Esta es la página de inicio de la API de Gestión de Neumáticos.
    
    ### Acceso a la documentación:
    - [Swagger UI](/api/v1/docs)
    - [ReDoc](/api/v1/redoc)
    - [OpenAPI JSON](/api/v1/openapi.json)
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Mensaje de bienvenida",
            "content": {
                "application/json": {
                    "example": {"message": "Bienvenido a la API de GES_NEU"}
                }
            },
        }
    }
)
@monitor_performance(log_level=logging.INFO)
async def root():
    return {
        "message": "Bienvenido a la API de GES_NEU",
        "documentation": f"{settings.API_V1_STR}/docs",
        "version": "1.0.0",
    }
