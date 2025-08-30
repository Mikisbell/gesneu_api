"""
Módulo para tipos compartidos en el módulo de neumáticos.
Esto ayuda a evitar importaciones circulares entre módulos.
"""
from typing import TYPE_CHECKING, TypeVar, Any, Dict, List, Optional
from enum import Enum

if TYPE_CHECKING:
    from sqlmodel import SQLModel
    from datetime import date, datetime
    from decimal import Decimal
    from uuid import UUID
    
    # Tipos de modelos
    from ..catalogos.models import (
        ModeloNeumatico, Proveedor, Almacen, MotivoDesecho,
        BitacoraOperacionNeumatico, GarantiasNeumaticos
    )
    from ..vehiculos.models import Vehiculo, PosicionNeumatico

# Tipo genérico para modelos SQLModel
ModelType = TypeVar("ModelType", bound="SQLModel")

# Enums
class TipoEventoNeumaticoEnum(str, Enum):
    """Enumeración para los tipos de eventos de neumáticos."""
    INSTALACION = "INSTALACION"
    DESMONTAJE = "DESMONTAJE"
    INSPECCION = "INSPECCION"
    ROTACION = "ROTACION"
    REPARACION = "REPARACION"
    REENCAUCHE_ENTRADA = "REENCAUCHE_ENTRADA"
    REENCAUCHE_SALIDA = "REENCAUCHE_SALIDA"
    ALMACENAMIENTO = "ALMACENAMIENTO"
    DESECHO = "DESECHO"
    AJUSTE = "AJUSTE"
    OTRO = "OTRO"
