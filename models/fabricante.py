# gesneu_api2/models/fabricante.py
import uuid
from pydantic import ConfigDict
import uuid
from datetime import datetime, timezone # Asegurarse que timezone esté importado si se usa
from typing import Optional, List, TYPE_CHECKING, ClassVar, Dict, Any

from sqlmodel import Field, SQLModel, Relationship
# Column, text, ForeignKey ya no son necesarios aquí para los campos de auditoría
# from sqlalchemy import Column, text, ForeignKey 

# --- Importar SQLModelTimestamp y la base del schema ---
from .common import SQLModelTimestamp # <--- CORREGIDO: Importar SQLModelTimestamp
# FabricanteNeumaticoBase de schemas ya es un SQLModel y se asume que define 'activo'.
from schemas.fabricante import FabricanteNeumaticoBase as FabricanteSchemaBase

# Para relaciones futuras
if TYPE_CHECKING:
    from .modelo import ModeloNeumatico
    from .usuario import Usuario # Si se definen relaciones explícitas para creador/actualizador

# Modelo de Tabla FabricanteNeumatico
# Hereda los campos de auditoría de SQLModelTimestamp
# y los campos base (incluyendo 'activo') de FabricanteSchemaBase.
class FabricanteNeumatico(SQLModelTimestamp, FabricanteSchemaBase, table=True):
    __tablename__ = "fabricantes_neumatico"

    # --- Clave Primaria ---
    # FabricanteSchemaBase no define 'id', así que lo definimos aquí.
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, index=True) # Añadido index=True

    # --- Campos heredados de FabricanteSchemaBase ---
    # nombre: str (unique, index, max_length=100)
    # codigo_abreviado: Optional[str] (unique, index, max_length=20)
    # pais_origen: Optional[str] (max_length=50)
    # activo: bool (default=True) -> Este campo se asume que viene de FabricanteSchemaBase.
    # Si FabricanteSchemaBase NO define 'activo', entonces deberías heredar también de '.common.EstadoItem'
    # class FabricanteNeumatico(SQLModelTimestamp, EstadoItem, FabricanteSchemaBase, table=True):

    # --- Campos heredados de SQLModelTimestamp ---
    # creado_en: datetime
    # actualizado_en: Optional[datetime]
    # creado_por: Optional[uuid.UUID] (ForeignKey a usuarios.id)
    # actualizado_por: Optional[uuid.UUID] (ForeignKey a usuarios.id)

    # --- Relaciones ---
    # Un fabricante puede tener muchos modelos de neumáticos
    modelos: List["ModeloNeumatico"] = Relationship(back_populates="fabricante")

    # Si quieres relacionar explícitamente con el usuario creador/actualizador más allá
    # de los campos UUID heredados de SQLModelTimestamp:
    # creador: Optional["Usuario"] = Relationship(
    #     sa_relationship_kwargs={'foreign_keys': '[FabricanteNeumatico.creado_por]'}
    # )
    # actualizador: Optional["Usuario"] = Relationship(
    #     sa_relationship_kwargs={'foreign_keys': '[FabricanteNeumatico.actualizado_por]'}
    # )

    # Configuración moderna usando model_config con ConfigDict
        

    model_config: ClassVar[Dict[str, Any]] = ConfigDict(
        

        from_attributes=True  # Reemplaza orm_mode=True
        

    )
