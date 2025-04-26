# models/registro_odometro.py

import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, ForeignKey, text
from models.common import TimestampTZ, utcnow_aware

class RegistroOdometro(SQLModel, table=True):
    __tablename__ = "registros_odometro"
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    vehiculo_id: uuid.UUID = Field(foreign_key="vehiculos.id")
    odometro: int
    fecha_medicion: datetime = Field(default_factory=utcnow_aware, sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()")))
    fuente: Optional[str] = Field(default="manual", max_length=50)
    creado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    notas: Optional[str] = None

