"""
Router para el módulo de bitácoras y auditoría.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from .service import BitacoraService
from .models import (
    BitacoraMantenimiento,
    BitacoraOperaciones,
    AuditoriaLog,
    AuditoriaRolesUsuarios
)
from ..sistema.models import (
    ConfiguracionAuditoria,
    ErroresAplicacion,
    ParametrosSistema,
    TareasProgramadas,
    Rutas,
    TiposRuta
)

router = APIRouter()

async def get_bitacora_service(db: AsyncSession = Depends(get_session)) -> BitacoraService:
    """Dependency para obtener el servicio de bitácoras."""
    return BitacoraService(db)

# Endpoints de Bitácora de Mantenimiento
@router.get("/mantenimiento", response_model=List[BitacoraMantenimiento])
async def get_bitacoras_mantenimiento(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: BitacoraService = Depends(get_bitacora_service)
):
    """Obtener bitácoras de mantenimiento."""
    return await service.get_bitacoras_mantenimiento(skip=skip, limit=limit)

@router.get("/mantenimiento/{bitacora_id}", response_model=BitacoraMantenimiento)
async def get_bitacora_mantenimiento(
    bitacora_id: UUID,
    service: BitacoraService = Depends(get_bitacora_service)
):
    """Obtener bitácora de mantenimiento por ID."""
    bitacora = await service.get_bitacora_mantenimiento(bitacora_id)
    if not bitacora:
        raise HTTPException(status_code=404, detail="Bitácora de mantenimiento no encontrada")
    return bitacora

@router.post("/mantenimiento", response_model=BitacoraMantenimiento)
async def create_bitacora_mantenimiento(
    bitacora_data: dict,
    service: BitacoraService = Depends(get_bitacora_service)
):
    """Crear nueva entrada de bitácora de mantenimiento."""
    return await service.create_bitacora_mantenimiento(bitacora_data)

# Endpoints de Bitácora de Operaciones
@router.get("/operaciones", response_model=List[BitacoraOperaciones])
async def get_bitacoras_operaciones(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    tipo_operacion: Optional[str] = Query(None, description="Filtrar por tipo de operación"),
    estado_operacion: Optional[str] = Query(None, description="Filtrar por estado de operación"),
    service: BitacoraService = Depends(get_bitacora_service)
):
    """Obtener bitácoras de operaciones con filtros opcionales."""
    return await service.get_bitacoras_operaciones(
        skip=skip, 
        limit=limit, 
        tipo_operacion=tipo_operacion, 
        estado_operacion=estado_operacion
    )

@router.get("/operaciones/{operacion_id}", response_model=BitacoraOperaciones)
async def get_bitacora_operacion(
    operacion_id: UUID,
    service: BitacoraService = Depends(get_bitacora_service)
):
    """Obtener bitácora de operación por ID."""
    bitacora = await service.get_bitacora_operacion(operacion_id)
    if not bitacora:
        raise HTTPException(status_code=404, detail="Bitácora de operación no encontrada")
    return bitacora

@router.post("/operaciones", response_model=BitacoraOperaciones)
async def create_bitacora_operacion(
    operacion_data: dict,
    service: BitacoraService = Depends(get_bitacora_service)
):
    """Crear nueva operación en bitácora."""
    return await service.create_bitacora_operacion(operacion_data)

@router.patch("/operaciones/{operacion_id}", response_model=BitacoraOperaciones)
async def update_bitacora_operacion(
    operacion_id: UUID,
    operacion_data: dict,
    service: BitacoraService = Depends(get_bitacora_service)
):
    """Actualizar bitácora de operación."""
    bitacora = await service.update_bitacora_operacion(operacion_id, operacion_data)
    if not bitacora:
        raise HTTPException(status_code=404, detail="Bitácora de operación no encontrada")
    return bitacora

# Endpoints de Auditoría
@router.get("/auditoria", response_model=List[AuditoriaLog])
async def get_auditoria_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    tabla: Optional[str] = Query(None, description="Filtrar por tabla específica"),
    service: BitacoraService = Depends(get_bitacora_service)
):
    """Obtener logs de auditoría."""
    if tabla:
        return await service.get_auditoria_by_tabla(tabla, skip=skip, limit=limit)
    return await service.get_auditoria_logs(skip=skip, limit=limit)

@router.get("/auditoria-roles", response_model=List[AuditoriaRolesUsuarios])
async def get_auditoria_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: BitacoraService = Depends(get_bitacora_service)
):
    """Obtener auditoría específica de roles y usuarios."""
    return await service.get_auditoria_roles_usuarios(skip=skip, limit=limit)

@router.get("/auditoria/configuracion", response_model=List[ConfiguracionAuditoria])
async def get_configuracion_auditoria(
    service: BitacoraService = Depends(get_bitacora_service)
):
    """Obtener configuración de auditoría."""
    return await service.get_configuracion_auditoria()

@router.put("/auditoria/configuracion/{tabla}")
async def update_configuracion_auditoria(
    tabla: str,
    config_data: dict,
    service: BitacoraService = Depends(get_bitacora_service)
):
    """Actualizar configuración de auditoría para una tabla."""
    config = await service.update_configuracion_auditoria(tabla, config_data)
    if not config:
        raise HTTPException(status_code=404, detail="Configuración de auditoría no encontrada")
    return config

# Endpoints de Errores de Aplicación
@router.get("/errores", response_model=List[ErroresAplicacion])
async def get_errores_aplicacion(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    resuelto: Optional[bool] = Query(None, description="Filtrar por estado de resolución"),
    service: BitacoraService = Depends(get_bitacora_service)
):
    """Obtener errores de aplicación."""
    return await service.get_errores_aplicacion(skip=skip, limit=limit, resuelto=resuelto)

@router.post("/errores", response_model=ErroresAplicacion)
async def create_error_aplicacion(
    error_data: dict,
    service: BitacoraService = Depends(get_bitacora_service)
):
    """Registrar error de aplicación."""
    return await service.create_error_aplicacion(error_data)

@router.put("/errores/{error_id}/resolver")
async def resolver_error(
    error_id: UUID,
    resuelto_por: str,
    comentario: str,
    service: BitacoraService = Depends(get_bitacora_service)
):
    """Marcar error como resuelto."""
    error = await service.resolver_error(error_id, resuelto_por, comentario)
    if not error:
        raise HTTPException(status_code=404, detail="Error no encontrado")
    return error

# Endpoints de Parámetros del Sistema
@router.get("/sistema/parametros", response_model=List[ParametrosSistema])
async def get_parametros_sistema(
    service: BitacoraService = Depends(get_bitacora_service)
):
    """Obtener parámetros del sistema."""
    return await service.get_parametros_sistema()

@router.get("/sistema/parametros/{clave}", response_model=ParametrosSistema)
async def get_parametro_sistema(
    clave: str,
    service: BitacoraService = Depends(get_bitacora_service)
):
    """Obtener parámetro específico del sistema."""
    parametro = await service.get_parametro_sistema(clave)
    if not parametro:
        raise HTTPException(status_code=404, detail="Parámetro no encontrado")
    return parametro

@router.put("/sistema/parametros/{clave}")
async def update_parametro_sistema(
    clave: str,
    valor: str,
    descripcion: Optional[str] = None,
    service: BitacoraService = Depends(get_bitacora_service)
):
    """Actualizar parámetro del sistema."""
    parametro = await service.update_parametro_sistema(clave, valor, descripcion)
    if not parametro:
        raise HTTPException(status_code=404, detail="Parámetro no encontrado")
    return parametro

# Endpoints de Tareas Programadas
@router.get("/sistema/tareas", response_model=List[TareasProgramadas])
async def get_tareas_programadas(
    activa: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    service: BitacoraService = Depends(get_bitacora_service)
):
    """Obtener tareas programadas."""
    return await service.get_tareas_programadas(activa=activa)

@router.put("/sistema/tareas/{tarea_id}")
async def update_tarea_programada(
    tarea_id: UUID,
    tarea_data: dict,
    service: BitacoraService = Depends(get_bitacora_service)
):
    """Actualizar tarea programada."""
    tarea = await service.update_tarea_programada(tarea_id, tarea_data)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea

# Endpoints de Rutas
@router.get("/rutas", response_model=List[Rutas])
async def get_rutas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: BitacoraService = Depends(get_bitacora_service)
):
    """Obtener rutas."""
    return await service.get_rutas(skip=skip, limit=limit)

@router.post("/rutas", response_model=Rutas)
async def create_ruta(
    ruta_data: dict,
    service: BitacoraService = Depends(get_bitacora_service)
):
    """Crear nueva ruta."""
    return await service.create_ruta(ruta_data)

@router.get("/rutas/{ruta_id}", response_model=Rutas)
async def get_ruta(
    ruta_id: UUID,
    service: BitacoraService = Depends(get_bitacora_service)
):
    """Obtener ruta por ID."""
    ruta = await service.get_ruta(ruta_id)
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    return ruta

# Endpoints de Tipos de Ruta
@router.get("/tipos-ruta", response_model=List[TiposRuta])
async def get_tipos_ruta(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: BitacoraService = Depends(get_bitacora_service)
):
    """Obtener tipos de ruta."""
    return await service.get_tipos_ruta(skip=skip, limit=limit)

@router.post("/tipos-ruta", response_model=TiposRuta)
async def create_tipo_ruta(
    tipo_data: dict,
    service: BitacoraService = Depends(get_bitacora_service)
):
    """Crear nuevo tipo de ruta."""
    return await service.create_tipo_ruta(tipo_data)

@router.get("/tipos-ruta/{tipo_id}", response_model=TiposRuta)
async def get_tipo_ruta(
    tipo_id: UUID,
    service: BitacoraService = Depends(get_bitacora_service)
):
    """Obtener tipo de ruta por ID."""
    tipo = await service.get_tipo_ruta(tipo_id)
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de ruta no encontrado")
    return tipo
