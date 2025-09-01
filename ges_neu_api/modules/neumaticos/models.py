"""
Modelos del módulo de neumáticos - Alineados exactamente con ESQUEMA_BD_REAL.md
Sin herencia BaseModel para evitar conflictos de metadata SQLAlchemy
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, UniqueConstraint, CheckConstraint, Integer, Numeric, Date, SmallInteger, Index, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import Enum as SQLAlchemyEnum, text

if TYPE_CHECKING:
    from ..auth.models import Usuario
    from ..vehiculos.models import Vehiculos, PosicionesNeumatico
    from ..catalogos.models import Proveedor

# Enums basados en el esquema de la BD
class EstadoNeumaticoEnum(str, Enum):
    EN_STOCK = "EN_STOCK"
    INSTALADO = "INSTALADO"
    EN_REPARACION = "EN_REPARACION"
    EN_DESECHO = "EN_DESECHO"
    VENDIDO = "VENDIDO"
    PERDIDO = "PERDIDO"
    EN_TRANSITO = "EN_TRANSITO"
    EN_RECICLAJE = "EN_RECICLAJE"
    DESECHADO = "DESECHADO"

class TipoConstruccionEnum(str, Enum):
    RADIAL = "RADIAL"
    DIAGONAL = "DIAGONAL"
    MIXTA = "MIXTA"

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
    """Modelo para neumáticos con campos de auditoría"""
    __tablename__ = "neumaticos"
    __table_args__ = {'extend_existing': True}
    
    # Campos exactos del esquema real
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    )
    numero_serie: Optional[str] = Field(default=None, sa_column=Column(String(100)))
    dot: Optional[str] = Field(default=None, sa_column=Column(String(20)))  # dot_code domain type
    modelo_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("modelos_neumatico.id"), nullable=False))
    fecha_compra: date = Field(sa_column=Column(Date, nullable=False))
    fecha_fabricacion: Optional[date] = Field(default=None, sa_column=Column(Date))
    costo_compra: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    moneda_compra: str = Field(default="PEN", sa_column=Column(String(3), server_default=text("'PEN'")))
    proveedor_compra_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("proveedores.id")))
    es_reencauchado: bool = Field(default=False, sa_column=Column(Boolean, nullable=False, server_default=text("false")))
    vida_actual: int = Field(default=1, sa_column=Column(SmallInteger, nullable=False, server_default=text("1")))
    estado_actual: str = Field(default="EN_STOCK", sa_column=Column(String(20), nullable=False, server_default=text("'EN_STOCK'")))  # estado_neumatico_enum
    ubicacion_actual_vehiculo_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("vehiculos.id")))
    ubicacion_actual_posicion_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("posiciones_neumatico.id")))
    fecha_ultimo_evento: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP))
    profundidad_inicial_mm: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5, 2)))
    kilometraje_acumulado: int = Field(default=0, sa_column=Column(Integer, nullable=False, server_default=text("0")))
    reencauches_realizados: int = Field(default=0, sa_column=Column(SmallInteger, nullable=False, server_default=text("0")))
    fecha_desecho: Optional[date] = Field(default=None, sa_column=Column(Date))
    motivo_desecho_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("motivos_desecho.id")))
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    )
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL")))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP, onupdate=text("now()")))
    actualizado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL")))
    ubicacion_almacen_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("almacenes.id")))
    sensor_id: Optional[str] = Field(default=None, sa_column=Column(String(100)))
    profundidad_remanente_actual_mm: Decimal = Field(sa_column=Column(Numeric(5, 2), nullable=False))
    fecha_ultima_medicion_profundidad: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP))
    kilometraje_vida_actual: Optional[int] = Field(default=0, sa_column=Column(Integer, server_default=text("0")))
    fecha_inicio_vida_actual: Optional[date] = Field(default=None, sa_column=Column(Date))
    odometro_instalacion_vida_actual: Optional[int] = Field(default=None, sa_column=Column(Integer))
    tasa_desgaste_actual_mm_km: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 8)))
    vida_util_restante_km: Optional[int] = Field(default=None, sa_column=Column(Integer))
    fecha_ultimo_reencauche: Optional[date] = Field(default=None, sa_column=Column(Date))
    activo: bool = Field(default=True, sa_column=Column(Boolean, server_default=text("true")))
    proxima_inspeccion_fecha: Optional[date] = Field(default=None, sa_column=Column(Date))
    proxima_inspeccion_km: Optional[int] = Field(default=None, sa_column=Column(Integer))
    profundidad_inicio_vida_actual_mm: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5, 2)))
    
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

class EspecificacionesDesgaste(SQLModel, table=True):
    """Especificaciones de desgaste por modelo y posición - Esquema exacto ESQUEMA_BD_REAL.md"""
    __tablename__ = 'especificaciones_desgaste'
    
    # Campos exactos del esquema real
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    )
    modelo_neumatico_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("modelos_neumatico.id"), nullable=False))
    tipo_posicion: str = Field(sa_column=Column(String(50), nullable=False))
    vida_util_km_min: int = Field(sa_column=Column(Integer, nullable=False))
    vida_util_km_max: int = Field(sa_column=Column(Integer, nullable=False))
    descripcion_estado: str = Field(sa_column=Column(String(100), nullable=False))
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    )
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL")))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP, onupdate=text("now()")))
    actualizado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL")))
    
    __table_args__ = (
        CheckConstraint('vida_util_km_min < vida_util_km_max', name='especificaciones_desgaste_km_check'),
        Index('idx_especificaciones_modelo', 'modelo_neumatico_id'),
    )

class ParametrosRendimientoEsperadoModelo(SQLModel, table=True):
    """Parámetros de rendimiento esperado por modelo - Esquema exacto ESQUEMA_BD_REAL.md"""
    __tablename__ = 'parametros_rendimiento_esperado_modelo'
    
    # Campos exactos del esquema real
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    )
    modelo_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("modelos_neumatico.id"), nullable=False))
    tipo_eje_aplicacion: str = Field(sa_column=Column(String(20), nullable=False))
    km_esperado_vida_original_min: Optional[int] = Field(default=None, sa_column=Column(Integer))
    km_esperado_vida_original_max: Optional[int] = Field(default=None, sa_column=Column(Integer))
    activo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text("true")))
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    )
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL")))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP, onupdate=text("now()")))
    actualizado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL")))
    
    __table_args__ = (
        CheckConstraint('km_esperado_vida_original_min >= 0', name='parametros_rendimiento_km_min_check'),
        CheckConstraint('km_esperado_vida_original_max >= km_esperado_vida_original_min', name='parametros_rendimiento_km_max_check'),
        UniqueConstraint('modelo_id', 'tipo_eje_aplicacion', name='uq_parametros_rendimiento_modelo_eje'),
        Index('idx_parametros_rendimiento_modelo', 'modelo_id'),
    )

class ModelosPosicionesPermitidas(SQLModel, table=True):
    """Posiciones permitidas por modelo de neumático - Esquema exacto ESQUEMA_BD_REAL.md"""
    __tablename__ = 'modelos_posiciones_permitidas'
    
    # Campos exactos del esquema real
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    )
    modelo_neumatico_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("modelos_neumatico.id"), nullable=False))
    posicion_neumatico_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("posiciones_neumatico.id"), nullable=False))
    activo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text("true")))
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    )
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL")))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP, onupdate=text("now()")))
    actualizado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL")))
    
    __table_args__ = (
        UniqueConstraint('modelo_neumatico_id', 'posicion_neumatico_id', name='uq_modelo_posicion_permitida'),
        Index('idx_modelos_posiciones_modelo', 'modelo_neumatico_id'),
        Index('idx_modelos_posiciones_posicion', 'posicion_neumatico_id'),
    )

# Modelos completamente independientes sin relaciones SQLModel para evitar conflictos de metadata