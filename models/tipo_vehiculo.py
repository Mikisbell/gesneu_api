# gesneu_api2/models/tipo_vehiculo.py
from typing import Optional, List, TYPE_CHECKING, ClassVar, Dict, Any, Union
from sqlmodel import Field, SQLModel, Relationship
import uuid
# Se importarán SQLModelTimestamp y EstadoItem para heredar de ellos
from .common import SQLModelTimestamp, EstadoItem # <--- Importación corregida
from .configuracion_eje import ConfiguracionEje # Importación añadida
from .vehiculo import Vehiculo # Importación añadida
from pydantic import ConfigDict, field_serializer # Importar ConfigDict para la configuración moderna

class TipoVehiculoBase(SQLModel):
    nombre: str = Field(max_length=100, unique=True, index=True)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    # Los campos 'activo' y timestamps serán heredados

class TipoVehiculo(SQLModelTimestamp, EstadoItem, TipoVehiculoBase, table=True): # <--- Herencia actualizada
    __tablename__ = "tipos_vehiculo"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    
    # Relaciones
    # Un tipo de vehículo puede tener muchas configuraciones de eje
    configuraciones_eje: List["ConfiguracionEje"] = Relationship(back_populates="tipo_vehiculo")
    # Un tipo de vehículo puede estar asociado a muchos vehículos
    vehiculos: List["Vehiculo"] = Relationship(back_populates="tipo_vehiculo")
    
    # Configuración moderna usando model_config con ConfigDict
    model_config: ClassVar[Dict[str, Any]] = ConfigDict(
        from_attributes=True,  # Equivalente a from_attributes = True en la clase Config
        json_schema_extra={"example": {"id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"}}
    )
    
    # Serializador para manejar conversiones de UUID a string
    @field_serializer('id')
    def serialize_uuid(self, value: Optional[Union[uuid.UUID, str]]) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return str(value)
        return value
