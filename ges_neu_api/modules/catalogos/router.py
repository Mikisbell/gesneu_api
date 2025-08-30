# ges_neu_api/catalogos/router.py

from uuid import UUID
from typing import List, Optional

from fastapi import APIRouter, Depends, status, Query, HTTPException

# Application imports
from ges_neu_api.modules.auth.schemas import UserRead
from ..auth.dependencies import get_current_user
from ges_neu_api.modules.catalogos.schemas import (
    FabricanteCreate, FabricanteRead, FabricanteUpdate,
    ModeloNeumaticoCreate, ModeloNeumaticoRead, ModeloNeumaticoUpdate,
    ProveedorCreate, ProveedorRead, ProveedorUpdate,
    MotivoDesechoCreate, MotivoDesechoRead, MotivoDesechoUpdate,
    AlmacenCreate, AlmacenRead, AlmacenUpdate,
    ParametroInventarioCreate, ParametroInventarioRead, ParametroInventarioUpdate,
    CatalogoItemCreate, CatalogoItemRead, CatalogoItemUpdate
)
from .dependencies import get_catalogos_service
from .service import CatalogosService


router = APIRouter(tags=["Catálogos"])

# --- Dependencies ---



# --- Endpoints para Fabricantes ---

@router.post(
    "/fabricantes/", 
    response_model=FabricanteRead, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo fabricante",
    dependencies=[Depends(get_current_user)]  # Requiere autenticación
)
async def create_fabricante(
    fabricante_in: FabricanteCreate,
    service: CatalogosService = Depends(get_catalogos_service)
):
    """
    Crea un nuevo fabricante.
    
    Requiere permisos de administrador.
    """
    return await service.create_fabricante(fabricante_in, service.current_user)

@router.get(
    "/fabricantes/", 
    response_model=List[FabricanteRead],
    summary="Listar fabricantes",
    dependencies=[Depends(get_current_user)]  # Requiere autenticación
)
async def read_fabricantes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    activo: Optional[bool] = Query(None),
    service: CatalogosService = Depends(get_catalogos_service)
):
    """
    Lista todos los fabricantes con paginación.
    
    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Número máximo de registros a devolver (máx. 100)
    - **activo**: Filtrar por estado activo/inactivo (opcional)
    """
    return await service.get_all_fabricantes(
        user=service.current_user,
        skip=skip, limit=limit, activo=activo
    )

@router.get(
    "/fabricantes/{fabricante_id}",
    response_model=FabricanteRead,
    summary="Obtener un fabricante por ID",
    dependencies=[Depends(get_current_user)]  # Requiere autenticación
)
async def read_fabricante(
    fabricante_id: UUID,
    service: CatalogosService = Depends(get_catalogos_service)
):
    """
    Obtiene los detalles de un fabricante por su ID.
    """
    return await service.get_fabricante_by_id(fabricante_id, service.current_user)

@router.put(
    "/fabricantes/{fabricante_id}",
    response_model=FabricanteRead,
    summary="Actualizar un fabricante",
    dependencies=[Depends(get_current_user)]  # Requiere autenticación
)
async def update_fabricante(
    fabricante_id: UUID,
    fabricante_in: FabricanteUpdate,
    service: CatalogosService = Depends(get_catalogos_service)
):
    """
    Actualiza un fabricante existente.
    
    Requiere permisos de administrador.
    """
    return await service.update_fabricante(
        fabricante_id=fabricante_id,
        fabricante_update=fabricante_in,
        user=service.current_user
    )

@router.delete(
    "/fabricantes/{fabricante_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un fabricante",
    dependencies=[Depends(get_current_user)]  # Requiere autenticación
)
async def delete_fabricante(
    fabricante_id: UUID,
    service: CatalogosService = Depends(get_catalogos_service)
):
    """
    Elimina un fabricante.
    
    Requiere permisos de administrador.
    """
    await service.delete_fabricante(fabricante_id, service.current_user)
    return None

