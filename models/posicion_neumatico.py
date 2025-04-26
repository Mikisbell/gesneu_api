# models/posicion_neumatico.py
import uuid
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Enum as SAEnum
# --- Importar Enum desde common ---
from schemas.common import LadoVehiculoEnum

class PosicionNeumatico(SQLModel, table=True):
    __tablename__ = "posiciones_neumatico"
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    configuracion_eje_id: uuid.UUID = Field(foreign_key="configuraciones_eje.id")
    codigo_posicion: str = Field(max_length=10)
    lado: LadoVehiculoEnum = Field(sa_column=Column(SAEnum(LadoVehiculoEnum, name="lado_vehiculo_enum", create_type=False), nullable=False))
    posicion_relativa: int
    es_interna: bool = False
    es_direccion: bool = False
    es_traccion: bool = False