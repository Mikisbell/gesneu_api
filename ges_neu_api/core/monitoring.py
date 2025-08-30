"""
Módulo de monitoreo para la API.

Este módulo configura el monitoreo de la aplicación usando Prometheus para métricas
y OpenTelemetry para trazas distribuidas.
"""
import os
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
    make_asgi_app,
)
from prometheus_client.registry import CollectorRegistry
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from .logging_config import get_logger

logger = get_logger(__name__)

# Inicializar el registro de métricas
METRICS_REGISTRY = CollectorRegistry()

# Definir métricas
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total de solicitudes HTTP",
    ["method", "endpoint", "http_status"],
    registry=METRICS_REGISTRY,
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Tiempo de respuesta de las solicitudes HTTP en segundos",
    ["method", "endpoint"],
    registry=METRICS_REGISTRY,
)

REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Número de solicitudes HTTP en progreso",
    ["method", "endpoint"],
    registry=METRICS_REGISTRY,
)

EXCEPTIONS_COUNT = Counter(
    "http_exceptions_total",
    "Total de excepciones por tipo",
    ["exception_type", "endpoint"],
    registry=METRICS_REGISTRY,
)

import time
from functools import wraps

# Add a simple decorator for service method monitoring
def monitor_service_method(func):
    """
    Decorator to monitor the execution time of a service method.
    Logs the duration and can optionally integrate with OpenTelemetry spans.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        
        # Optional: OpenTelemetry span integration
        span = None
        if "opentelemetry.trace" in globals(): # Check if OpenTelemetry is available
            tracer = opentelemetry.trace.get_tracer(__name__)
            span = tracer.start_span(f"service.{func.__name__}")
            
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            if span:
                span.record_exception(e)
                span.set_status(opentelemetry.trace.Status(opentelemetry.trace.StatusCode.ERROR, str(e)))
            raise
        finally:
            end_time = time.perf_counter()
            duration = (end_time - start_time) * 1000 # duration in milliseconds
            logger.info(f"Service method '{func.__name__}' executed in {duration:.2f}ms",
                        extra={"method_name": func.__name__, "duration_ms": duration})
            if span:
                span.end()
    return wrapper


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware para registrar métricas de Prometheus."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        method = request.method
        endpoint = request.url.path
        
        # Registrar solicitud en progreso
        REQUESTS_IN_PROGRESS.labels(method=method, endpoint=endpoint).inc()
        
        # Medir tiempo de respuesta
        with REQUEST_LATENCY.labels(method=method, endpoint=endpoint).time():
            try:
                response = await call_next(request)
                status_code = response.status_code
            except Exception as e:
                # Registrar excepción
                EXCEPTIONS_COUNT.labels(
                    exception_type=type(e).__name__, 
                    endpoint=endpoint
                ).inc()
                raise
            finally:
                # Decrementar contador de solicitudes en progreso
                REQUESTS_IN_PROGRESS.labels(method=method, endpoint=endpoint).dec()
        
        # Registrar solicitud completada
        REQUEST_COUNT.labels(
            method=method, 
            endpoint=endpoint, 
            http_status=status_code
        ).inc()
        
        return response


def setup_metrics(app: FastAPI) -> None:
    """Configura las métricas de Prometheus en la aplicación FastAPI."""
    # Agregar middleware de métricas
    app.add_middleware(PrometheusMiddleware)
    
    # Agregar endpoint de métricas
    metrics_app = make_asgi_app(registry=METRICS_REGISTRY)
    
    @app.get("/metrics")
    async def metrics() -> Response:
        """Endpoint para exponer las métricas de Prometheus."""
        return Response(
            content=generate_latest(registry=METRICS_REGISTRY),
            media_type=CONTENT_TYPE_LATEST,
        )
    
    logger.info("Métricas de Prometheus configuradas en /metrics")


def setup_tracing(app: FastAPI, service_name: str) -> None:
    """Configura el tracing distribuido con OpenTelemetry.
    
    Args:
        app: Instancia de FastAPI
        service_name: Nombre del servicio para el tracing
    """
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        
        # Configurar proveedor de trazas
        resource = Resource(attributes={"service.name": service_name})
        trace.set_tracer_provider(TracerProvider(resource=resource))
        
        # Configurar exportador OTLP (para Jaeger/OpenTelemetry Collector)
        otlp_endpoint = os.getenv("OTLP_ENDPOINT")
        if otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
            span_processor = BatchSpanProcessor(otlp_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)
            
            # Instrumentar FastAPI
            FastAPIInstrumentor.instrument_app(app)
            
            # Instrumentar SQLAlchemy si es necesario
            SQLAlchemyInstrumentor().instrument()
            
            logger.info(f"Tracing configurado con OTLP en {otlp_endpoint}")
        else:
            logger.warning("OTLP_ENDPOINT no configurado. El tracing no estará habilitado.")
            
    except ImportError:
        logger.warning("OpenTelemetry no está instalado. El tracing no estará habilitado.")
    except Exception as e:
        logger.error(f"Error al configurar el tracing: {e}")


def setup_health_check(app: FastAPI) -> None:
    """Configura el endpoint de health check."""
    
    @app.get("/health")
    async def health_check() -> Dict[str, str]:
        """Endpoint de health check."""
        return {"status": "ok"}
    
    logger.info("Health check configurado en /health")


def setup_monitoring(app: FastAPI, service_name: str) -> None:
    """Configura todo el sistema de monitoreo.
    
    Args:
        app: Instancia de FastAPI
        service_name: Nombre del servicio para el tracing
    """
    # Configurar tracing
    setup_tracing(app, service_name)
    
    # Configurar health check
    setup_health_check(app)
    
    logger.info("Sistema de monitoreo configurado correctamente")