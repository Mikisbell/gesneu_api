"""
Modelos de neumáticos completamente limpios - Sin herencia BaseModel
Alineados exactamente con ESQUEMA_BD_REAL.md
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, UniqueConstraint, CheckConstraint, Integer, Numeric, Date, SmallInteger, Index, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import text

class FabricanteNeumatico(SQLModel, table=True):
    """Fabricantes de neumáticos - Esquema exacto ESQUEMA_BD_REAL.md"""
    __tablename__ = 'fabricantes_neumatico'
    
    # Campos exactos del esquema real
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    )
    nombre: str = Field(sa_column=Column(String(100), nullable=False, unique=True))
    activo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text("true")))
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    )
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL")))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP, onupdate=text("now()")))
    actualizado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL")))
    
    __table_args__ = (
        CheckConstraint('length(nombre) >= 2', name='fabricantes_neumatico_nombre_length'),
    )

class ModeloNeumatico(SQLModel, table=True):
    """Modelos de neumáticos - Esquema exacto ESQUEMA_BD_REAL.md"""
    __tablename__ = 'modelos_neumatico'
    
    # Campos exactos del esquema real
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    )
    fabricante_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("fabricantes_neumatico.id"), nullable=False))
    nombre: str = Field(sa_column=Column(String(100), nullable=False))
    medida: str = Field(sa_column=Column(String(20), nullable=False))
    tipo_construccion: str = Field(default="RADIAL", sa_column=Column(String(20), server_default=text("'RADIAL'")))
    indice_carga: Optional[str] = Field(default=None, sa_column=Column(String(5)))
    indice_velocidad: Optional[str] = Field(default=None, sa_column=Column(String(2)))
    profundidad_original_mm: Decimal = Field(sa_column=Column(Numeric(5, 2), nullable=False))
    max_vidas_utiles: int = Field(default=3, sa_column=Column(Integer, nullable=False, server_default=text("3")))
    porcentaje_desgaste_por_vida: Optional[Decimal] = Field(default=Decimal('33.33'), sa_column=Column(Numeric(5, 2), server_default=text("33.33")))
    tasa_desgaste_esperada_mm_km: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 8)))
    vida_util_teorica_km: Optional[int] = Field(default=None, sa_column=Column(Integer))
    activo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text("true")))
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    )
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL")))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP, onupdate=text("now()")))
    actualizado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL")))
    
    __table_args__ = (
        CheckConstraint('max_vidas_utiles > 0', name='modelos_neumatico_max_vidas_check'),
        CheckConstraint('porcentaje_desgaste_por_vida >= 0', name='modelos_neumatico_porcentaje_check'),
        UniqueConstraint('fabricante_id', 'nombre', 'medida', name='modelos_neumatico_fabricante_nombre_medida_key'),
        Index('idx_modelos_fabricante', 'fabricante_id'),
    )

class Neumatico(SQLModel, table=True):
    """Neumáticos - Esquema exacto ESQUEMA_BD_REAL.md"""
    __tablename__ = 'neumaticos'
    
    # Campos exactos del esquema real
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    )
    modelo_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("modelos_neumatico.id"), nullable=False))
    numero_serie: Optional[str] = Field(default=None, sa_column=Column(String(100)))
    dot: Optional[str] = Field(default=None, sa_column=Column(String(20)))
    fecha_fabricacion: Optional[date] = Field(default=None, sa_column=Column(Date))
    fecha_compra: date = Field(sa_column=Column(Date, nullable=False))
    costo_compra: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    moneda_compra: str = Field(default="PEN", sa_column=Column(String(3), server_default=text("'PEN'")))
    proveedor_compra_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("proveedores.id")))
    es_reencauchado: bool = Field(default=False, sa_column=Column(Boolean, nullable=False, server_default=text("false")))
    vida_actual: int = Field(default=1, sa_column=Column(SmallInteger, nullable=False, server_default=text("1")))
    estado_actual: str = Field(default="EN_STOCK", sa_column=Column(String(20), nullable=False, server_default=text("'EN_STOCK'")))
    ubicacion_actual_vehiculo_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("vehiculos.id")))
    ubicacion_actual_posicion_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("posiciones_neumatico.id")))
    ubicacion_almacen_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("almacenes.id")))
    kilometraje_acumulado: int = Field(default=0, sa_column=Column(Integer, nullable=False, server_default=text("0")))
    kilometraje_vida_actual: Optional[int] = Field(default=0, sa_column=Column(Integer, server_default=text("0")))
    profundidad_actual_mm: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5, 2)))
    presion_recomendada_psi: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5, 2)))
    presion_actual_psi: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5, 2)))
    temperatura_operacion_max: Optional[int] = Field(default=None, sa_column=Column(SmallInteger))
    observaciones: Optional[str] = Field(default=None, sa_column=Column(Text))
    activo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text("true")))
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    )
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL")))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP, onupdate=text("now()")))
    actualizado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL")))
    
    __table_args__ = (
        CheckConstraint('vida_actual >= 1 AND vida_actual <= 11', name='neumaticos_vida_actual_check'),
        CheckConstraint('costo_compra >= 0', name='neumaticos_costo_compra_check'),
        CheckConstraint('kilometraje_acumulado >= 0', name='neumaticos_kilometraje_acumulado_check'),
        CheckConstraint('kilometraje_vida_actual >= 0', name='neumaticos_kilometraje_vida_actual_check'),
        CheckConstraint("dot ~ '^[0-9]{4}$'", name='neumaticos_dot_format_check'),
        CheckConstraint("estado_actual IN ('EN_STOCK', 'INSTALADO', 'EN_REPARACION', 'EN_REENCAUCHE', 'DESECHADO', 'EN_TRANSITO')", name='neumaticos_estado_actual_check'),
        Index('idx_neumaticos_modelo', 'modelo_id'),
        Index('idx_neumaticos_numero_serie', 'numero_serie'),
        Index('idx_neumaticos_estado', 'estado_actual'),
    )
