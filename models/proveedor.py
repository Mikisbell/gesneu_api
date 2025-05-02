# models/proveedor.py

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel
# --- Asegúrate de importar Column, text, TIMESTAMP, ForeignKey ---
from sqlalchemy import Column, text, TIMESTAMP, ForeignKey

# Importar Base y Enum desde schemas
from schemas.proveedor import ProveedorBase
from schemas.common import TipoProveedorEnum # Asegúrate que este Enum exista y se importe bien

# Importar helpers (ajusta ruta si es necesario)
from models.common import TimestampTZ, utcnow_aware

# ---------------------------------------------------------------------------
# ESTA ES LA ÚNICA DEFINICIÓN DE CLASE QUE DEBE HABER EN ESTE ARCHIVO
# ---------------------------------------------------------------------------
class Proveedor(ProveedorBase, table=True): # Hereda de Base
    # --- Nombre de tabla corregido ---
    __tablename__ = "proveedores"
    # ---------------------------------

    # Si ProveedorBase NO tiene table=True, podrías necesitar extenderla:
    # __table_args__ = {'extend_existing': True}

    # --- Campos específicos de tabla ---
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Los campos como nombre, tipo, rfc, activo se heredan de ProveedorBase.

    # --- Campos de contacto (si existen en tu tabla) ---
    contacto_principal: Optional[str] = Field(default=None)
    telefono: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=100)
    direccion: Optional[str] = Field(default=None)

    # --- Campos de auditoría con mapeo TZ ---
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
# NO DEBE HABER OTRA "class Proveedor(...)" MÁS ABAJO
# ---------------------------------------------------------------------------