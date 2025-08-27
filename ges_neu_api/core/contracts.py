"""
Contratos (Protocols) para los servicios de la aplicación.

Este módulo define las interfaces que deben implementar los servicios
para garantizar la interoperabilidad entre módulos.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Protocol, runtime_checkable

from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.models.usuario import Usuario


@runtime_checkable
class AuthServiceContract(Protocol):
    """
    Contrato para el servicio de autenticación.
    
    Define las operaciones que debe implementar cualquier servicio de autenticación.
    """
    
    async def authenticate_user(
        self,
        username: str,
        password: str
    ) -> Optional[Usuario]:
        """
        Autentica un usuario por nombre de usuario y contraseña.
        
        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano
            
        Returns:
            Usuario autenticado o None si la autenticación falla
        """
        ...
    
    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Crea un token de acceso JWT.
        
        Args:
            data: Datos a incluir en el token
            expires_delta: Tiempo de expiración del token
            
        Returns:
            Token JWT codificado
        """
        ...
    
    async def get_current_user(
        self,
        token: str
    ) -> Usuario:
        """
        Obtiene el usuario actual a partir de un token JWT.
        
        Args:
            token: Token JWT
            
        Returns:
            Usuario autenticado
            
        Raises:
            HTTPException: Si el token es inválido o el usuario no existe
        """
        ...


@runtime_checkable
class UserServiceContract(Protocol):
    """
    Contrato para el servicio de usuarios.
    
    Define las operaciones CRUD para la gestión de usuarios.
    """
    
    async def get_user_by_id(
        self,
        user_id: int
    ) -> Optional[Usuario]:
        """Obtiene un usuario por su ID."""
        ...
    
    async def get_user_by_username(
        self,
        username: str
    ) -> Optional[Usuario]:
        """Obtiene un usuario por su nombre de usuario."""
        ...
    
    async def create_user(
        self,
        user_data: Dict[str, Any]
    ) -> Usuario:
        """Crea un nuevo usuario."""
        ...
    
    async def update_user(
        self,
        user_id: int,
        user_data: Dict[str, Any]
    ) -> Optional[Usuario]:
        """Actualiza un usuario existente."""
        ...
    
    async def delete_user(
        self,
        user_id: int
    ) -> bool:
        """Elimina un usuario."""
        ...


# Alias para compatibilidad con código existente
AuthService = AuthServiceContract
UserService = UserServiceContract
