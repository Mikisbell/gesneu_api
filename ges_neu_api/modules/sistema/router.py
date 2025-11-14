"""
Router para el módulo de sistema - Reescrito completamente.
Endpoints para ParametrosSistema, TareasProgramadas, Rutas y TiposRuta.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from .service import SistemaService
from .models import ParametrosSistema, TareasProgramadas, Rutas, TiposRuta

router = APIRouter()

def get_sistema_service(db: AsyncSession = Depends(get_session)) -> SistemaService:
    """Dependency para obtener el servicio de sistema."""
    return SistemaService(db)

# ============================================================================
# ENDPOINTS BÁSICOS CRUD - PARAMETROS SISTEMA
# ============================================================================

@router.get("/parametros", response_model=List[ParametrosSistema])
async def get_parametros_sistema(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: SistemaService = Depends(get_sistema_service)
):
    """Obtener todos los parámetros del sistema."""
    return await service.parametros_sistema_crud.get_multi(skip=skip, limit=limit)

@router.get("/parametros/{parametro_id}", response_model=ParametrosSistema)
async def get_parametro_sistema(
    parametro_id: UUID,
    service: SistemaService = Depends(get_sistema_service)
):
    """Obtener parámetro específico del sistema por ID."""
    parametro = await service.parametros_sistema_crud.get(parametro_id)
    if not parametro:
        raise HTTPException(status_code=404, detail="Parámetro no encontrado")
    return parametro

@router.post("/parametros", response_model=ParametrosSistema)
async def create_parametro_sistema(
    parametro: ParametrosSistema,
    service: SistemaService = Depends(get_sistema_service)
):
    """Crear nuevo parámetro del sistema."""
    return await service.parametros_sistema_crud.create(parametro)

@router.put("/parametros/{parametro_id}", response_model=ParametrosSistema)
async def update_parametro_sistema(
    parametro_id: UUID,
    parametro_update: ParametrosSistema,
    service: SistemaService = Depends(get_sistema_service)
):
    """Actualizar parámetro del sistema."""
    parametro = await service.parametros_sistema_crud.update(parametro_id, parametro_update)
    if not parametro:
        raise HTTPException(status_code=404, detail="Parámetro no encontrado")
    return parametro

@router.delete("/parametros/{parametro_id}")
async def delete_parametro_sistema(
    parametro_id: UUID,
    service: SistemaService = Depends(get_sistema_service)
):
    """Eliminar parámetro del sistema."""
    parametro = await service.parametros_sistema_crud.remove(parametro_id)
    if not parametro:
        raise HTTPException(status_code=404, detail="Parámetro no encontrado")
    return {"message": "Parámetro eliminado exitosamente"}

# ============================================================================
# ENDPOINTS BÁSICOS CRUD - TAREAS PROGRAMADAS
# ============================================================================

@router.get("/tareas", response_model=List[TareasProgramadas])
async def get_tareas_programadas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: SistemaService = Depends(get_sistema_service)
):
    """Obtener tareas programadas."""
    return await service.tareas_programadas_crud.get_multi(skip=skip, limit=limit)

@router.get("/tareas/{tarea_id}", response_model=TareasProgramadas)
async def get_tarea_programada(
    tarea_id: UUID,
    service: SistemaService = Depends(get_sistema_service)
):
    """Obtener tarea programada por ID."""
    tarea = await service.tareas_programadas_crud.get(tarea_id)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea

@router.post("/tareas", response_model=TareasProgramadas)
async def create_tarea_programada(
    tarea: TareasProgramadas,
    service: SistemaService = Depends(get_sistema_service)
):
    """Crear nueva tarea programada."""
    return await service.tareas_programadas_crud.create(tarea)

@router.put("/tareas/{tarea_id}", response_model=TareasProgramadas)
async def update_tarea_programada(
    tarea_id: UUID,
    tarea_update: TareasProgramadas,
    service: SistemaService = Depends(get_sistema_service)
):
    """Actualizar tarea programada."""
    tarea = await service.tareas_programadas_crud.update(tarea_id, tarea_update)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea

@router.delete("/tareas/{tarea_id}")
async def delete_tarea_programada(
    tarea_id: UUID,
    service: SistemaService = Depends(get_sistema_service)
):
    """Eliminar tarea programada."""
    tarea = await service.tareas_programadas_crud.remove(tarea_id)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return {"message": "Tarea eliminada exitosamente"}

# ============================================================================
# ENDPOINTS BÁSICOS CRUD - RUTAS
# ============================================================================

@router.get("/rutas", response_model=List[Rutas])
async def get_rutas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: SistemaService = Depends(get_sistema_service)
):
    """Obtener rutas."""
    return await service.rutas_crud.get_multi(skip=skip, limit=limit)

@router.get("/rutas/{ruta_id}", response_model=Rutas)
async def get_ruta(
    ruta_id: UUID,
    service: SistemaService = Depends(get_sistema_service)
):
    """Obtener ruta por ID."""
    ruta = await service.rutas_crud.get(ruta_id)
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    return ruta

@router.post("/rutas", response_model=Rutas)
async def create_ruta(
    ruta: Rutas,
    service: SistemaService = Depends(get_sistema_service)
):
    """Crear nueva ruta."""
    return await service.rutas_crud.create(ruta)

@router.put("/rutas/{ruta_id}", response_model=Rutas)
async def update_ruta(
    ruta_id: UUID,
    ruta_update: Rutas,
    service: SistemaService = Depends(get_sistema_service)
):
    """Actualizar ruta."""
    ruta = await service.rutas_crud.update(ruta_id, ruta_update)
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    return ruta

@router.delete("/rutas/{ruta_id}")
async def delete_ruta(
    ruta_id: UUID,
    service: SistemaService = Depends(get_sistema_service)
):
    """Eliminar ruta."""
    ruta = await service.rutas_crud.remove(ruta_id)
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    return {"message": "Ruta eliminada exitosamente"}

# ============================================================================
# ENDPOINTS BÁSICOS CRUD - TIPOS RUTA
# ============================================================================

@router.get("/tipos-ruta", response_model=List[TiposRuta])
async def get_tipos_ruta(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: SistemaService = Depends(get_sistema_service)
):
    """Obtener tipos de ruta."""
    return await service.tipos_ruta_crud.get_multi(skip=skip, limit=limit)

@router.get("/tipos-ruta/{tipo_id}", response_model=TiposRuta)
async def get_tipo_ruta(
    tipo_id: UUID,
    service: SistemaService = Depends(get_sistema_service)
):
    """Obtener tipo de ruta por ID."""
    tipo = await service.tipos_ruta_crud.get(tipo_id)
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de ruta no encontrado")
    return tipo

@router.post("/tipos-ruta", response_model=TiposRuta)
async def create_tipo_ruta(
    tipo: TiposRuta,
    service: SistemaService = Depends(get_sistema_service)
):
    """Crear nuevo tipo de ruta."""
    return await service.tipos_ruta_crud.create(tipo)

@router.put("/tipos-ruta/{tipo_id}", response_model=TiposRuta)
async def update_tipo_ruta(
    tipo_id: UUID,
    tipo_update: TiposRuta,
    service: SistemaService = Depends(get_sistema_service)
):
    """Actualizar tipo de ruta."""
    tipo = await service.tipos_ruta_crud.update(tipo_id, tipo_update)
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de ruta no encontrado")
    return tipo

@router.delete("/tipos-ruta/{tipo_id}")
async def delete_tipo_ruta(
    tipo_id: UUID,
    service: SistemaService = Depends(get_sistema_service)
):
    """Eliminar tipo de ruta."""
    tipo = await service.tipos_ruta_crud.remove(tipo_id)
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de ruta no encontrado")
    return {"message": "Tipo de ruta eliminado exitosamente"}