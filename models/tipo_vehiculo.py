# gesneu_api2/models/tipo_vehiculo.py
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
import uuid
# Se importarán SQLModelTimestamp y EstadoItem para heredar de ellos
from .common import SQLModelTimestamp, EstadoItem # <--- Importación corregida
from .configuracion_eje import ConfiguracionEje # Importación añadida
from .vehiculo import Vehiculo # Importación añadida

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

    class Config:
        from_attributes = True # Para Pydantic V2 (reemplaza orm_mode)
        # orm_mode = True # Para Pydantic V1
