"""
Router para el módulo de inventario de neumáticos - Alineado con esquema real PostgreSQL.
"""
import logging
import traceback
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from .service import InventarioService
from .models import ParametrosInventario, ResumenInventario
from .schemas import ParametroInventarioResponse, InventarioViewResponse, ResumenInventarioResponse
from ..neumaticos.models import Neumatico

# Configurar logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["inventario"])

async def get_inventario_service(db: AsyncSession = Depends(get_session)) -> InventarioService:
    return InventarioService(db)

# ============================================================================
# PARÁMETROS DE INVENTARIO (tabla real)
# ============================================================================

@router.get("/parametros", response_model=List[ParametroInventarioResponse], summary="Obtener parámetros de inventario")
async def get_parametros_inventario(
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    inventario_service: InventarioService = Depends(get_inventario_service)
):
    """Listar parámetros de inventario."""
    try:
        logger.info(f"Listando parámetros de inventario - skip: {skip}, limit: {limit}")
        parametros = await inventario_service.get_parametros_inventario(skip=skip, limit=limit, activo=activo)
        logger.info(f"Parámetros obtenidos exitosamente: {len(parametros)}")
        return parametros
    except Exception as e:
        logger.error(f"Error en listar_parametros_inventario: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500, 
            detail=f"Error interno: {str(e)}"
        )

@router.get("/parametros/{parametro_id}", response_model=ParametrosInventario)
async def obtener_parametro_inventario(
    parametro_id: UUID,
    service: InventarioService = Depends(get_inventario_service)
):
    """Obtener parámetro de inventario por ID."""
    try:
        logger.info(f"Obteniendo parámetro {parametro_id}")
        parametro = await service.get_parametro_inventario(parametro_id)
        if not parametro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parámetro de inventario no encontrado"
            )
        return parametro
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en obtener_parametro_inventario: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error interno: {str(e)}"
        )

# ============================================================================
# INVENTARIO BASADO EN NEUMÁTICOS (tabla real)
# ============================================================================

@router.get("/resumen", response_model=List[ResumenInventario])
async def obtener_resumen_inventario(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: InventarioService = Depends(get_inventario_service)
):
    """Obtener resumen de inventario por modelo."""
    try:
        logger.info(f"Obteniendo resumen de inventario - skip: {skip}, limit: {limit}")
        resumen = await service.get_inventario_resumen(skip=skip, limit=limit)
        logger.info(f"Resumen obtenido exitosamente: {len(resumen)} modelos")
        return resumen
    except Exception as e:
        logger.error(f"Error en obtener_resumen_inventario: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500, 
            detail=f"Error interno: {str(e)}"
        )

@router.get("/neumaticos", response_model=List[Neumatico])
async def listar_neumaticos_en_stock(
    almacen_id: Optional[UUID] = Query(None, description="Filtrar por almacén"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: InventarioService = Depends(get_inventario_service)
):
    """Listar neumáticos en stock."""
    try:
        logger.info(f"Listando neumáticos en stock - almacen_id: {almacen_id}, skip: {skip}, limit: {limit}")
        neumaticos = await service.get_neumaticos_en_stock(almacen_id=almacen_id, skip=skip, limit=limit)
        logger.info(f"Neumáticos obtenidos exitosamente: {len(neumaticos)}")
        return neumaticos
    except Exception as e:
        logger.error(f"Error en listar_neumaticos_en_stock: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error interno: {str(e)}"
        )

@router.get("/stock-bajo")
async def obtener_stock_bajo(
    service: InventarioService = Depends(get_inventario_service)
):
    """Obtener modelos con stock bajo según parámetros configurados."""
    try:
        logger.info("Obteniendo stock bajo por parámetros")
        stock_bajo = await service.get_stock_bajo_por_parametros()
        logger.info(f"Stock bajo obtenido exitosamente: {len(stock_bajo)} casos")
        return stock_bajo
    except Exception as e:
        logger.error(f"Error en obtener_stock_bajo: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error interno: {str(e)}"
        )
