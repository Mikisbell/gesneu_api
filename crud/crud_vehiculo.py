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
        result = await session.execute(select(Vehiculo).where(Vehiculo.numero_economico == numero_economico))
        return result.scalar_one_or_none()

    async def get_by_placa(self, session: AsyncSession, *, placa: str) -> Optional[Vehiculo]:
        """
        Retrieve a vehicle by its license plate.

        Args:
            session: The database session.
            placa: The license plate of the vehicle to retrieve.

        Returns:
            The vehicle instance if found, otherwise None.
        """
        result = await session.execute(select(Vehiculo).where(Vehiculo.placa == placa))
        return result.scalar_one_or_none()

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
        statement = select(self.model).where(self.model.activo == True).offset(skip).limit(limit)
        result = await session.exec(statement)
        return result.scalars().all()

vehiculo = CRUDVehiculo(Vehiculo)