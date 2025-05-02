# schemas/usuario.py
import uuid
from datetime import datetime
from typing import Optional
from pydantic import EmailStr, Field # Asegúrate que Field esté importado
from sqlmodel import SQLModel # Asegúrate que SQLModel esté importado

class UsuarioBase(SQLModel):
    username: str = Field(index=True, unique=True, max_length=50) # <-- ASÍ
    email: Optional[EmailStr] = Field(default=None, unique=True, index=True, max_length=100) # <-- ASÍ
    nombre_completo: Optional[str] = Field(default=None, max_length=200)
    rol: str = Field(default="OPERADOR", max_length=50)
    activo: bool = True

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioRead(UsuarioBase):
    id: uuid.UUID
    creado_en: datetime
    actualizado_en: Optional[datetime] = None
    # Podrías añadir creado_por/actualizado_por si los necesitas en la respuesta
# --- NUEVO SCHEMA PARA ACTUALIZAR ---
class UsuarioUpdate(SQLModel):
    # Todos los campos son opcionales
    # Excluimos username porque generalmente no se cambia
    # Excluimos password por seguridad (usar endpoint dedicado si se necesita)
    email: Optional[EmailStr] = Field(default=None, max_length=100)
    nombre_completo: Optional[str] = Field(default=None, max_length=200)
    rol: Optional[str] = Field(default=None, max_length=50)
    activo: Optional[bool] = None
    # No incluimos campos de auditoría aquí (creado_en, etc.)