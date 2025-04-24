# models/posicion_neumatico.py
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.types import Enum as SAEnum
from typing import Optional
import uuid
from schemas.common import LadoVehiculoEnum
from models.common import TimestampTZ, utcnow_aware

class PosicionNeumatico(SQLModel, table=True):
    __tablename__ = "posiciones_neumatico"
    # Formato limpio
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    configuracion_eje_id: uuid.UUID = Field(foreign_key="configuraciones_eje.id")
    codigo_posicion: str = Field(max_length=10)
    lado: LadoVehiculoEnum = Field(sa_column=Column(SAEnum(LadoVehiculoEnum, name="lado_vehiculo_enum", create_type=False), nullable=False))
    posicion_relativa: int
    es_interna: bool = False
    es_direccion: bool = False
    es_traccion: bool = False
