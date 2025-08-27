"""
Módulo de dependencias para el módulo de catálogos.
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session
from .service import CatalogosService


async def get_catalogos_service(
    db: Annotated[AsyncSession, Depends(get_session)]
) -> CatalogosService:
    """
    Proveedor de dependencias para el servicio de catálogos.
    """
    return CatalogosService(db)

# Tipo anotado para inyección de dependencias
CurrentCatalogosService = Annotated[CatalogosService, Depends(get_catalogos_service)]
