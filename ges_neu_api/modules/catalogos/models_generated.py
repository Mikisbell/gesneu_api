"""
Modelos generados automáticamente para catalogos
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

class Proveedores(SQLModel, table=True):
    """Modelo para tabla proveedores - Alineado con esquema real de BD"""
    __tablename__ = "proveedores"

    # Campos exactos del esquema real
    id: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')))
    nombre: str = Field(sa_column=Column(String(200), nullable=False))
    ruc: Optional[str] = Field(default=None, sa_column=Column(String(20)))
    contacto: Optional[str] = Field(default=None, sa_column=Column(String(200)))
    telefono: Optional[str] = Field(default=None, sa_column=Column(String(20)))
    email: Optional[str] = Field(default=None, sa_column=Column(String(100)))
    direccion: Optional[str] = Field(default=None, sa_column=Column(Text))
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

class Almacenes(SQLModel, table=True):
    """Modelo para tabla almacenes - Alineado con esquema real de BD"""
    __tablename__ = "almacenes"

    # Campos exactos del esquema real
    id: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')))
    nombre: str = Field(sa_column=Column(String(100), nullable=False, unique=True))
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))
    ubicacion: Optional[str] = Field(default=None, sa_column=Column(String(200)))
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

class MotivosDesecho(SQLModel, table=True):
    """Modelo para tabla motivos_desecho - Alineado con esquema real de BD"""
    __tablename__ = "motivos_desecho"

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

class ParametrosInventario(SQLModel, table=True):
    """Modelo para tabla parametros_inventario - Alineado con esquema real de BD"""
    __tablename__ = "parametros_inventario"

    # Campos exactos del esquema real
    id: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')))
    parametro_tipo: str = Field(sa_column=Column(String(255), nullable=False))
    modelo_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('modelos_neumatico.id'), nullable=False))
    ubicacion_almacen_id: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('almacenes.id')))
    valor_numerico: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    valor_texto: Optional[str] = Field(default=None, sa_column=Column(Text))
    notas: Optional[str] = Field(default=None, sa_column=Column(Text))
    activo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False))
    creado_en: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
    creado_por: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('usuarios.id')))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    actualizado_por: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('usuarios.id')))

    __table_args__ = (
        UniqueConstraint(parametro_tipo, modelo_id, ubicacion_almacen_id),
    )

