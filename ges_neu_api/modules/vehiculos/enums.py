from enum import Enum

class LadoVehiculoEnum(str, Enum):
    """Enum alineado exactamente con lado_vehiculo_enum de PostgreSQL"""
    IZQUIERDO = "IZQUIERDO"
    DERECHO = "DERECHO"
    CENTRAL = "CENTRAL"
    INDETERMINADO = "INDETERMINADO"


class TipoEjeEnum(str, Enum):
    DIRECCION = "DIRECCION"
    TRACCION = "TRACCION"
    ARRASTRE = "ARRASTRE"
    ELEVADOR = "ELEVADOR"
    RETRACTIL = "RETRACTIL"
    OTRO = "OTRO"
