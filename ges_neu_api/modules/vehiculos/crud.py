from typing import Optional, List, Type, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlmodel import SQLModel

from .models import Vehiculos, TiposVehiculo, ConfiguracionesEje, PosicionesNeumatico, RegistrosOdometro
from .schemas import (
    VehiculoCreate, VehiculoUpdate, 
    TiposVehiculoCreate, TiposVehiculoUpdate, 
    ConfiguracionesEjeCreate, ConfiguracionesEjeUpdate, 
    PosicionesNeumaticoCreate, PosicionesNeumaticoUpdate, 
    RegistrosOdometroCreate, RegistrosOdometroUpdate
)

class CRUDVehiculo:
    def __init__(self, model: Type[SQLModel]):
        self.model = model

    async def get(self, db: AsyncSession, id: UUID) -> Optional[SQLModel]:
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()

    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[SQLModel]:
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, obj_in: SQLModel) -> SQLModel:
        db_obj = self.model.from_orm(obj_in) # Use from_orm for SQLModel
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, db_obj: SQLModel, obj_in: Dict[str, Any]) -> SQLModel:
        for key, value in obj_in.items():
            setattr(db_obj, key, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: UUID) -> Optional[UUID]:
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
            return id
        return None

# Instantiate CRUD operations for each model
crud_vehiculo = CRUDVehiculo(Vehiculos)
crud_tipos_vehiculo = CRUDVehiculo(TiposVehiculo)
crud_configuraciones_eje = CRUDVehiculo(ConfiguracionesEje)
crud_posiciones_neumatico = CRUDVehiculo(PosicionesNeumatico)
crud_registros_odometro = CRUDVehiculo(RegistrosOdometro)
