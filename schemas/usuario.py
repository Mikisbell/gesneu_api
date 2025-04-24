# schemas/usuario.py
import uuid
from datetime import datetime
from typing import Optional
from pydantic import EmailStr
from sqlmodel import SQLModel, Field

class UsuarioBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: Optional[EmailStr] = Field(default=None, unique=True, index=True)
    nombre_completo: Optional[str] = None
    rol: str = Field(default="OPERADOR")
    activo: bool = True

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioRead(UsuarioBase):
    id: uuid.UUID
    creado_en: datetime
    actualizado_en: Optional[datetime] = None