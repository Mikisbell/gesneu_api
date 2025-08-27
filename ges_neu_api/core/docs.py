"""
Configuración de la documentación de la API.

Este módulo configura la documentación interactiva de la API usando
OpenAPI (Swagger) y ReDoc.
"""
from typing import Any, Dict, List, Optional, Union

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
from fastapi.openapi.models import OpenAPI
from fastapi.openapi.utils import get_openapi
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse

def setup_documentation(app: FastAPI) -> None:
    """Configura la documentación de la API.
    
    Habilita la documentación interactiva en /docs (Swagger UI) y /redoc.
    """
    # Configuración personalizada para Swagger UI
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html() -> HTMLResponse:
        return get_swagger_ui_html(
            openapi_url=app.openapi_url or "/openapi.json",
            title=f"{app.title} - Documentación de la API",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="/static/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui.css",
            swagger_favicon_url="/static/favicon.ico",
            swagger_ui_parameters={
                "defaultModelsExpandDepth": -1,  # Oculta los modelos por defecto
                "docExpansion": "list",  # Solo expande las listas
                "filter": "",  # Habilita la búsqueda
                "persistAuthorization": True,  # Persiste la autorización
                "displayRequestDuration": True,  # Muestra la duración de las solicitudes
            },
        )

    # Configuración personalizada para ReDoc
    @app.get("/redoc", include_in_schema=False)
    async def redoc_html() -> HTMLResponse:
        return get_swagger_ui_html(
            openapi_url=app.openapi_url or "/openapi.json",
            title=f"{app.title} - Documentación de la API (ReDoc)",
            swagger_js_url="/static/redoc.standalone.js",
            swagger_css_url="",
            swagger_favicon_url="/static/favicon.ico",
        )
    
    # Configuración personalizada para OpenAPI
    def custom_openapi() -> Dict[str, Any]:
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description or "",
            routes=app.routes,
            tags=app.openapi_tags,
            servers=app.servers,
        )
        
        # Personalización adicional del esquema OpenAPI
        openapi_schema["info"]["x-logo"] = {
            "url": "/static/logo.png"
        }
        
        # Configuración de seguridad
        openapi_schema["components"]["securitySchemes"] = {
            "OAuth2PasswordBearer": {
                "type": "oauth2",
                "flows": {
                    "password": {
                        "tokenUrl": "/api/v1/auth/token",
                        "scopes": {
                            "read": "Permiso de lectura",
                            "write": "Permiso de escritura",
                            "admin": "Permisos de administrador"
                        }
                    }
                }
            }
        }
        
        # Asegurar que todas las rutas requieran autenticación por defecto
        for path in openapi_schema.get("paths", {}).values():
            for method in path.values():
                if method.get("security") is None:
                    method["security"] = [{"OAuth2PasswordBearer": []}]
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    # Asignar la función personalizada de OpenAPI
    app.openapi = custom_openapi  # type: ignore
    
    # Registrar los archivos estáticos necesarios
    @app.get("/static/{file_path:path}", include_in_schema=False)
    async def serve_static(file_path: str) -> JSONResponse:
        # En producción, esto debería ser manejado por un servidor web como Nginx
        # o un servicio de CDN para archivos estáticos
        return JSONResponse(
            status_code=404,
            content={"detail": "Static file not found"}
        )
    
    print(f"\n📚 Documentación disponible en /docs (Swagger UI) y /redoc\n")
