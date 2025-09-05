"""
Router para el módulo de alertas del sistema.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from ..auth.dependencies import get_current_user
from ..auth.schemas import UserRead
from .service import AlertasService
from .models import Alertas

router = APIRouter(tags=["alertas"])

async def get_alertas_service(db: AsyncSession = Depends(get_session)) -> AlertasService:
    return AlertasService(db)

@router.get("/{alerta_id}", response_model=Alertas)
async def get_alerta(
    alerta_id: UUID,
    current_user: UserRead = Depends(get_current_user),
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
    current_user: UserRead = Depends(get_current_user),
    service: AlertasService = Depends(get_alertas_service)
):
    """Obtener alertas pendientes."""
    return await service.get_alertas_pendientes(skip, limit)

@router.get("/tipo/{tipo_alerta}", response_model=List[Alertas])
async def get_alertas_by_tipo(
    tipo_alerta: str,
    skip: int = 0,
    limit: int = 100,
    current_user: UserRead = Depends(get_current_user),
    service: AlertasService = Depends(get_alertas_service)
):
    """Obtener alertas por tipo."""
    return await service.get_alertas_by_tipo(tipo_alerta, skip, limit)

@router.get("/prioridad/{prioridad}", response_model=List[Alertas])
async def get_alertas_by_prioridad(
    prioridad: str,
    skip: int = 0,
    limit: int = 100,
    current_user: UserRead = Depends(get_current_user),
    service: AlertasService = Depends(get_alertas_service)
):
    """Obtener alertas por prioridad."""
    return await service.get_alertas_by_prioridad(prioridad, skip, limit)

@router.post("/", response_model=Alertas)
async def crear_alerta(
    tipo_alerta: str,
    mensaje: str,
    nivel_severidad: str = 'INFO',
    neumatico_id: Optional[UUID] = None,
    parametro_id: Optional[UUID] = None,
    current_user: UserRead = Depends(get_current_user),
    service: AlertasService = Depends(get_alertas_service)
):
    """Crear nueva alerta."""
    return await service.crear_alerta(
        tipo_alerta, mensaje, nivel_severidad, neumatico_id, parametro_id
    )

@router.put("/{alerta_id}/vista", response_model=Alertas)
async def marcar_como_vista(
    alerta_id: UUID,
    usuario_id: UUID,
    current_user: UserRead = Depends(get_current_user),
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
    current_user: UserRead = Depends(get_current_user),
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
    current_user: UserRead = Depends(get_current_user),
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
