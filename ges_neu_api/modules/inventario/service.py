"""
Servicio para el módulo de inventario de neumáticos.
"""
from typing import List, Optional
from uuid import UUID
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import InventarioNeumaticos, MovimientosInventario, TipoMovimientoEnum
from ...core.crud import CRUDBase

# CRUD para InventarioNeumaticos
crud_inventario = CRUDBase(InventarioNeumaticos)

# CRUD para MovimientosInventario  
crud_movimientos = CRUDBase(MovimientosInventario)

class InventarioService:
    """Servicio para gestión de inventario de neumáticos."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ============================================================================
    # INVENTARIO NEUMÁTICOS
    # ============================================================================
    
    async def get_inventario(self, inventario_id: UUID) -> Optional[InventarioNeumaticos]:
        """Obtener inventario por ID."""
        return await crud_inventario.get(self.db, inventario_id)
    
    async def get_inventario_by_modelo_almacen(
        self, modelo_id: UUID, almacen_id: UUID
    ) -> Optional[InventarioNeumaticos]:
        """Obtener inventario por modelo y almacén."""
        stmt = select(InventarioNeumaticos).where(
            InventarioNeumaticos.modelo_id == modelo_id,
            InventarioNeumaticos.almacen_id == almacen_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_inventarios_by_almacen(
        self, almacen_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[InventarioNeumaticos]:
        """Obtener inventarios por almacén."""
        stmt = select(InventarioNeumaticos).where(
            InventarioNeumaticos.almacen_id == almacen_id
        ).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_stock_bajo(self) -> List[InventarioNeumaticos]:
        """Obtener inventarios con stock bajo."""
        stmt = select(InventarioNeumaticos).where(
            InventarioNeumaticos.cantidad_stock <= InventarioNeumaticos.stock_minimo
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def actualizar_stock(
        self, modelo_id: UUID, almacen_id: UUID, nueva_cantidad: int
    ) -> Optional[InventarioNeumaticos]:
        """Actualizar cantidad de stock."""
        inventario = await self.get_inventario_by_modelo_almacen(modelo_id, almacen_id)
        if inventario:
            inventario.cantidad_stock = nueva_cantidad
            await self.db.commit()
            await self.db.refresh(inventario)
        return inventario
    
    # ============================================================================
    # MOVIMIENTOS INVENTARIO
    # ============================================================================
    
    async def get_movimiento(self, movimiento_id: UUID) -> Optional[MovimientosInventario]:
        """Obtener movimiento por ID."""
        return await crud_movimientos.get(self.db, movimiento_id)
    
    async def get_movimientos_by_neumatico(
        self, neumatico_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[MovimientosInventario]:
        """Obtener movimientos por neumático."""
        stmt = select(MovimientosInventario).where(
            MovimientosInventario.neumatico_id == neumatico_id
        ).order_by(MovimientosInventario.creado_en.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_movimientos_by_tipo(
        self, tipo_movimiento: TipoMovimientoEnum, skip: int = 0, limit: int = 100
    ) -> List[MovimientosInventario]:
        """Obtener movimientos por tipo."""
        stmt = select(MovimientosInventario).where(
            MovimientosInventario.tipo_movimiento == tipo_movimiento
        ).order_by(MovimientosInventario.creado_en.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def registrar_entrada(
        self, neumatico_id: UUID, almacen_destino_id: UUID, 
        cantidad: int, motivo: str, observaciones: Optional[str] = None
    ) -> MovimientosInventario:
        """Registrar entrada de neumático al inventario."""
        movimiento_data = {
            "neumatico_id": neumatico_id,
            "tipo_movimiento": TipoMovimientoEnum.ENTRADA,
            "almacen_destino_id": almacen_destino_id,
            "cantidad": cantidad,
            "motivo": motivo,
            "observaciones": observaciones
        }
        return await crud_movimientos.create(self.db, movimiento_data)
    
    async def registrar_salida(
        self, neumatico_id: UUID, almacen_origen_id: UUID,
        cantidad: int, motivo: str, observaciones: Optional[str] = None
    ) -> MovimientosInventario:
        """Registrar salida de neumático del inventario."""
        movimiento_data = {
            "neumatico_id": neumatico_id,
            "tipo_movimiento": TipoMovimientoEnum.SALIDA,
            "almacen_origen_id": almacen_origen_id,
            "cantidad": cantidad,
            "motivo": motivo,
            "observaciones": observaciones
        }
        return await crud_movimientos.create(self.db, movimiento_data)
    
    async def registrar_transferencia(
        self, neumatico_id: UUID, almacen_origen_id: UUID, almacen_destino_id: UUID,
        cantidad: int, motivo: str, observaciones: Optional[str] = None
    ) -> MovimientosInventario:
        """Registrar transferencia entre almacenes."""
        movimiento_data = {
            "neumatico_id": neumatico_id,
            "tipo_movimiento": TipoMovimientoEnum.TRANSFERENCIA,
            "almacen_origen_id": almacen_origen_id,
            "almacen_destino_id": almacen_destino_id,
            "cantidad": cantidad,
            "motivo": motivo,
            "observaciones": observaciones
        }
        return await crud_movimientos.create(self.db, movimiento_data)
