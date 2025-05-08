from crud.base import CRUDBase
from models.almacen import Almacen
from schemas.almacen import AlmacenCreate, AlmacenUpdate

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

class CRUDAlmacen(CRUDBase[Almacen, AlmacenCreate, AlmacenUpdate]):
    async def get_by_name(self, session: AsyncSession, *, name: str) -> Optional[Almacen]:
        """
        Retrieve an almacen by its name.

        Args:
            session: The database session.
            name: The name of the almacen to retrieve.

        Returns:
            The almacen instance if found, otherwise None.
        """
        result = await session.execute(select(Almacen).where(Almacen.nombre == name))
        return result.scalar_one_or_none()

almacen = CRUDAlmacen(Almacen)