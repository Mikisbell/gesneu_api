# models/configuracion_eje.py
import uuid
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Enum as SAEnum
# --- Importar Enum desde common ---
from schemas.common import TipoEjeEnum

class ConfiguracionEje(SQLModel, table=True):
    __tablename__ = "configuraciones_eje"
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    tipo_vehiculo_id: uuid.UUID = Field(foreign_key="tipos_vehiculo.id")
    numero_eje: int
    nombre_eje: str
    tipo_eje: TipoEjeEnum = Field(sa_column=Column(SAEnum(TipoEjeEnum, name="tipo_eje_enum", create_type=False), nullable=False))
    numero_posiciones: int
    posiciones_duales: bool = False
    neumaticos_por_posicion: int = 1