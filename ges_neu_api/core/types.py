"""Módulo para tipos compartidos y utilidades de tipado."""
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Generic, Any, Type
from uuid import UUID

if TYPE_CHECKING:
    from sqlmodel import SQLModel

# Tipos genéricos para relaciones
ModelType = TypeVar("ModelType", bound="SQLModel")

# Tipos para relaciones circulares comunes
if TYPE_CHECKING:
    from ..auth.models.usuario import Usuario
    from ..vehiculos.models import Vehiculo, TipoVehiculo, ConfiguracionEje, PosicionNeumatico
    from ..neumaticos.models import Neumatico, EventoNeumatico
    from ..catalogos.models import (
        ModeloNeumatico, ModeloVehiculo, 
        BitacoraOperacionNeumatico, Proveedor, Almacen
    )

# Re-exportar tipos comunes para facilitar las importaciones
__all__ = [
    'ModelType', 'UUID', 
    'Usuario', 'Vehiculo', 'TipoVehiculo', 'ConfiguracionEje', 'PosicionNeumatico',
    'Neumatico', 'EventoNeumatico', 'ModeloNeumatico', 'ModeloVehiculo',
    'BitacoraOperacionNeumatico', 'Proveedor', 'Almacen'
]
