"""
Módulo de dependencias para el módulo de autenticación.

Este módulo proporciona las dependencias inyectables para los routers y servicios
del módulo de autenticación.
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session
from .service import AuthService


async def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_session)]
) -> AuthService:
    """
    Proveedor de dependencias para el servicio de autenticación.
    
    Args:
        db: Sesión de base de datos inyectada por FastAPI
        
    Returns:
        Instancia del servicio de autenticación configurada
    """
    # Importación local para evitar dependencias circulares
    from .service import AuthService
    
    # Crear y retornar una instancia del servicio de autenticación
    return AuthService(db)


# Tipo anotado para inyección de dependencias
CurrentAuthService = Annotated[AuthService, Depends(get_auth_service)]
