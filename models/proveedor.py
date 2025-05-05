# models/proveedor.py

import uuid
from datetime import datetime, timezone # timezone no se usa aquí, podrías quitarla
from typing import Optional
from sqlmodel import Field, SQLModel
# --- Asegúrate de importar Column, text, TIMESTAMP, ForeignKey ---
from sqlalchemy import Column, text, ForeignKey # TIMESTAMP no se usa explícitamente aquí, TimestampTZ sí
# Importar TimestampTZ y utcnow_aware desde common
from models.common import TimestampTZ, utcnow_aware

# Importar Base y Enum desde schemas
from schemas.proveedor import ProveedorBase # <--- IMPORTANTE: Aquí se hereda 'nombre' y 'ruc'
from schemas.common import TipoProveedorEnum # Asegúrate que este Enum exista y se importe bien


# ---------------------------------------------------------------------------
# Modelo de Tabla Proveedor
# ---------------------------------------------------------------------------
class Proveedor(ProveedorBase, table=True): # Hereda de ProveedorBase
    __tablename__ = "proveedores"

    # ID y campos de auditoría definidos aquí están bien
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # --- Campos específicos de tabla (no heredados) ---
    # Estos no tienen unique/index, así que están bien
    contacto_principal: Optional[str] = Field(default=None)
    telefono: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=100)
    direccion: Optional[str] = Field(default=None)

    # --- Campos de auditoría con mapeo TZ ---
    # Estos usan sa_column=Column(...) y están bien
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