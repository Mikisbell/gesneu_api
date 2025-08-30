"""
Dependencias del módulo de autenticación.

Este módulo proporciona las dependencias inyectables para los servicios
y componentes del módulo de autenticación.
"""
from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from ges_neu_api.core.config import settings
from ges_neu_api.core.database import get_session
from ges_neu_api.core.security import verify_password

from . import schemas
from .models import Usuario
from .service import AuthService, UserService, RoleService, PermissionService

# Esquema de autenticación OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


# Proveedores de servicios
async def get_auth_service(db: AsyncSession = Depends(get_session)) -> AuthService:
    """
    Proporciona una instancia de AuthService.
    
    Args:
        db: Sesión de base de datos inyectada
        
    Returns:
        Instancia de AuthService
    """
    return AuthService(db)


async def get_user_service(db: AsyncSession = Depends(get_session)) -> UserService:
    """
    Proporciona una instancia de UserService.
    
    Args:
        db: Sesión de base de datos inyectada
        
    Returns:
        Instancia de UserService
    """
    return UserService(db)


async def get_role_service(db: AsyncSession = Depends(get_session)) -> RoleService:
    """
    Proporciona una instancia de RoleService.
    
    Args:
        db: Sesión de base de datos inyectada
        
    Returns:
        Instancia de RoleService
    """
    return RoleService(db)


async def get_permission_service(db: AsyncSession = Depends(get_session)) -> PermissionService:
    """
    Proporciona una instancia de PermissionService.
    
    Args:
        db: Sesión de base de datos inyectada
        
    Returns:
        Instancia de PermissionService
    """
    return PermissionService(db)


# Dependencias de autenticación
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service)
) -> schemas.UserRead:
    """
    Obtiene el usuario actual a partir del token JWT.
    
    Args:
        token: Token JWT
        auth_service: Servicio de autenticación inyectado
        user_service: Servicio de usuarios inyectado
        
    Returns:
        Usuario autenticado
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verificar el token y obtener el usuario
        user = await auth_service.get_current_user(token)
        if not user:
            raise credentials_exception
            
        # Obtener los datos completos del usuario
        db_user = await user_service.get_user_by_id(user.id)
        if not db_user:
            raise credentials_exception
            
        return db_user
        
    except (jwt.JWTError, ValidationError):
        raise credentials_exception


async def get_current_active_user(
    current_user: schemas.UserRead = Depends(get_current_user),
) -> schemas.UserRead:
    """
    Verifica que el usuario actual esté activo.
    
    Args:
        current_user: Usuario actual inyectado
        
    Returns:
        Usuario activo
        
    Raises:
        HTTPException: Si el usuario está inactivo
    """
    if not current_user.activo:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user


def get_current_active_superuser(
    current_user: schemas.UserRead = Depends(get_current_user),
) -> schemas.UserRead:
    """
    Verifica que el usuario actual sea un superusuario.
    
    Args:
        current_user: Usuario actual inyectado
        
    Returns:
        Usuario superusuario
        
    Raises:
        HTTPException: Si el usuario no es superusuario
    """
    if not current_user.es_superusuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene suficientes privilegios"
        )
    return current_user


# Dependencias de permisos
class PermissionChecker:
    """
    Verificador de permisos para rutas protegidas.
    
    Esta clase se utiliza como dependencia en los endpoints para verificar
    que el usuario tenga los permisos necesarios.
    """
    
    def __init__(self, resource: str, action: str):
        """
        Inicializa el verificador de permisos.
        
        Args:
            resource: Recurso al que se intenta acceder
            action: Acción que se intenta realizar
        """
        self.resource = resource
        self.action = action
    
    async def __call__(
        self,
        current_user: schemas.UserRead = Depends(get_current_user),
        permission_service: PermissionService = Depends(get_permission_service)
    ) -> schemas.UserRead:
        """
        Verifica si el usuario tiene el permiso requerido.
        
        Args:
            current_user: Usuario actual inyectado
            permission_service: Servicio de permisos inyectado
            
        Returns:
            Usuario autenticado
            
        Raises:
            HTTPException: Si el usuario no tiene el permiso requerido
        """
        # Los superusuarios tienen acceso a todo
        if current_user.es_superusuario:
            return current_user
            
        # Verificar si el usuario tiene el permiso
        has_permission = await permission_service.check_permission(
            user_id=current_user.id,
            resource=self.resource,
            action=self.action
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tiene permiso para realizar esta acción: {self.action} en {self.resource}"
            )
            
        return current_user


# Dependencias de permisos para roles
has_role_read = PermissionChecker(resource="roles", action="read")
has_role_write = PermissionChecker(resource="roles", action="write")
has_role_delete = PermissionChecker(resource="roles", action="delete")
has_role_manage = PermissionChecker(resource="roles", action="manage")

# Dependencias de permisos para usuarios
has_user_read = PermissionChecker(resource="users", action="read")
has_user_write = PermissionChecker(resource="users", action="write")
has_user_delete = PermissionChecker(resource="users", action="delete")

# Dependencias de permisos para permisos
has_permission_read = PermissionChecker(resource="permissions", action="read")
has_permission_write = PermissionChecker(resource="permissions", action="write")
has_permission_delete = PermissionChecker(resource="permissions", action="delete")
