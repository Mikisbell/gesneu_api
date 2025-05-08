# Importar todos los modelos para que SQLAlchemy los descubra
from .alerta import Alerta
from .almacen import Almacen
from .configuracion_eje import ConfiguracionEje
from .evento_neumatico import EventoNeumatico
from .fabricante import FabricanteNeumatico
from .modelo import ModeloNeumatico
from .motivo_desecho import MotivoDesecho
from .neumatico import Neumatico
from .parametro_inventario import ParametroInventario
from .posicion_neumatico import PosicionNeumatico
from .proveedor import Proveedor
from .registro_odometro import RegistroOdometro
from .tipo_vehiculo import TipoVehiculo
from .usuario import Usuario
from .vehiculo import Vehiculo

# Opcional: Importar también los schemas base si se usan directamente
# from .common import SQLModelTimestamp, EstadoItem, TipoEventoNeumaticoEnum, EstadoNeumaticoEnum, TipoAlertaEnum, TipoParametroEnum

# Esto asegura que todos los modelos estén registrados con SQLModel/SQLAlchemy
__all__ = [
    "Alerta",
    "Almacen",
    "ConfiguracionEje",
    "EventoNeumatico",
    "FabricanteNeumatico",
    "ModeloNeumatico",
    "MotivoDesecho",
    "Neumatico",
    "ParametroInventario",
    "PosicionNeumatico",
    "Proveedor",
    "RegistroOdometro",
    "TipoVehiculo",
    "Usuario",
    "Vehiculo",
    # "SQLModelTimestamp", # Si se descomenta la importación de common
    # "EstadoItem",
    # "TipoEventoNeumaticoEnum",
    # "EstadoNeumaticoEnum",
    # "TipoAlertaEnum",
    # "TipoParametroEnum",
]