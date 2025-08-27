"""
Module for shared type definitions in the auth module.
This helps avoid circular imports between models.
"""
from typing import TYPE_CHECKING, List, Optional, TypeVar, Any, Dict
from enum import Enum
from datetime import datetime
from uuid import UUID

if TYPE_CHECKING:
    from sqlmodel import SQLModel, Field, Relationship
    from sqlalchemy import Column
    from sqlalchemy.dialects.postgresql import UUID as PG_UUID
    
    # Import models that would cause circular imports
    from .usuario import Usuario
    from .rol import Rol
    from .permiso import Permiso
    from .usuario_rol import UsuarioRol
    from .rol_permiso import RolPermiso
    from ges_neu_api.catalogos.models import BitacoraOperaciones

# Generic type for SQLModel classes
ModelType = TypeVar("ModelType", bound="SQLModel")

# Enums for auth module
class EstadoUsuarioEnum(str, Enum):
    """User status enumeration."""
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    PENDIENTE = "PENDIENTE"
    BLOQUEADO = "BLOQUEADO"

class TipoAutenticacionEnum(str, Enum):
    """Authentication type enumeration."""
    LOCAL = "LOCAL"
    LDAP = "LDAP"
    OAUTH2 = "OAUTH2"
    JWT = "JWT"

# Common field types for reuse
class UsuarioBase:
    """Base fields for Usuario model."""
    email: str
    nombre: str
    apellido: str
    hashed_password: str
    es_superusuario: bool = False
    es_activo: bool = True
    ultimo_inicio_sesion: Optional[datetime] = None
    intentos_fallidos: int = 0
    fecha_bloqueo: Optional[datetime] = None
    tipo_autenticacion: str = "LOCAL"
    avatar_url: Optional[str] = None
    telefono: Optional[str] = None
    cargo: Optional[str] = None
    departamento: Optional[str] = None
    notificaciones_activas: bool = True
    preferencias: Dict[str, Any] = {}
    ultima_actividad: Optional[datetime] = None
    zona_horaria: str = "UTC"
