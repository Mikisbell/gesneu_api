from crud.base import CRUDBase
from models.tipo_vehiculo import TipoVehiculo
from schemas.tipo_vehiculo import TipoVehiculoCreate, TipoVehiculoUpdate

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

class CRUDTipoVehiculo(CRUDBase[TipoVehiculo, TipoVehiculoCreate, TipoVehiculoUpdate]):
    async def get_by_name(self, session: AsyncSession, *, name: str) -> Optional[TipoVehiculo]:
        """
        Retrieve a vehicle type by its name.

        Args:
            session: The database session.
            name: The name of the vehicle type to retrieve.

        Returns:
            The vehicle type instance if found, otherwise None.
        """
        try:
            # Usar session.exec() en lugar de session.execute()
            statement = select(TipoVehiculo).where(TipoVehiculo.nombre == name)
            result = await session.exec(statement)
            tipo_vehiculo = result.first()
            
            # Verificar que el tipo de vehículo existe y tiene un ID válido
            if tipo_vehiculo and hasattr(tipo_vehiculo, 'id'):
                return tipo_vehiculo
            return None
        except Exception as e:
            print(f"Error en get_by_name: {e}")
            # Fallback al método anterior si es necesario
            try:
                result = await session.execute(select(TipoVehiculo).where(TipoVehiculo.nombre == name))
                return result.scalar_one_or_none()
            except Exception as e2:
                print(f"Error en fallback get_by_name: {e2}")
                return None

    async def get_multi_active(
        self, session: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[TipoVehiculo]:
        """
        Retrieve multiple active vehicle types.

        Args:
            session: The database session.
            skip: The number of records to skip.
            limit: The maximum number of records to return.

        Returns:
            A list of active vehicle type instances.
        """
        statement = select(self.model).where(self.model.activo == True).offset(skip).limit(limit)
        result = await session.exec(statement)
        return result.scalars().all()

tipo_vehiculo = CRUDTipoVehiculo(TipoVehiculo)