from crud.base import CRUDBase
from models.vehiculo import Vehiculo
from schemas.vehiculo import VehiculoCreate, VehiculoUpdate

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

class CRUDVehiculo(CRUDBase[Vehiculo, VehiculoCreate, VehiculoUpdate]):
    async def get_by_numero_economico(self, session: AsyncSession, *, numero_economico: str) -> Optional[Vehiculo]:
        """
        Retrieve a vehicle by its economic number.

        Args:
            session: The database session.
            numero_economico: The economic number of the vehicle to retrieve.

        Returns:
            The vehicle instance if found, otherwise None.
        """
        try:
            # Usar session.exec() en lugar de session.execute()
            statement = select(Vehiculo).where(Vehiculo.numero_economico == numero_economico)
            result = await session.exec(statement)
            vehiculo = result.first()
            
            # Verificar que el vehículo existe y tiene un ID válido
            if vehiculo and hasattr(vehiculo, 'id'):
                return vehiculo
            return None
        except Exception as e:
            print(f"Error en get_by_numero_economico: {e}")
            # Fallback al método anterior si es necesario
            try:
                result = await session.execute(select(Vehiculo).where(Vehiculo.numero_economico == numero_economico))
                return result.scalar_one_or_none()
            except Exception as e2:
                print(f"Error en fallback get_by_numero_economico: {e2}")
                return None

    async def get_by_placa(self, session: AsyncSession, *, placa: str) -> Optional[Vehiculo]:
        """
        Retrieve a vehicle by its license plate.

        Args:
            session: The database session.
            placa: The license plate of the vehicle to retrieve.

        Returns:
            The vehicle instance if found, otherwise None.
        """
        try:
            # Usar session.exec() en lugar de session.execute()
            statement = select(Vehiculo).where(Vehiculo.placa == placa)
            result = await session.exec(statement)
            vehiculo = result.first()
            
            # Verificar que el vehículo existe y tiene un ID válido
            if vehiculo and hasattr(vehiculo, 'id'):
                return vehiculo
            return None
        except Exception as e:
            print(f"Error en get_by_placa: {e}")
            # Fallback al método anterior si es necesario
            try:
                result = await session.execute(select(Vehiculo).where(Vehiculo.placa == placa))
                return result.scalar_one_or_none()
            except Exception as e2:
                print(f"Error en fallback get_by_placa: {e2}")
                return None

    async def get_multi_active(
        self, session: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Vehiculo]:
        """
        Retrieve multiple active vehicles.

        Args:
            session: The database session.
            skip: The number of records to skip.
            limit: The maximum number of records to return.

        Returns:
            A list of active vehicle instances.
        """
        try:
            # Usar session.exec() con manejo adecuado del resultado
            statement = select(self.model).where(self.model.activo == True).offset(skip).limit(limit)
            result = await session.exec(statement)
            # Convertir explícitamente a lista y verificar que cada elemento tenga un ID válido
            vehiculos = []
            for item in result:
                if item and hasattr(item, 'id'):
                    vehiculos.append(item)
            return vehiculos
        except Exception as e:
            print(f"Error en get_multi_active: {e}")
            # Fallback al método anterior si es necesario
            try:
                statement = select(self.model).where(self.model.activo == True).offset(skip).limit(limit)
                result = await session.execute(statement)
                return list(result.scalars().all())
            except Exception as e2:
                print(f"Error en fallback get_multi_active: {e2}")
                return []

vehiculo = CRUDVehiculo(Vehiculo)