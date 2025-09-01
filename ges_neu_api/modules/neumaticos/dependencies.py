"""
Dependencias para el módulo de neumáticos.
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from .service import NeumaticoService


async def get_neumatico_service(
    db: AsyncSession = Depends(get_db)
) -> NeumaticoService:
    """Proveedor de dependencia para el servicio de neumáticos."""
    return NeumaticoService(db)
