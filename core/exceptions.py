"""
Excepciones personalizadas para la aplicación.

Este módulo define excepciones personalizadas para manejar diferentes
tipos de errores en la aplicación de manera consistente.
"""
from http import HTTPStatus
from typing import Any, Dict, Optional

class BaseAPIError(Exception):
    """Clase base para excepciones de la API."""
    
    def __init__(
        self,
        message: str,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Inicializa la excepción base.
        
        Args:
            message: Mensaje descriptivo del error
            status_code: Código de estado HTTP
            error_code: Código de error personalizado
            details: Detalles adicionales del error
        """
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or str(status_code)
        self.details = details or {}
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la excepción a un diccionario para la respuesta de la API."""
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details
            }
        }

class NotFoundError(BaseAPIError):
    """Excepción para recursos no encontrados."""
    
    def __init__(
        self, 
        resource: str, 
        resource_id: Any,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Inicializa la excepción de recurso no encontrado.
        
        Args:
            resource: Tipo de recurso no encontrado (ej: 'usuario', 'alerta')
            resource_id: Identificador del recurso no encontrado
            details: Detalles adicionales del error
        """
        message = f"{resource.capitalize()} con ID {resource_id} no encontrado"
        super().__init__(
            message=message,
            status_code=HTTPStatus.NOT_FOUND,
            error_code="not_found",
            details=details or {}
        )

class ValidationError(BaseAPIError):
    """Excepción para errores de validación."""
    
    def __init__(
        self, 
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Inicializa la excepción de validación.
        
        Args:
            message: Mensaje descriptivo del error de validación
            field: Campo que falló la validación (opcional)
            details: Detalles adicionales del error
        """
        error_details = details or {}
        if field:
            error_details["field"] = field
            
        super().__init__(
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
            error_code="validation_error",
            details=error_details
        )

class DatabaseError(BaseAPIError):
    """Excepción para errores de base de datos."""
    
    def __init__(
        self, 
        message: str = "Error en la base de datos",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Inicializa la excepción de base de datos.
        
        Args:
            message: Mensaje descriptivo del error
            details: Detalles adicionales del error
        """
        super().__init__(
            message=message,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            error_code="database_error",
            details=details or {}
        )

class UnauthorizedError(BaseAPIError):
    """Excepción para errores de autenticación/autoriación."""
    
    def __init__(
        self, 
        message: str = "No autorizado",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Inicializa la excepción de no autorizado.
        
        Args:
            message: Mensaje descriptivo del error
            details: Detalles adicionales del error
        """
        super().__init__(
            message=message,
            status_code=HTTPStatus.UNAUTHORIZED,
            error_code="unauthorized",
            details=details or {}
        )

class ForbiddenError(BaseAPIError):
    """Excepción para operaciones no permitidas."""
    
    def __init__(
        self, 
        message: str = "No tiene permiso para realizar esta acción",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Inicializa la excepción de prohibido.
        
        Args:
            message: Mensaje descriptivo del error
            details: Detalles adicionales del error
        """
        super().__init__(
            message=message,
            status_code=HTTPStatus.FORBIDDEN,
            error_code="forbidden",
            details=details or {}
        )

class ConflictError(BaseAPIError):
    """Excepción para conflictos (ej: recursos duplicados)."""
    
    def __init__(
        self, 
        message: str = "Conflicto con el recurso solicitado",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Inicializa la excepción de conflicto.
        
        Args:
            message: Mensaje descriptivo del error
            details: Detalles adicionales del error
        """
        super().__init__(
            message=message,
            status_code=HTTPStatus.CONFLICT,
            error_code="conflict",
            details=details or {}
        )

class RateLimitExceededError(BaseAPIError):
    """Excepción para límites de tasa excedidos."""
    
    def __init__(
        self, 
        message: str = "Límite de tasa excedido",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Inicializa la excepción de límite de tasa excedido.
        
        Args:
            message: Mensaje descriptivo del error
            retry_after: Segundos a esperar antes de reintentar
            details: Detalles adicionales del error
        """
        headers = {}
        if retry_after is not None:
            headers["Retry-After"] = str(retry_after)
            
        error_details = details or {}
        if retry_after is not None:
            error_details["retry_after"] = retry_after
            
        super().__init__(
            message=message,
            status_code=HTTPStatus.TOO_MANY_REQUESTS,
            error_code="rate_limit_exceeded",
            details=error_details
        )
        
        self.headers = headers

class ServiceUnavailableError(BaseAPIError):
    """Excepción para servicios temporalmente no disponibles."""
    
    def __init__(
        self, 
        message: str = "Servicio temporalmente no disponible",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Inicializa la excepción de servicio no disponible.
        
        Args:
            message: Mensaje descriptivo del error
            retry_after: Segundos a esperar antes de reintentar
            details: Detalles adicionales del error
        """
        error_details = details or {}
        if retry_after is not None:
            error_details["retry_after"] = retry_after
            
        super().__init__(
            message=message,
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            error_code="service_unavailable",
            details=error_details
        )
        
        if retry_after is not None:
            self.headers = {"Retry-After": str(retry_after)}

class ExternalServiceError(BaseAPIError):
    """Excepción para errores en servicios externos."""
    
    def __init__(
        self, 
        service_name: str,
        status_code: int,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Inicializa la excepción de servicio externo.
        
        Args:
            service_name: Nombre del servicio externo
            status_code: Código de estado HTTP devuelto por el servicio
            message: Mensaje descriptivo del error (opcional)
            details: Detalles adicionales del error
        """
        error_message = message or f"Error en el servicio externo: {service_name}"
        error_details = details or {}
        error_details["service"] = service_name
        error_details["status_code"] = status_code
        
        super().__init__(
            message=error_message,
            status_code=HTTPStatus.BAD_GATEWAY,
            error_code=f"external_service_error",
            details=error_details
        )
