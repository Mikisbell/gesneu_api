"""Módulo para la gestión de neumáticos."""

# Importaciones condicionales para evitar dependencias circulares
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Neumatico, EventoNeumatico
    from .types import TipoEventoNeumaticoEnum, EstadoNeumaticoEnum

# Solo expone los tipos necesarios para evitar importaciones circulares
__all__ = [
    'Neumatico',
    'EventoNeumatico',
    'TipoEventoNeumaticoEnum',
    'EstadoNeumaticoEnum'
]