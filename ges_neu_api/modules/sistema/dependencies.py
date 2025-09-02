"""
Dependencias para el módulo de sistema.
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from .service import SistemaService


async def get_sistema_service(
    db: AsyncSession = Depends(get_session)
) -> SistemaService:
    """Proveedor de dependencia para el servicio de sistema."""
    return SistemaService(db)
