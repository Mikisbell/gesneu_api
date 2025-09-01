"""
Módulo de monitoreo para la API.

Este módulo configura el monitoreo de la aplicación. 
Versión simplificada sin Prometheus para desarrollo inicial.
"""
import os
import time
from typing import Any, Dict, Optional
from functools import wraps

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from .logging_config import get_logger

logger = get_logger(__name__)


def monitor_service_method(func):
    """
    Decorator to monitor the execution time of a service method.
    Logs the duration for development monitoring.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            logger.error(f"Error in service method '{func.__name__}': {str(e)}")
            raise
        finally:
            end_time = time.perf_counter()
            duration = (end_time - start_time) * 1000
            logger.info(f"Service method '{func.__name__}' executed in {duration:.2f}ms")
    return wrapper


class SimpleMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware simplificado para logging de requests."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.perf_counter()
        
        try:
            response = await call_next(request)
            process_time = time.perf_counter() - start_time
            
            logger.info(
                f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
            )
            
            return response
        except Exception as e:
            process_time = time.perf_counter() - start_time
            logger.error(
                f"{request.method} {request.url.path} - ERROR: {str(e)} - {process_time:.3f}s"
            )
            raise


def setup_metrics(app: FastAPI) -> None:
    """Configura monitoreo básico sin Prometheus."""
    app.add_middleware(SimpleMonitoringMiddleware)
    logger.info("Monitoreo básico configurado")


def setup_tracing(app: FastAPI, service_name: str) -> None:
    """Placeholder para tracing - versión simplificada."""
    logger.info(f"Tracing placeholder configurado para servicio: {service_name}")


def setup_monitoring(app: FastAPI, service_name: str) -> None:
    """Configura sistema de monitoreo simplificado."""
    setup_tracing(app, service_name)
    logger.info("Sistema de monitoreo simplificado configurado")