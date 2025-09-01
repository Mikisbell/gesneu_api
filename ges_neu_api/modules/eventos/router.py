"""
Router para el módulo de eventos de neumáticos.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from .service import EventosService
from .models import EventosNeumaticos, HistorialEstadosNeumaticos, MedicionesProfundidad
from .models import TipoEventoNeumaticoEnum, EstadoNeumaticoEnum

router = APIRouter(prefix="/eventos", tags=["eventos"])

async def get_eventos_service(db: AsyncSession = Depends(get_session)) -> EventosService:
    return EventosService(db)

# ============================================================================
# EVENTOS NEUMÁTICOS
# ============================================================================

@router.post("/", response_model=EventosNeumaticos)
async def registrar_evento(
    neumatico_id: UUID,
    tipo_evento: TipoEventoNeumaticoEnum,
    usuario_id: UUID,
    datos_evento: dict,
    observaciones: Optional[str] = None,
    vehiculo_id: Optional[UUID] = None,
    service: EventosService = Depends(get_eventos_service)
):
    """Registrar nuevo evento de neumático."""
    return await service.registrar_evento(
        neumatico_id, tipo_evento, usuario_id, datos_evento, observaciones, vehiculo_id
    )

@router.get("/neumatico/{neumatico_id}", response_model=List[EventosNeumaticos])
async def get_eventos_neumatico(
    neumatico_id: UUID,
    skip: int = 0,
    limit: int = 100,
    service: EventosService = Depends(get_eventos_service)
):
    """Obtener eventos de un neumático."""
    return await service.get_eventos_neumatico(neumatico_id, skip, limit)

@router.get("/tipo/{tipo_evento}", response_model=List[EventosNeumaticos])
async def get_eventos_by_tipo(
    tipo_evento: TipoEventoNeumaticoEnum,
    skip: int = 0,
    limit: int = 100,
    service: EventosService = Depends(get_eventos_service)
):
    """Obtener eventos por tipo."""
    return await service.get_eventos_by_tipo(tipo_evento, skip, limit)

# ============================================================================
# HISTORIAL ESTADOS
# ============================================================================

@router.post("/estados/cambiar", response_model=HistorialEstadosNeumaticos)
async def cambiar_estado_neumatico(
    neumatico_id: UUID,
    estado_nuevo: EstadoNeumaticoEnum,
    motivo_cambio: Optional[str] = None,
    observaciones: Optional[str] = None,
    service: EventosService = Depends(get_eventos_service)
):
    """Registrar cambio de estado de neumático."""
    return await service.cambiar_estado_neumatico(
        neumatico_id, estado_nuevo, motivo_cambio, observaciones
    )

@router.get("/estados/neumatico/{neumatico_id}", response_model=List[HistorialEstadosNeumaticos])
async def get_historial_estados(
    neumatico_id: UUID,
    skip: int = 0,
    limit: int = 100,
    service: EventosService = Depends(get_eventos_service)
):
    """Obtener historial de estados de un neumático."""
    return await service.get_historial_estados(neumatico_id, skip, limit)

# ============================================================================
# MEDICIONES PROFUNDIDAD
# ============================================================================

@router.post("/mediciones", response_model=MedicionesProfundidad)
async def registrar_medicion(
    neumatico_id: UUID,
    profundidad_mm: float,
    metodo_medicion: str = "MANUAL",
    observaciones: Optional[str] = None,
    service: EventosService = Depends(get_eventos_service)
):
    """Registrar nueva medición de profundidad."""
    return await service.registrar_medicion(
        neumatico_id, profundidad_mm, metodo_medicion, observaciones
    )

@router.get("/mediciones/neumatico/{neumatico_id}", response_model=List[MedicionesProfundidad])
async def get_mediciones_neumatico(
    neumatico_id: UUID,
    skip: int = 0,
    limit: int = 100,
    service: EventosService = Depends(get_eventos_service)
):
    """Obtener mediciones de un neumático."""
    return await service.get_mediciones_neumatico(neumatico_id, skip, limit)

@router.get("/mediciones/ultima/{neumatico_id}", response_model=MedicionesProfundidad)
async def get_ultima_medicion(
    neumatico_id: UUID,
    service: EventosService = Depends(get_eventos_service)
):
    """Obtener la última medición de profundidad."""
    medicion = await service.get_ultima_medicion(neumatico_id)
    if not medicion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontraron mediciones para este neumático"
        )
    return medicion
