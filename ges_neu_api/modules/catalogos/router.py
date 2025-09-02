# ges_neu_api/catalogos/router.py

from uuid import UUID
from typing import List, Optional

from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# Application imports
from ges_neu_api.core.database import get_session
from ges_neu_api.modules.catalogos.schemas import (
    ProveedorCreate, ProveedorRead, ProveedorUpdate,
    MotivoDesechoCreate, MotivoDesechoRead, MotivoDesechoUpdate,
    AlmacenCreate, AlmacenRead, AlmacenUpdate,
    ParametroInventarioCreate, ParametroInventarioRead, ParametroInventarioUpdate
)
from .service import CatalogService


router = APIRouter(tags=["catalogos"])

# --- Dependencies ---

def get_catalog_service() -> CatalogService:
    """Dependency para obtener el servicio de catálogos."""
    return CatalogService()


# --- Endpoints para Proveedores ---

@router.post(
    "/proveedores/", 
    response_model=ProveedorRead, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo proveedor"
)
async def create_proveedor(
    proveedor_data: ProveedorCreate,
    db: AsyncSession = Depends(get_session),
    service: CatalogService = Depends(get_catalog_service)
):
    """Crear un nuevo proveedor."""
    return await service.create_proveedor(db, proveedor_data)

@router.get(
    "/proveedores/", 
    response_model=List[ProveedorRead],
    summary="Listar proveedores"
)
async def get_proveedores(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_session),
    service: CatalogService = Depends(get_catalog_service)
):
    """Obtener lista de proveedores."""
    return await service.get_proveedores(db, skip, limit)

@router.get(
    "/proveedores/{proveedor_id}", 
    response_model=ProveedorRead,
    summary="Obtener proveedor por ID"
)
async def get_proveedor(
    proveedor_id: UUID,
    db: AsyncSession = Depends(get_session),
    service: CatalogService = Depends(get_catalog_service)
):
    """Obtener un proveedor por ID."""
    proveedor = await service.get_proveedor(db, proveedor_id)
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return proveedor

@router.put(
    "/proveedores/{proveedor_id}", 
    response_model=ProveedorRead,
    summary="Actualizar proveedor"
)
async def update_proveedor(
    proveedor_id: UUID,
    proveedor_data: ProveedorUpdate,
    db: AsyncSession = Depends(get_session),
    service: CatalogService = Depends(get_catalog_service)
):
    """Actualizar un proveedor."""
    proveedor = await service.update_proveedor(db, proveedor_id, proveedor_data)
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return proveedor

@router.delete(
    "/proveedores/{proveedor_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar proveedor"
)
async def delete_proveedor(
    proveedor_id: UUID,
    db: AsyncSession = Depends(get_session),
    service: CatalogService = Depends(get_catalog_service)
):
    """Eliminar un proveedor (soft delete)."""
    success = await service.delete_proveedor(db, proveedor_id)
    if not success:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

# --- Endpoints para Motivos de Desecho ---

@router.post(
    "/motivos-desecho/", 
    response_model=MotivoDesechoRead, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo motivo de desecho"
)
async def create_motivo_desecho(
    motivo_data: MotivoDesechoCreate,
    db: AsyncSession = Depends(get_session),
    service: CatalogService = Depends(get_catalog_service)
):
    """Crear un nuevo motivo de desecho."""
    return await service.create_motivo_desecho(db, motivo_data)

@router.get(
    "/motivos-desecho/", 
    response_model=List[MotivoDesechoRead],
    summary="Listar motivos de desecho"
)
async def get_motivos_desecho(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_session),
    service: CatalogService = Depends(get_catalog_service)
):
    """Obtener lista de motivos de desecho."""
    return await service.get_motivos_desecho(db, skip, limit)

@router.get(
    "/motivos-desecho/{motivo_id}", 
    response_model=MotivoDesechoRead,
    summary="Obtener motivo de desecho por ID"
)
async def get_motivo_desecho(
    motivo_id: UUID,
    db: AsyncSession = Depends(get_session),
    service: CatalogService = Depends(get_catalog_service)
):
    """Obtener un motivo de desecho por ID."""
    motivo = await service.get_motivo_desecho(db, motivo_id)
    if not motivo:
        raise HTTPException(status_code=404, detail="Motivo de desecho no encontrado")
    return motivo

@router.put(
    "/motivos-desecho/{motivo_id}", 
    response_model=MotivoDesechoRead,
    summary="Actualizar motivo de desecho"
)
async def update_motivo_desecho(
    motivo_id: UUID,
    motivo_data: MotivoDesechoUpdate,
    db: AsyncSession = Depends(get_session),
    service: CatalogService = Depends(get_catalog_service)
):
    """Actualizar un motivo de desecho."""
    motivo = await service.update_motivo_desecho(db, motivo_id, motivo_data)
    if not motivo:
        raise HTTPException(status_code=404, detail="Motivo de desecho no encontrado")
    return motivo

