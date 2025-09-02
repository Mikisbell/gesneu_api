"""
Router del módulo de eventos - Creado desde cero basado en ESQUEMA_COMPLETO_BD.md
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ges_neu_api.core.database import get_session
from ges_neu_api.modules.auth.dependencies import get_current_user
from ges_neu_api.modules.auth.schemas import UserRead
from .service import EventosService
from .schemas import EventoNeumaticoResponse, EventoNeumaticoCreate

router = APIRouter()

def get_eventos_service(session: AsyncSession = Depends(get_session)) -> EventosService:
    """Dependency para obtener el servicio de eventos."""
    return EventosService(session)

@router.get("/", response_model=List[EventoNeumaticoResponse])
async def get_eventos(
    skip: int = 0,
    limit: int = 100,
    current_user: UserRead = Depends(get_current_user),
    service: EventosService = Depends(get_eventos_service)
):
    """Obtener lista de eventos de neumáticos."""
    try:
        eventos = await service.get_eventos(skip=skip, limit=limit)
        return eventos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener eventos: {str(e)}"
        )

@router.get("/{evento_id}", response_model=EventoNeumaticoResponse)
async def get_evento(
    evento_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    service: EventosService = Depends(get_eventos_service)
):
    """Obtener evento por ID."""
    try:
        evento = await service.get_evento_by_id(evento_id)
        if not evento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado"
            )
        return evento
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener evento: {str(e)}"
        )

@router.post("/", response_model=EventoNeumaticoResponse)
async def create_evento(
    evento_data: EventoNeumaticoCreate,
    current_user: UserRead = Depends(get_current_user),
    service: EventosService = Depends(get_eventos_service)
):
    """Crear nuevo evento de neumático."""
    try:
        evento = await service.create_evento(evento_data)
        return evento
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear evento: {str(e)}"
        )

@router.get("/neumatico/{neumatico_id}", response_model=List[EventoNeumaticoResponse])
async def get_eventos_by_neumatico(
    neumatico_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    service: EventosService = Depends(get_eventos_service)
):
    """Obtener eventos por ID de neumático."""
    try:
        eventos = await service.get_eventos_by_neumatico(neumatico_id)
        return eventos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener eventos del neumático: {str(e)}"
        )
