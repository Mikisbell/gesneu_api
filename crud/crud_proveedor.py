from crud.base import CRUDBase
from models.proveedor import Proveedor
from schemas.proveedor import ProveedorCreate, ProveedorUpdate

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

class CRUDProveedor(CRUDBase[Proveedor, ProveedorCreate, ProveedorUpdate]):
    async def get_by_name(self, session: AsyncSession, *, name: str) -> Optional[Proveedor]:
        """
        Retrieve a provider by its name.

        Args:
            session: The database session.
            name: The name of the provider to retrieve.

        Returns:
            The provider instance if found, otherwise None.
        """
        result = await session.execute(select(Proveedor).where(Proveedor.nombre == name))
        return result.scalar_one_or_none()

    async def get_multi_active(
        self, session: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Proveedor]:
        """
        Retrieve multiple active providers.

        Args:
            session: The database session.
            skip: The number of records to skip.
            limit: The maximum number of records to return.

        Returns:
            A list of active provider instances.
        """
        statement = select(self.model).where(self.model.activo == True).offset(skip).limit(limit)
        result = await session.exec(statement)
        return result.scalars().all()

proveedor = CRUDProveedor(Proveedor)