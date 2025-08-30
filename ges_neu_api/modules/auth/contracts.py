"""
Contratos (Interfaces) para el módulo de autenticación.

Este módulo define las interfaces que deben implementar los servicios
del módulo de autenticación, siguiendo el principio de inversión de dependencias.
"""
from typing import Protocol, Optional, Dict, Any, List, TypeVar
from datetime import datetime, timedelta
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

# Importaciones locales
from . import models

# Tipos genéricos
T = TypeVar('T', bound=BaseModel)

class AuthServiceContract(Protocol):
    """
    Contrato para el servicio de autenticación.
    
    Este contrato define las operaciones que debe implementar cualquier servicio
    de autenticación en la aplicación.
    """
    
    def __init__(self, db: AsyncSession) -> None:
        """
        Inicializa el servicio de autenticación con una sesión de base de datos.
        
        Args:
            db: Sesión asíncrona de SQLAlchemy
        """
        ...
    
    async def authenticate_user(self, username: str, password: str) -> Optional[models.Usuario]:
        """
        Autentica un usuario con nombre de usuario y contraseña.
        
        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano
            
        Returns:
            Instancia del modelo Usuario si la autenticación es exitosa, None en caso contrario
            
        Raises:
            UnauthorizedException: Si el usuario está inactivo
        """
        ...
    
    async def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Crea un token de acceso JWT.
        
        Args:
            data: Datos a incluir en el token (debe incluir al menos 'sub' para el subject)
            expires_delta: Tiempo de expiración del token. Si no se especifica,
                         se usará el valor por defecto de configuración.
            
        Returns:
            Token JWT codificado como string
            
        Raises:
            JWTError: Si hay un error al codificar el token
        """
        ...
    
    async def get_current_user(self, token: str) -> models.Usuario:
        """
        Obtiene el usuario actual a partir de un token JWT.
        
        Args:
            token: Token JWT codificado
            
        Returns:
            Instancia del modelo Usuario si el token es válido
            
        Raises:
            UnauthorizedException: Si el token es inválido o el usuario no existe
        """
        ...


class UserServiceContract(Protocol):
    """Contrato para el servicio de gestión de usuarios."""
    
    async def get_user_by_id(self, user_id: UUID) -> Optional["models.UsuarioRead"]:
        """
        Obtiene un usuario por su ID.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Información del usuario o None si no existe
        """
        ...
    
    async def get_user_by_username(self, username: str) -> Optional["models.UsuarioRead"]:
        """
        Obtiene un usuario por su nombre de usuario.
        
        Args:
            username: Nombre de usuario
            
        Returns:
            Información del usuario o None si no existe
        """
        ...
    
    async def create_user(self, user_data: "models.UsuarioCreate") -> "models.UsuarioRead":
        """
        Crea un nuevo usuario.
        
        Args:
            user_data: Datos del usuario a crear
            
        Returns:
            Usuario creado
            
        Raises:
            ValueError: Si el usuario ya existe
        """
        ...
    
    async def update_user(self, user_id: UUID, user_data: "models.UsuarioUpdate") -> Optional["models.UsuarioRead"]:
        """
        Actualiza un usuario existente.
        
        Args:
            user_id: ID del usuario a actualizar
            user_data: Datos a actualizar
            
        Returns:
            Usuario actualizado o None si no existe
        """
        ...
    
    async def delete_user(self, user_id: UUID) -> bool:
        """
        Elimina un usuario por su ID.
        
        Args:
            user_id: ID del usuario a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        ...


class RoleServiceContract(Protocol):
    """Contrato para el servicio de gestión de roles."""
    
    async def assign_role_to_user(self, user_id: UUID, role_id: UUID) -> bool:
        """
        Asigna un rol a un usuario.
        
        Args:
            user_id: ID del usuario
            role_id: ID del rol
            
        Returns:
            True si se asignó correctamente, False en caso contrario
        """
        ...
    
    async def revoke_role_from_user(self, user_id: UUID, role_id: UUID) -> bool:
        """
        Revoca un rol de un usuario.
        
        Args:
            user_id: ID del usuario
            role_id: ID del rol
            
        Returns:
            True si se revocó correctamente, False en caso contrario
        """
        ...


class PermissionServiceContract(Protocol):
    """Contrato para el servicio de gestión de permisos."""
    
    async def check_permission(self, user_id: UUID, resource: str, action: str) -> bool:
        """
        Verifica si un usuario tiene un permiso específico.
        
        Args:
            user_id: ID del usuario
            resource: Recurso al que se intenta acceder
            action: Acción que se intenta realizar
            
        Returns:
            True si el usuario tiene el permiso, False en caso contrario
        """
        ...
    
    async def get_user_permissions(self, user_id: UUID) -> List[Dict[str, Any]]:
        """
        Obtiene todos los permisos de un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Lista de permisos del usuario
        """
        ...