# models/vehiculo.py
# ¡ESTE ARCHIVO NO NECESITÓ CAMBIOS PARA LOS WARNINGS DE FIELD!

import uuid
from datetime import date, datetime
from typing import Optional, TYPE_CHECKING # Añadir TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship # Añadir Relationship si usas relaciones
from sqlalchemy import Column, text, ForeignKey, String, Integer, Date, Boolean # Importar tipos necesarios

# Importar Base y Helpers
from schemas.vehiculo import VehiculoBase # Base viene de schemas
from models.common import TimestampTZ, utcnow_aware

# Importar para relaciones y Foreign Key
if TYPE_CHECKING:
    from .tipo_vehiculo import TipoVehiculo
    from .usuario import Usuario


class Vehiculo(VehiculoBase, table=True):
    __tablename__ = "vehiculos"
    # __table_args__ = {'extend_existing': True} # No es necesario si Base no tiene table=True

    # --- Campos específicos de tabla (ya estaban bien) ---
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    fecha_baja: Optional[date] = Field(default=None, sa_column=Column(Date)) # Especificar Date
    odometro_actual: Optional[int] = Field(default=None, sa_column=Column(Integer)) # Especificar Integer
    fecha_ultimo_odometro: Optional[datetime] = Field(
        default=None,
        sa_column=Column(TimestampTZ, nullable=True)
    )
    creado_en: datetime = Field(
        default_factory=utcnow_aware,
        sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()"))
    )
    # Usamos Optional[uuid.UUID] para claves foráneas opcionales
    creado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(TimestampTZ, nullable=True)
    )
    actualizado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")

    # --- Definir relaciones (si se usan) ---
    # tipo_vehiculo: Optional["TipoVehiculo"] = Relationship(back_populates="vehiculos")
    # creado_por_usuario: Optional["Usuario"] = Relationship(back_populates="vehiculos_creados", sa_relationship_kwargs={'foreign_keys': '[Vehiculo.creado_por]'})
    # actualizado_por_usuario: Optional["Usuario"] = Relationship(back_populates="vehiculos_actualizados", sa_relationship_kwargs={'foreign_keys': '[Vehiculo.actualizado_por]'})