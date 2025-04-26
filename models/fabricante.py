# models/fabricante.py
import uuid
from datetime import datetime
from typing import Optional, List # Añadir List si se reactivan relaciones
from sqlmodel import Field, SQLModel, Relationship # Añadir Relationship
from sqlalchemy import Column, text, ForeignKey # Añadir ForeignKey
# Importar Base desde schemas
from schemas.fabricante import FabricanteNeumaticoBase
# Importar helpers
from models.common import TimestampTZ, utcnow_aware
# Para relaciones futuras
# if TYPE_CHECKING:
#     from .modelo import ModeloNeumatico

class FabricanteNeumatico(FabricanteNeumaticoBase, table=True): # Hereda de Base
    __tablename__ = "fabricantes_neumatico"
    # extend_existing no es estrictamente necesario si Base no tiene table=True
    # pero lo añadimos por consistencia con otros modelos heredados
    __table_args__ = {'extend_existing': True}

    # Campos específicos de la tabla
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    creado_en: datetime = Field(default_factory=utcnow_aware, sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()")))
    creado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TimestampTZ, nullable=True))
    actualizado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")

    # Relationship (si se reactiva después)
    # modelos: List["ModeloNeumatico"] = Relationship(back_populates="fabricante")