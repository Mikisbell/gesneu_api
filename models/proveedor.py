# gesneu_api2/models/proveedor.py
import uuid
from pydantic import ConfigDict
from typing import Optional, List, TYPE_CHECKING, ClassVar, Dict, Any # Añadido ClassVar, Dict y Any

from sqlmodel import Field, SQLModel, Relationship # Añadido Relationship
# Column, text, ForeignKey ya no son necesarios aquí para los campos de auditoría
# from sqlalchemy import Column, text, ForeignKey

# --- Importar SQLModelTimestamp y la base del schema ---
from .common import SQLModelTimestamp # <--- CORREGIDO: Importar SQLModelTimestamp
# ProveedorBase de schemas ya es un SQLModel y define 'activo', 'nombre', 'ruc', 'tipo_proveedor'
from schemas.proveedor import ProveedorBase as ProveedorSchemaBase 
# TipoProveedorEnum es usado por ProveedorSchemaBase, así que su importación allí es suficiente.

# Para referencias adelantadas en relaciones
if TYPE_CHECKING:
    from .neumatico import Neumatico # Para la relación neumaticos_comprados
    from .usuario import Usuario # Si se definen relaciones explícitas para creador/actualizador


# Modelo de Tabla Proveedor
# Hereda los campos de auditoría de SQLModelTimestamp
# y los campos base (incluyendo 'activo') de ProveedorSchemaBase.
class Proveedor(SQLModelTimestamp, ProveedorSchemaBase, table=True):
    __tablename__ = "proveedores"

    # --- Clave Primaria ---
    # ProveedorSchemaBase no define 'id', así que lo definimos aquí.
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # --- Campos heredados de ProveedorSchemaBase ---
    # nombre: str (unique, index, max_length=100)
    # ruc: Optional[str] (unique, index, max_length=20)
    # tipo_proveedor: Optional[TipoProveedorEnum]
    # activo: bool (default=True)

    # --- Campos heredados de SQLModelTimestamp ---
    # creado_en: datetime
    # actualizado_en: Optional[datetime]
    # creado_por: Optional[uuid.UUID] (ForeignKey a usuarios.id)
    # actualizado_por: Optional[uuid.UUID] (ForeignKey a usuarios.id)

    # --- Campos adicionales específicos de la tabla 'proveedores' ---
    contacto_principal: Optional[str] = Field(default=None, max_length=150) # Especificar max_length
    telefono: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=100, index=True) # Considerar index si se busca por email
    direccion: Optional[str] = Field(default=None, max_length=255) # Especificar max_length

    # --- Relaciones ---
    # Un proveedor puede haber suministrado muchos neumáticos
    # Esta relación asume que Neumatico tiene un campo 'proveedor_compra_id' y una relación 'proveedor_compra'
    neumaticos_comprados: List["Neumatico"] = Relationship(back_populates="proveedor_compra")

    # Si quieres relacionar explícitamente con el usuario creador/actualizador más allá
    # de los campos UUID heredados de SQLModelTimestamp:
    # creador: Optional["Usuario"] = Relationship(
    #     sa_relationship_kwargs={'foreign_keys': '[Proveedor.creado_por]'}
    # )
    # actualizador: Optional["Usuario"] = Relationship(
    #     sa_relationship_kwargs={'foreign_keys': '[Proveedor.actualizado_por]'}
    # )

    # Configuración moderna usando model_config con ConfigDict
    model_config: ClassVar[Dict[str, Any]] = ConfigDict(
        from_attributes=True  # Reemplaza orm_mode=True
    )
