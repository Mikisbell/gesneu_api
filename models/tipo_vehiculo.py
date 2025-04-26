# models/tipo_vehiculo.py
import uuid
from datetime import datetime
from typing import Optional # List si añades relaciones
from sqlmodel import Field, SQLModel, Relationship # Añadir Relationship
from sqlalchemy import Column, text, ForeignKey
# Importar helpers
from models.common import TimestampTZ, utcnow_aware

class TipoVehiculo(SQLModel, table=True):
    __tablename__ = "tipos_vehiculo"
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    nombre: str = Field(index=True)
    # Asegúrate de que estos campos coincidan con tu tabla real
    descripcion: Optional[str] = Field(default=None)
    categoria_principal: Optional[str] = Field(default=None, max_length=50)
    subtipo: Optional[str] = Field(default=None, max_length=50)
    ejes_standard: int = Field(default=2)
    activo: bool = Field(default=True)
    creado_en: datetime = Field(default_factory=utcnow_aware, sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()")))
    creado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TimestampTZ, nullable=True))
    actualizado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")