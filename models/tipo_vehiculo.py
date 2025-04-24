# models/tipo_vehiculo.py (CORREGIDO Y COMPLETO)
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, text, TIMESTAMP, ForeignKey
from models.common import TimestampTZ, utcnow_aware

class TipoVehiculo(SQLModel, table=True): # No necesita heredar de Base si no creamos TipoVehiculoBase
    __tablename__ = "tipos_vehiculo"
    # No necesita extend_existing si no hereda de otra clase Base SQLModel aquí

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    nombre: str = Field(index=True)
    categoria_principal: Optional[str] = Field(default=None, max_length=50)
    ejes_standard: int = Field(default=2) # Default aquí
    activo: bool = Field(default=True) # Default aquí
    # --- Mapeo Timestamps ---
    creado_en: datetime = Field(default_factory=utcnow_aware, sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()")))
    creado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TimestampTZ, nullable=True))
    actualizado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")