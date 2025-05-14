# gesneu_api2/schemas/configuracion_eje.py
from typing import Optional, List, ClassVar, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from .common import EstadoItem # Asumo que tienes EstadoItem en schemas/common.py
# Si necesitas devolver información detallada de las posiciones o tipo de vehículo,
# necesitarás importar sus respectivos schemas. Por ejemplo:
# from .posicion_neumatico import PosicionNeumaticoResponse # O el schema que corresponda
# from .tipo_vehiculo import TipoVehiculo # O el schema que corresponda

# Properties to receive via API on creation
class ConfiguracionEjeBase(BaseModel):
    tipo_vehiculo_id: int
    descripcion: str = Field(..., max_length=100)
    numero_ejes: int = Field(..., gt=0) # Ejes debe ser mayor a 0
    numero_posiciones_por_eje: int = Field(..., gt=0) # Posiciones por eje debe ser mayor a 0
    # activo: bool = True # Se manejará a través de EstadoItem o por defecto en el modelo

class ConfiguracionEjeCreate(ConfiguracionEjeBase):
    pass

# Properties to receive via API on update, all optional
class ConfiguracionEjeUpdate(BaseModel):
    tipo_vehiculo_id: Optional[int] = None
    descripcion: Optional[str] = Field(None, max_length=100)
    numero_ejes: Optional[int] = Field(None, gt=0)
    numero_posiciones_por_eje: Optional[int] = Field(None, gt=0)
    activo: Optional[bool] = None # Para permitir activar/desactivar

# Properties shared by models stored in DB
class ConfiguracionEjeInDBBase(ConfiguracionEjeBase, EstadoItem):
    id: int
    # created_at: datetime # Si SQLModelTimestamp los añade y quieres exponerlos
    # updated_at: datetime # Si SQLModelTimestamp los añade y quieres exponerlos

    # Configuración moderna usando model_config con ConfigDict
        

    model_config: ClassVar[Dict[str, Any]] = ConfigDict(
        

        from_attributes=True  # Reemplaza orm_mode=True
        

    )

# Additional properties to return via API
class ConfiguracionEje(ConfiguracionEjeInDBBase):
    # Aquí puedes incluir los schemas de las relaciones si quieres que se devuelvan
    # tipo_vehiculo: Optional[TipoVehiculo] = None # Ejemplo
    # posiciones_neumatico: List[PosicionNeumaticoResponse] = [] # Ejemplo
    pass

class ConfiguracionEjeResponse(ConfiguracionEje):
    """Schema para la respuesta de una configuración de eje individual."""
    # Si quieres incluir relaciones por defecto en la respuesta, defínelas aquí.
    # Por ejemplo, para incluir el tipo de vehículo asociado:
    # from .tipo_vehiculo import TipoVehiculoResponse # Asegúrate de tener este schema
    # tipo_vehiculo: Optional[TipoVehiculoResponse] = None
    pass

class ConfiguracionEjeConDetallesResponse(ConfiguracionEje):
    """
    Schema extendido para respuestas de configuración de eje que podrían incluir detalles de relaciones.
    """
    # from .tipo_vehiculo import TipoVehiculoResponse
    # from .posicion_neumatico import PosicionNeumaticoResponse
    # tipo_vehiculo: Optional[TipoVehiculoResponse] = None
    # posiciones_neumatico: List[PosicionNeumaticoResponse] = []
    pass
