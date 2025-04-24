# models/configuracion_eje.py
import uuid
from typing import Optional # Aunque no se use ahora, buena práctica tenerlo
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Enum as SAEnum
# --- Importar Enum desde common ---
from schemas.common import TipoEjeEnum
from models.common import TimestampTZ, utcnow_aware

class ConfiguracionEje(SQLModel, table=True):
    __tablename__ = "configuraciones_eje"
    # No necesita extend_existing si no hereda de otra Base SQLModel
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    tipo_vehiculo_id: uuid.UUID = Field(foreign_key="tipos_vehiculo.id") # FK a TipoVehiculo (que está en models/tipo_vehiculo.py)
    numero_eje: int
    nombre_eje: str
    tipo_eje: TipoEjeEnum = Field( # Usa el Enum importado
        sa_column=Column(SAEnum(TipoEjeEnum, name="tipo_eje_enum", create_type=False), nullable=False)
    )
    numero_posiciones: int
    posiciones_duales: bool = False
    neumaticos_por_posicion: int = 1