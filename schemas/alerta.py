# gesneu_api2/schemas/alerta.py
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from .common import TipoAlertaEnum # Asegúrate que TipoAlertaEnum esté en schemas/common.py

# Properties to receive via API on creation
class AlertaBase(BaseModel):
    neumatico_id: Optional[int] = None
    vehiculo_id: Optional[int] = None
    tipo_alerta: TipoAlertaEnum
    descripcion: str = Field(..., max_length=255)
    # fecha_creacion se manejará por defecto en el modelo con default_factory=datetime.utcnow
    # resuelta se manejará por defecto en el modelo como False

class AlertaCreate(AlertaBase):
    pass

# Properties to receive via API on update
# Generalmente para resolver una alerta o añadir detalles
class AlertaUpdate(BaseModel):
    resuelta: Optional[bool] = None
    # Puedes añadir otros campos que quieras que sean actualizables, por ejemplo:
    # descripcion: Optional[str] = Field(None, max_length=255)
    # Para la resolución, podrías querer registrar quién y cuándo:
    # usuario_resolucion_id: Optional[int] = None # Se asignaría en el endpoint/servicio
    # fecha_resolucion: Optional[datetime] = None # Se asignaría en el endpoint/servicio

# Properties shared by models stored in DB
class AlertaInDBBase(AlertaBase):
    id: int
    fecha_creacion: datetime
    resuelta: bool
    fecha_resolucion: Optional[datetime] = None
    usuario_resolucion_id: Optional[int] = None

    class Config:
        from_attributes = True # Para Pydantic V2 (reemplaza orm_mode)
        # orm_mode = True # Para Pydantic V1

# Additional properties to return via API
class Alerta(AlertaInDBBase):
    # Aquí podrías añadir schemas para las relaciones si las quieres devolver
    # Por ejemplo, si quieres devolver el objeto usuario que resolvió:
    # from .usuario import Usuario  # Importación circular potencial, manejar con cuidado o usar ForwardRef
    # usuario_que_resolvio: Optional[Usuario] = None
    pass

class AlertaResponse(Alerta):
    """Schema para la respuesta de una alerta individual, puede ser igual a Alerta."""
    pass

class AlertaConDetallesResponse(Alerta):
    """
    Schema extendido para respuestas de alerta que podrían incluir detalles de relaciones.
    Asegúrate de tener los schemas correspondientes si los descomentas.
    """
    # from .neumatico import Neumatico  # Ejemplo
    # from .vehiculo import Vehiculo    # Ejemplo
    # neumatico_asociado: Optional[Neumatico] = None
    # vehiculo_asociado: Optional[Vehiculo] = None
    pass
