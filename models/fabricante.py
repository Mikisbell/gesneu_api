# models/fabricante.py (CORREGIDO)
import uuid
from datetime import datetime # Ya no se necesita timezone aquí si usamos utcnow_aware importado
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, text, ForeignKey # TIMESTAMP no se usa directamente aquí

# Importar Base desde schemas
from schemas.fabricante import FabricanteNeumaticoBase

# --- Importar Helpers desde common ---
from models.common import TimestampTZ, utcnow_aware # <-- Usar estos importados

class FabricanteNeumatico(FabricanteNeumaticoBase, table=True): # <-- Hereda de Base
    __tablename__ = "fabricantes_neumatico"
    # Añadido extend_existing por si acaso
    __table_args__ = {'extend_existing': True}

    # --- Campos específicos de la tabla ---
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    # Hereda: nombre, codigo_abreviado, pais_origen, sitio_web, activo

    # Campos de auditoría/timestamp usando helpers importados y mapeo explícito
    creado_en: datetime = Field(default_factory=utcnow_aware, sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()")))
    creado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TimestampTZ, nullable=True))
    actualizado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")

    # Relationships (si las añadimos después)
    # modelos: List["ModeloNeumatico"] = Relationship(back_populates="fabricante")

# --- La definición duplicada de FabricanteNeumatico ha sido ELIMINADA ---