"""
Módulo de monitoreo para la aplicación.

Proporciona utilidades para monitorear el rendimiento de la aplicación,
incluyendo decoradores para medir el tiempo de ejecución de funciones.
"""
import functools
import logging
import time
from typing import Any, Callable, Optional, TypeVar, cast

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

# Configuración de logging
logger = logging.getLogger(__name__)

# Tipo genérico para preservar la firma de la función decorada
F = TypeVar('F', bound=Callable[..., Any])

def monitor_performance(
    name: Optional[str] = None,
    log_level: int = logging.DEBUG,
    log_args: bool = False,
    log_result: bool = False
) -> Callable[[F], F]:
    """
    Decorador para monitorear el rendimiento de una función.
    
    Registra el tiempo de ejecución de la función decorada y opcionalmente
    los argumentos y el resultado.
    
    Args:
        name: Nombre personalizado para la función en los logs. Si es None, se usará el nombre de la función.
        log_level: Nivel de logging a utilizar (logging.DEBUG, logging.INFO, etc.)
        log_args: Si es True, registra los argumentos de la función
        log_result: Si es True, registra el resultado de la función
        
    Returns:
        La función decorada con capacidades de monitoreo
    """
    def decorator(func: F) -> F:
        func_name = name or func.__name__
        
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            
            try:
                # Ejecutar la función
                result = await func(*args, **kwargs)
                return result
                
            finally:
                # Calcular tiempo de ejecución
                end_time = time.perf_counter()
                execution_time = (end_time - start_time) * 1000  # en milisegundos
                
                # Construir mensaje de log
                log_parts = [f"{func_name} ejecutado en {execution_time:.2f}ms"]
                
                if log_args:
                    args_repr = [repr(a) for a in args]
                    kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
                    signature = ", ".join(args_repr + kwargs_repr)
                    log_parts.append(f"args: {signature}")
                
                if log_result and 'result' in locals():
                    result_repr = repr(result) if result is not None else "None"
                    log_parts.append(f"result: {result_repr}")
                
                # Registrar el mensaje
                logger.log(log_level, " | ".join(log_parts))
        
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            
            try:
                # Ejecutar la función
                result = func(*args, **kwargs)
                return result
                
            finally:
                # Calcular tiempo de ejecución
                end_time = time.perf_counter()
                execution_time = (end_time - start_time) * 1000  # en milisegundos
                
                # Construir mensaje de log
                log_parts = [f"{func_name} ejecutado en {execution_time:.2f}ms"]
                
                if log_args:
                    args_repr = [repr(a) for a in args]
                    kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
                    signature = ", ".join(args_repr + kwargs_repr)
                    log_parts.append(f"args: {signature}")
                
                if log_result and 'result' in locals():
                    result_repr = repr(result) if result is not None else "None"
                    log_parts.append(f"result: {result_repr}")
                
                # Registrar el mensaje
                logger.log(log_level, " | ".join(log_parts))
        
        # Devolver el wrapper apropiado basado en si la función es asíncrona o no
        if getattr(func, "__code__", None) and func.__code__.co_flags & 0x80:
            return cast(F, async_wrapper)
        return cast(F, sync_wrapper)
    
    return decorator


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para registrar información detallada sobre las solicitudes HTTP.
    
    Registra información como el método HTTP, la ruta, el código de estado
    y el tiempo de procesamiento de cada solicitud.
    """
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Registrar información de la solicitud
        method = request.method
        url = str(request.url)
        client = request.client.host if request.client else "unknown"
        
        logger.info(f"Inicio de solicitud: {method} {url} desde {client}")
        
        # Medir tiempo de procesamiento
        start_time = time.perf_counter()
        
        try:
            # Procesar la solicitud
            response = await call_next(request)
            return response
            
        except Exception as e:
            # Registrar errores no manejados
            logger.error(f"Error en la solicitud {method} {url}: {str(e)}", exc_info=True)
            raise
            
        finally:
            # Calcular y registrar tiempo de procesamiento
            end_time = time.perf_counter()
            processing_time = (end_time - start_time) * 1000  # en milisegundos
            
            # Obtener código de estado (si hay una respuesta)
            status_code = getattr(response, 'status_code', 500) if 'response' in locals() else 500
            
            logger.info(
                f"Fin de solicitud: {method} {url} - "
                f"Estatus: {status_code} | "
                f"Tiempo: {processing_time:.2f}ms"
            )


def setup_monitoring(app):
    """
    Configura el monitoreo para la aplicación FastAPI.
    
    Args:
        app: Instancia de FastAPI
    """
    # Añadir middleware de logging de solicitudes
    app.add_middleware(RequestLoggingMiddleware)
    
    logger.info("Monitoreo configurado correctamente")
