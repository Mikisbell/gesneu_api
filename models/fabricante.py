# models/fabricante.py
# ¡ESTE ARCHIVO NO NECESITÓ CAMBIOS PARA LOS WARNINGS DE FIELD!

import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING # Añadir TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship # Añadir Relationship
from sqlalchemy import Column, text, ForeignKey # Añadir ForeignKey

# Importar Base desde schemas
from schemas.fabricante import FabricanteNeumaticoBase

# Importar helpers
from models.common import TimestampTZ, utcnow_aware

# Para relaciones futuras (uso correcto de TYPE_CHECKING)
if TYPE_CHECKING:
    from .modelo import ModeloNeumatico

class FabricanteNeumatico(FabricanteNeumaticoBase, table=True): # Hereda de Base
    __tablename__ = "fabricantes_neumatico"
    # __table_args__ = {'extend_existing': True} # Puedes quitarlo si Base no tiene table=True

    # Campos específicos de la tabla (estos ya estaban bien)
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    creado_en: datetime = Field(default_factory=utcnow_aware, sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()")))
    creado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TimestampTZ, nullable=True))
    actualizado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")

    # Relationship (si se reactiva después)
    # modelos: List["ModeloNeumatico"] = Relationship(back_populates="fabricante")