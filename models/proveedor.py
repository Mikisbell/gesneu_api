# models/proveedor.py

import uuid
from datetime import datetime, timezone # Asegúrate que timezone esté si usas utcnow_aware
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, text, TIMESTAMP, ForeignKey # Asegúrate que estos imports estén

# Importar Base y Enum desde schemas
from schemas.proveedor import ProveedorBase
from schemas.common import TipoProveedorEnum # Asegúrate que este Enum exista y se importe bien

# Importar helpers (ajusta ruta si es necesario)
from models.common import TimestampTZ, utcnow_aware

# ---------------------------------------------------------------------------
# QUÉDATE CON ESTA CLASE (La que hereda de ProveedorBase)
# ---------------------------------------------------------------------------
class Proveedor(ProveedorBase, table=True): # <-- Hereda de Base
    _tablename = "proveedores"
    # Si ProveedorBase NO tiene table=True, necesitas extenderla:
    # _table_args_ = {'extend_existing': True}

    # Campos específicos de tabla (ID y Auditoría)
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Los campos como nombre, tipo, rfc, activo, etc., se HEREDAN de ProveedorBase.

    # Añadir campos de contacto aquí si NO están en la Base pero sí en tu tabla
    contacto_principal: Optional[str] = Field(default=None)
    telefono: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=100)
    direccion: Optional[str] = Field(default=None)

    # Campos de auditoría con mapeo TZ
    creado_en: datetime = Field(
        default_factory=utcnow_aware,
        sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()"))
    )
    creado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(TimestampTZ, nullable=True)
    )
    actualizado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")

# ---------------------------------------------------------------------------
# ELIMINA ESTA SEGUNDA DEFINICIÓN COMPLETA DE ABAJO
# ---------------------------------------------------------------------------
# class Proveedor(SQLModel, table=True):  <-- ¡BORRA ESTO Y TODO SU CONTENIDO!
#     _tablename = "proveedores"
#     # Formato limpio
#     id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
#     nombre: str = Field(index=True)
#     tipo: Optional[TipoProveedorEnum] = None
#     rfc: Optional[str] = Field(default=None, max_length=13)
#     activo: bool = True
#     creado_en: datetime = Field(default_factory=utcnow_aware, sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()")))
#     creado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
#     actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TimestampTZ, nullable=True))
#     actualizado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
# ---------------------------------------------------------------------------