@router.delete(
    "/motivos-desecho/{motivo_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar motivo de desecho"
)
async def delete_motivo_desecho(
    motivo_id: UUID,
    db: AsyncSession = Depends(get_session),
    service: CatalogService = Depends(get_catalog_service)
):
    """Eliminar un motivo de desecho (soft delete)."""
    success = await service.delete_motivo_desecho(db, motivo_id)
    if not success:
        raise HTTPException(status_code=404, detail="Motivo de desecho no encontrado")

# --- Endpoints para Almacenes ---

@router.post(
    "/almacenes/", 
    response_model=AlmacenRead, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo almacén"
)
async def create_almacen(
    almacen_data: AlmacenCreate,
    db: AsyncSession = Depends(get_session),
    service: CatalogService = Depends(get_catalog_service)
):
    """Crear un nuevo almacén."""
    return await service.create_almacen(db, almacen_data)

@router.get(
    "/almacenes/", 
    response_model=List[AlmacenRead],
    summary="Listar almacenes"
)
async def get_almacenes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_session),
    service: CatalogService = Depends(get_catalog_service)
):
    """Obtener lista de almacenes."""
    return await service.get_almacenes(db, skip, limit)

@router.get(
    "/almacenes/{almacen_id}", 
    response_model=AlmacenRead,
    summary="Obtener almacén por ID"
)
async def get_almacen(
    almacen_id: UUID,
    db: AsyncSession = Depends(get_session),
    service: CatalogService = Depends(get_catalog_service)
):
    """Obtener un almacén por ID."""
    almacen = await service.get_almacen(db, almacen_id)
    if not almacen:
        raise HTTPException(status_code=404, detail="Almacén no encontrado")
    return almacen

@router.put(
    "/almacenes/{almacen_id}", 
    response_model=AlmacenRead,
    summary="Actualizar almacén"
)
async def update_almacen(
    almacen_id: UUID,
    almacen_data: AlmacenUpdate,
    db: AsyncSession = Depends(get_session),
    service: CatalogService = Depends(get_catalog_service)
):
    """Actualizar un almacén."""
    almacen = await service.update_almacen(db, almacen_id, almacen_data)
    if not almacen:
        raise HTTPException(status_code=404, detail="Almacén no encontrado")
    return almacen

@router.delete(
    "/almacenes/{almacen_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar almacén"
)
async def delete_almacen(
    almacen_id: UUID,
    db: AsyncSession = Depends(get_session),
    service: CatalogService = Depends(get_catalog_service)
):
    """Eliminar un almacén (soft delete)."""
    success = await service.delete_almacen(db, almacen_id)
    if not success:
        raise HTTPException(status_code=404, detail="Almacén no encontrado")

# --- Endpoints para Parámetros de Inventario ---

@router.post(
    "/parametros-inventario/", 
    response_model=ParametroInventarioRead, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo parámetro de inventario"
)
async def create_parametro_inventario(
    parametro_data: ParametroInventarioCreate,
    db: AsyncSession = Depends(get_session),
    service: CatalogService = Depends(get_catalog_service)
):
    """Crear un nuevo parámetro de inventario."""
    return await service.create_parametro_inventario(db, parametro_data)

@router.get(
    "/parametros-inventario/", 
    response_model=List[ParametroInventarioRead],
    summary="Listar parámetros de inventario"
)
async def get_parametros_inventario(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_session),
    service: CatalogService = Depends(get_catalog_service)
):
    """Obtener lista de parámetros de inventario."""
    return await service.get_parametros_inventario(db, skip, limit)

@router.get(
    "/parametros-inventario/{parametro_id}", 
    response_model=ParametroInventarioRead,
    summary="Obtener parámetro de inventario por ID"
)
async def get_parametro_inventario(
    parametro_id: UUID,
    db: AsyncSession = Depends(get_session),
    service: CatalogService = Depends(get_catalog_service)
):
    """Obtener un parámetro de inventario por ID."""
    parametro = await service.get_parametro_inventario(db, parametro_id)
    if not parametro:
        raise HTTPException(status_code=404, detail="Parámetro de inventario no encontrado")
    return parametro

@router.put(
    "/parametros-inventario/{parametro_id}", 
    response_model=ParametroInventarioRead,
    summary="Actualizar parámetro de inventario"
)
async def update_parametro_inventario(
    parametro_id: UUID,
    parametro_data: ParametroInventarioUpdate,
    db: AsyncSession = Depends(get_session),
    service: CatalogService = Depends(get_catalog_service)
):
    """Actualizar un parámetro de inventario."""
    parametro = await service.update_parametro_inventario(db, parametro_id, parametro_data)
    if not parametro:
        raise HTTPException(status_code=404, detail="Parámetro de inventario no encontrado")
    return parametro

@router.delete(
    "/parametros-inventario/{parametro_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar parámetro de inventario"
)
async def delete_parametro_inventario(
    parametro_id: UUID,
    db: AsyncSession = Depends(get_session),
    service: CatalogService = Depends(get_catalog_service)
):
    """Eliminar un parámetro de inventario (soft delete)."""
    success = await service.delete_parametro_inventario(db, parametro_id)
    if not success:
        raise HTTPException(status_code=404, detail="Parámetro de inventario no encontrado")
