# gesneu_api2/schemas/common.py
from enum import Enum
from sqlmodel import SQLModel # Importar SQLModel si se usa para EstadoItem
from datetime import datetime # Importar datetime si se usa para EstadoItem
from typing import Optional # Importar Optional si se usa para EstadoItem

# --- Enums Existentes ---
class EstadoNeumaticoEnum(str, Enum):
    EN_STOCK = "EN_STOCK"
    INSTALADO = "INSTALADO"
    EN_REPARACION = "EN_REPARACION"
    EN_REENCAUCHE = "EN_REENCAUCHE"
    DESECHADO = "DESECHADO"
    EN_TRANSITO = "EN_TRANSITO"

class LadoVehiculoEnum(str, Enum):
    IZQUIERDO = "IZQUIERDO"
    DERECHO = "DERECHO"
    CENTRAL = "CENTRAL"
    INDETERMINADO = "INDETERMINADO"

class TipoEjeEnum(str, Enum):
    DIRECCION = "DIRECCION"
    TRACCION = "TRACCION"
    LIBRE = "LIBRE"
    PORTADOR = "PORTADOR"
    ARRASTRE = "ARRASTRE"

class TipoEventoNeumaticoEnum(str, Enum):
    COMPRA = "COMPRA"
    INSTALACION = "INSTALACION"
    DESMONTAJE = "DESMONTAJE"
    INSPECCION = "INSPECCION"
    ROTACION = "ROTACION"
    REPARACION_ENTRADA = "REPARACION_ENTRADA"
    REPARACION_SALIDA = "REPARACION_SALIDA"
    REENCAUCHE_ENTRADA = "REENCAUCHE_ENTRADA"
    REENCAUCHE_SALIDA = "REENCAUCHE_SALIDA"
    DESECHO = "DESECHO"
    AJUSTE_INVENTARIO = "AJUSTE_INVENTARIO"
    TRANSFERENCIA_UBICACION = "TRANSFERENCIA_UBICACION"

class TipoProveedorEnum(str, Enum):
    FABRICANTE = "FABRICANTE"
    DISTRIBUIDOR = "DISTRIBUIDOR"
    SERVICIO_REPARACION = "SERVICIO_REPARACION"
    SERVICIO_REENCAUCHE = "SERVICIO_REENCAUCHE"
    OTRO = "OTRO"

class TipoParametroEnum(str, Enum):
    PROFUNDIDAD_MINIMA = "PROFUNDIDAD_MINIMA"
    STOCK_MINIMO = "STOCK_MINIMO"
    STOCK_MAXIMO = "STOCK_MAXIMO"
    VIDA_UTIL_KM = "VIDA_UTIL_KM"
    VIDA_UTIL_ANIOS = "VIDA_UTIL_ANIOS"
    # Otros posibles parámetros...

# --- ENUM AÑADIDO ---
class TipoAlertaEnum(str, Enum):
    PRESION_BAJA = "PRESION_BAJA"
    PRESION_ALTA = "PRESION_ALTA"
    PROFUNDIDAD_BAJA = "PROFUNDIDAD_BAJA"
    DESGASTE_IRREGULAR = "DESGASTE_IRREGULAR"
    SOBRECARGA = "SOBRECARGA"
    FIN_VIDA_UTIL_ESTIMADO = "FIN_VIDA_UTIL_ESTIMADO"
    MANTENIMIENTO_PREVENTIVO = "MANTENIMIENTO_PREVENTIVO"
    LIMITE_REENCAUCHES_ALCANZADO = "LIMITE_REENCAUCHES_ALCANZADO"
    STOCK_MINIMO = "STOCK_MINIMO"
    STOCK_MAXIMO = "STOCK_MAXIMO"
    OTRO = "OTRO"
# --------------------

# --- Clases Base de Schemas Comunes (si las tienes aquí) ---
# Por ejemplo, si EstadoItem se define como un schema Pydantic/SQLModel aquí:
class EstadoItem(SQLModel): # O Pydantic BaseModel si no es SQLModel
    activo: bool = True
    fecha_baja: Optional[datetime] = None

    class Config:
        from_attributes = True # Para Pydantic V2
        # orm_mode = True # Para Pydantic V1
