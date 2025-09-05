"""
Módulo de autenticación y gestión de usuarios.

Este módulo proporciona funcionalidades para la autenticación de usuarios,
gestión de roles y permisos, y operaciones relacionadas con la seguridad.
"""
from typing import List

# Importar componentes principales
from . import models
from . import schemas
from . import service
from . import router
from . import dependencies
from . import contracts

# Exportar modelos
from .models import (
    Permiso,
    Rol,
    Usuario,
    RolesPermisos,
    UsuariosRoles
)

# Exportar esquemas (SOLO los que existen en schemas.py)
from .schemas import (
    Token,
    TokenData,
    UserBase,
    UserCreate,
    UserRead,
    UserUpdate,
    UserInDBBase,
    UserLogin,
    UserChangePassword,
    UserWithToken,
    RoleBase,
    RoleCreate,
    RoleUpdate,
    RoleInDB,
    RoleWithPermissions,
    PermissionBase,
    PermissionInDB
)

# Exportar servicios
from .service import (
    AuthService,
    UserService,
    RoleService,
    PermissionService
)

# Exportar dependencias
from .dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_active_superuser,
    has_user_read,
    has_user_write,
    has_user_delete,
    has_role_read,
    has_role_write,
    has_role_delete,
    has_role_manage,
    has_permission_read,
    has_permission_write,
    has_permission_delete,
    get_auth_service,
    get_user_service,
    get_role_service,
    get_permission_service
)

# Lista de todos los componentes exportados
__all__ = [
    # Módulos
    'models',
    'schemas',
    'service',
    'router',
    'dependencies',
    'contracts',
    
    # Modelos
    'Permiso',
    'Rol',
    'Usuario',
    'RolesPermisos',
    'UsuariosRoles',
    
    # Esquemas
    'Token',
    'TokenData',
    'UserBase',
    'UserCreate',
    'UserRead',
    'UserUpdate',
    'UserInDBBase',
    'UserLogin',
    'UserChangePassword',
    'UserWithToken',
    'RoleBase',
    'RoleCreate',
    'RoleUpdate',
    'RoleInDB',
    'RoleWithPermissions',
    'PermissionBase',
    'PermissionInDB',
    
    # Servicios
    'AuthService',
    'UserService',
    'RoleService',
    'PermissionService',
    
    # Dependencias
    'get_current_user',
    'get_current_active_user',
    'get_current_active_superuser',
    'has_user_read',
    'has_user_write',
    'has_user_delete',
    'has_role_read',
    'has_role_write',
    'has_role_delete',
    'has_role_manage',
    'has_permission_read',
    'has_permission_write',
    'has_permission_delete',
    'get_auth_service',
    'get_user_service',
    'get_role_service',
    'get_permission_service'
]
