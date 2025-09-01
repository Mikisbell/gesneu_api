"""
Router para el módulo de inventario de neumáticos.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from .service import InventarioService
from .models import InventarioNeumaticos, MovimientosInventario, TipoMovimientoEnum

router = APIRouter(prefix="/inventario", tags=["inventario"])

async def get_inventario_service(db: AsyncSession = Depends(get_session)) -> InventarioService:
    return InventarioService(db)

# ============================================================================
# INVENTARIO NEUMÁTICOS
# ============================================================================

@router.get("/stock/{inventario_id}", response_model=InventarioNeumaticos)
async def get_inventario(
    inventario_id: UUID,
    service: InventarioService = Depends(get_inventario_service)
):
    """Obtener inventario por ID."""
    inventario = await service.get_inventario(inventario_id)
    if not inventario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventario no encontrado"
        )
    return inventario

@router.get("/stock/modelo/{modelo_id}/almacen/{almacen_id}", response_model=InventarioNeumaticos)
async def get_inventario_by_modelo_almacen(
    modelo_id: UUID,
    almacen_id: UUID,
    service: InventarioService = Depends(get_inventario_service)
):
    """Obtener inventario por modelo y almacén."""
    inventario = await service.get_inventario_by_modelo_almacen(modelo_id, almacen_id)
    if not inventario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventario no encontrado para este modelo y almacén"
        )
    return inventario

@router.get("/stock/almacen/{almacen_id}", response_model=List[InventarioNeumaticos])
async def get_inventarios_by_almacen(
    almacen_id: UUID,
    skip: int = 0,
    limit: int = 100,
    service: InventarioService = Depends(get_inventario_service)
):
    """Obtener inventarios por almacén."""
    return await service.get_inventarios_by_almacen(almacen_id, skip, limit)

@router.get("/stock/bajo", response_model=List[InventarioNeumaticos])
async def get_stock_bajo(
    service: InventarioService = Depends(get_inventario_service)
):
    """Obtener inventarios con stock bajo."""
    return await service.get_stock_bajo()

@router.put("/stock/modelo/{modelo_id}/almacen/{almacen_id}/cantidad/{nueva_cantidad}")
async def actualizar_stock(
    modelo_id: UUID,
    almacen_id: UUID,
    nueva_cantidad: int,
    service: InventarioService = Depends(get_inventario_service)
):
    """Actualizar cantidad de stock."""
    inventario = await service.actualizar_stock(modelo_id, almacen_id, nueva_cantidad)
    if not inventario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventario no encontrado"
        )
    return {"message": "Stock actualizado correctamente", "nuevo_stock": nueva_cantidad}

# ============================================================================
# MOVIMIENTOS INVENTARIO
# ============================================================================

@router.get("/movimientos/{movimiento_id}", response_model=MovimientosInventario)
async def get_movimiento(
    movimiento_id: UUID,
    service: InventarioService = Depends(get_inventario_service)
):
    """Obtener movimiento por ID."""
    movimiento = await service.get_movimiento(movimiento_id)
    if not movimiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movimiento no encontrado"
        )
    return movimiento

@router.get("/movimientos/neumatico/{neumatico_id}", response_model=List[MovimientosInventario])
async def get_movimientos_by_neumatico(
    neumatico_id: UUID,
    skip: int = 0,
    limit: int = 100,
    service: InventarioService = Depends(get_inventario_service)
):
    """Obtener movimientos por neumático."""
    return await service.get_movimientos_by_neumatico(neumatico_id, skip, limit)

@router.get("/movimientos/tipo/{tipo_movimiento}", response_model=List[MovimientosInventario])
async def get_movimientos_by_tipo(
    tipo_movimiento: TipoMovimientoEnum,
    skip: int = 0,
    limit: int = 100,
    service: InventarioService = Depends(get_inventario_service)
):
    """Obtener movimientos por tipo."""
    return await service.get_movimientos_by_tipo(tipo_movimiento, skip, limit)

@router.post("/movimientos/entrada", response_model=MovimientosInventario)
async def registrar_entrada(
    neumatico_id: UUID,
    almacen_destino_id: UUID,
    cantidad: int,
    motivo: str,
    observaciones: str = None,
    service: InventarioService = Depends(get_inventario_service)
):
    """Registrar entrada de neumático."""
    return await service.registrar_entrada(
        neumatico_id, almacen_destino_id, cantidad, motivo, observaciones
    )

@router.post("/movimientos/salida", response_model=MovimientosInventario)
async def registrar_salida(
    neumatico_id: UUID,
    almacen_origen_id: UUID,
    cantidad: int,
    motivo: str,
    observaciones: str = None,
    service: InventarioService = Depends(get_inventario_service)
):
    """Registrar salida de neumático."""
    return await service.registrar_salida(
        neumatico_id, almacen_origen_id, cantidad, motivo, observaciones
    )

@router.post("/movimientos/transferencia", response_model=MovimientosInventario)
async def registrar_transferencia(
    neumatico_id: UUID,
    almacen_origen_id: UUID,
    almacen_destino_id: UUID,
    cantidad: int,
    motivo: str,
    observaciones: str = None,
    service: InventarioService = Depends(get_inventario_service)
):
    """Registrar transferencia entre almacenes."""
    return await service.registrar_transferencia(
        neumatico_id, almacen_origen_id, almacen_destino_id, cantidad, motivo, observaciones
    )
