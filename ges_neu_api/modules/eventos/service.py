"""
Servicio para el módulo de eventos de neumáticos.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import EventosNeumaticos, HistorialEstadosNeumaticos, MedicionesProfundidad
from .models import TipoEventoNeumaticoEnum, EstadoNeumaticoEnum, MetodoMedicionEnum
from ...core.crud import CRUDBase

# CRUD instances
crud_eventos = CRUDBase(EventosNeumaticos)
crud_historial = CRUDBase(HistorialEstadosNeumaticos)
crud_mediciones = CRUDBase(MedicionesProfundidad)

class EventosService:
    """Servicio para gestión de eventos de neumáticos."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ============================================================================
    # EVENTOS NEUMÁTICOS
    # ============================================================================
    
    async def registrar_evento(
        self, neumatico_id: UUID, tipo_evento: TipoEventoNeumaticoEnum,
        usuario_id: UUID, datos_evento: dict, observaciones: Optional[str] = None,
        vehiculo_id: Optional[UUID] = None
    ) -> EventosNeumaticos:
        """Registrar nuevo evento de neumático."""
        evento_data = {
            "neumatico_id": neumatico_id,
            "tipo_evento": tipo_evento,
            "usuario_id": usuario_id,
            "vehiculo_id": vehiculo_id,
            "datos_evento": datos_evento,
            "observaciones": observaciones
        }
        return await crud_eventos.create(self.db, evento_data)
    
    async def get_eventos_neumatico(
        self, neumatico_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[EventosNeumaticos]:
        """Obtener eventos de un neumático."""
        stmt = select(EventosNeumaticos).where(
            EventosNeumaticos.neumatico_id == neumatico_id
        ).order_by(EventosNeumaticos.timestamp_evento.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_eventos_by_tipo(
        self, tipo_evento: TipoEventoNeumaticoEnum, skip: int = 0, limit: int = 100
    ) -> List[EventosNeumaticos]:
        """Obtener eventos por tipo."""
        stmt = select(EventosNeumaticos).where(
            EventosNeumaticos.tipo_evento == tipo_evento
        ).order_by(EventosNeumaticos.timestamp_evento.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    # ============================================================================
    # HISTORIAL ESTADOS
    # ============================================================================
    
    async def cambiar_estado_neumatico(
        self, neumatico_id: UUID, estado_nuevo: EstadoNeumaticoEnum,
        motivo_cambio: Optional[str] = None, observaciones: Optional[str] = None
    ) -> HistorialEstadosNeumaticos:
        """Registrar cambio de estado de neumático."""
        
        # Obtener estado anterior
        stmt_anterior = select(HistorialEstadosNeumaticos).where(
            HistorialEstadosNeumaticos.neumatico_id == neumatico_id
        ).order_by(HistorialEstadosNeumaticos.fecha_cambio.desc()).limit(1)
        result = await self.db.execute(stmt_anterior)
        ultimo_estado = result.scalar_one_or_none()
        
        estado_anterior = ultimo_estado.estado_nuevo if ultimo_estado else None
        
        historial_data = {
            "neumatico_id": neumatico_id,
            "estado_anterior": estado_anterior,
            "estado_nuevo": estado_nuevo,
            "motivo_cambio": motivo_cambio,
            "observaciones": observaciones
        }
        return await crud_historial.create(self.db, historial_data)
    
    async def get_historial_estados(
        self, neumatico_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[HistorialEstadosNeumaticos]:
        """Obtener historial de estados de un neumático."""
        stmt = select(HistorialEstadosNeumaticos).where(
            HistorialEstadosNeumaticos.neumatico_id == neumatico_id
        ).order_by(HistorialEstadosNeumaticos.fecha_cambio.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    # ============================================================================
    # MEDICIONES PROFUNDIDAD
    # ============================================================================
    
    async def registrar_medicion(
        self, neumatico_id: UUID, profundidad_mm: float,
        metodo_medicion: str = "MANUAL", observaciones: Optional[str] = None
    ) -> MedicionesProfundidad:
        """Registrar nueva medición de profundidad."""
        medicion_data = {
            "neumatico_id": neumatico_id,
            "profundidad_mm": profundidad_mm,
            "metodo_medicion": metodo_medicion,
            "observaciones": observaciones
        }
        return await crud_mediciones.create(self.db, medicion_data)
    
    async def get_mediciones_neumatico(
        self, neumatico_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[MedicionesProfundidad]:
        """Obtener mediciones de un neumático."""
        stmt = select(MedicionesProfundidad).where(
            MedicionesProfundidad.neumatico_id == neumatico_id
        ).order_by(MedicionesProfundidad.fecha_medicion.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_ultima_medicion(self, neumatico_id: UUID) -> Optional[MedicionesProfundidad]:
        """Obtener la última medición de profundidad."""
        stmt = select(MedicionesProfundidad).where(
            MedicionesProfundidad.neumatico_id == neumatico_id
        ).order_by(MedicionesProfundidad.fecha_medicion.desc()).limit(1)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
