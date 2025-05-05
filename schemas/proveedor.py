# schemas/proveedor.py
import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
# --- Importar Enum desde common ---
from .common import TipoProveedorEnum # Ajustado a import relativo
# --- AÑADIR IMPORT PARA ConfigDict ---
from pydantic import ConfigDict

class ProveedorBase(SQLModel):
    # --- CAMPO NOMBRE CORREGIDO ---
    nombre: str = Field(
        ..., # Usa ... si el campo es obligatorio en la creación
        max_length=150,
        sa_column_kwargs={"index": True} # <-- CORRECCIÓN: Mover index aquí
    )
    # -----------------------------
    tipo: Optional[TipoProveedorEnum] = Field(default=None) # Añadido default=None si es opcional
    rfc: Optional[str] = Field(default=None, max_length=13) # Este no tenía index, estaba bien
    activo: bool = Field(default=True) # Añadido default=True

    # Campos de contacto opcionales (definición base para la API)
    contacto_principal: Optional[str] = Field(default=None)
    telefono: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=100)
    direccion: Optional[str] = Field(default=None)


class ProveedorCreate(ProveedorBase):
    # Hereda todos los campos de ProveedorBase
    # Puedes añadir validaciones o campos específicos de creación aquí si es necesario
    pass # No necesita 'from_attributes'

class ProveedorRead(ProveedorBase):
    id: uuid.UUID
    creado_en: datetime
    actualizado_en: Optional[datetime] = None

    # --- CORRECCIÓN: Añadir model_config ---
    model_config = ConfigDict(from_attributes=True)
    # ------------------------------------

class ProveedorUpdate(SQLModel): # No hereda de Base si quieres todos opcionales
    # Hacemos todos los campos opcionales para la actualización parcial (PATCH)
    nombre: Optional[str] = Field(default=None, max_length=150)
    tipo: Optional[TipoProveedorEnum] = Field(default=None)
    rfc: Optional[str] = Field(default=None, max_length=13)
    activo: Optional[bool] = Field(default=None)
    contacto_principal: Optional[str] = Field(default=None)
    telefono: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=100)
    direccion: Optional[str] = Field(default=None)
    # No necesita 'from_attributes'