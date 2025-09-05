"""
Router ML para endpoints de Machine Learning.
Sprint 1: Endpoint para datos de entrenamiento.
Sprint 3: Endpoints de predicción implementados.
"""
from datetime import date
from typing import Optional, List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from ...core.exceptions import RecursoNoEncontradoError, OperacionInvalidaError
from .service import MLService
from .schemas import TrainingDataResponse, PredictionRequest, PredictionResponse, BatchPredictionRequest, BatchPredictionResponse

router = APIRouter(prefix="/ml", tags=["Machine Learning"])


def get_ml_service(db: AsyncSession = Depends(get_session)) -> MLService:
    """Dependency para obtener el servicio ML."""
    return MLService(db)


@router.get("/training-data", response_model=TrainingDataResponse)
async def get_training_data(
    start_date: Optional[date] = Query(None, description="Fecha inicio del rango (fecha_compra)"),
    end_date: Optional[date] = Query(None, description="Fecha fin del rango (fecha_compra)"),
    include_active: bool = Query(True, description="Incluir neumáticos activos"),
    include_inactive: bool = Query(True, description="Incluir neumáticos inactivos/desechados"),
    min_km: Optional[int] = Query(None, ge=0, description="Kilometraje mínimo acumulado"),
    max_km: Optional[int] = Query(None, ge=0, description="Kilometraje máximo acumulado"),
    service: MLService = Depends(get_ml_service)
):
    """
    Obtiene datos históricos de neumáticos para entrenamiento de modelos ML.
    
    Este endpoint proporciona datos estructurados que incluyen:
    - Información del neumático y su modelo
    - Historial de kilometraje y desgaste
    - Mediciones de profundidad actuales
    - Variables objetivo para entrenamiento supervisado
    
    Los datos están preparados para algoritmos de ML como:
    - Regresión para predicción de vida útil restante
    - Clasificación para predicción de estado futuro
    - Series temporales para análisis de desgaste
    """
    return await service.get_training_data(
        start_date=start_date,
        end_date=end_date,
        include_active=include_active,
        include_inactive=include_inactive,
        min_km=min_km,
        max_km=max_km
    )


@router.post("/predict", response_model=PredictionResponse)
async def predict_single_tire(
    request: PredictionRequest,
    service: MLService = Depends(get_ml_service)
):
    """
    Genera predicción para un neumático específico usando modelo ML entrenado.
    
    Sprint 3: Implementación completa con integración al script predict.py
    """
    return await service.predict_single_neumatico(request.neumatico_id)


@router.post("/recalculate-all")
async def recalculate_all_predictions(
    only_active: bool = Query(True, description="Solo recalcular neumáticos activos"),
    service: MLService = Depends(get_ml_service)
) -> Dict[str, Any]:
    """
    Recalcula predicciones para todos los neumáticos usando modelo ML entrenado.
    
    Sprint 3: Implementación completa con procesamiento batch optimizado.
    """
    return await service.recalculate_all_predictions(only_active=only_active)
