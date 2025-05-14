"""
Esquemas Pydantic para el servicio de alertas.

Este módulo define los modelos de datos utilizados para la validación
y serialización en el servicio de alertas.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field, validator
from enum import Enum

class AlertSeverity(str, Enum):
    """Niveles de severidad para las alertas."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class AlertStatus(str, Enum):
    """Estados posibles de una alerta."""
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"

class AlertBase(BaseModel):
    """Modelo base para alertas."""
    title: str = Field(..., max_length=200, description="Título descriptivo de la alerta")
    description: str = Field(..., description="Descripción detallada de la alerta")
    severity: AlertSeverity = Field(..., description="Nivel de severidad de la alerta")
    status: AlertStatus = Field(default=AlertStatus.OPEN, description="Estado actual de la alerta")
    source: Optional[str] = Field(None, description="Fuente o componente que generó la alerta")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Metadatos adicionales de la alerta"
    )

class AlertCreate(AlertBase):
    """Modelo para la creación de nuevas alertas."""
    related_entity_type: Optional[str] = Field(
        None,
        description="Tipo de entidad relacionada (neumatico, vehiculo, etc.)"
    )
    related_entity_id: Optional[UUID] = Field(
        None,
        description="ID de la entidad relacionada"
    )

class AlertUpdate(BaseModel):
    """Modelo para actualización de alertas existentes."""
    status: Optional[AlertStatus] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    resolved_by: Optional[UUID] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Notas sobre cómo se resolvió la alerta"
    )

    class Config:
        extra = "forbid"  # No permitir campos adicionales

class AlertResponse(AlertBase):
    """Modelo de respuesta para alertas."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    resolved_by: Optional[UUID] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[UUID] = None

    class Config:
        orm_mode = True

class AlertSummary(BaseModel):
    """Resumen de estadísticas de alertas."""
    total: int = 0
    by_severity: Dict[AlertSeverity, int] = Field(
        default_factory=dict,
        description="Conteo de alertas por nivel de severidad"
    )
    by_status: Dict[AlertStatus, int] = Field(
        default_factory=dict,
        description="Conteo de alertas por estado"
    )
    recent_alerts: List[AlertResponse] = Field(
        default_factory=list,
        description="Lista de alertas recientes"
    )

class AlertFilter(BaseModel):
    """Filtros para consulta de alertas."""
    status: Optional[AlertStatus] = None
    severity: Optional[AlertSeverity] = None
    source: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[UUID] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    search: Optional[str] = None

    @validator('created_after', 'created_before', pre=True)
    def parse_dates(cls, value):
        """Valida y parsea fechas en diferentes formatos."""
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass
        return value
