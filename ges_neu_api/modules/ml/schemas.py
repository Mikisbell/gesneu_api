"""
Esquemas Pydantic para el módulo ML.
Sprint 1: Schemas para datos de entrenamiento y predicciones.
"""
from datetime import date, datetime
from typing import Optional, List, Any
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field


class TrainingDataPoint(BaseModel):
    """Punto de datos para entrenamiento del modelo ML."""
    neumatico_id: UUID
    numero_serie: Optional[str]
    modelo_neumatico_id: UUID
    
    # Datos del modelo
    medida: str
    profundidad_original_mm: Decimal
    tasa_desgaste_esperada_mm_km: Decimal
    vida_util_teorica_km: Optional[int]
    
    # Datos del neumático
    fecha_compra: date
    fecha_fabricacion: Optional[date]
    vida_actual: int
    es_reencauchado: bool
    kilometraje_acumulado: int
    kilometraje_vida_actual: Optional[int]
    
    # Mediciones actuales
    profundidad_remanente_actual_mm: Optional[Decimal]
    fecha_ultima_medicion_profundidad: Optional[datetime]
    tasa_desgaste_actual_mm_km: Optional[Decimal]
    
    # Ubicación y uso
    ubicacion_actual_vehiculo_id: Optional[UUID]
    ubicacion_actual_posicion_id: Optional[UUID]
    
    # Variables objetivo (para entrenamiento)
    vida_util_restante_km: Optional[int]
    fecha_desecho: Optional[date]  # Si ya fue desechado
    
    class Config:
        from_attributes = True


class TrainingDataResponse(BaseModel):
    """Respuesta con datos históricos para entrenamiento."""
    total_records: int
    data_points: List[TrainingDataPoint]
    date_range: dict[str, Optional[date]]
    summary_stats: dict[str, Any]
    
    class Config:
        from_attributes = True


class PredictionRequest(BaseModel):
    """Request para predicción individual."""
    neumatico_id: UUID
    force_recalculate: bool = Field(default=False, description="Forzar recálculo aunque ya exista predicción")


class PredictionResponse(BaseModel):
    """Respuesta de predicción para un neumático."""
    neumatico_id: UUID
    vida_util_restante_km: Optional[int]
    prediccion_fecha_reemplazo: Optional[date]
    confianza_prediccion: Optional[Decimal]
    fecha_prediccion: datetime
    modelo_version: str
    
    class Config:
        from_attributes = True


class BatchPredictionRequest(BaseModel):
    """Request para predicciones masivas."""
    neumatico_ids: Optional[List[UUID]] = Field(None, description="IDs específicos, si es None procesa todos")
    only_active: bool = Field(default=True, description="Solo neumáticos activos")
    force_recalculate: bool = Field(default=False, description="Forzar recálculo de todas las predicciones")


class BatchPredictionResponse(BaseModel):
    """Respuesta de predicciones masivas."""
    total_processed: int
    successful_predictions: int
    failed_predictions: int
    predictions: List[PredictionResponse]
    errors: List[dict]
    processing_time_seconds: float
    
    class Config:
        from_attributes = True
