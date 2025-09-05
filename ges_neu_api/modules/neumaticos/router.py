"""
Router completo para el módulo de neumáticos.
"""
from typing import List, Optional
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
from ..auth.dependencies import get_current_user
from ..auth import schemas as auth_schemas

router = APIRouter(
    tags=["neumaticos"]
)

# Endpoints para Neumáticos
@router.get("/health", summary="Estado del módulo de neumáticos")
async def health_neumaticos():
    """Verifica el estado del módulo de neumáticos."""
    return {
        "module": "neumaticos",
        "status": "active",
        "models_status": "functional",
        "endpoints_status": "complete"
    }

@router.post("/", response_model=NeumaticoResponse)
async def create_neumatico(
    neumatico_data: NeumaticoCreate,
    service: NeumaticoService = Depends(get_neumatico_service)
):
    """Crear un nuevo neumático."""
    return await service.create_neumatico(neumatico_data)

# Endpoints para Fabricantes (ANTES de rutas con parámetros)
@router.post("/fabricantes", response_model=FabricanteResponse)
@router.post("/fabricantes/", response_model=FabricanteResponse)
async def create_fabricante(
    fabricante_data: FabricanteCreate,
    service: NeumaticoService = Depends(get_neumatico_service)
):
    """Crear un nuevo fabricante."""
    return await service.create_fabricante(fabricante_data)

@router.get("/fabricantes", response_model=List[FabricanteResponse])
@router.get("/fabricantes/", response_model=List[FabricanteResponse])
async def get_fabricantes(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    service: NeumaticoService = Depends(get_neumatico_service)
):
    """Obtener lista de fabricantes."""
    return await service.get_fabricantes(skip=skip, limit=limit)

@router.get("/fabricantes/{fabricante_id}", response_model=FabricanteResponse)
@router.get("/fabricantes/{fabricante_id}/", response_model=FabricanteResponse)
async def get_fabricante(
    fabricante_id: UUID,
    service: NeumaticoService = Depends(get_neumatico_service)
):
    """Obtener un fabricante por ID."""
    return await service.get_fabricante(fabricante_id)

@router.put("/fabricantes/{fabricante_id}", response_model=FabricanteResponse)
@router.put("/fabricantes/{fabricante_id}/", response_model=FabricanteResponse)
async def update_fabricante(
    fabricante_id: UUID,
    fabricante_data: FabricanteUpdate,
    service: NeumaticoService = Depends(get_neumatico_service)
):
    """Actualizar un fabricante."""
    return await service.update_fabricante(fabricante_id, fabricante_data)

@router.delete("/fabricantes/{fabricante_id}")
@router.delete("/fabricantes/{fabricante_id}/")
async def delete_fabricante(
    fabricante_id: UUID,
    service: NeumaticoService = Depends(get_neumatico_service)
):
    """Eliminar un fabricante."""
    await service.delete_fabricante(fabricante_id)
    return {"message": "Fabricante eliminado exitosamente"}

# Endpoints para Modelos
@router.post("/modelos", response_model=ModeloResponse)
@router.post("/modelos/", response_model=ModeloResponse)
async def create_modelo(
    modelo_data: ModeloCreate,
    service: NeumaticoService = Depends(get_neumatico_service)
):
    """Crear un nuevo modelo."""
    return await service.create_modelo(modelo_data)

@router.get("/modelos", response_model=List[ModeloResponse])
@router.get("/modelos/", response_model=List[ModeloResponse])
async def get_modelos(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    service: NeumaticoService = Depends(get_neumatico_service)
):
    """Obtener lista de modelos."""
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Obteniendo modelos: skip={skip}, limit={limit}")
        
        modelos = await service.get_modelos(skip=skip, limit=limit)
        logger.info(f"Modelos obtenidos exitosamente: {len(modelos)} modelos")
        return modelos
    except Exception as e:
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error en get_modelos: {str(e)}")
        logger.error(f"Traceback completo: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno: {str(e)}"
        )

@router.get("/modelos/{modelo_id}", response_model=ModeloResponse)
@router.get("/modelos/{modelo_id}/", response_model=ModeloResponse)
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
@router.put("/modelos/{modelo_id}/", response_model=ModeloResponse)
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
@router.delete("/modelos/{modelo_id}/")
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
    estado: Optional[str] = Query(None, description="Filtrar por estado del neumático"),
    service: NeumaticoService = Depends(get_neumatico_service),
    current_user: auth_schemas.UserRead = Depends(get_current_user)
):
    """Obtener lista de neumáticos con filtro opcional por estado."""
    return await service.get_neumaticos(skip=skip, limit=limit, estado=estado)

@router.get("/{neumatico_id}", response_model=NeumaticoResponse)
async def get_neumatico(
    neumatico_id: UUID,
    service: NeumaticoService = Depends(get_neumatico_service)
):
    """Obtener un neumático por ID."""
    try:
        neumatico = await service.get_neumatico(neumatico_id)
        if not neumatico:
            raise HTTPException(status_code=404, detail="Neumático no encontrado")
        return neumatico
    except HTTPException:
        # Propagar HTTPExceptions controladas
        raise
    except Exception as e:
        # Error inesperado (por ejemplo, base de datos no disponible)
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

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

 