# --- Endpoints para Modelos ---

@router.post(
    "/modelos/", 
    response_model=ModeloNeumaticoRead, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo modelo",
    dependencies=[Depends(get_current_user)]  # Requiere autenticación
)
async def create_modelo(
    modelo_in: ModeloNeumaticoCreate,
    service: CatalogosService = Depends(get_catalogos_service)
):
    """
    Crea un nuevo modelo.
    
    Requiere permisos de administrador.
    """
    return await service.create_modelo(modelo_in, service.current_user)

@router.get(
    "/modelos/", 
    response_model=List[ModeloNeumaticoRead],
    summary="Listar modelos",
    dependencies=[Depends(get_current_user)]  # Requiere autenticación
)
async def read_modelos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    fabricante_id: Optional[UUID] = Query(None),
    activo: Optional[bool] = Query(None),
    service: CatalogosService = Depends(get_catalogos_service)
):
    """
    Lista todos los modelos con paginación.
    
    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Número máximo de registros a devolver (máx. 100)
    - **fabricante_id**: Filtrar por ID de fabricante (opcional)
    - **activo**: Filtrar por estado activo/inactivo (opcional)
    """
    return await service.get_all_modelos(
        user=service.current_user,
        skip=skip, limit=limit, fabricante_id=fabricante_id, activo=activo
    )

@router.get(
    "/modelos/{modelo_id}",
    response_model=ModeloNeumaticoRead,
    summary="Obtener un modelo por ID",
    dependencies=[Depends(get_current_user)]  # Requiere autenticación
)
async def read_modelo(
    modelo_id: UUID,
    service: CatalogosService = Depends(get_catalogos_service)
):
    """
    Obtiene los detalles de un modelo por su ID.
    """
    return await service.get_modelo_by_id(modelo_id, service.current_user)

@router.put(
    "/modelos/{modelo_id}",
    response_model=ModeloNeumaticoRead,
    summary="Actualizar un modelo",
    dependencies=[Depends(get_current_user)]  # Requiere autenticación
)
async def update_modelo(
    modelo_id: UUID,
    modelo_in: ModeloNeumaticoUpdate,
    service: CatalogosService = Depends(get_catalogos_service)
):
    """
    Actualiza un modelo existente.
    
    Requiere permisos de administrador.
    """
    return await service.update_modelo(
        modelo_id=modelo_id,
        modelo_update=modelo_in,
        user=service.current_user
    )

@router.delete(
    "/modelos/{modelo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un modelo",
    dependencies=[Depends(get_current_user)]  # Requiere autenticación
)
async def delete_modelo(
    modelo_id: UUID,
    service: CatalogosService = Depends(get_catalogos_service)
):
    """
    Elimina un modelo.
    
    Requiere permisos de administrador.
    """
    await service.delete_modelo(modelo_id, service.current_user)
    return None

# --- Endpoints para Proveedores ---

@router.post(
    "/proveedores/", 
    response_model=ProveedorRead, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo proveedor",
    dependencies=[Depends(get_current_user)]  # Requiere autenticación
)
async def create_proveedor(
    proveedor_in: ProveedorCreate,
    service: CatalogosService = Depends(get_catalogos_service)
):
    """
    Crea un nuevo proveedor.
    
    Requiere permisos de administrador.
    """
    return await service.create_proveedor(proveedor_in, service.current_user)

@router.get(
    "/proveedores/", 
    response_model=List[ProveedorRead],
    summary="Listar proveedores",
    dependencies=[Depends(get_current_user)]  # Requiere autenticación
)
async def read_proveedores(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    activo: Optional[bool] = Query(None),
    service: CatalogosService = Depends(get_catalogos_service)
):
    """
    Lista todos los proveedores con paginación.
    
    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Número máximo de registros a devolver (máx. 100)
    - **activo**: Filtrar por estado activo/inactivo (opcional)
    """
    return await service.get_all_proveedores(
        user=service.current_user,
        skip=skip, limit=limit, activo=activo
    )

