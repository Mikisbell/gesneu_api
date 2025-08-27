"""
Módulo principal de modelos de autenticación.

Este archivo importa todos los modelos del paquete models para mantener la compatibilidad
con el código existente. Se recomienda importar los modelos directamente desde sus módulos.
"""

# Importar todos los modelos para mantener la compatibilidad
from .models.usuario import Usuario
from .models.rol import Rol
from .models.permiso import Permiso
from .models.rol_permiso import RolPermiso
from .models.usuario_rol import UsuarioRol

# Hacer que los modelos estén disponibles en el nivel del paquete
__all__ = [
    'Usuario',
    'Rol',
    'Permiso',
    'RolPermiso',
    'UsuarioRol',
]
