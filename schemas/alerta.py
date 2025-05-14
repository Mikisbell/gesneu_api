# gesneu_api2/schemas/alerta.py
import uuid
from typing import Optional, ClassVar, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from .common import TipoAlertaEnum # Asegúrate que TipoAlertaEnum esté en schemas/common.py

# Properties to receive via API on creation
class AlertaBase(BaseModel):
    neumatico_id: Optional[uuid.UUID] = None
    vehiculo_id: Optional[uuid.UUID] = None
    modelo_id: Optional[uuid.UUID] = None
    almacen_id: Optional[uuid.UUID] = None
    parametro_id: Optional[uuid.UUID] = None
    # Usar Union[str, TipoAlertaEnum] para aceptar ambos tipos y evitar warnings
    tipo_alerta: Union[str, TipoAlertaEnum]
    descripcion: str = Field(...)
    nivel_severidad: str = Field(default='INFO')
    datos_contexto: Optional[Dict[str, Any]] = None
    # creado_en se manejará por defecto en el modelo con default_factory=datetime.utcnow
    # resuelta se manejará por defecto en el modelo como False

class AlertaCreate(AlertaBase):
    pass

# Properties to receive via API on update
# Generalmente para resolver una alerta o añadir detalles
class AlertaUpdate(BaseModel):
    resuelta: Optional[bool] = None
    notas_resolucion: Optional[str] = None
    gestionada_por: Optional[uuid.UUID] = None
    timestamp_gestion: Optional[datetime] = None

# Properties shared by models stored in DB
class AlertaInDBBase(AlertaBase):
    id: uuid.UUID
    resuelta: bool
    notas_resolucion: Optional[str] = None
    creado_en: datetime
    actualizado_en: Optional[datetime] = None
    creado_por: Optional[uuid.UUID] = None
    actualizado_por: Optional[uuid.UUID] = None
    
    model_config: ClassVar[Dict[str, Any]] = ConfigDict(
        from_attributes=True
    )

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
