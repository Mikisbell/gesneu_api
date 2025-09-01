"""
Módulos principales de la aplicación.

Este paquete contiene todos los submódulos que componen la aplicación,
cada uno con su propia funcionalidad específica.
"""
from typing import List

# Importar y exponer los submódulos
from . import auth
from . import catalogos
from . import neumaticos
from . import vehiculos
from . import inventario
from . import eventos
from . import garantias
from . import alertas
from . import bitacoras
from . import sistema

# Lista de módulos disponibles
__all__ = [
    'auth',
    'catalogos',
    'neumaticos',
    'vehiculos',
    'inventario',
    'eventos',
    'garantias',
    'alertas',
    'bitacoras',
    'sistema'
]

# Versión del paquete
__version__ = '1.0.0'

def get_available_modules() -> List[str]:
    """
    Devuelve una lista de los nombres de los módulos disponibles.
    
    Returns:
        List[str]: Lista de nombres de módulos.
    """
    return __all__