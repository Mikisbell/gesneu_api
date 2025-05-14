"""
Manejadores de excepciones globales para FastAPI.

Este módulo define los manejadores de excepciones globales que capturan
y formatean las respuestas de error de manera consistente.
"""
from typing import Any, Callable, Dict, Optional, Type, Union

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .exceptions import BaseAPIError

# Tipos de excepciones que manejaremos
ExceptionHandlerType = Callable[[Request, Any], JSONResponse]

async def http_exception_handler(
    request: Request, 
    exc: StarletteHTTPException
) -> JSONResponse:
    """
    Maneja excepciones HTTP de Starlette/FastAPI.
    
    Args:
        request: Objeto de solicitud de FastAPI
        exc: Excepción HTTP
        
    Returns:
        Respuesta JSON formateada
    """
    status_code = exc.status_code
    detail = exc.detail
    
    error_response = {
        "error": {
            "code": str(status_code),
            "message": detail if isinstance(detail, str) else "Error en la solicitud",
            "details": detail if not isinstance(detail, str) else {}
        }
    }
    
    return JSONResponse(
        status_code=status_code,
        content=error_response,
        headers=getattr(exc, "headers", None)
    )

async def validation_exception_handler(
    request: Request, 
    exc: Union[RequestValidationError, ValidationError]
) -> JSONResponse:
    """
    Maneja errores de validación de Pydantic.
    
    Args:
        request: Objeto de solicitud de FastAPI
        exc: Excepción de validación
        
    Returns:
        Respuesta JSON con errores de validación
    """
    errors = []
    
    # Manejar tanto RequestValidationError como ValidationError
    if hasattr(exc, "errors"):
        # Para RequestValidationError
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"]
            })
    
    error_response = {
        "error": {
            "code": "validation_error",
            "message": "Error de validación en los datos de entrada",
            "details": {"errors": errors}
        }
    }
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response
    )

async def api_error_handler(
    request: Request, 
    exc: BaseAPIError
) -> JSONResponse:
    """
    Maneja excepciones personalizadas de la API.
    
    Args:
        request: Objeto de solicitud de FastAPI
        exc: Excepción personalizada de la API
        
    Returns:
        Respuesta JSON formateada
    """
    response_data = exc.to_dict()
    
    # Obtener encabezados personalizados si existen
    headers = getattr(exc, "headers", None)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_data,
        headers=headers
    )

async def generic_exception_handler(
    request: Request, 
    exc: Exception
) -> JSONResponse:
    """
    Maneja excepciones no capturadas.
    
    Args:
        request: Objeto de solicitud de FastAPI
        exc: Excepción no capturada
        
    Returns:
        Respuesta JSON genérica de error
    """
    # En producción, no exponer detalles del error interno
    error_response = {
        "error": {
            "code": "internal_server_error",
            "message": "Error interno del servidor",
            "details": {}
        }
    }
    
    # En desarrollo, incluir más detalles
    import os
    if os.getenv("ENV") == "development":
        import traceback
        error_response["error"]["details"] = {
            "type": exc.__class__.__name__,
            "message": str(exc),
            "traceback": traceback.format_exc().splitlines()
        }
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response
    )

def register_exception_handlers(app: FastAPI) -> None:
    """
    Registra los manejadores de excepciones en la aplicación FastAPI.
    
    Args:
        app: Instancia de FastAPI
    """
    # Manejadores de excepciones estándar
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    
    # Manejador para excepciones personalizadas
    app.add_exception_handler(BaseAPIError, api_error_handler)
    
    # Manejador genérico para cualquier otra excepción no capturada
    app.add_exception_handler(Exception, generic_exception_handler)
