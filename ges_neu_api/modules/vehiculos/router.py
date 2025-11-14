"""
Router para el módulo de vehículos - Completamente reconstruido y alineado con PostgreSQL
Sin rutas genéricas conflictivas
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from .models import Vehiculos, TiposVehiculo, ConfiguracionesEje, PosicionesNeumatico, RegistrosOdometro
from .schemas import (
    VehiculosRead, VehiculosCreate, VehiculosUpdate,
    TiposVehiculoRead, TiposVehiculoCreate, TiposVehiculoUpdate,
    ConfiguracionesEjeRead, ConfiguracionesEjeCreate, ConfiguracionesEjeUpdate,
    PosicionesNeumaticoRead, PosicionesNeumaticoCreate, PosicionesNeumaticoUpdate,
    RegistrosOdometroRead, RegistrosOdometroCreate, RegistrosOdometroUpdate
)
from .service import VehiculosService

router = APIRouter(tags=["vehiculos"])


def get_vehiculos_service(db: AsyncSession = Depends(get_session)) -> VehiculosService:
    """Dependencia para obtener el servicio de vehículos"""
    return VehiculosService(db)


# ============================================================================
# ENDPOINTS DE TIPOS DE VEHÍCULO
# ============================================================================

@router.get("/tipos-vehiculo/", response_model=List[TiposVehiculoRead])
@router.get("/tipos", response_model=List[TiposVehiculoRead])
async def get_tipos_vehiculo(
    skip: int = 0,
    limit: int = 100,
    service: VehiculosService = Depends(get_vehiculos_service)
):
    """Obtiene todos los tipos de vehículo activos"""
    return await service.get_multi_tipos_vehiculo(skip=skip, limit=limit)


@router.post("/tipos", response_model=TiposVehiculoRead, status_code=status.HTTP_201_CREATED)
async def create_tipo_vehiculo(
    tipo_in: TiposVehiculoCreate,
    service: VehiculosService = Depends(get_vehiculos_service)
):
    """Crea un nuevo tipo de vehículo"""
    return await service.create_tipo_vehiculo(tipo_in)


@router.get("/tipos/{tipo_id}", response_model=TiposVehiculoRead)
async def get_tipo_vehiculo(
    tipo_id: UUID,
    service: VehiculosService = Depends(get_vehiculos_service)
):
    """Obtiene un tipo de vehículo por ID"""
    return await service.get_tipo_vehiculo(tipo_id)


@router.put("/tipos/{tipo_id}", response_model=TiposVehiculoRead)
async def update_tipo_vehiculo(
    tipo_id: UUID,
    tipo_in: TiposVehiculoUpdate,
    service: VehiculosService = Depends(get_vehiculos_service)
):
    """Actualiza un tipo de vehículo"""
    return await service.update_tipo_vehiculo(tipo_id, tipo_in)


# ============================================================================
# ENDPOINTS DE CONFIGURACIONES DE EJE
# ============================================================================

@router.get("/configuraciones-eje", response_model=List[ConfiguracionesEjeRead])
async def get_configuraciones_eje(
    skip: int = 0,
    limit: int = 100,
    service: VehiculosService = Depends(get_vehiculos_service)
):
    """Obtiene todas las configuraciones de eje"""
    return await service.get_multi_configuraciones_eje(skip=skip, limit=limit)


@router.post("/configuraciones-eje", response_model=ConfiguracionesEjeRead, status_code=status.HTTP_201_CREATED)
async def create_configuracion_eje(
    config_in: ConfiguracionesEjeCreate,
    service: VehiculosService = Depends(get_vehiculos_service)
):
    """Crea una nueva configuración de eje"""
    return await service.create_configuracion_eje(config_in)


@router.get("/configuraciones-eje/{config_id}", response_model=ConfiguracionesEjeRead)
async def get_configuracion_eje(
    config_id: UUID,
    service: VehiculosService = Depends(get_vehiculos_service)
):
    """Obtiene una configuración de eje por ID"""
    return await service.get_configuracion_eje(config_id)


@router.put("/configuraciones-eje/{config_id}", response_model=ConfiguracionesEjeRead)
async def update_configuracion_eje(
    config_id: UUID,
    config_in: ConfiguracionesEjeUpdate,
    service: VehiculosService = Depends(get_vehiculos_service)
):
    """Actualiza una configuración de eje"""
    return await service.update_configuracion_eje(config_id, config_in)


# ============================================================================
# ENDPOINTS DE POSICIONES DE NEUMÁTICO
# ============================================================================

@router.get("/posiciones-neumatico", response_model=List[PosicionesNeumaticoRead])
async def get_posiciones_neumatico(
    skip: int = 0,
    limit: int = 100,
    service: VehiculosService = Depends(get_vehiculos_service)
):
    """Obtiene todas las posiciones de neumático"""
    return await service.get_multi_posiciones_neumatico(skip=skip, limit=limit)


@router.post("/posiciones-neumatico", response_model=PosicionesNeumaticoRead, status_code=status.HTTP_201_CREATED)
async def create_posicion_neumatico(
    posicion_in: PosicionesNeumaticoCreate,
    service: VehiculosService = Depends(get_vehiculos_service)
):
    """Crea una nueva posición de neumático"""
    return await service.create_posicion_neumatico(posicion_in)


@router.get("/posiciones-neumatico/{posicion_id}", response_model=PosicionesNeumaticoRead)
async def get_posicion_neumatico(
    posicion_id: UUID,
    service: VehiculosService = Depends(get_vehiculos_service)
):
    """Obtiene una posición de neumático por ID"""
    return await service.get_posicion_neumatico(posicion_id)


@router.put("/posiciones-neumatico/{posicion_id}", response_model=PosicionesNeumaticoRead)
async def update_posicion_neumatico(
    posicion_id: UUID,
    posicion_in: PosicionesNeumaticoUpdate,
    service: VehiculosService = Depends(get_vehiculos_service)
):
    """Actualiza una posición de neumático"""
    return await service.update_posicion_neumatico(posicion_id, posicion_in)


# ============================================================================
# ENDPOINTS PRINCIPALES DE VEHÍCULOS
# ============================================================================

@router.get("/", response_model=List[VehiculosRead])
async def get_vehiculos(
    skip: int = 0,
    limit: int = 100,
    service: VehiculosService = Depends(get_vehiculos_service)
):
    """Obtiene todos los vehículos activos"""
    return await service.get_multi_vehiculos(skip=skip, limit=limit)


@router.post("/", response_model=VehiculosRead, status_code=status.HTTP_201_CREATED)
async def create_vehiculo(
    vehiculo_in: VehiculosCreate,
    service: VehiculosService = Depends(get_vehiculos_service)
):
    """Crea un nuevo vehículo"""
    return await service.create_vehiculo(vehiculo_in)


@router.get("/vehiculo/{vehiculo_id}", response_model=VehiculosRead)
async def get_vehiculo(
    vehiculo_id: UUID,
    service: VehiculosService = Depends(get_vehiculos_service)
):
    """Obtiene un vehículo por ID"""
    return await service.get_vehiculo(vehiculo_id)


@router.put("/vehiculo/{vehiculo_id}", response_model=VehiculosRead)
async def update_vehiculo(
    vehiculo_id: UUID,
    vehiculo_in: VehiculosUpdate,
    service: VehiculosService = Depends(get_vehiculos_service)
):
    """Actualiza un vehículo"""
    return await service.update_vehiculo(vehiculo_id, vehiculo_in)


@router.delete("/vehiculo/{vehiculo_id}")
async def delete_vehiculo(
    vehiculo_id: UUID,
    service: VehiculosService = Depends(get_vehiculos_service)
):
    """Elimina un vehículo (soft delete)"""
    return await service.delete_vehiculo(vehiculo_id)


# ============================================================================
# ENDPOINTS DE REGISTROS DE ODÓMETRO
# ============================================================================

@router.get("/registros-odometro", response_model=List[RegistrosOdometroRead])
async def get_registros_odometro(
    skip: int = 0,
    limit: int = 100,
    service: VehiculosService = Depends(get_vehiculos_service)
):
    """Obtiene todos los registros de odómetro"""
    return await service.get_multi_registros_odometro(skip=skip, limit=limit)


@router.post("/registros-odometro", response_model=RegistrosOdometroRead, status_code=status.HTTP_201_CREATED)
async def create_registro_odometro(
    registro_in: RegistrosOdometroCreate,
    service: VehiculosService = Depends(get_vehiculos_service)
):
    """Crea un nuevo registro de odómetro"""
    return await service.create_registro_odometro(registro_in)


@router.get("/registros-odometro/{registro_id}", response_model=RegistrosOdometroRead)
async def get_registro_odometro(
    registro_id: UUID,
    service: VehiculosService = Depends(get_vehiculos_service)
):
    """Obtiene un registro de odómetro por ID"""
    return await service.get_registro_odometro(registro_id)


@router.put("/registros-odometro/{registro_id}", response_model=RegistrosOdometroRead)
async def update_registro_odometro(
    registro_id: UUID,
    registro_in: RegistrosOdometroUpdate,
    service: VehiculosService = Depends(get_vehiculos_service)
):
    """Actualiza un registro de odómetro"""
    return await service.update_registro_odometro(registro_id, registro_in)
