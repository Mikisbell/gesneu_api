# models/neumatico.py
import uuid
from datetime import date, datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, text, TIMESTAMP, ForeignKey
from sqlalchemy import Enum as SAEnum
# --- Importar Base y Enum desde schemas ---
from schemas.neumatico import NeumaticoBase
from schemas.common import EstadoNeumaticoEnum
# --- Importar Helpers desde common ---
from models.common import TimestampTZ, utcnow_aware

class Neumatico(NeumaticoBase, table=True):
    __tablename__ = "neumaticos"; __table_args__ = {'extend_existing': True}
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    # Hereda campos base
    # --- Campos específicos tabla con mapeo/defaults ---
    estado_actual: EstadoNeumaticoEnum = Field(default=EstadoNeumaticoEnum.EN_STOCK, sa_column=Column(SAEnum(EstadoNeumaticoEnum, name="estado_neumatico_enum", create_type=False), nullable=False, default=EstadoNeumaticoEnum.EN_STOCK))
    ubicacion_actual_vehiculo_id: Optional[uuid.UUID] = Field(default=None, foreign_key="vehiculos.id")
    ubicacion_actual_posicion_id: Optional[uuid.UUID] = Field(default=None, foreign_key="posiciones_neumatico.id")
    fecha_ultimo_evento: Optional[datetime] = Field(default=None, sa_column=Column(TimestampTZ, nullable=True))
    profundidad_inicial_mm: Optional[float] = Field(default=None) # Validado en Create
    kilometraje_acumulado: int = Field(default=0)
    reencauches_realizados: int = Field(default=0)
    vida_actual: int = Field(default=1)
    es_reencauchado: bool = Field(default=False)
    fecha_desecho: Optional[date] = Field(default=None)
    motivo_desecho_id: Optional[uuid.UUID] = Field(default=None, foreign_key="motivos_desecho.id")
    creado_en: datetime = Field(default_factory=utcnow_aware, sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()")))
    creado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TimestampTZ, nullable=True))
    actualizado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    # Relationship eliminada