"""
Modelos del módulo de autenticación.
"""
from __future__ import annotations
from datetime import datetime
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship, SQLModel, text

if TYPE_CHECKING:
    from ..eventos.models import EventosNeumaticos
    from ..alertas.models import Alertas

# --- Tablas de Unión (definidas antes para que las relaciones las encuentren) ---

class RolesPermisos(SQLModel, table=True):
    """Tabla de unión muchos a muchos entre roles y permisos."""
    __tablename__ = 'roles_permisos'
    
    rol_id: UUID = Field(
        sa_column=sa.Column(PG_UUID(as_uuid=True), sa.ForeignKey('roles.id'), primary_key=True)
    )
    permiso_id: UUID = Field(
        sa_column=sa.Column(PG_UUID(as_uuid=True), sa.ForeignKey('permisos.id'), primary_key=True)
    )
    asignado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )
    asignado_por: Optional[UUID] = Field(
        default=None, 
        sa_column=sa.Column(PG_UUID(as_uuid=True), sa.ForeignKey("usuarios.id"))
    )

class UsuariosRoles(SQLModel, table=True):
    """Tabla de unión muchos a muchos entre usuarios y roles."""
    __tablename__ = 'usuarios_roles'
    
    usuario_id: UUID = Field(
        sa_column=sa.Column(PG_UUID(as_uuid=True), sa.ForeignKey('usuarios.id'), primary_key=True)
    )
    rol_id: UUID = Field(
        sa_column=sa.Column(PG_UUID(as_uuid=True), sa.ForeignKey('roles.id'), primary_key=True)
    )
    asignado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )
    asignado_por: Optional[UUID] = Field(
        default=None, 
        sa_column=sa.Column(PG_UUID(as_uuid=True), sa.ForeignKey("usuarios.id"))
    )

# --- Modelos Principales ---

class Permiso(SQLModel, table=True):
    """Modelo que representa un permiso en el sistema."""
    __tablename__ = 'permisos'
    
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=sa.Column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    )
    nombre_recurso: str = Field(sa_column=sa.Column(sa.String(100), nullable=False, index=True))
    accion: str = Field(sa_column=sa.Column(sa.String(100), nullable=False, index=True))
    descripcion: Optional[str] = Field(default=None, sa_column=sa.Text)
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )
    
    # Relationship removed to avoid SQLAlchemy metadata conflicts
    # roles: handled at service layer

class Rol(SQLModel, table=True):
    """Modelo que representa un rol en el sistema."""
    __tablename__ = 'roles'
    
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=sa.Column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    )
    nombre: str = Field(sa_column=sa.Column(sa.String(100), unique=True, nullable=False, index=True))
    descripcion: Optional[str] = Field(default=None, sa_column=sa.Text)
    es_rol_sistema: bool = Field(default=False, sa_column=sa.Column(sa.Boolean, nullable=False, server_default=sa.text('false')))
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )
    creado_por: Optional[UUID] = Field(
        default=None, 
        sa_column=sa.Column(PG_UUID(as_uuid=True), sa.ForeignKey("usuarios.id"))
    )
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=sa.Column(sa.DateTime(timezone=True)))
    actualizado_por: Optional[UUID] = Field(
        default=None, 
        sa_column=sa.Column(PG_UUID(as_uuid=True), sa.ForeignKey("usuarios.id"))
    )
    
    # Relationships removed to avoid SQLAlchemy metadata conflicts
    # usuarios: handled at service layer
    # permisos: handled at service layer

class Usuario(SQLModel, table=True):
    """Modelo que representa a un usuario del sistema."""
    __tablename__ = 'usuarios'
    
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=sa.Column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'))
    )
    username: str = Field(sa_column=sa.Column(sa.String(50), unique=True, nullable=False, index=True))
    nombre_completo: Optional[str] = Field(default=None, sa_column=sa.Column(sa.String(200)))
    email: Optional[str] = Field(default=None, sa_column=sa.Column(sa.String(100), unique=True, index=True))
    password_hash: str = Field(sa_column=sa.Column(sa.Text, nullable=False))
    activo: bool = Field(default=True, sa_column=sa.Column(sa.Boolean, nullable=False, server_default=sa.text('true')))
    ultimo_login: Optional[datetime] = Field(default=None, sa_column=sa.Column(sa.DateTime(timezone=True)))
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )
    creado_por: Optional[UUID] = Field(
        default=None, 
        sa_column=sa.Column(PG_UUID(as_uuid=True), sa.ForeignKey("usuarios.id"))
    )
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=sa.Column(sa.DateTime(timezone=True)))
    actualizado_por: Optional[UUID] = Field(
        default=None, 
        sa_column=sa.Column(PG_UUID(as_uuid=True), sa.ForeignKey("usuarios.id"))
    )

    # Relationships removed to avoid SQLAlchemy metadata conflicts
    # roles: handled at service layer
    # eventos_neumaticos: handled at service layer

class AuditoriaRolUsuario(SQLModel, table=True):
    """Modelo que registra cambios en las asignaciones de roles a usuarios."""
    __tablename__ = 'auditoria_roles_usuarios'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: UUID = Field(sa_column=sa.Column(PG_UUID(as_uuid=True), nullable=False, index=True))
    rol_id: UUID = Field(sa_column=sa.Column(PG_UUID(as_uuid=True), nullable=False, index=True))
    accion: str = Field(sa_column=sa.Column(sa.String(10), nullable=False))
    ejecutado_por: Optional[UUID] = Field(default=None, sa_column=sa.Column(PG_UUID(as_uuid=True)))
    ejecutado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )
    metadata_: Optional[Dict[str, Any]] = Field(default=None, sa_column=sa.Column('metadata', JSONB))