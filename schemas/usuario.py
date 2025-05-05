# schemas/usuario.py
# --- CÓDIGO CORREGIDO (IMPORTACIÓN DE FIELD) ---

import uuid
from datetime import datetime
from typing import Optional
# --- IMPORTAR Field DESDE sqlmodel ---
from pydantic import EmailStr, ConfigDict # Field ya no se importa de pydantic
from sqlmodel import SQLModel, Field # <-- Asegurarse que Field viene de aquí

class UsuarioBase(SQLModel):
    # --- Los campos con sa_column_kwargs ahora usarán sqlmodel.Field ---
    username: str = Field(
        ...,
        max_length=50,
        sa_column_kwargs={"index": True, "unique": True}
    )
    email: Optional[EmailStr] = Field(
        default=None,
        max_length=100,
        sa_column_kwargs={"unique": True, "index": True}
    )
    # ------------------------------------------------------------------
    nombre_completo: Optional[str] = Field(default=None, max_length=200)
    rol: str = Field(default="OPERADOR", max_length=50)
    activo: bool = Field(default=True)

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioRead(UsuarioBase):
    id: uuid.UUID
    creado_en: datetime
    actualizado_en: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True) # Esto ya estaba bien

class UsuarioUpdate(SQLModel):
    email: Optional[EmailStr] = Field(default=None, max_length=100)
    nombre_completo: Optional[str] = Field(default=None, max_length=200)
    rol: Optional[str] = Field(default=None, max_length=50)
    activo: Optional[bool] = Field(default=None)