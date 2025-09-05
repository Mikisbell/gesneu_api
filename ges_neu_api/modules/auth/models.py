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
    """Modelo para tabla usuarios - Exacto según ESQUEMA_COMPLETO_BD.md"""
    __tablename__ = "usuarios"
    __table_args__ = (
        {'extend_existing': True, 'schema': None}  # No schema for SQLite compatibility
    )

    # Campos exactos según esquema PostgreSQL real
    id: UUID = Field(default_factory=uuid4, primary_key=True)  # uuid NOT NULL DEFAULT gen_random_uuid()
    username: str = Field(max_length=50, unique=True)  # character varying(50) NOT NULL UNIQUE
    nombre_completo: Optional[str] = Field(default=None, max_length=200)  # character varying(200) NULLABLE
    email: Optional[str] = Field(default=None, max_length=100, unique=True)  # character varying(100) NULLABLE UNIQUE
    password_hash: Optional[str] = Field(default=None)  # text NULLABLE
    activo: bool = Field(default=True)  # boolean NOT NULL DEFAULT true
    ultimo_login: Optional[datetime] = Field(default=None)  # timestamp with time zone NULLABLE
    creado_en: datetime = Field(default_factory=datetime.utcnow)  # timestamp with time zone NOT NULL DEFAULT now()
    creado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")  # uuid NULLABLE FK
    actualizado_en: Optional[datetime] = Field(default=None)  # timestamp with time zone NULLABLE
    actualizado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")  # uuid NULLABLE FK

class Rol(SQLModel, table=True):
    """Modelo para tabla roles - Exacto según ESQUEMA_COMPLETO_BD.md"""
    __tablename__ = "roles"
    __table_args__ = (
        {'extend_existing': True, 'schema': None}  # No schema for SQLite compatibility
    )

    # Campos exactos según esquema PostgreSQL real
    id: UUID = Field(default_factory=uuid4, primary_key=True)  # uuid NOT NULL DEFAULT gen_random_uuid()
    nombre: str = Field(max_length=100, unique=True)  # character varying(100) NOT NULL UNIQUE
    descripcion: Optional[str] = Field(default=None)  # text NULLABLE
    es_rol_sistema: bool = Field(default=False)  # boolean NOT NULL DEFAULT false
    creado_en: datetime = Field(default_factory=datetime.utcnow)  # timestamp with time zone NOT NULL DEFAULT now()
    creado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")  # uuid NULLABLE FK
    actualizado_en: Optional[datetime] = Field(default=None)  # timestamp with time zone NULLABLE
    actualizado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")  # uuid NULLABLE FK

class Permiso(SQLModel, table=True):
    """Modelo para tabla permisos - Exacto según ESQUEMA_COMPLETO_BD.md"""
    __tablename__ = "permisos"
    __table_args__ = (
        UniqueConstraint('nombre_recurso', 'accion'),
        {'extend_existing': True, 'schema': None}  # No schema for SQLite compatibility
    )

    # Campos exactos según esquema PostgreSQL real
    id: UUID = Field(default_factory=uuid4, primary_key=True)  # uuid NOT NULL DEFAULT gen_random_uuid()
    nombre_recurso: str = Field(max_length=100)  # character varying(100) NOT NULL
    accion: str = Field(max_length=100)  # character varying(100) NOT NULL
    descripcion: Optional[str] = Field(default=None)  # text NULLABLE
    creado_en: datetime = Field(default_factory=datetime.utcnow)  # timestamp with time zone NOT NULL DEFAULT now()

class UsuariosRoles(SQLModel, table=True):
    """Modelo para tabla usuarios_roles - Exacto según ESQUEMA_COMPLETO_BD.md"""
    __tablename__ = "usuarios_roles"
    __table_args__ = (
        {'extend_existing': True, 'schema': None}  # No schema for SQLite compatibility
    )

    # Campos exactos según esquema PostgreSQL real
    usuario_id: UUID = Field(foreign_key="usuarios.id", primary_key=True)  # uuid NOT NULL FK PRIMARY KEY
    rol_id: UUID = Field(foreign_key="roles.id", primary_key=True)  # uuid NOT NULL FK PRIMARY KEY
    asignado_en: datetime = Field(default_factory=datetime.utcnow)  # timestamp with time zone NOT NULL DEFAULT now()
    asignado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")  # uuid NULLABLE FK

class RolesPermisos(SQLModel, table=True):
    """Modelo para tabla roles_permisos - Exacto según ESQUEMA_COMPLETO_BD.md"""
    __tablename__ = "roles_permisos"
    __table_args__ = (
        {'extend_existing': True, 'schema': None}  # No schema for SQLite compatibility
    )

    # Campos exactos según esquema PostgreSQL real
    rol_id: UUID = Field(foreign_key="roles.id", primary_key=True)  # uuid NOT NULL FK PRIMARY KEY
    permiso_id: UUID = Field(foreign_key="permisos.id", primary_key=True)  # uuid NOT NULL FK PRIMARY KEY
    asignado_en: datetime = Field(default_factory=datetime.utcnow)  # timestamp with time zone NOT NULL DEFAULT now()
    asignado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")  # uuid NULLABLE FK