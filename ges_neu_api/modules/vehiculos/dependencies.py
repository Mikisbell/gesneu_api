from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ges_neu_api.core.database import get_session
from .service import VehiculosService

def get_vehiculos_service(db: AsyncSession = Depends(get_session)) -> VehiculosService:
    """Provee una instancia de VehiculosService."""
    return VehiculosService(db)
