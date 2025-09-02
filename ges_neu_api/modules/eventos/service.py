"""
Servicio del módulo de eventos - Creado desde cero basado en ESQUEMA_COMPLETO_BD.md
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ges_neu_api.core.crud import CRUDBase
from .models import EventosNeumaticos
from .schemas import EventoNeumaticoCreate, EventoNeumaticoResponse

class EventosService:
    """Servicio para gestión de eventos de neumáticos."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.crud = CRUDBase(EventosNeumaticos)
    
    async def get_eventos(self, skip: int = 0, limit: int = 100) -> List[EventosNeumaticos]:
        """Obtener lista de eventos de neumáticos."""
        try:
            stmt = select(EventosNeumaticos).offset(skip).limit(limit).order_by(EventosNeumaticos.timestamp_evento.desc())
            result = await self.session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            print(f"Error en get_eventos: {e}")
            raise e
    
    async def get_evento_by_id(self, evento_id: UUID) -> Optional[EventosNeumaticos]:
        """Obtener evento por ID."""
        try:
            stmt = select(EventosNeumaticos).where(EventosNeumaticos.id == evento_id)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            print(f"Error en get_evento_by_id: {e}")
            raise e
    
    async def create_evento(self, evento_data: EventoNeumaticoCreate) -> EventosNeumaticos:
        """Crear nuevo evento de neumático."""
        try:
            evento = EventosNeumaticos(**evento_data.model_dump())
            self.session.add(evento)
            await self.session.commit()
            await self.session.refresh(evento)
            return evento
        except Exception as e:
            await self.session.rollback()
            print(f"Error en create_evento: {e}")
            raise e
    
    async def get_eventos_by_neumatico(self, neumatico_id: UUID) -> List[EventosNeumaticos]:
        """Obtener eventos por ID de neumático."""
        try:
            stmt = select(EventosNeumaticos).where(
                EventosNeumaticos.neumatico_id == neumatico_id
            ).order_by(EventosNeumaticos.timestamp_evento.desc())
            result = await self.session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            print(f"Error en get_eventos_by_neumatico: {e}")
            raise e
