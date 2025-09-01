"""
Modelos generados automáticamente para auth
Basado en ESQUEMA_BD_REAL.md - NO MODIFICAR MANUALMENTE
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer, Numeric, Date, SmallInteger, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import text

class Usuarios(SQLModel, table=True):
    """Modelo para tabla usuarios - Alineado con esquema real de BD"""
    __tablename__ = "usuarios"

    # Campos exactos del esquema real
    id: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')))
    username: str = Field(sa_column=Column(String(50), nullable=False, unique=True))
    email: Optional[str] = Field(default=None, sa_column=Column(String(100), unique=True))
    password_hash: Optional[str] = Field(default=None, sa_column=Column(Text))
    nombre_completo: Optional[str] = Field(default=None, sa_column=Column(String(200)))
    activo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False))
    ultimo_login: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    creado_en: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
    creado_por: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('usuarios.id')))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    actualizado_por: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('usuarios.id')))

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer, Numeric, Date, SmallInteger, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import text

class Roles(SQLModel, table=True):
    """Modelo para tabla roles - Alineado con esquema real de BD"""
    __tablename__ = "roles"

    # Campos exactos del esquema real
    id: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')))
    nombre: str = Field(sa_column=Column(String(100), nullable=False, unique=True))
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))
    activo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False))
    creado_en: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
    creado_por: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('usuarios.id')))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    actualizado_por: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('usuarios.id')))

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer, Numeric, Date, SmallInteger, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import text

class Permisos(SQLModel, table=True):
    """Modelo para tabla permisos - Alineado con esquema real de BD"""
    __tablename__ = "permisos"

    # Campos exactos del esquema real
    id: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')))
    nombre_recurso: str = Field(sa_column=Column(String(100), nullable=False))
    accion: str = Field(sa_column=Column(String(100), nullable=False))
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))
    creado_en: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))

    __table_args__ = (
        UniqueConstraint(nombre_recurso, accion),
    )

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer, Numeric, Date, SmallInteger, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import text

class UsuariosRoles(SQLModel, table=True):
    """Modelo para tabla usuarios_roles - Alineado con esquema real de BD"""
    __tablename__ = "usuarios_roles"

    # Campos exactos del esquema real
    usuario_id: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('usuarios.id')))
    rol_id: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('roles.id')))
    asignado_en: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
    asignado_por: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('usuarios.id')))

    __table_args__ = (
        # Primary key: usuario_id, rol_id
    )

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer, Numeric, Date, SmallInteger, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import text

class RolesPermisos(SQLModel, table=True):
    """Modelo para tabla roles_permisos - Alineado con esquema real de BD"""
    __tablename__ = "roles_permisos"

    # Campos exactos del esquema real
    rol_id: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('roles.id')))
    permiso_id: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('permisos.id')))
    asignado_en: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
    asignado_por: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('usuarios.id')))

    __table_args__ = (
        # Primary key: rol_id, permiso_id
    )

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer, Numeric, Date, SmallInteger, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import text

class AuditoriaRolesUsuarios(SQLModel, table=True):
    """Modelo para tabla auditoria_roles_usuarios - Alineado con esquema real de BD"""
    __tablename__ = "auditoria_roles_usuarios"

    # Campos exactos del esquema real
    id: Optional[int] = Field(default=None, sa_column=Column(Integer))
    usuario_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), nullable=False))
    rol_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), nullable=False))
    accion: str = Field(sa_column=Column(String(10), nullable=False))
    ejecutado_en: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
    ejecutado_por: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
    metadata: Optional[str] = Field(default=None, sa_column=Column(String(255)))

