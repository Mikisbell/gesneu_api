"""
Router para el módulo de alertas del sistema.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from .service import AlertasService
from .models_fixed import Alertas

router = APIRouter(prefix="/alertas", tags=["alertas"])

async def get_alertas_service(db: AsyncSession = Depends(get_session)) -> AlertasService:
    return AlertasService(db)

@router.get("/{alerta_id}", response_model=Alertas)
async def get_alerta(
    alerta_id: UUID,
    service: AlertasService = Depends(get_alertas_service)
):
    """Obtener alerta por ID."""
    alerta = await service.get_alerta(alerta_id)
    if not alerta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta no encontrada"
        )
    return alerta

@router.get("/", response_model=List[Alertas])
async def get_alertas_pendientes(
    skip: int = 0,
    limit: int = 100,
    service: AlertasService = Depends(get_alertas_service)
):
    """Obtener alertas pendientes."""
    return await service.get_alertas_pendientes(skip, limit)

@router.get("/tipo/{tipo_alerta}", response_model=List[Alertas])
async def get_alertas_by_tipo(
    tipo_alerta: str,
    skip: int = 0,
    limit: int = 100,
    service: AlertasService = Depends(get_alertas_service)
):
    """Obtener alertas por tipo."""
    return await service.get_alertas_by_tipo(tipo_alerta, skip, limit)

@router.get("/prioridad/{prioridad}", response_model=List[Alertas])
async def get_alertas_by_prioridad(
    prioridad: str,
    skip: int = 0,
    limit: int = 100,
    service: AlertasService = Depends(get_alertas_service)
):
    """Obtener alertas por prioridad."""
    return await service.get_alertas_by_prioridad(prioridad, skip, limit)

@router.post("/", response_model=Alertas)
async def crear_alerta(
    tipo_alerta: str,
    mensaje: str,
    prioridad: str = 'MEDIA',
    neumatico_id: Optional[UUID] = None,
    parametro_id: Optional[UUID] = None,
    fecha_vencimiento: Optional[datetime] = None,
    service: AlertasService = Depends(get_alertas_service)
):
    """Crear nueva alerta."""
    return await service.crear_alerta(
        tipo_alerta, mensaje, prioridad, neumatico_id, parametro_id, fecha_vencimiento
    )

@router.put("/{alerta_id}/vista", response_model=Alertas)
async def marcar_como_vista(
    alerta_id: UUID,
    usuario_id: UUID,
    service: AlertasService = Depends(get_alertas_service)
):
    """Marcar alerta como vista."""
    alerta = await service.marcar_como_vista(alerta_id, usuario_id)
    if not alerta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta no encontrada"
        )
    return alerta

@router.put("/{alerta_id}/resolver", response_model=Alertas)
async def resolver_alerta(
    alerta_id: UUID,
    usuario_id: UUID,
    observaciones_resolucion: Optional[str] = None,
    service: AlertasService = Depends(get_alertas_service)
):
    """Resolver alerta."""
    alerta = await service.resolver_alerta(alerta_id, usuario_id, observaciones_resolucion)
    if not alerta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta no encontrada"
        )
    return alerta

@router.put("/{alerta_id}/ignorar", response_model=Alertas)
async def ignorar_alerta(
    alerta_id: UUID,
    usuario_id: UUID,
    service: AlertasService = Depends(get_alertas_service)
):
    """Ignorar alerta."""
    alerta = await service.ignorar_alerta(alerta_id, usuario_id)
    if not alerta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta no encontrada"
        )
    return alerta
