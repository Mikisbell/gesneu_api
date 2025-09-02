"""
Router completo para el módulo de neumáticos.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from .service import NeumaticoService
from .dependencies import get_neumatico_service
from .schemas import (
    NeumaticoCreate, NeumaticoUpdate, NeumaticoResponse,
    FabricanteCreate, FabricanteUpdate, FabricanteResponse,
    ModeloCreate, ModeloUpdate, ModeloResponse
)

router = APIRouter(
    tags=["neumaticos"]
)

# Endpoints para Neumáticos
@router.post("/", response_model=NeumaticoResponse)
async def create_neumatico(
    neumatico_data: NeumaticoCreate,
    service: NeumaticoService = Depends(get_neumatico_service)
):
    """Crear un nuevo neumático."""
    return await service.create_neumatico(neumatico_data)

# Endpoints para Fabricantes (ANTES de rutas con parámetros)
@router.post("/fabricantes", response_model=FabricanteResponse)
async def create_fabricante(
    fabricante_data: FabricanteCreate,
    service: NeumaticoService = Depends(get_neumatico_service)
):
    """Crear un nuevo fabricante."""
    return await service.create_fabricante(fabricante_data)

@router.get("/fabricantes", response_model=List[FabricanteResponse])
async def get_fabricantes(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    service: NeumaticoService = Depends(get_neumatico_service)
):
    """Obtener lista de fabricantes."""
    return await service.get_fabricantes(skip=skip, limit=limit)

@router.get("/fabricantes/{fabricante_id}", response_model=FabricanteResponse)
async def get_fabricante(
    fabricante_id: UUID,
    service: NeumaticoService = Depends(get_neumatico_service)
):
    """Obtener un fabricante por ID."""
    fabricante = await service.get_fabricante(fabricante_id)
    if not fabricante:
        raise HTTPException(status_code=404, detail="Fabricante no encontrado")
    return fabricante

@router.put("/fabricantes/{fabricante_id}", response_model=FabricanteResponse)
async def update_fabricante(
    fabricante_id: UUID,
    fabricante_data: FabricanteUpdate,
    service: NeumaticoService = Depends(get_neumatico_service)
):
    """Actualizar un fabricante."""
    fabricante = await service.update_fabricante(fabricante_id, fabricante_data)
    if not fabricante:
        raise HTTPException(status_code=404, detail="Fabricante no encontrado")
    return fabricante

@router.delete("/fabricantes/{fabricante_id}")
async def delete_fabricante(
    fabricante_id: UUID,
    service: NeumaticoService = Depends(get_neumatico_service)
):
    """Eliminar un fabricante."""
    success = await service.delete_fabricante(fabricante_id)
    if not success:
        raise HTTPException(status_code=404, detail="Fabricante no encontrado")
    return {"message": "Fabricante eliminado exitosamente"}

# Endpoints para Modelos
@router.post("/modelos", response_model=ModeloResponse)
async def create_modelo(
    modelo_data: ModeloCreate,
    service: NeumaticoService = Depends(get_neumatico_service)
):
    """Crear un nuevo modelo."""
    return await service.create_modelo(modelo_data)

@router.get("/modelos", response_model=List[ModeloResponse])
async def get_modelos(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    service: NeumaticoService = Depends(get_neumatico_service)
):
    """Obtener lista de modelos."""
    return await service.get_modelos(skip=skip, limit=limit)

@router.get("/modelos/{modelo_id}", response_model=ModeloResponse)
async def get_modelo(
    modelo_id: UUID,
    service: NeumaticoService = Depends(get_neumatico_service)
):
    """Obtener un modelo por ID."""
    modelo = await service.get_modelo(modelo_id)
    if not modelo:
        raise HTTPException(status_code=404, detail="Modelo no encontrado")
    return modelo

@router.put("/modelos/{modelo_id}", response_model=ModeloResponse)
async def update_modelo(
    modelo_id: UUID,
    modelo_data: ModeloUpdate,
    service: NeumaticoService = Depends(get_neumatico_service)
):
    """Actualizar un modelo."""
    modelo = await service.update_modelo(modelo_id, modelo_data)
    if not modelo:
        raise HTTPException(status_code=404, detail="Modelo no encontrado")
    return modelo

@router.delete("/modelos/{modelo_id}")
async def delete_modelo(
    modelo_id: UUID,
    service: NeumaticoService = Depends(get_neumatico_service)
):
    """Eliminar un modelo."""
    success = await service.delete_modelo(modelo_id)
    if not success:
        raise HTTPException(status_code=404, detail="Modelo no encontrado")
    return {"message": "Modelo eliminado exitosamente"}

@router.get("/", response_model=List[NeumaticoResponse])
async def get_neumaticos(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    service: NeumaticoService = Depends(get_neumatico_service)
):
    """Obtener lista de neumáticos."""
    return await service.get_neumaticos(skip=skip, limit=limit)

@router.get("/{neumatico_id}", response_model=NeumaticoResponse)
async def get_neumatico(
    neumatico_id: UUID,
    service: NeumaticoService = Depends(get_neumatico_service)
):
    """Obtener un neumático por ID."""
    neumatico = await service.get_neumatico(neumatico_id)
    if not neumatico:
        raise HTTPException(status_code=404, detail="Neumático no encontrado")
    return neumatico

@router.put("/{neumatico_id}", response_model=NeumaticoResponse)
async def update_neumatico(
    neumatico_id: UUID,
    neumatico_data: NeumaticoUpdate,
    service: NeumaticoService = Depends(get_neumatico_service)
):
    """Actualizar un neumático."""
    neumatico = await service.update_neumatico(neumatico_id, neumatico_data)
    if not neumatico:
        raise HTTPException(status_code=404, detail="Neumático no encontrado")
    return neumatico

@router.delete("/{neumatico_id}")
async def delete_neumatico(
    neumatico_id: UUID,
    service: NeumaticoService = Depends(get_neumatico_service)
):
    """Eliminar un neumático."""
    success = await service.delete_neumatico(neumatico_id)
    if not success:
        raise HTTPException(status_code=404, detail="Neumático no encontrado")
    return {"message": "Neumático eliminado exitosamente"}

@router.get("/health", summary="Estado del módulo de neumáticos")
async def health_neumaticos():
    """Verifica el estado del módulo de neumáticos."""
    return {
        "module": "neumaticos",
        "status": "active",
        "models_status": "functional",
        "endpoints_status": "complete"
    }
