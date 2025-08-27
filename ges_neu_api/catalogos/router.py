# ges_neu_api/catalogos/router.py

from uuid import UUID
from typing import List, Optional

from fastapi import APIRouter, Depends, status, Query, HTTPException

# Importaciones de la aplicación
from ges_neu_api.auth.schemas import UsuarioRead
from ges_neu_api.auth.dependencies import get_current_user # Usar la dependencia de auth
from ges_neu_api.catalogos.schemas import (
    FabricanteCreate, FabricanteRead, FabricanteUpdate,
    ModeloNeumaticoCreate, ModeloNeumaticoRead, ModeloNeumaticoUpdate,
    ProveedorCreate, ProveedorRead, ProveedorUpdate,
    MotivoDesechoCreate, MotivoDesechoRead, MotivoDesechoUpdate,
    AlmacenCreate, AlmacenRead, AlmacenUpdate,
    ParametroInventarioCreate, ParametroInventarioRead, ParametroInventarioUpdate
)
from .dependencies import get_catalogos_service, CurrentCatalogosService
from .service import CatalogosService

router = APIRouter(tags=["Catálogos"])

# --- Endpoints para Fabricantes ---

@router.post(
    "/fabricantes/", 
    response_model=FabricanteRead, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo fabricante",
)
async def create_fabricante(
    fabricante_in: FabricanteCreate,
    service: CatalogosService = Depends(get_catalogos_service),
    current_user: UsuarioRead = Depends(get_current_user)
):
    return await service.create_fabricante(
        fabricante_in=fabricante_in, user_id=current_user.id
    )

@router.get(
    "/fabricantes/", 
    response_model=List[FabricanteRead],
    summary="Listar fabricantes",
)
async def read_fabricantes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    activo: Optional[bool] = Query(None),
    service: CatalogosService = Depends(get_catalogos_service),
    current_user: UsuarioRead = Depends(get_current_user)
):
    return await service.get_all_fabricantes(skip=skip, limit=limit, activo=activo)

@router.get(
    "/fabricantes/{fabricante_id}", 
    response_model=FabricanteRead,
    summary="Obtener un fabricante",
)
async def read_fabricante(
    fabricante_id: UUID,
    service: CatalogosService = Depends(get_catalogos_service),
    current_user: UsuarioRead = Depends(get_current_user)
):
    return await service.get_fabricante_by_id(fabricante_id=fabricante_id)

@router.put(
    "/fabricantes/{fabricante_id}", 
    response_model=FabricanteRead,
    summary="Actualizar un fabricante",
)
async def update_fabricante(
    fabricante_id: UUID,
    fabricante_in: FabricanteUpdate,
    service: CatalogosService = Depends(get_catalogos_service),
    current_user: UsuarioRead = Depends(get_current_user)
):
    return await service.update_fabricante(
        fabricante_id=fabricante_id, fabricante_in=fabricante_in, user_id=current_user.id
    )

@router.delete(
    "/fabricantes/{fabricante_id}",
    response_model=FabricanteRead,
    summary="Eliminar un fabricante",
)
async def delete_fabricante(
    fabricante_id: UUID,
    service: CatalogosService = Depends(get_catalogos_service),
    current_user: UsuarioRead = Depends(get_current_user)
):
    return await service.delete_fabricante(fabricante_id=fabricante_id)

# --- Endpoints para Modelos ---

@router.post(
    "/modelos/", 
    response_model=ModeloNeumaticoRead, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo modelo",
)
async def create_modelo(
    modelo_in: ModeloNeumaticoCreate,
    service: CatalogosService = Depends(get_catalogos_service),
    current_user: UsuarioRead = Depends(get_current_user)
):
    return await service.create_modelo(modelo_in=modelo_in, user_id=current_user.id)

@router.get(
    "/modelos/", 
    response_model=List[ModeloNeumaticoRead],
    summary="Listar modelos",
)
async def read_modelos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    fabricante_id: Optional[UUID] = Query(None),
    activo: Optional[bool] = Query(None),
    service: CatalogosService = Depends(get_catalogos_service),
    current_user: UsuarioRead = Depends(get_current_user)
):
    return await service.get_all_modelos(
        skip=skip, limit=limit, fabricante_id=fabricante_id, activo=activo
    )

@router.get(
    "/modelos/{modelo_id}", 
    response_model=ModeloNeumaticoRead,
    summary="Obtener un modelo",
)
async def read_modelo(
    modelo_id: UUID,
    service: CatalogosService = Depends(get_catalogos_service),
    current_user: UsuarioRead = Depends(get_current_user)
):
    return await service.get_modelo_by_id(modelo_id=modelo_id)

@router.put(
    "/modelos/{modelo_id}", 
    response_model=ModeloNeumaticoRead,
    summary="Actualizar un modelo",
)
async def update_modelo(
    modelo_id: UUID,
    modelo_in: ModeloNeumaticoUpdate,
    service: CatalogosService = Depends(get_catalogos_service),
    current_user: UsuarioRead = Depends(get_current_user)
):
    return await service.update_modelo(
        modelo_id=modelo_id, modelo_in=modelo_in, user_id=current_user.id
    )

@router.delete(
    "/modelos/{modelo_id}",
    response_model=ModeloNeumaticoRead,
    summary="Eliminar un modelo",
)
async def delete_modelo(
    modelo_id: UUID,
    service: CatalogosService = Depends(get_catalogos_service),
    current_user: UsuarioRead = Depends(get_current_user)
):
    return await service.delete_modelo(modelo_id=modelo_id)

# ... (El resto de endpoints para Proveedores, Motivos, etc. seguirían el mismo patrón)
# Por brevedad, se omiten, pero la refactorización sería idéntica.
