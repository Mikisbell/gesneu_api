from enum import Enum

class LadoVehiculoEnum(str, Enum):
    IZQUIERDO = "IZQUIERDO"
    DERECHO = "DERECHO"
    CENTRO = "CENTRO"
    TRASERO = "TRASERO"
    DELANTERO = "DELANTERO"


class TipoEjeEnum(str, Enum):
    DELANTERO = "DELANTERO"
    TRASERO = "TRASERO"
    DIRECCIONAL = "DIRECCIONAL"
    MOTRIZ = "MOTRIZ"
    ARRASTRE = "ARRASTRE"
    ELEVABLE = "ELEVABLE"
