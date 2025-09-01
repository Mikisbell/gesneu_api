"""
Modelos generados automáticamente para neumaticos
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

class Neumaticos(SQLModel, table=True):
    """Modelo para tabla neumaticos - Alineado con esquema real de BD"""
    __tablename__ = "neumaticos"

    # Campos exactos del esquema real
    id: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')))
    modelo_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('modelos_neumatico.id'), nullable=False))
    numero_serie: Optional[str] = Field(default=None, sa_column=Column(String(100)))
    dot: Optional[str] = Field(default=None, sa_column=Column(String(255)))
    fecha_fabricacion: Optional[date] = Field(default=None, sa_column=Column(Date))
    fecha_compra: date = Field(sa_column=Column(Date, nullable=False))
    costo_compra: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    moneda_compra: Optional[str] = Field(default=None, sa_column=Column(String(3)))
    proveedor_compra_id: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('proveedores.id')))
    es_reencauchado: bool = Field(default=False, sa_column=Column(Boolean, nullable=False))
    vida_actual: int = Field(sa_column=Column(Integer, nullable=False))
    estado_actual: str = Field(sa_column=Column(String(255), nullable=False))
    ubicacion_actual_vehiculo_id: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('vehiculos.id')))
    ubicacion_actual_posicion_id: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('posiciones_neumatico.id')))
    ubicacion_almacen_id: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('almacenes.id')))
    kilometraje_acumulado: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    kilometraje_vida_actual: Optional[int] = Field(default=0, sa_column=Column(Integer))
    fecha_inicio_vida_actual: Optional[date] = Field(default=None, sa_column=Column(Date))
    odometro_instalacion_vida_actual: Optional[int] = Field(default=None, sa_column=Column(Integer))
    reencauches_realizados: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    fecha_ultimo_reencauche: Optional[date] = Field(default=None, sa_column=Column(Date))
    profundidad_inicial_mm: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5, 2)))
    profundidad_remanente_actual_mm: Decimal = Field(sa_column=Column(Numeric(5, 2), nullable=False))
    fecha_ultima_medicion_profundidad: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    tasa_desgaste_actual_mm_km: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 8)))
    vida_util_restante_km: Optional[int] = Field(default=None, sa_column=Column(Integer))
    fecha_ultimo_evento: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    fecha_desecho: Optional[date] = Field(default=None, sa_column=Column(Date))
    motivo_desecho_id: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('motivos_desecho.id')))
    sensor_id: Optional[str] = Field(default=None, sa_column=Column(String(100)))
    proxima_inspeccion_fecha: Optional[date] = Field(default=None, sa_column=Column(Date))
    proxima_inspeccion_km: Optional[int] = Field(default=None, sa_column=Column(Integer))
    profundidad_inicio_vida_actual_mm: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5, 2)))
    activo: Optional[bool] = Field(default=True, sa_column=Column(Boolean))
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

class FabricantesNeumatico(SQLModel, table=True):
    """Modelo para tabla fabricantes_neumatico - Alineado con esquema real de BD"""
    __tablename__ = "fabricantes_neumatico"

    # Campos exactos del esquema real
    id: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')))
    nombre: str = Field(sa_column=Column(String(100), nullable=False, unique=True))
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

class ModelosNeumatico(SQLModel, table=True):
    """Modelo para tabla modelos_neumatico - Alineado con esquema real de BD"""
    __tablename__ = "modelos_neumatico"

    # Campos exactos del esquema real
    id: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')))
    fabricante_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('fabricantes_neumatico.id'), nullable=False))
    nombre: str = Field(sa_column=Column(String(100), nullable=False))
    medida: str = Field(sa_column=Column(String(20), nullable=False))
    tipo_construccion: Optional[str] = Field(default=None, sa_column=Column(String(20)))
    indice_carga: Optional[str] = Field(default=None, sa_column=Column(String(5)))
    indice_velocidad: Optional[str] = Field(default=None, sa_column=Column(String(2)))
    profundidad_original_mm: Decimal = Field(sa_column=Column(Numeric(5, 2), nullable=False))
    max_vidas_utiles: int = Field(sa_column=Column(Integer, nullable=False))
    porcentaje_desgaste_por_vida: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5, 2)))
    tasa_desgaste_esperada_mm_km: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 8)))
    vida_util_teorica_km: Optional[int] = Field(default=None, sa_column=Column(Integer))
    activo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False))
    creado_en: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False))
    creado_por: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('usuarios.id')))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    actualizado_por: UUID = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey('usuarios.id')))

    __table_args__ = (
        UniqueConstraint(fabricante_id, nombre, medida),
    )

