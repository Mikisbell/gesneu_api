# models/vehiculo.py (CORREGIDO Y COMPLETO)
import uuid
from datetime import date, datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, text, TIMESTAMP, ForeignKey

# Importar Base desde schemas (Asegúrate que la ruta sea correcta)
from schemas.vehiculo import VehiculoBase
from models.common import TimestampTZ, utcnow_aware

class Vehiculo(VehiculoBase, table=True): # Hereda de VehiculoBase
    __tablename__ = "vehiculos"
    __table_args__ = {'extend_existing': True} 

    # --- Campos específicos de la tabla (no en Base o con mapeo/default diferente) ---
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    fecha_baja: Optional[date] = Field(default=None)
    odometro_actual: Optional[int] = Field(default=None)
    fecha_ultimo_odometro: Optional[datetime] = Field(default=None, sa_column=Column(TimestampTZ, nullable=True)) # FIX: Mapeo Timestamp
    creado_en: datetime = Field(default_factory=utcnow_aware, sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()"))) # FIX: Mapeo Timestamp
    creado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TimestampTZ, nullable=True)) # FIX: Mapeo Timestamp
    actualizado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    # --- Fin campos específicos ---

    # Nota: Los campos heredados de VehiculoBase (tipo_vehiculo_id, numero_economico, placa, etc.)
    # son manejados automáticamente por SQLModel/SQLAlchemy.
