"""
Modelos consolidados del módulo de autenticación.
Basado en esquema real de PostgreSQL - Fuente única de verdad.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import text

class Usuario(SQLModel, table=True):
    """Modelo para tabla usuarios - Alineado exactamente con esquema real PostgreSQL"""
    __tablename__ = "usuarios"
    __table_args__ = {'extend_existing': True}

    # Campos exactos según esquema BD real
    id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text('gen_random_uuid()')))
    username: str = Field(sa_column=Column(String(50), nullable=False, unique=True))
    nombre_completo: Optional[str] = Field(default=None, sa_column=Column(String(200)))
    email: Optional[str] = Field(default=None, sa_column=Column(String(100), unique=True))
    password_hash: Optional[str] = Field(default=None, sa_column=Column(Text))
    activo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text('true')))
    ultimo_login: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    creado_en: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text('now()')))
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('usuarios.id')))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    actualizado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('usuarios.id')))

class Rol(SQLModel, table=True):
    """Modelo para tabla roles - Alineado exactamente con esquema real PostgreSQL"""
    __tablename__ = "roles"
    __table_args__ = {'extend_existing': True}

    # Campos exactos según esquema BD real
    id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text('gen_random_uuid()')))
    nombre: str = Field(sa_column=Column(String(100), nullable=False, unique=True))
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))
    es_rol_sistema: bool = Field(default=False, sa_column=Column(Boolean, nullable=False, server_default=text('false')))
    creado_en: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text('now()')))
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('usuarios.id')))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    actualizado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('usuarios.id')))

class Permiso(SQLModel, table=True):
    """Modelo para tabla permisos - Alineado con esquema real"""
    __tablename__ = "permisos"
    __table_args__ = (
        UniqueConstraint('nombre_recurso', 'accion'),
        {'extend_existing': True}
    )

    id: UUID = Field(default_factory=uuid4, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')))
    nombre_recurso: str = Field(sa_column=Column(String(100), nullable=False))
    accion: str = Field(sa_column=Column(String(100), nullable=False))
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))
    creado_en: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text('now()')))

class UsuarioRol(SQLModel, table=True):
    """Modelo para tabla usuarios_roles - Relación muchos a muchos"""
    __tablename__ = "usuarios_roles"
    __table_args__ = {'extend_existing': True}

    usuario_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('usuarios.id'), primary_key=True))
    rol_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True))
    asignado_en: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text('now()')))
    asignado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('usuarios.id')))

class RolPermiso(SQLModel, table=True):
    """Modelo para tabla roles_permisos - Relación muchos a muchos"""
    __tablename__ = "roles_permisos"
    __table_args__ = {'extend_existing': True}

    rol_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True))
    permiso_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('permisos.id'), primary_key=True))
    asignado_en: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text('now()')))
    asignado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('usuarios.id')))
