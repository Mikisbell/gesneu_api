"""
Servicio para el módulo de alertas del sistema.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models_fixed import Alertas
from ...core.crud import CRUDBase

# CRUD para Alertas
crud_alertas = CRUDBase(Alertas)

class AlertasService:
    """Servicio para gestión de alertas del sistema."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_alerta(self, alerta_id: UUID) -> Optional[Alertas]:
        """Obtener alerta por ID."""
        return await crud_alertas.get(self.db, alerta_id)
    
    async def get_alertas_pendientes(
        self, skip: int = 0, limit: int = 100
    ) -> List[Alertas]:
        """Obtener alertas pendientes."""
        stmt = select(Alertas).where(
            Alertas.estado == 'PENDIENTE'
        ).order_by(Alertas.prioridad.desc(), Alertas.fecha_generacion.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_alertas_by_tipo(
        self, tipo_alerta: str, skip: int = 0, limit: int = 100
    ) -> List[Alertas]:
        """Obtener alertas por tipo."""
        stmt = select(Alertas).where(
            Alertas.tipo_alerta == tipo_alerta
        ).order_by(Alertas.fecha_generacion.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_alertas_by_prioridad(
        self, prioridad: str, skip: int = 0, limit: int = 100
    ) -> List[Alertas]:
        """Obtener alertas por prioridad."""
        stmt = select(Alertas).where(
            Alertas.prioridad == prioridad
        ).order_by(Alertas.fecha_generacion.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def crear_alerta(
        self, tipo_alerta: str, mensaje: str,
        prioridad: str = 'MEDIA',
        neumatico_id: Optional[UUID] = None,
        parametro_id: Optional[UUID] = None,
        fecha_vencimiento: Optional[datetime] = None
    ) -> Alertas:
        """Crear nueva alerta."""
        alerta_data = {
            "tipo_alerta": tipo_alerta,
            "mensaje": mensaje,
            "prioridad": prioridad,
            "neumatico_id": neumatico_id,
            "parametro_id": parametro_id,
            "fecha_vencimiento": fecha_vencimiento
        }
        return await crud_alertas.create(self.db, alerta_data)
    
    async def marcar_como_vista(
        self, alerta_id: UUID, usuario_id: UUID
    ) -> Optional[Alertas]:
        """Marcar alerta como vista."""
        alerta = await self.get_alerta(alerta_id)
        if alerta:
            alerta.estado = 'VISTA'
            alerta.vista_por = usuario_id
            alerta.fecha_vista = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(alerta)
        return alerta
    
    async def resolver_alerta(
        self, alerta_id: UUID, usuario_id: UUID,
        observaciones_resolucion: Optional[str] = None
    ) -> Optional[Alertas]:
        """Resolver alerta."""
        alerta = await self.get_alerta(alerta_id)
        if alerta:
            alerta.estado = 'RESUELTA'
            alerta.resuelta_por = usuario_id
            alerta.fecha_resolucion = datetime.utcnow()
            alerta.observaciones_resolucion = observaciones_resolucion
            await self.db.commit()
            await self.db.refresh(alerta)
        return alerta
    
    async def ignorar_alerta(
        self, alerta_id: UUID, usuario_id: UUID
    ) -> Optional[Alertas]:
        """Ignorar alerta."""
        alerta = await self.get_alerta(alerta_id)
        if alerta:
            alerta.estado = 'IGNORADA'
            alerta.vista_por = usuario_id
            alerta.fecha_vista = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(alerta)
        return alerta
