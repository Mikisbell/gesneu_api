"""
Modelos generados automáticamente para vehiculos
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

class Vehiculos(SQLModel, table=True):
    """Modelo para tabla vehiculos - Alineado con esquema real de BD"""
    __tablename__ = "vehiculos"

    # Campos exactos del esquema real
    id: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')))
    numero_economico: str = Field(sa_column=Column(String(20), nullable=False, unique=True))
    tipo_vehiculo_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('tipos_vehiculo.id'), nullable=False))
    marca: Optional[str] = Field(default=None, sa_column=Column(String(50)))
    modelo: Optional[str] = Field(default=None, sa_column=Column(String(50)))
    anio_fabricacion: Optional[int] = Field(default=None, sa_column=Column(Integer))
    numero_serie: Optional[str] = Field(default=None, sa_column=Column(String(100)))
    placa: Optional[str] = Field(default=None, sa_column=Column(String(20)))
    fecha_alta: date = Field(sa_column=Column(Date, nullable=False))
    fecha_baja: Optional[date] = Field(default=None, sa_column=Column(Date))
    activo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False))
    observaciones: Optional[str] = Field(default=None, sa_column=Column(Text))
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

class TiposVehiculo(SQLModel, table=True):
    """Modelo para tabla tipos_vehiculo - Alineado con esquema real de BD"""
    __tablename__ = "tipos_vehiculo"

    # Campos exactos del esquema real
    id: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')))
    nombre: str = Field(sa_column=Column(String(100), nullable=False, unique=True))
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))
    ejes_standard: int = Field(sa_column=Column(Integer, nullable=False))
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

class ConfiguracionesEje(SQLModel, table=True):
    """Modelo para tabla configuraciones_eje - Alineado con esquema real de BD"""
    __tablename__ = "configuraciones_eje"

    # Campos exactos del esquema real
    id: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')))
    tipo_vehiculo_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('tipos_vehiculo.id'), nullable=False))
    numero_eje: int = Field(sa_column=Column(Integer, nullable=False))
    posicion_eje: str = Field(sa_column=Column(String(20), nullable=False))
    neumaticos_por_posicion: int = Field(sa_column=Column(Integer, nullable=False))
    activo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False))
    creado_en: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
    creado_por: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('usuarios.id')))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    actualizado_por: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('usuarios.id')))

    __table_args__ = (
        UniqueConstraint(tipo_vehiculo_id, numero_eje, posicion_eje),
    )

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer, Numeric, Date, SmallInteger, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import text

class PosicionesNeumatico(SQLModel, table=True):
    """Modelo para tabla posiciones_neumatico - Alineado con esquema real de BD"""
    __tablename__ = "posiciones_neumatico"

    # Campos exactos del esquema real
    id: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')))
    configuracion_eje_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('configuraciones_eje.id'), nullable=False))
    nombre: str = Field(sa_column=Column(String(50), nullable=False))
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

class RegistrosOdometro(SQLModel, table=True):
    """Modelo para tabla registros_odometro - Alineado con esquema real de BD"""
    __tablename__ = "registros_odometro"

    # Campos exactos del esquema real
    id: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')))
    vehiculo_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('vehiculos.id'), nullable=False))
    fecha_lectura: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    lectura_odometro: int = Field(sa_column=Column(Integer, nullable=False))
    observaciones: Optional[str] = Field(default=None, sa_column=Column(Text))
    creado_en: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
    creado_por: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('usuarios.id')))

