"""
Módulo de autenticación y autorización para GES_NEU API.

Este módulo proporciona funcionalidades de autenticación, autorización
y gestión de usuarios.
"""

# Import the router to make it available when importing from the package
from .router import router

# Import services and dependencies
from .service import (
    AuthService,
    UserService,
    get_current_user
)

from .dependencies import (
    CurrentAuthService,
    get_auth_service
)

# Import enums and types
from .models.types import (
    EstadoUsuarioEnum,
    TipoAutenticacionEnum
)

# Import schemas
from .schemas import (
    Token,
    UsuarioCreate,
    UsuarioRead,
    UsuarioUpdate,
    UsuarioInDB
)

# Lazy imports for models to avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .models.usuario import Usuario
    from .models.rol import Rol
    from .models.permiso import Permiso

# Define what gets imported with 'from auth import *'
__all__ = [
    # Router
    'router',
    
    # Services
    'AuthService',
    'UserService',
    'get_current_user',
    
    # Dependencies
    'CurrentAuthService',
    'get_auth_service',
    
    # Schemas
    'Token',
    'UsuarioCreate',
    'UsuarioRead',
    'UsuarioUpdate',
    'UsuarioInDB',
    
    # Enums
    'EstadoUsuarioEnum',
    'TipoAutenticacionEnum',
    
    # Models (for type hints)
    'Usuario',
    'Rol',
    'Permiso',
]