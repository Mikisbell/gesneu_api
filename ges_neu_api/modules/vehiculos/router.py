from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from .schemas import VehiculoCreate, VehiculoUpdate, VehiculoRead
from .service import VehiculosService
from .dependencies import get_vehiculos_service

router = APIRouter(tags=["vehiculos"])

@router.post(
    "/", 
    response_model=VehiculoRead, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo vehículo"
)
async def create_vehiculo(
    vehiculo_in: VehiculoCreate,
    vehiculos_service: VehiculosService = Depends(get_vehiculos_service)
) -> VehiculoRead:
    """Crea un nuevo registro de vehículo en la base de datos."""
    return await vehiculos_service.create_vehiculo(vehiculo_in)

@router.get(
    "/", 
    response_model=List[VehiculoRead],
    summary="Obtener todos los vehículos"
)
async def read_vehiculos(
    skip: int = 0,
    limit: int = 100,
    vehiculos_service: VehiculosService = Depends(get_vehiculos_service)
) -> List[VehiculoRead]:
    """Recupera una lista de todos los vehículos registrados."""
    return await vehiculos_service.get_multi_vehiculos(skip=skip, limit=limit)

@router.get(
    "/{vehiculo_id}", 
    response_model=VehiculoRead,
    summary="Obtener vehículo por ID"
)
async def read_vehiculo(
    vehiculo_id: UUID,
    vehiculos_service: VehiculosService = Depends(get_vehiculos_service)
) -> VehiculoRead:
    """Recupera un vehículo específico por su ID."""
    vehiculo = await vehiculos_service.get_vehiculo(vehiculo_id)
    if not vehiculo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
    return vehiculo

@router.put(
    "/{vehiculo_id}", 
    response_model=VehiculoRead,
    summary="Actualizar un vehículo"
)
async def update_vehiculo(
    vehiculo_id: UUID,
    vehiculo_in: VehiculoUpdate,
    vehiculos_service: VehiculosService = Depends(get_vehiculos_service)
) -> VehiculoRead:
    """Actualiza un vehículo existente por su ID."""
    vehiculo = await vehiculos_service.update_vehiculo(vehiculo_id, vehiculo_in)
    if not vehiculo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
    return vehiculo

@router.delete(
    "/{vehiculo_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un vehículo"
)
async def delete_vehiculo(
    vehiculo_id: UUID,
    vehiculos_service: VehiculosService = Depends(get_vehiculos_service)
):
    """Elimina un vehículo por su ID."""
    deleted_id = await vehiculos_service.delete_vehiculo(vehiculo_id)
    if not deleted_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
    return # No content for 204