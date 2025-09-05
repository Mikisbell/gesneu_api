"""
Router para el módulo de garantías de neumáticos.
"""
from typing import List, Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from .service import GarantiasService
from .models import GarantiasNeumaticos
from .schemas import GarantiaNeumaticoResponse, GarantiaNeumaticoCreate

router = APIRouter(tags=["garantias"])

async def get_garantias_service(db: AsyncSession = Depends(get_session)) -> GarantiasService:
    return GarantiasService(db)

@router.get("/", response_model=List[GarantiaNeumaticoResponse])
@router.get("/neumaticos", response_model=List[GarantiaNeumaticoResponse])
async def get_garantias_neumaticos(
    skip: int = 0,
    limit: int = 100,
    service: GarantiasService = Depends(get_garantias_service)
):
    """Obtener todas las garantías de neumáticos."""
    return await service.get_all_garantias(skip, limit)

@router.get("/vigentes", response_model=List[GarantiaNeumaticoResponse])
async def get_garantias_vigentes(
    fecha_referencia: Optional[date] = None,
    service: GarantiasService = Depends(get_garantias_service)
):
    """Obtener garantías vigentes."""
    return await service.get_garantias_vigentes(fecha_referencia)

@router.get("/por-vencer", response_model=List[GarantiaNeumaticoResponse])
async def get_garantias_por_vencer(
    dias_anticipacion: int = 30,
    service: GarantiasService = Depends(get_garantias_service)
):
    """Obtener garantías que vencen pronto."""
    return await service.get_garantias_por_vencer(dias_anticipacion)

@router.get("/neumatico/{neumatico_id}", response_model=List[GarantiaNeumaticoResponse])
async def get_garantias_neumatico(
    neumatico_id: UUID,
    skip: int = 0,
    limit: int = 100,
    service: GarantiasService = Depends(get_garantias_service)
):
    """Obtener garantías de un neumático."""
    return await service.get_garantias_neumatico(neumatico_id, skip, limit)

@router.get("/{garantia_id}", response_model=GarantiaNeumaticoResponse)
async def get_garantia(
    garantia_id: UUID,
    service: GarantiasService = Depends(get_garantias_service)
):
    """Obtener garantía por ID."""
    garantia = await service.get_garantia(garantia_id)
    if not garantia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Garantía no encontrada"
        )
    return garantia

@router.post("/", response_model=GarantiaNeumaticoResponse)
async def crear_garantia(
    garantia_data: GarantiaNeumaticoCreate,
    service: GarantiasService = Depends(get_garantias_service)
):
    """Crear nueva garantía."""
    return await service.crear_garantia(
        garantia_data.neumatico_id, garantia_data.proveedor_id, 
        garantia_data.fecha_inicio, garantia_data.fecha_fin,
        garantia_data.tipo_garantia, garantia_data.condiciones_url
    )
