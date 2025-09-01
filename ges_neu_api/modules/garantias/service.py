"""
Servicio para el módulo de garantías de neumáticos.
"""
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import GarantiasNeumaticos
from ...core.crud import CRUDBase

# CRUD para GarantiasNeumaticos
crud_garantias = CRUDBase(GarantiasNeumaticos)

class GarantiasService:
    """Servicio para gestión de garantías de neumáticos."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_garantia(self, garantia_id: UUID) -> Optional[GarantiasNeumaticos]:
        """Obtener garantía por ID."""
        return await crud_garantias.get(self.db, garantia_id)
    
    async def get_garantias_neumatico(
        self, neumatico_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[GarantiasNeumaticos]:
        """Obtener garantías de un neumático."""
        stmt = select(GarantiasNeumaticos).where(
            GarantiasNeumaticos.neumatico_id == neumatico_id
        ).order_by(GarantiasNeumaticos.fecha_inicio.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_garantias_vigentes(
        self, fecha_referencia: Optional[date] = None
    ) -> List[GarantiasNeumaticos]:
        """Obtener garantías vigentes."""
        if not fecha_referencia:
            fecha_referencia = date.today()
            
        stmt = select(GarantiasNeumaticos).where(
            GarantiasNeumaticos.fecha_inicio <= fecha_referencia,
            GarantiasNeumaticos.fecha_vencimiento >= fecha_referencia
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_garantias_por_vencer(
        self, dias_anticipacion: int = 30
    ) -> List[GarantiasNeumaticos]:
        """Obtener garantías que vencen pronto."""
        fecha_limite = date.today()
        from datetime import timedelta
        fecha_limite += timedelta(days=dias_anticipacion)
        
        stmt = select(GarantiasNeumaticos).where(
            GarantiasNeumaticos.fecha_vencimiento <= fecha_limite,
            GarantiasNeumaticos.fecha_vencimiento >= date.today()
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def crear_garantia(
        self, neumatico_id: UUID, proveedor_id: UUID, 
        fecha_inicio: date, fecha_vencimiento: date,
        tipo_garantia: str, cobertura_descripcion: Optional[str] = None
    ) -> GarantiasNeumaticos:
        """Crear nueva garantía."""
        garantia_data = {
            "neumatico_id": neumatico_id,
            "proveedor_id": proveedor_id,
            "fecha_inicio": fecha_inicio,
            "fecha_vencimiento": fecha_vencimiento,
            "tipo_garantia": tipo_garantia,
            "cobertura_descripcion": cobertura_descripcion
        }
        return await crud_garantias.create(self.db, garantia_data)
