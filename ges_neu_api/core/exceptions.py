"""Manejo centralizado de excepciones para la API GES_NEU."""
from typing import Any, Dict, Optional
from fastapi import status
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    """Modelo estándar para respuestas de error."""
    error: str
    code: str
    details: Optional[Dict[str, Any]] = None

class BaseAPIException(HTTPException):
    """Clase base para excepciones personalizadas de la API."""
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    code: str = "internal_server_error"
    
    def __init__(
        self,
        detail: str = "Ocurrió un error inesperado",
        headers: Optional[Dict[str, str]] = None,
        **details: Any,
    ) -> None:
        self.detail = detail
        self.details = details or {}
        self.headers = headers
        
        super().__init__(
            status_code=self.status_code,
            detail=detail,
            headers=headers
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la excepción a un diccionario para la respuesta."""
        return {
            "error": self.detail,
            "code": self.code,
            "details": self.details or None
        }

# Errores de autenticación y autorización
class UnauthorizedError(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "unauthorized"
    
class ForbiddenError(BaseAPIException):
    status_code = status.HTTP_403_FORBIDDEN
    code = "forbidden"

# Errores de validación
class ValidationError(BaseAPIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    code = "validation_error"

# Errores de recurso no encontrado
class NotFoundError(BaseAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"

# Errores de conflictos
class ConflictError(BaseAPIException):
    status_code = status.HTTP_409_CONFLICT
    code = "conflict"

# Errores de negocio
class BusinessRuleError(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "business_rule_violation"

# Manejador global de excepciones
async def global_exception_handler(request, exc):
    """Manejador global de excepciones para FastAPI."""
    from fastapi.responses import JSONResponse
    
    if isinstance(exc, BaseAPIException):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict()
        )
        
    # Manejar errores de validación de Pydantic
    if hasattr(exc, "errors") and hasattr(exc, "status_code"):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "Error de validación",
                "code": "validation_error",
                "details": {"errors": exc.errors()}
            }
        )
    
    # Error genérico no manejado
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Error interno del servidor",
            "code": "internal_server_error",
            "details": {"exception": str(exc) if str(exc) else "No hay detalles disponibles"}
        }
    )
