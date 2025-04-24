# models/proveedor.py
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, text, TIMESTAMP, ForeignKey

# Importar Base y Enum desde schemas
from schemas.proveedor import ProveedorBase
from schemas.common import TipoProveedorEnum # <-- Importar Enum
# Importar helpers (ajusta ruta si es necesario)
from models.common import TimestampTZ, utcnow_aware

class Proveedor(ProveedorBase, table=True): # <-- Hereda de Base
    __tablename__ = "proveedores"
    # No necesita extend_existing si ProveedorBase no tiene table=True

    # Campos específicos de tabla
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    # Hereda nombre, tipo, rfc, activo de Base

    # Añadir campos de contacto si estaban en tu tabla original
    contacto_principal: Optional[str] = Field(default=None)
    telefono: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=100)
    direccion: Optional[str] = Field(default=None)

    # Campos de auditoría con mapeo TZ
    creado_en: datetime = Field(default_factory=utcnow_aware, sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()")))
    creado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TimestampTZ, nullable=True))
    actualizado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")

class Proveedor(SQLModel, table=True):
    __tablename__ = "proveedores"
    # Formato limpio
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    nombre: str = Field(index=True)
    tipo: Optional[TipoProveedorEnum] = None
    rfc: Optional[str] = Field(default=None, max_length=13)
    activo: bool = True
    creado_en: datetime = Field(default_factory=utcnow_aware, sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()")))
    creado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TimestampTZ, nullable=True))
    actualizado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")