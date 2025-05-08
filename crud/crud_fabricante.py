from crud.base import CRUDBase
from models.fabricante import FabricanteNeumatico # Corregir la importación del modelo
from schemas.fabricante import FabricanteNeumaticoCreate, FabricanteNeumaticoUpdate # Corregir la importación de schemas

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

class CRUDFabricante(CRUDBase[FabricanteNeumatico, FabricanteNeumaticoCreate, FabricanteNeumaticoUpdate]):
    async def get_by_name(self, session: AsyncSession, *, name: str) -> Optional[FabricanteNeumatico]:
        """
        Retrieve a manufacturer by its name.

        Args:
            session: The database session.
            name: The name of the manufacturer to retrieve.

        Returns:
            The manufacturer instance if found, otherwise None.
        """
        result = await session.execute(select(FabricanteNeumatico).where(FabricanteNeumatico.nombre == name))
        return result.scalar_one_or_none()

    async def get_by_codigo_abreviado(self, session: AsyncSession, *, codigo_abreviado: str) -> Optional[FabricanteNeumatico]:
        """
        Retrieve a manufacturer by its abbreviated code.

        Args:
            session: The database session.
            codigo_abreviado: The abbreviated code of the manufacturer to retrieve.

        Returns:
            The manufacturer instance if found, otherwise None.
        """
        result = await session.execute(select(FabricanteNeumatico).where(FabricanteNeumatico.codigo_abreviado == codigo_abreviado))
        return result.scalar_one_or_none()

from typing import List

class CRUDFabricante(CRUDBase[FabricanteNeumatico, FabricanteNeumaticoCreate, FabricanteNeumaticoUpdate]):
    async def get_by_name(self, session: AsyncSession, *, name: str) -> Optional[FabricanteNeumatico]:
        """
        Retrieve a manufacturer by its name.

        Args:
            session: The database session.
            name: The name of the manufacturer to retrieve.

        Returns:
            The manufacturer instance if found, otherwise None.
        """
        result = await session.execute(select(FabricanteNeumatico).where(FabricanteNeumatico.nombre == name))
        return result.scalar_one_or_none()

    async def get_by_codigo_abreviado(self, session: AsyncSession, *, codigo_abreviado: str) -> Optional[FabricanteNeumatico]:
        """
        Retrieve a manufacturer by its abbreviated code.
        Args:
            session: The database session.
            codigo_abreviado: The abbreviated code of the manufacturer to retrieve.
        Returns:
            The manufacturer instance if found, otherwise None.
        """
        result = await session.execute(select(FabricanteNeumatico).where(FabricanteNeumatico.codigo_abreviado == codigo_abreviado))
        return result.scalar_one_or_none()

    async def get_multi_active(
        self, session: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[FabricanteNeumatico]:
        """
        Retrieve multiple active manufacturers.

        Args:
            session: The database session.
            skip: The number of records to skip.
            limit: The maximum number of records to return.

        Returns:
            A list of active manufacturer instances.
        """
        statement = select(self.model).where(self.model.activo == True).offset(skip).limit(limit)
        result = await session.exec(statement)
        return result.scalars().all()


fabricante = CRUDFabricante(FabricanteNeumatico)