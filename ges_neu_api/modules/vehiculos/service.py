from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ...core.exceptions import RecursoNoEncontradoError, DuplicadoError, VehiculoOcupadoError

from .models import (
    Vehiculos, TiposVehiculo, ConfiguracionesEje, 
    PosicionesNeumatico, RegistrosOdometro
)
from .schemas import (
    VehiculosCreate, VehiculosUpdate, VehiculosRead,
    TiposVehiculoCreate, TiposVehiculoUpdate, TiposVehiculoRead,
    ConfiguracionesEjeCreate, ConfiguracionesEjeUpdate, ConfiguracionesEjeRead,
    PosicionesNeumaticoCreate, PosicionesNeumaticoUpdate, PosicionesNeumaticoRead,
    RegistrosOdometroCreate, RegistrosOdometroUpdate, RegistrosOdometroRead
)


class VehiculosService:
    """Servicio para operaciones CRUD de vehículos"""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================================
    # VEHICULOS CRUD
    # ============================================================================
    
    async def get_vehiculo(self, vehiculo_id: UUID) -> Vehiculos:
        """Obtiene un vehículo por ID"""
        result = await self.db.execute(
            select(Vehiculos).where(Vehiculos.id == vehiculo_id)
        )
        db_obj = result.scalar_one_or_none()
        if not db_obj:
            raise RecursoNoEncontradoError("Vehículo", str(vehiculo_id))
        return db_obj
    
    async def get_multi_vehiculos(self, skip: int = 0, limit: int = 100) -> List[Vehiculos]:
        """Obtiene múltiples vehículos con paginación"""
        result = await self.db.execute(
            select(Vehiculos)
            .where(Vehiculos.activo == True)
            .offset(skip)
            .limit(limit)
            .order_by(Vehiculos.numero_economico)
        )
        return result.scalars().all()
    
    async def create_vehiculo(self, obj_in: VehiculosCreate) -> Vehiculos:
        """Crea un nuevo vehículo"""
        db_obj = Vehiculos(**obj_in.model_dump())
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update_vehiculo(self, vehiculo_id: UUID, obj_in: VehiculosUpdate) -> Optional[Vehiculos]:
        """Actualiza un vehículo existente"""
        db_obj = await self.get_vehiculo(vehiculo_id)
        
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def delete_vehiculo(self, vehiculo_id: UUID) -> Optional[UUID]:
        """Elimina un vehículo (soft delete)"""
        db_obj = await self.get_vehiculo(vehiculo_id)
        
        db_obj.activo = False
        await self.db.commit()
        return vehiculo_id

    # ============================================================================
    # TIPOS VEHICULO CRUD
    # ============================================================================
    
    async def get_tipo_vehiculo(self, tipo_id: UUID) -> Optional[TiposVehiculo]:
        """Obtiene un tipo de vehículo por ID"""
        result = await self.db.execute(
            select(TiposVehiculo).where(TiposVehiculo.id == tipo_id)
        )
        db_obj = result.scalar_one_or_none()
        if not db_obj:
            raise NotFoundException(resource=f"Tipo de vehículo con id {tipo_id}")
        return db_obj
    
    async def get_multi_tipos_vehiculo(self, skip: int = 0, limit: int = 100) -> List[TiposVehiculo]:
        """Obtiene múltiples tipos de vehículo con paginación"""
        result = await self.db.execute(
            select(TiposVehiculo)
            .where(TiposVehiculo.activo == True)
            .offset(skip)
            .limit(limit)
            .order_by(TiposVehiculo.nombre)
        )
        return result.scalars().all()
    
    async def create_tipo_vehiculo(self, obj_in: TiposVehiculoCreate) -> TiposVehiculo:
        """Crea un nuevo tipo de vehículo"""
        db_obj = TiposVehiculo(**obj_in.model_dump())
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update_tipo_vehiculo(self, tipo_id: UUID, obj_in: TiposVehiculoUpdate) -> Optional[TiposVehiculo]:
        """Actualiza un tipo de vehículo existente"""
        db_obj = await self.get_tipo_vehiculo(tipo_id)
        
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    # ============================================================================
    # CONFIGURACIONES EJE CRUD
    # ============================================================================
    
    async def get_configuracion_eje(self, config_id: UUID) -> Optional[ConfiguracionesEje]:
        """Obtiene una configuración de eje por ID"""
        result = await self.db.execute(
            select(ConfiguracionesEje).where(ConfiguracionesEje.id == config_id)
        )
        db_obj = result.scalar_one_or_none()
        if not db_obj:
            raise NotFoundException(resource=f"Configuración de eje con id {config_id}")
        return db_obj
    
    async def get_multi_configuraciones_eje(self, skip: int = 0, limit: int = 100) -> List[ConfiguracionesEje]:
        """Obtiene múltiples configuraciones de eje con paginación"""
        result = await self.db.execute(
            select(ConfiguracionesEje)
            .offset(skip)
            .limit(limit)
            .order_by(ConfiguracionesEje.tipo_vehiculo_id, ConfiguracionesEje.numero_eje)
        )
        return result.scalars().all()
    
    async def create_configuracion_eje(self, obj_in: ConfiguracionesEjeCreate) -> ConfiguracionesEje:
        """Crea una nueva configuración de eje"""
        db_obj = ConfiguracionesEje(**obj_in.model_dump())
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update_configuracion_eje(self, config_id: UUID, obj_in: ConfiguracionesEjeUpdate) -> Optional[ConfiguracionesEje]:
        """Actualiza una configuración de eje existente"""
        db_obj = await self.get_configuracion_eje(config_id)
        
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    # ============================================================================
    # POSICIONES NEUMATICO CRUD
    # ============================================================================
    
    async def get_posicion_neumatico(self, posicion_id: UUID) -> Optional[PosicionesNeumatico]:
        """Obtiene una posición de neumático por ID"""
        result = await self.db.execute(
            select(PosicionesNeumatico).where(PosicionesNeumatico.id == posicion_id)
        )
        db_obj = result.scalar_one_or_none()
        if not db_obj:
            raise NotFoundException(resource=f"Posición de neumático con id {posicion_id}")
        return db_obj
    
    async def get_multi_posiciones_neumatico(self, skip: int = 0, limit: int = 100) -> List[PosicionesNeumatico]:
        """Obtiene múltiples posiciones de neumático con paginación"""
        result = await self.db.execute(
            select(PosicionesNeumatico)
            .offset(skip)
            .limit(limit)
            .order_by(PosicionesNeumatico.configuracion_eje_id, PosicionesNeumatico.posicion_relativa)
        )
        return result.scalars().all()
    
    async def create_posicion_neumatico(self, obj_in: PosicionesNeumaticoCreate) -> PosicionesNeumatico:
        """Crea una nueva posición de neumático"""
        db_obj = PosicionesNeumatico(**obj_in.model_dump())
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update_posicion_neumatico(self, posicion_id: UUID, obj_in: PosicionesNeumaticoUpdate) -> Optional[PosicionesNeumatico]:
        """Actualiza una posición de neumático existente"""
        db_obj = await self.get_posicion_neumatico(posicion_id)
        
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    # ============================================================================
    # REGISTROS ODOMETRO CRUD
    # ============================================================================
    
    async def get_registro_odometro(self, registro_id: UUID) -> Optional[RegistrosOdometro]:
        """Obtiene un registro de odómetro por ID"""
        result = await self.db.execute(
            select(RegistrosOdometro).where(RegistrosOdometro.id == registro_id)
        )
        db_obj = result.scalar_one_or_none()
        if not db_obj:
            raise NotFoundException(resource=f"Registro de odómetro con id {registro_id}")
        return db_obj
    
    async def get_multi_registros_odometro(self, vehiculo_id: Optional[UUID] = None, skip: int = 0, limit: int = 100) -> List[RegistrosOdometro]:
        """Obtiene múltiples registros de odómetro con paginación"""
        query = select(RegistrosOdometro)
        
        if vehiculo_id:
            query = query.where(RegistrosOdometro.vehiculo_id == vehiculo_id)
        
        result = await self.db.execute(
            query
            .offset(skip)
            .limit(limit)
            .order_by(RegistrosOdometro.fecha_medicion.desc())
        )
        return result.scalars().all()
    
    async def create_registro_odometro(self, obj_in: RegistrosOdometroCreate) -> RegistrosOdometro:
        """Crea un nuevo registro de odómetro"""
        db_obj = RegistrosOdometro(**obj_in.model_dump())
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update_registro_odometro(self, registro_id: UUID, obj_in: RegistrosOdometroUpdate) -> Optional[RegistrosOdometro]:
        """Actualiza un registro de odómetro existente"""
        db_obj = await self.get_registro_odometro(registro_id)
        
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def delete_registro_odometro(self, registro_id: UUID) -> Optional[UUID]:
        """Elimina un registro de odómetro"""
        db_obj = await self.get_registro_odometro(registro_id)
        
        await self.db.delete(db_obj)
        await self.db.commit()
        return registro_id