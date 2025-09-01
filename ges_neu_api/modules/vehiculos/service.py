from typing import Optional, List, Type, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from .contracts import VehiculosServiceContract
from .crud import crud_vehiculo, crud_tipos_vehiculo, crud_configuraciones_eje, crud_posiciones_neumatico, crud_registros_odometro
from .models import Vehiculos, TiposVehiculo, ConfiguracionesEje, PosicionesNeumatico, RegistrosOdometro
from .schemas import (
    VehiculoCreate, VehiculoUpdate, 
    TiposVehiculoCreate, TiposVehiculoUpdate, 
    ConfiguracionesEjeCreate, ConfiguracionesEjeUpdate, 
    PosicionesNeumaticoCreate, PosicionesNeumaticoUpdate, 
    RegistrosOdometroCreate, RegistrosOdometroUpdate
)

class VehiculosService(VehiculosServiceContract):
    def __init__(self, db: AsyncSession):
        self.db = db

    # Vehiculos CRUD
    async def get_vehiculo(self, vehiculo_id: UUID) -> Optional[Vehiculos]:
        return await crud_vehiculo.get(self.db, vehiculo_id)

    async def get_multi_vehiculos(self, skip: int = 0, limit: int = 100) -> List[Vehiculos]:
        return await crud_vehiculo.get_multi(self.db, skip=skip, limit=limit)

    async def create_vehiculo(self, obj_in: VehiculoCreate) -> Vehiculos:
        return await crud_vehiculo.create(self.db, obj_in)

    async def update_vehiculo(self, vehiculo_id: UUID, obj_in: VehiculoUpdate) -> Optional[Vehiculos]:
        db_obj = await crud_vehiculo.get(self.db, vehiculo_id)
        if not db_obj: return None
        return await crud_vehiculo.update(self.db, db_obj, obj_in.dict(exclude_unset=True))

    async def delete_vehiculo(self, vehiculo_id: UUID) -> Optional[UUID]:
        return await crud_vehiculo.delete(self.db, vehiculo_id)

    # TiposVehiculo CRUD
    async def get_tipo_vehiculo(self, tipo_id: UUID) -> Optional[TiposVehiculo]:
        return await crud_tipos_vehiculo.get(self.db, tipo_id)

    async def get_multi_tipos_vehiculo(self, skip: int = 0, limit: int = 100) -> List[TiposVehiculo]:
        return await crud_tipos_vehiculo.get_multi(self.db, skip=skip, limit=limit)

    async def create_tipo_vehiculo(self, obj_in: TiposVehiculoCreate) -> TiposVehiculo:
        return await crud_tipos_vehiculo.create(self.db, obj_in)

    async def update_tipo_vehiculo(self, tipo_id: UUID, obj_in: TiposVehiculoUpdate) -> Optional[TiposVehiculo]:
        db_obj = await crud_tipos_vehiculo.get(self.db, tipo_id)
        if not db_obj: return None
        return await crud_tipos_vehiculo.update(self.db, db_obj, obj_in.dict(exclude_unset=True))

    async def delete_tipo_vehiculo(self, tipo_id: UUID) -> Optional[UUID]:
        return await crud_tipos_vehiculo.delete(self.db, tipo_id)

    # ConfiguracionesEje CRUD
    async def get_configuracion_eje(self, config_id: UUID) -> Optional[ConfiguracionesEje]:
        return await crud_configuraciones_eje.get(self.db, config_id)

    async def get_multi_configuraciones_eje(self, skip: int = 0, limit: int = 100) -> List[ConfiguracionesEje]:
        return await crud_configuraciones_eje.get_multi(self.db, skip=skip, limit=limit)

    async def create_configuracion_eje(self, obj_in: ConfiguracionesEjeCreate) -> ConfiguracionesEje:
        return await crud_configuraciones_eje.create(self.db, obj_in)

    async def update_configuracion_eje(self, config_id: UUID, obj_in: ConfiguracionesEjeUpdate) -> Optional[ConfiguracionesEje]:
        db_obj = await crud_configuraciones_eje.get(self.db, config_id)
        if not db_obj: return None
        return await crud_configuraciones_eje.update(self.db, db_obj, obj_in.dict(exclude_unset=True))

    async def delete_configuracion_eje(self, config_id: UUID) -> Optional[UUID]:
        return await crud_configuraciones_eje.delete(self.db, config_id)

    # PosicionesNeumatico CRUD
    async def get_posicion_neumatico(self, posicion_id: UUID) -> Optional[PosicionesNeumatico]:
        return await crud_posiciones_neumatico.get(self.db, posicion_id)

    async def get_multi_posiciones_neumatico(self, skip: int = 0, limit: int = 100) -> List[PosicionesNeumatico]:
        return await crud_posiciones_neumatico.get_multi(self.db, skip=skip, limit=limit)

    async def create_posicion_neumatico(self, obj_in: PosicionesNeumaticoCreate) -> PosicionesNeumatico:
        return await crud_posiciones_neumatico.create(self.db, obj_in)

    async def update_posicion_neumatico(self, posicion_id: UUID, obj_in: PosicionesNeumaticoUpdate) -> Optional[PosicionesNeumatico]:
        db_obj = await crud_posiciones_neumatico.get(self.db, posicion_id)
        if not db_obj: return None
        return await crud_posiciones_neumatico.update(self.db, db_obj, obj_in.dict(exclude_unset=True))

    async def delete_posicion_neumatico(self, posicion_id: UUID) -> Optional[UUID]:
        return await crud_posiciones_neumatico.delete(self.db, posicion_id)

    # RegistrosOdometro CRUD
    async def get_registro_odometro(self, registro_id: UUID) -> Optional[RegistrosOdometro]:
        return await crud_registros_odometro.get(self.db, registro_id)

    async def get_multi_registros_odometro(self, skip: int = 0, limit: int = 100) -> List[RegistrosOdometro]:
        return await crud_registros_odometro.get_multi(self.db, skip=skip, limit=limit)

    async def create_registro_odometro(self, obj_in: RegistrosOdometroCreate) -> RegistrosOdometro:
        return await crud_registros_odometro.create(self.db, obj_in)

    async def update_registro_odometro(self, registro_id: UUID, obj_in: RegistrosOdometroUpdate) -> Optional[RegistrosOdometro]:
        db_obj = await crud_registros_odometro.get(self.db, registro_id)
        if not db_obj: return None
        return await crud_registros_odometro.update(self.db, db_obj, obj_in.dict(exclude_unset=True))

    async def delete_registro_odometro(self, registro_id: UUID) -> Optional[UUID]:
        return await crud_registros_odometro.delete(self.db, registro_id)