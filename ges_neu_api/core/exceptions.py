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


# ========================================
# EXCEPCIONES ESPECÍFICAS DEL DOMINIO
# ========================================

class RecursoNoEncontradoError(NotFoundException):
    """Excepción para recursos específicos no encontrados."""
    
    def __init__(self, recurso: str, identificador: str, **kwargs):
        message = f"{recurso} con ID '{identificador}' no encontrado"
        super().__init__(resource=recurso, **kwargs)
        self.detail = message
        self.recurso = recurso
        self.identificador = identificador


class OperacionInvalidaError(BusinessRuleError):
    """Excepción para operaciones que violan reglas de negocio."""
    
    def __init__(self, operacion: str, razon: str, **kwargs):
        message = f"Operación '{operacion}' inválida: {razon}"
        super().__init__(message=message, **kwargs)
        self.operacion = operacion
        self.razon = razon


class EstadoInvalidoError(BusinessRuleError):
    """Excepción para transiciones de estado inválidas."""
    
    def __init__(self, recurso: str, estado_actual: str, estado_destino: str, **kwargs):
        message = f"{recurso} no puede cambiar de '{estado_actual}' a '{estado_destino}'"
        super().__init__(message=message, **kwargs)
        self.recurso = recurso
        self.estado_actual = estado_actual
        self.estado_destino = estado_destino


class DuplicadoError(ConflictException):
    """Excepción para recursos duplicados."""
    
    def __init__(self, recurso: str, campo: str, valor: str, **kwargs):
        message = f"{recurso} con {campo} '{valor}' ya existe"
        super().__init__(message=message, **kwargs)
        self.recurso = recurso
        self.campo = campo
        self.valor = valor


class DependenciaError(BusinessRuleError):
    """Excepción para errores de dependencias entre recursos."""
    
    def __init__(self, recurso: str, dependencia: str, **kwargs):
        message = f"No se puede procesar {recurso}: dependencia con {dependencia}"
        super().__init__(message=message, **kwargs)
        self.recurso = recurso
        self.dependencia = dependencia


class InventarioInsuficienteError(BusinessRuleError):
    """Excepción para stock insuficiente."""
    
    def __init__(self, producto: str, disponible: int, requerido: int, **kwargs):
        message = f"Stock insuficiente de {producto}: disponible {disponible}, requerido {requerido}"
        super().__init__(message=message, **kwargs)
        self.producto = producto
        self.disponible = disponible
        self.requerido = requerido


class NeumaticoNoDisponibleError(BusinessRuleError):
    """Excepción para neumáticos no disponibles para operación."""
    
    def __init__(self, neumatico_id: str, estado_actual: str, operacion: str, **kwargs):
        message = f"Neumático {neumatico_id} en estado '{estado_actual}' no disponible para {operacion}"
        super().__init__(message=message, **kwargs)
        self.neumatico_id = neumatico_id
        self.estado_actual = estado_actual
        self.operacion = operacion


class VehiculoOcupadoError(BusinessRuleError):
    """Excepción para vehículos ocupados."""
    
    def __init__(self, vehiculo_id: str, **kwargs):
        message = f"Vehículo {vehiculo_id} está ocupado y no puede ser modificado"
        super().__init__(message=message, **kwargs)
        self.vehiculo_id = vehiculo_id


# ========================================
# MAPEO DE EXCEPCIONES A HTTP STATUS
# ========================================

EXCEPTION_STATUS_MAP = {
    RecursoNoEncontradoError: status.HTTP_404_NOT_FOUND,
    OperacionInvalidaError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    EstadoInvalidoError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    DuplicadoError: status.HTTP_409_CONFLICT,
    DependenciaError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    InventarioInsuficienteError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    NeumaticoNoDisponibleError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    VehiculoOcupadoError: status.HTTP_422_UNPROCESSABLE_ENTITY,
}


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
    
    # Manejar excepciones HTTP estándar devolviendo estructura FastAPI por defecto
    if isinstance(exc, HTTPException):
        headers = getattr(exc, "headers", None)
        content = {"detail": exc.detail}
        return JSONResponse(
            status_code=exc.status_code,
            content=content,
            headers=headers
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
