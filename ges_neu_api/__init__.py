"""
Paquete principal de la API de Gestión de Neumáticos.

Este paquete contiene toda la lógica de negocio y la configuración principal
de la aplicación.
"""

# Asegurarse de que las importaciones funcionen correctamente
import os
import sys
from pathlib import Path

# Añadir el directorio raíz al path para que Python pueda encontrar los módulos
sys.path.insert(0, str(Path(__file__).parent.parent))
