"""
Módulo para excepciones personalizadas y manejo de errores.

Este módulo define excepciones personalizadas para la API y un manejador
global para convertirlas en respuestas HTTP apropiadas.
"""
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Modelo estándar para respuestas de error."""
    status: str = "error"
    message: str
    code: str
    details: Optional[Dict[str, Any]] = None


class AppException(HTTPException):
    """Excepción base para la aplicación.
    
    Args:
        status_code: Código de estado HTTP
        message: Mensaje de error legible
        code: Código de error único
        details: Detalles adicionales del error
    """
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    code: str = "internal_server_error"
    
    def __init__(
        self,
        message: str = "Error interno del servidor",
        status_code: Optional[int] = None,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code or self.status_code
        self.code = code or self.code
        self.details = details
        super().__init__(status_code=self.status_code, detail=message)


class BadRequestException(AppException):
    """Excepción para solicitudes incorrectas o inválidas."""
    status_code = status.HTTP_400_BAD_REQUEST
    code = "bad_request"
    
    def __init__(self, message: str = "Solicitud incorrecta", **kwargs):
        super().__init__(message=message, **kwargs)


class NotFoundException(AppException):
    """Excepción para recursos no encontrados."""
    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"
    
    def __init__(self, resource: str, **kwargs):
        message = f"{resource} no encontrado"
        super().__init__(message=message, **kwargs)


class UnauthorizedException(AppException):
    """Excepción para autenticación fallida."""
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "unauthorized"
    
    def __init__(self, message: str = "No autorizado", **kwargs):
        super().__init__(message=message, **kwargs)


class ForbiddenException(AppException):
    """Excepción para acceso denegado."""
    status_code = status.HTTP_403_FORBIDDEN
    code = "forbidden"
    
    def __init__(self, message: str = "Acceso denegado", **kwargs):
        super().__init__(message=message, **kwargs)


class ValidationException(AppException):
    """Excepción para errores de validación."""
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    code = "validation_error"
    
    def __init__(self, message: str = "Error de validación", **kwargs):
        super().__init__(message=message, **kwargs)


class ConflictException(AppException):
    """Excepción para conflictos (ej: recurso ya existe)."""
    status_code = status.HTTP_409_CONFLICT
    code = "conflict"
    
    def __init__(self, message: str = "Conflicto con el recurso", **kwargs):
        super().__init__(message=message, **kwargs)


class BusinessRuleError(AppException):
    """Excepción para errores de reglas de negocio."""
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    code = "business_rule_error"
    
    def __init__(self, message: str = "Error de regla de negocio", **kwargs):
        super().__init__(message=message, **kwargs)


async def global_exception_handler(request, exc):
    """Manejador global de excepciones.
    
    Convierte excepciones en respuestas JSON estandarizadas.
    """
    if isinstance(exc, AppException):
        response = ErrorResponse(
            status="error",
            message=str(exc.detail),
            code=exc.code,
            details=exc.details
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=response.dict(exclude_none=True)
        )
    
    # Manejar excepciones de validación de Pydantic
    if hasattr(exc, "errors"):
        response = ErrorResponse(
            status="error",
            message="Error de validación en los datos de entrada",
            code="validation_error",
            details={"errors": exc.errors()}
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response.dict(exclude_none=True)
        )
    
    # Manejar excepciones HTTP estándar
    if isinstance(exc, HTTPException):
        response = ErrorResponse(
            status="error",
            message=str(exc.detail),
            code="http_error"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=response.dict(exclude_none=True)
        )
    
    # Manejar cualquier otra excepción no controlada
    response = ErrorResponse(
        status="error",
        message="Error interno del servidor",
        code="internal_server_error"
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response.dict(exclude_none=True)
    )
