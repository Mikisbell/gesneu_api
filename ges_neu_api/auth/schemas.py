# ges_neu_api/ges_neu_api/auth/schemas.py

from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr

# Schema base con los campos comunes que comparten otros schemas
class UsuarioBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    nombre_completo: Optional[str] = None
    activo: bool = True

# Schema para crear un usuario (lo que la API recibe)
# Hereda de UsuarioBase y añade el campo de la contraseña.
class UsuarioCreate(UsuarioBase):
    password: str
    # Campos de auditoría
    creado_por: Optional[UUID] = None
    actualizado_por: Optional[UUID] = None

# Schema para actualizar un usuario (todos los campos son opcionales)
class UsuarioUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    nombre_completo: Optional[str] = None
    activo: Optional[bool] = None
    password: Optional[str] = None

# Schema para leer un usuario (lo que la API devuelve)
# Hereda de UsuarioBase y añade el ID, pero NUNCA la contraseña.
class UsuarioRead(UsuarioBase):
    id: UUID

# Schema para el token de seguridad
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
