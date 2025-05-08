# models/registro_odometro.py

import uuid
from datetime import datetime, timezone # Importar timezone
from typing import Optional, TYPE_CHECKING # Importar TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship # Importar Relationship
from sqlalchemy import Column, ForeignKey, text, DateTime # Importar DateTime
# Eliminar la importación de TimestampTZ y utcnow_aware
# from models.common import TimestampTZ, utcnow_aware

# Importación solo para type checking
if TYPE_CHECKING:
    from .vehiculo import Vehiculo # Importar Vehiculo

class RegistroOdometro(SQLModel, table=True):
    __tablename__ = "registros_odometro"
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    vehiculo_id: uuid.UUID = Field(foreign_key="vehiculos.id")
    odometro: int
    # Usar DateTime(timezone=True) para el tipo de columna
    fecha_medicion: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()")))
    fuente: Optional[str] = Field(default="manual", max_length=50)
    creado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    notas: Optional[str] = None

    # Definir la relación inversa con Vehiculo
    vehiculo: "Vehiculo" = Relationship(back_populates="registros_odometro")

