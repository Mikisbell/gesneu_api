"""
Dependencias para el módulo de bitácoras.
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from .service import BitacoraService


async def get_bitacora_service(
    db: AsyncSession = Depends(get_session)
) -> BitacoraService:
    """Proveedor de dependencia para el servicio de bitácoras."""
    return BitacoraService(db)
