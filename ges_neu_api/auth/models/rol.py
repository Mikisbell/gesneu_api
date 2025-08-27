from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Boolean, DateTime, text, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import SQLModel, Field, Relationship

# Import base model
from ges_neu_api.core.base_models import BaseModel

# Use TYPE_CHECKING for model imports to avoid circular imports
if TYPE_CHECKING:
    from .usuario import Usuario
    from .usuario_rol import UsuarioRol
    from .permiso import Permiso
    from .rol_permiso import RolPermiso

class Rol(BaseModel, table=True):
    """Modelo para los roles del sistema."""
    __tablename__ = "roles"
    
    # Sobrescribir campos heredados de BaseModel para asegurar consistencia
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único del rol"
    )
    
    activo: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
        description="Indica si el rol está activo"
    )
    
    nombre: str = Field(
        max_length=100,
        sa_column=Column(String(100), nullable=False, unique=True),
        description="Nombre del rol"
    )
    
    descripcion: Optional[str] = Field(
        default=None,
        sa_column=Column(String(255)),
        description="Descripción del rol"
    )
    
    es_rol_sistema: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default=text("false")),
        description="Indica si es un rol del sistema que no puede ser eliminado"
    )
    
    # Campos de auditoría
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=text("now()"), nullable=False),
        description="Fecha de creación del rol"
    )
    
    creado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
        description="ID del usuario que creó el rol"
    )
    
    actualizado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), onupdate=datetime.utcnow),
        description="Fecha de última actualización del rol"
    )
    
    actualizado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
        description="ID del usuario que actualizó el rol por última vez"
    )
    
    # Relaciones
    usuarios_rel: List["UsuarioRol"] = Relationship(back_populates="rol")
    permisos_rel: List["RolPermiso"] = Relationship(back_populates="rol")
    
    # Relaciones de auditoría
    creado_por_usuario: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Rol.creado_por]"}
    )
    
    actualizado_por_usuario: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Rol.actualizado_por]"}
    )
    
    # Propiedades para acceder a los usuarios y permisos directamente
    @property
    def usuarios(self) -> List["Usuario"]:
        return [rel.usuario for rel in self.usuarios_rel] if hasattr(self, 'usuarios_rel') else []
    
    @property
    def permisos(self) -> List["Permiso"]:
        return [rel.permiso for rel in self.permisos_rel] if hasattr(self, 'permisos_rel') else []
    
    __table_args__ = (
        Index('idx_roles_nombre_lower', text('lower(nombre::text)'), postgresql_using='btree'),
        Index('idx_roles_nombre_lower_unaccent', text('f_immutable_lower_unaccent(nombre::text)'), postgresql_using='btree'),
        {
            'comment': 'Roles del sistema que definen los permisos de los usuarios',
            'schema': 'public'
        }
    )
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            UUID: lambda v: str(v) if v else None,
            datetime: lambda v: v.isoformat() if v else None
        }

# Importaciones condicionales al final para evitar dependencias circulares
if not TYPE_CHECKING:
    from .usuario import Usuario
    from .permiso import Permiso
    from .rol_permiso import RolPermiso
    from .usuario_rol import UsuarioRol
