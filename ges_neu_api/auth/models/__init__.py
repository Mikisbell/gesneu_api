"""
Módulo de modelos de autenticación y autorización.
"""

# Importaciones estándar
from typing import TYPE_CHECKING, List, Optional

# Importaciones condicionales para evitar dependencias circulares
if not TYPE_CHECKING:
    from .usuario import Usuario
    from .rol import Rol
    from .permiso import Permiso
    from .rol_permiso import RolPermiso
    from .usuario_rol import UsuarioRol
    from .auditoria_rol_usuario import AuditoriaRolUsuario
    from .bitacora_operaciones import BitacoraOperaciones, TipoOperacionEnum, EstadoOperacionEnum
    from ges_neu_api.catalogos.models import Almacen, Proveedor
    from ges_neu_api.vehiculos.models import Vehiculo

# Hacemos que los modelos estén disponibles a nivel de paquete
__all__ = [
    'Usuario',
    'Rol',
    'Permiso',
    'RolPermiso',
    'UsuarioRol',
    'AuditoriaRolUsuario',
    'BitacoraOperaciones',
    'TipoOperacionEnum',
    'EstadoOperacionEnum',
    'setup_relationships'
]

def setup_relationships():
    """
    Configura las relaciones entre modelos para evitar importaciones circulares.
    Esta función debe ser llamada después de que todos los modelos hayan sido definidos.
    """
    # Importaciones locales para evitar dependencias circulares
    from .usuario import Usuario
    from .bitacora_operaciones import BitacoraOperaciones
    
    # Reconstruimos los modelos para manejar referencias circulares
    Usuario.model_rebuild()
    BitacoraOperaciones.model_rebuild()
    
    # Configuración de relaciones adicionales
    if hasattr(Usuario, 'model_fields'):
        Usuario.model_fields.update({
            'bitacora_operaciones': 'List[BitacoraOperaciones]',
            'bitacoras_creadas': 'List[BitacoraOperaciones]',
            'bitacoras_actualizadas': 'List[BitacoraOperaciones]',
            'roles_rel': 'List[UsuarioRol]',
            'asignaciones_roles': 'List[UsuarioRol]',
            'creado_por_usuario': 'Optional[Usuario]',
            'actualizado_por_usuario': 'Optional[Usuario]',
            'usuarios_creados': 'List[Usuario]',
            'usuarios_actualizados': 'List[Usuario]'
        })
    
    if hasattr(BitacoraOperaciones, 'model_fields'):
        BitacoraOperaciones.model_fields.update({
            'usuario': 'Optional[Usuario]',
            'almacen': 'Optional[Almacen]',
            'vehiculo': 'Optional[Vehiculo]',
            'proveedor': 'Optional[Proveedor]',
            'creado_por_usuario': 'Optional[Usuario]',
            'actualizado_por_usuario': 'Optional[Usuario]',
            'neumaticos_relacionados': 'List[BitacoraOperacionNeumatico]'
        })

# Configuramos las relaciones al importar el módulo
setup_relationships()
