"""
Router para el módulo de sistema.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from ...core.database import get_db
from .service import SistemaService
from ..bitacoras.models import ParametrosSistema, TareasProgramadas, Rutas, TiposRuta

router = APIRouter()

def get_sistema_service(db: Session = Depends(get_db)) -> SistemaService:
    """Dependency para obtener el servicio de sistema."""
    return SistemaService(db)

# Endpoints de Parámetros del Sistema
@router.get("/parametros", response_model=List[ParametrosSistema])
async def get_parametros_sistema(
    service: SistemaService = Depends(get_sistema_service)
):
    """Obtener todos los parámetros del sistema."""
    return await service.get_parametros_sistema()

@router.get("/parametros/{clave}", response_model=ParametrosSistema)
async def get_parametro_sistema(
    clave: str,
    service: SistemaService = Depends(get_sistema_service)
):
    """Obtener parámetro específico del sistema por clave."""
    parametro = await service.get_parametro_sistema(clave)
    if not parametro:
        raise HTTPException(status_code=404, detail="Parámetro no encontrado")
    return parametro

@router.post("/parametros", response_model=ParametrosSistema)
async def create_parametro_sistema(
    parametro_data: dict,
    service: SistemaService = Depends(get_sistema_service)
):
    """Crear nuevo parámetro del sistema."""
    return await service.create_parametro_sistema(parametro_data)

@router.put("/parametros/{clave}", response_model=ParametrosSistema)
async def update_parametro_sistema(
    clave: str,
    valor: str,
    descripcion: Optional[str] = None,
    service: SistemaService = Depends(get_sistema_service)
):
    """Actualizar parámetro del sistema."""
    parametro = await service.update_parametro_sistema(clave, valor, descripcion)
    if not parametro:
        raise HTTPException(status_code=404, detail="Parámetro no encontrado")
    return parametro

@router.delete("/parametros/{parametro_id}")
async def delete_parametro_sistema(
    parametro_id: int,
    service: SistemaService = Depends(get_sistema_service)
):
    """Eliminar parámetro del sistema."""
    success = await service.delete_parametro_sistema(parametro_id)
    if not success:
        raise HTTPException(status_code=404, detail="Parámetro no encontrado")
    return {"message": "Parámetro eliminado exitosamente"}

# Endpoints de Tareas Programadas
@router.get("/tareas", response_model=List[TareasProgramadas])
async def get_tareas_programadas(
    activa: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    service: SistemaService = Depends(get_sistema_service)
):
    """Obtener tareas programadas."""
    return await service.get_tareas_programadas(activa=activa)

@router.get("/tareas/{tarea_id}", response_model=TareasProgramadas)
async def get_tarea_programada(
    tarea_id: int,
    service: SistemaService = Depends(get_sistema_service)
):
    """Obtener tarea programada por ID."""
    tarea = await service.get_tarea_programada(tarea_id)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea

@router.post("/tareas", response_model=TareasProgramadas)
async def create_tarea_programada(
    tarea_data: dict,
    service: SistemaService = Depends(get_sistema_service)
):
    """Crear nueva tarea programada."""
    return await service.create_tarea_programada(tarea_data)

@router.put("/tareas/{tarea_id}", response_model=TareasProgramadas)
async def update_tarea_programada(
    tarea_id: int,
    tarea_data: dict,
    service: SistemaService = Depends(get_sistema_service)
):
    """Actualizar tarea programada."""
    tarea = await service.update_tarea_programada(tarea_id, tarea_data)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea

@router.put("/tareas/{tarea_id}/estado", response_model=TareasProgramadas)
async def activar_desactivar_tarea(
    tarea_id: int,
    activa: bool,
    service: SistemaService = Depends(get_sistema_service)
):
    """Activar o desactivar tarea programada."""
    tarea = await service.activar_desactivar_tarea(tarea_id, activa)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea

@router.put("/tareas/{tarea_id}/ejecucion", response_model=TareasProgramadas)
async def actualizar_ejecucion_tarea(
    tarea_id: int,
    proxima_ejecucion: Optional[datetime] = None,
    service: SistemaService = Depends(get_sistema_service)
):
    """Actualizar fechas de ejecución de tarea."""
    tarea = await service.actualizar_ejecucion_tarea(tarea_id, proxima_ejecucion)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea

# Endpoints de Rutas
@router.get("/rutas", response_model=List[Rutas])
async def get_rutas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    service: SistemaService = Depends(get_sistema_service)
):
    """Obtener rutas."""
    return await service.get_rutas(skip=skip, limit=limit, activo=activo)

@router.get("/rutas/{ruta_id}", response_model=Rutas)
async def get_ruta(
    ruta_id: UUID,
    service: SistemaService = Depends(get_sistema_service)
):
    """Obtener ruta por ID."""
    ruta = await service.get_ruta(ruta_id)
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    return ruta

@router.get("/rutas/codigo/{codigo}", response_model=Rutas)
async def get_ruta_by_codigo(
    codigo: str,
    service: SistemaService = Depends(get_sistema_service)
):
    """Obtener ruta por código."""
    ruta = await service.get_ruta_by_codigo(codigo)
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    return ruta

@router.post("/rutas", response_model=Rutas)
async def create_ruta(
    ruta_data: dict,
    service: SistemaService = Depends(get_sistema_service)
):
    """Crear nueva ruta."""
    return await service.create_ruta(ruta_data)

@router.put("/rutas/{ruta_id}", response_model=Rutas)
async def update_ruta(
    ruta_id: UUID,
    ruta_data: dict,
    service: SistemaService = Depends(get_sistema_service)
):
    """Actualizar ruta."""
    ruta = await service.update_ruta(ruta_id, ruta_data)
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    return ruta

@router.delete("/rutas/{ruta_id}")
async def delete_ruta(
    ruta_id: UUID,
    service: SistemaService = Depends(get_sistema_service)
):
    """Eliminar ruta (desactivar)."""
    success = await service.delete_ruta(ruta_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    return {"message": "Ruta desactivada exitosamente"}

# Endpoints de Tipos de Ruta
@router.get("/tipos-ruta", response_model=List[TiposRuta])
async def get_tipos_ruta(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    service: SistemaService = Depends(get_sistema_service)
):
    """Obtener tipos de ruta."""
    return await service.get_tipos_ruta(skip=skip, limit=limit, activo=activo)

@router.get("/tipos-ruta/{tipo_id}", response_model=TiposRuta)
async def get_tipo_ruta(
    tipo_id: UUID,
    service: SistemaService = Depends(get_sistema_service)
):
    """Obtener tipo de ruta por ID."""
    tipo = await service.get_tipo_ruta(tipo_id)
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de ruta no encontrado")
    return tipo

@router.get("/tipos-ruta/nombre/{nombre}", response_model=TiposRuta)
async def get_tipo_ruta_by_nombre(
    nombre: str,
    service: SistemaService = Depends(get_sistema_service)
):
    """Obtener tipo de ruta por nombre."""
    tipo = await service.get_tipo_ruta_by_nombre(nombre)
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de ruta no encontrado")
    return tipo

@router.post("/tipos-ruta", response_model=TiposRuta)
async def create_tipo_ruta(
    tipo_data: dict,
    service: SistemaService = Depends(get_sistema_service)
):
    """Crear nuevo tipo de ruta."""
    return await service.create_tipo_ruta(tipo_data)

@router.put("/tipos-ruta/{tipo_id}", response_model=TiposRuta)
async def update_tipo_ruta(
    tipo_id: UUID,
    tipo_data: dict,
    service: SistemaService = Depends(get_sistema_service)
):
    """Actualizar tipo de ruta."""
    tipo = await service.update_tipo_ruta(tipo_id, tipo_data)
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de ruta no encontrado")
    return tipo

@router.delete("/tipos-ruta/{tipo_id}")
async def delete_tipo_ruta(
    tipo_id: UUID,
    service: SistemaService = Depends(get_sistema_service)
):
    """Eliminar tipo de ruta (desactivar)."""
    success = await service.delete_tipo_ruta(tipo_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tipo de ruta no encontrado")
    return {"message": "Tipo de ruta desactivado exitosamente"}

# Endpoints de Utilidad
@router.get("/configuracion")
async def get_configuracion_completa(
    service: SistemaService = Depends(get_sistema_service)
):
    """Obtener configuración completa del sistema."""
    return await service.get_configuracion_completa()

@router.get("/backup")
async def backup_configuracion(
    service: SistemaService = Depends(get_sistema_service)
):
    """Crear backup de la configuración del sistema."""
    return await service.backup_configuracion()
