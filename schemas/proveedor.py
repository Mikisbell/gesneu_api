# schemas/proveedor.py
import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
# --- Importar Enum desde common ---
from schemas.common import TipoProveedorEnum

class ProveedorBase(SQLModel):
    nombre: str = Field(index=True, max_length=150)
    tipo: Optional[TipoProveedorEnum] = None # Usa el Enum importado
    rfc: Optional[str] = Field(default=None, max_length=13)
    activo: bool = True
    # Campos de contacto opcionales (puedes añadirlos si los necesitas en la API)
    # contacto_principal: Optional[str] = None
    # telefono: Optional[str] = None
    # email: Optional[str] = None
    # direccion: Optional[str] = None

class ProveedorCreate(ProveedorBase):
    # Hereda nombre, tipo, rfc, activo
    pass

class ProveedorRead(ProveedorBase):
    id: uuid.UUID
    creado_en: datetime
    actualizado_en: Optional[datetime] = None

class ProveedorUpdate(SQLModel):
    nombre: Optional[str] = None
    tipo: Optional[TipoProveedorEnum] = None
    rfc: Optional[str] = None
    activo: Optional[bool] = None
    # Añadir otros campos si permites actualizarlos