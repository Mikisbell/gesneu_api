"""
Schemas para el módulo de autenticación.

Este módulo contiene los esquemas Pydantic utilizados para la validación y documentación
de la API de autenticación y gestión de usuarios.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# --- Schemas de Token ---

class Token(BaseModel):
    """Schema para la respuesta de autenticación exitosa."""
    access_token: str = Field(..., description="Token JWT para autenticación")
    token_type: str = Field(default="bearer", description="Tipo de token")

class TokenData(BaseModel):
    """Schema para los datos contenidos en el token JWT."""
    sub: Optional[str] = Field(None, description="Sujeto del token (username)")

# --- Schemas de Usuario (Corregidos y Completos) ---

class UserBase(BaseModel):
    """Schema base con los campos comunes de usuario, alineado con la BD."""
    username: str = Field(..., description="Nombre de usuario único")
    email: Optional[EmailStr] = Field(None, description="Correo electrónico del usuario")
    nombre_completo: Optional[str] = Field(None, description="Nombre completo del usuario")
    activo: bool = Field(True, description="Indica si el usuario está activo")

class UserCreate(UserBase):
    """Schema para la creación de un nuevo usuario."""
    password: str = Field(..., min_length=8, description="Contraseña del usuario (mínimo 8 caracteres)")

class UserUpdate(BaseModel):
    """Schema para la actualización de un usuario existente."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    nombre_completo: Optional[str] = None
    activo: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8, description="Nueva contraseña (opcional)")

class UserInDBBase(UserBase):
    """Schema base para usuarios leídos desde la base de datos."""
    id: UUID = Field(..., description="Identificador único del usuario")
    ultimo_login: Optional[datetime] = Field(None, description="Último inicio de sesión")
    creado_en: datetime = Field(..., description="Fecha de creación del usuario")

    model_config = ConfigDict(from_attributes=True)

class UserRead(UserInDBBase):
    """Schema para la lectura de usuarios (respuesta de la API)."""
    roles: List[Dict[str, Any]] = Field(default_factory=list, description="Lista de roles asignados al usuario")

class UserWithToken(UserRead):
    """Schema que combina la información del usuario con su token de acceso."""
    token: Token = Field(..., description="Token de autenticación")

class UserLogin(BaseModel):
    """Schema para el inicio de sesión de usuarios."""
    username: str = Field(..., description="Nombre de usuario o correo electrónico")
    password: str = Field(..., description="Contraseña del usuario")

class UserChangePassword(BaseModel):
    """Schema para el cambio de contraseña."""
    current_password: str = Field(..., description="Contraseña actual")
    new_password: str = Field(..., min_length=8, description="Nueva contraseña (mínimo 8 caracteres)")

# --- Schemas de Rol y Permiso ---

class RoleBase(BaseModel):
    """Schema base para roles."""
    nombre: str = Field(..., description="Nombre del rol")
    descripcion: Optional[str] = Field(None, description="Descripción del rol")
    es_rol_sistema: bool = Field(False, description="Indica si es un rol del sistema")

class RoleCreate(RoleBase):
    """Schema para la creación de un nuevo rol."""
    pass

class RoleUpdate(BaseModel):
    """Schema para la actualización de un rol existente."""
    nombre: Optional[str] = Field(None, description="Nuevo nombre del rol")
    descripcion: Optional[str] = Field(None, description="Nueva descripción del rol")

class RoleInDB(RoleBase):
    """Schema para la lectura de roles desde la base de datos."""
    id: UUID = Field(..., description="Identificador único del rol")
    model_config = ConfigDict(from_attributes=True)

class PermissionBase(BaseModel):
    """Schema base para permisos."""
    nombre_recurso: str = Field(..., description="Nombre del recurso al que se aplica el permiso")
    accion: str = Field(..., description="Acción que se permite realizar sobre el recurso")
    descripcion: Optional[str] = Field(None, description="Descripción detallada del permiso")

class PermissionInDB(PermissionBase):
    """Schema para la lectura de permisos desde la base de datos."""
    id: UUID = Field(..., description="Identificador único del permiso")
    model_config = ConfigDict(from_attributes=True)

class RoleWithPermissions(RoleInDB):
    """Schema para la lectura de roles con sus permisos asociados."""
    permisos: List[PermissionInDB] = Field(default_factory=list, description="Lista de permisos asociados al rol")