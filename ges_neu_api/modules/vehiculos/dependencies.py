from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ges_neu_api.core.database import get_session
from .service import VehiculosService

def get_vehiculos_service(db: AsyncSession = Depends(get_session)) -> VehiculosService:
    return VehiculosService(db)

# Alias for clarity in router, pointing to the same service
get_tipos_vehiculo_service = get_vehiculos_service
get_configuraciones_eje_service = get_vehiculos_service
get_posiciones_neumatico_service = get_vehiculos_service
