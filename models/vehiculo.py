# models/vehiculo.py
import uuid
from datetime import date, datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, text, ForeignKey
# Importar Base y Helpers
from schemas.vehiculo import VehiculoBase
from models.common import TimestampTZ, utcnow_aware
# Importar TipoVehiculo para que SQLAlchemy lo conozca al definir FK
from models.tipo_vehiculo import TipoVehiculo

class Vehiculo(VehiculoBase, table=True):
    __tablename__ = "vehiculos"; __table_args__ = {'extend_existing': True}
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    fecha_baja: Optional[date] = Field(default=None)
    odometro_actual: Optional[int] = Field(default=None)
    fecha_ultimo_odometro: Optional[datetime] = Field(default=None, sa_column=Column(TimestampTZ, nullable=True))
    creado_en: datetime = Field(default_factory=utcnow_aware, sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()")))
    creado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TimestampTZ, nullable=True))
    actualizado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")