@router.get(
    "/proveedores/{proveedor_id}",
    response_model=ProveedorRead,
    summary="Obtener un proveedor por ID",
    dependencies=[Depends(get_current_user)]  # Requiere autenticación
)
async def read_proveedor(
    proveedor_id: UUID,
    service: CatalogosService = Depends(get_catalogos_service)
):
    """
    Obtiene los detalles de un proveedor por su ID.
    """
    return await service.get_proveedor_by_id(proveedor_id, service.current_user)

@router.put(
    "/proveedores/{proveedor_id}",
    response_model=ProveedorRead,
    summary="Actualizar un proveedor",
    dependencies=[Depends(get_current_user)]  # Requiere autenticación
)
async def update_proveedor(
    proveedor_id: UUID,
    proveedor_in: ProveedorUpdate,
    service: CatalogosService = Depends(get_catalogos_service)
):
    """
    Actualiza un proveedor existente.
    
    Requiere permisos de administrador.
    """
    return await service.update_proveedor(
        proveedor_id=proveedor_id,
        proveedor_update=proveedor_in,
        user=service.current_user
    )

@router.delete(
    "/proveedores/{proveedor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un proveedor",
    dependencies=[Depends(get_current_user)]  # Requiere autenticación
)
async def delete_proveedor(
    proveedor_id: UUID,
    service: CatalogosService = Depends(get_catalogos_service)
):
    """
    Elimina un proveedor.
    
    Requiere permisos de administrador.
    """
    await service.delete_proveedor(proveedor_id, service.current_user)
    return None

# --- Endpoints para Catálogo de Ítems ---

@router.post(
    "/items/",
    response_model=CatalogoItemRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo ítem en el catálogo",
    dependencies=[Depends(get_current_user)]
)
async def create_catalogo_item(
    item_in: CatalogoItemCreate,
    service: CatalogosService = Depends(get_catalogos_service)
):
    """
    Crea un nuevo ítem en el catálogo.
    
    Los usuarios solo pueden crear ítems para sí mismos a menos que sean administradores.
    """
    return await service.create_catalogo_item(item_in, service.current_user)

@router.get(
    "/items/{item_id}",
    response_model=CatalogoItemRead,
    summary="Obtener un ítem del catálogo por ID",
    dependencies=[Depends(get_current_user)]
)
async def get_catalogo_item(
    item_id: UUID,
    service: CatalogosService = Depends(get_catalogos_service)
):
    """
    Obtiene un ítem del catálogo por su ID.
    
    Los usuarios solo pueden ver sus propios ítems a menos que sean administradores.
    """
    return await service.get_catalogo_item(item_id, service.current_user)

@router.put(
    "/items/{item_id}",
    response_model=CatalogoItemRead,
    summary="Actualizar un ítem del catálogo",
    dependencies=[Depends(get_current_user)]
)
async def update_catalogo_item(
    item_id: UUID,
    item_in: CatalogoItemUpdate,
    service: CatalogosService = Depends(get_catalogos_service)
):
    """
    Actualiza un ítem del catálogo.
    
    Los usuarios solo pueden actualizar sus propios ítems a menos que sean administradores.
    """
    return await service.update_catalogo_item(
        item_id=item_id,
        item_update=item_in,
        user=service.current_user
    )

@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un ítem del catálogo",
    dependencies=[Depends(get_current_user)]
)
async def delete_catalogo_item(
    item_id: UUID,
    service: CatalogosService = Depends(get_catalogos_service)
):
    """
    Elimina un ítem del catálogo.
    
    Los usuarios solo pueden eliminar sus propios ítems a menos que sean administradores.
    """
    await service.delete_catalogo_item(item_id, service.current_user)
    return None

# ... (otros endpoints para Motivos, Almacenes, etc. seguirían el mismo patrón) ...
