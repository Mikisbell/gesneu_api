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
            Alertas.estado_alerta == 'NUEVA'
        ).order_by(Alertas.nivel_severidad.desc(), Alertas.timestamp_generacion.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_alertas_by_tipo(
        self, tipo_alerta: str, skip: int = 0, limit: int = 100
    ) -> List[Alertas]:
        """Obtener alertas por tipo."""
        stmt = select(Alertas).where(
            Alertas.tipo_alerta == tipo_alerta
        ).order_by(Alertas.timestamp_generacion.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_alertas_by_prioridad(
        self, prioridad: str, skip: int = 0, limit: int = 100
    ) -> List[Alertas]:
        """Obtener alertas por prioridad."""
        stmt = select(Alertas).where(
            Alertas.nivel_severidad == prioridad
        ).order_by(Alertas.timestamp_generacion.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def crear_alerta(
        self, tipo_alerta: str, mensaje: str,
        nivel_severidad: str = 'INFO',
        neumatico_id: Optional[UUID] = None,
        parametro_id: Optional[UUID] = None
    ) -> Alertas:
        """Crear nueva alerta."""
        alerta_data = {
            "tipo_alerta": tipo_alerta,
            "mensaje": mensaje,
            "nivel_severidad": nivel_severidad,
            "neumatico_id": neumatico_id,
            "parametro_id": parametro_id
        }
        return await crud_alertas.create(self.db, alerta_data)
    
    async def marcar_como_vista(
        self, alerta_id: UUID, usuario_id: UUID
    ) -> Optional[Alertas]:
        """Marcar alerta como vista."""
        alerta = await self.get_alerta(alerta_id)
        if alerta:
            alerta.estado_alerta = 'VISTA'
            alerta.usuario_gestion_id = usuario_id
            alerta.timestamp_gestion = datetime.utcnow()
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
            alerta.estado_alerta = 'GESTIONADA'
            alerta.usuario_gestion_id = usuario_id
            alerta.timestamp_gestion = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(alerta)
        return alerta
    
    async def ignorar_alerta(
        self, alerta_id: UUID, usuario_id: UUID
    ) -> Optional[Alertas]:
        """Ignorar alerta."""
        alerta = await self.get_alerta(alerta_id)
        if alerta:
            alerta.estado_alerta = 'GESTIONADA'
            alerta.usuario_gestion_id = usuario_id
            alerta.timestamp_gestion = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(alerta)
        return alerta
