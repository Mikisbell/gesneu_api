"""
Test-specific auth service using SQLite compatible models.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from ges_neu_api.core.exceptions import UnauthorizedException
from ges_neu_api.core.security import verify_password, create_access_token
from ges_neu_api.core.test_models import Usuario

logger = logging.getLogger(__name__)


class TestAuthService:
    """Test implementation of auth service using SQLite compatible models."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate_user(self, username: str, password: str) -> Optional[Usuario]:
        """Authenticate user with SQLite compatible models."""
        stmt = select(Usuario).where(
            or_(
                Usuario.username == username,
                Usuario.email == username
            )
        )
        result = await self.db.execute(stmt)
        user = result.scalars().first()
        
        if not user:
            logger.warning(f"Usuario no encontrado: {username}")
            raise UnauthorizedException(f"El usuario '{username}' no existe en el sistema")
            
        if not user.activo:
            logger.warning(f"Intento de inicio de sesión para usuario inactivo: {username}")
            raise UnauthorizedException("Inactive user")
            
        if not verify_password(password, user.password_hash):
            logger.warning(f"Contraseña incorrecta para el usuario: {username}")
            raise UnauthorizedException("La contraseña es incorrecta")
            
        user.ultimo_login = datetime.utcnow()
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        return create_access_token(data, expires_delta)

    async def get_current_user(self, token: str) -> Usuario:
        """Get current user from JWT token."""
        from ges_neu_api.core.security import decode_access_token
        
        try:
            payload = decode_access_token(token)
            user_id = payload.get("sub")
            if user_id is None:
                raise UnauthorizedException("Token inválido")
                
            stmt = select(Usuario).where(Usuario.id == UUID(user_id))
            result = await self.db.execute(stmt)
            user = result.scalars().first()
            
            if user is None:
                raise UnauthorizedException("Usuario no encontrado")
                
            if not user.activo:
                raise UnauthorizedException("Usuario inactivo")
                
            return user
            
        except Exception as e:
            logger.warning(f"Error al obtener usuario actual: {e}")
            raise UnauthorizedException("Token inválido o expirado")
