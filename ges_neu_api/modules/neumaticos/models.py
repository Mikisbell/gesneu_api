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
from sqlalchemy import Column, String, Boolean, DateTime, UniqueConstraint, CheckConstraint, Integer, Numeric, Date, SmallInteger, Index, TIMESTAMP, text
from sqlalchemy import Enum as SQLAlchemyEnum

if TYPE_CHECKING:
    from ..auth.models import Usuario
    from ..vehiculos.models import Vehiculos, PosicionesNeumatico
    from ..catalogos.models import Proveedor

# Enums basados en el esquema de la BD
class EstadoNeumaticoEnum(str, Enum):
    EN_STOCK = "EN_STOCK"
    INSTALADO = "INSTALADO"
    EN_REPARACION = "EN_REPARACION"
    EN_REENCAUCHE = "EN_REENCAUCHE"
    DESECHADO = "DESECHADO"
    EN_TRANSITO = "EN_TRANSITO"

class TipoConstruccionEnum(str, Enum):
    RADIAL = "RADIAL"
    DIAGONAL = "DIAGONAL"
    MIXTA = "MIXTA"

class TipoEjeEnum(str, Enum):
    DIRECCION = "DIRECCION"
    TRACCION = "TRACCION"
    ARRASTRE = "ARRASTRE"
    ELEVADOR = "ELEVADOR"
    RETRACTIL = "RETRACTIL"
    OTRO = "OTRO"

class FabricanteNeumatico(SQLModel, table=True):
    """Fabricantes de neumáticos - Alineado exactamente con ESQUEMA_COMPLETO_BD.md líneas 950-961"""
    __tablename__ = 'fabricantes_neumatico'
    
    # Campos exactos según ESQUEMA_COMPLETO_BD.md
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    nombre: str = Field(sa_column=Column(String(100), nullable=False))
    codigo_abreviado: Optional[str] = Field(default=None, sa_column=Column(String(10), nullable=True))
    pais_origen: Optional[str] = Field(default=None, sa_column=Column(String(50), nullable=True))
    sitio_web: Optional[str] = Field(default=None, sa_column=Column(String(255), nullable=True))
    activo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text("true")))
    creado_en: datetime = Field(
        sa_column=Column(DateTime(timezone=False), nullable=False, server_default=text("now()"))
    )
    creado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=False)))
    actualizado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")
    
    __table_args__ = (
        CheckConstraint('length(nombre::text) >= 2', name='fabricantes_neumatico_nombre_length'),
        UniqueConstraint('codigo_abreviado', name='fabricantes_neumatico_codigo_abreviado_key'),
        Index(
            'idx_fabricantes_nombre_unique',
            text('f_immutable_lower_unaccent((nombre)::text)'),
            unique=True,
            postgresql_where=text('activo = true')
        ),
    )

class ModeloNeumatico(SQLModel, table=True):
    """Modelos de neumáticos - Alineado exactamente con esquema real PostgreSQL"""
    __tablename__ = 'modelos_neumatico'
    
    # Campos exactos según esquema BD real
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    fabricante_id: UUID = Field(foreign_key="fabricantes_neumatico.id")
    nombre_modelo: str = Field(sa_column=Column(String(100), nullable=False))
    medida: str = Field(sa_column=Column(String(20), nullable=False))
    indice_carga: Optional[str] = Field(default=None, sa_column=Column(String(5)))
    indice_velocidad: Optional[str] = Field(default=None, sa_column=Column(String(2)))
    profundidad_original_mm: Decimal = Field(sa_column=Column(Numeric(5, 2), nullable=False))
    presion_recomendada_psi: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5, 2)))
    permite_reencauche: bool = Field(default=False, sa_column=Column(Boolean, nullable=False, server_default=text("false")))
    reencauches_maximos: Optional[int] = Field(default=0, sa_column=Column(SmallInteger, server_default=text("0")))
    patron_dibujo: Optional[str] = Field(default=None, sa_column=Column(String(50)))
    tipo_servicio: Optional[str] = Field(default=None, sa_column=Column(String(50)))
    posicion_uso_recomendada: Optional[TipoEjeEnum] = Field(default=None, sa_column=Column(SQLAlchemyEnum(TipoEjeEnum, name="tipo_eje_enum")))
    diseno_predominante_para_eje: Optional[TipoEjeEnum] = Field(default=None, sa_column=Column(SQLAlchemyEnum(TipoEjeEnum, name="tipo_eje_enum")))
    vida_util_teorica_km: Optional[int] = Field(default=None, sa_column=Column(Integer))
    profundidad_minima_retiro_mm: Decimal = Field(default=Decimal('1.6'), sa_column=Column(Numeric(5, 2), nullable=False, server_default=text("1.6")))
    tasa_desgaste_esperada_mm_km: Decimal = Field(sa_column=Column(Numeric(10, 8), nullable=False))
    activo: Optional[bool] = Field(default=True, sa_column=Column(Boolean, nullable=True, server_default=text("true")))
    frecuencia_inspeccion_km: Optional[int] = Field(default=5000, sa_column=Column(Integer, nullable=True, server_default=text("5000")))
    max_vidas_utiles: Optional[int] = Field(default=5, sa_column=Column(Integer, nullable=True, server_default=text("5")))
    porcentaje_desgaste_por_vida: Optional[Decimal] = Field(default=Decimal('10.0'), sa_column=Column(Numeric(5, 2), server_default=text("10.0")))
    creado_en: datetime = Field(sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")))
    creado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP(timezone=True)))
    actualizado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")
    
    __table_args__ = (
        CheckConstraint('max_vidas_utiles > 0', name='chk_max_vidas_utiles_positivo'),
        CheckConstraint('porcentaje_desgaste_por_vida >= 0', name='chk_porcentaje_desgaste_positivo'),
        CheckConstraint('profundidad_minima_retiro_mm > 0', name='chk_profundidad_minima_positiva'),
        CheckConstraint('tasa_desgaste_esperada_mm_km > 0', name='chk_tasa_desgaste_positiva'),
        CheckConstraint('presion_recomendada_psi IS NULL OR presion_recomendada_psi > 0', name='modelos_neumatico_presion_recomendada_psi_check'),
        CheckConstraint('profundidad_minima_retiro_mm > 0 AND profundidad_minima_retiro_mm <= profundidad_original_mm', name='modelos_neumatico_profundidad_minima_retiro_mm_check'),
        CheckConstraint('profundidad_original_mm > 0', name='modelos_neumatico_profundidad_original_mm_check'),
        CheckConstraint('reencauches_maximos >= 0 AND reencauches_maximos <= 10', name='modelos_neumatico_reencauches_maximos_check'),
        CheckConstraint('vida_util_teorica_km IS NULL OR vida_util_teorica_km > 0', name='modelos_neumatico_vida_util_teorica_km_check'),
        Index('idx_modelos_fabricante', 'fabricante_id'),
        Index(
            'idx_modelos_unique',
            'fabricante_id',
            text('f_immutable_lower_unaccent(nombre_modelo::text)'),
            'medida',
            unique=True,
            postgresql_where=text('fabricante_id IS NOT NULL')
        ),
    )

class Neumatico(SQLModel, table=True):
    """Modelo para neumáticos con campos de auditoría"""
    __tablename__ = "neumaticos"
    __table_args__ = {'extend_existing': True}
    
    # Campos exactos del esquema real
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    numero_serie: Optional[str] = Field(default=None, max_length=100)
    dot: Optional[str] = Field(default=None, sa_column=Column(String))  # dominio dot_code mapeado a String
    modelo_id: UUID = Field(foreign_key="modelos_neumatico.id")
    fecha_compra: date
    fecha_fabricacion: Optional[date] = Field(default=None)
    costo_compra: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    moneda_compra: Optional[str] = Field(default="PEN", sa_column=Column(String(3), server_default=text("'PEN'::character varying")))
    proveedor_compra_id: Optional[UUID] = Field(default=None, foreign_key="proveedores.id")
    es_reencauchado: bool = Field(sa_column=Column(Boolean, nullable=False, server_default=text("false")))
    vida_actual: int = Field(sa_column=Column(SmallInteger, nullable=False, server_default=text("1")))
    estado_actual: EstadoNeumaticoEnum = Field(
        sa_column=Column(
            SQLAlchemyEnum(EstadoNeumaticoEnum, name="estado_neumatico_enum"),
            nullable=False,
            server_default=text("'EN_STOCK'::estado_neumatico_enum")
        )
    )
    ubicacion_actual_vehiculo_id: Optional[UUID] = Field(default=None, foreign_key="vehiculos.id")
    ubicacion_actual_posicion_id: Optional[UUID] = Field(default=None, foreign_key="posiciones_neumatico.id")
    fecha_ultimo_evento: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP(timezone=True)))
    profundidad_inicial_mm: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5, 2)))
    kilometraje_acumulado: int = Field(sa_column=Column(Integer, nullable=False, server_default=text("0")))
    reencauches_realizados: int = Field(sa_column=Column(SmallInteger, nullable=False, server_default=text("0")))
    fecha_desecho: Optional[date] = Field(default=None)
    motivo_desecho_id: Optional[UUID] = Field(default=None, foreign_key="motivos_desecho.id")
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    )
    creado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP(timezone=True)))
    actualizado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")
    ubicacion_almacen_id: Optional[UUID] = Field(default=None, foreign_key="almacenes.id")
    sensor_id: Optional[str] = Field(default=None, max_length=100)
    profundidad_remanente_actual_mm: Decimal = Field(sa_column=Column(Numeric(5, 2), nullable=False))
    fecha_ultima_medicion_profundidad: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP(timezone=True)))
    kilometraje_vida_actual: Optional[int] = Field(default=0, sa_column=Column(Integer, server_default=text("0")))
    fecha_inicio_vida_actual: Optional[date] = Field(default=None)
    odometro_instalacion_vida_actual: Optional[int] = Field(default=None)
    tasa_desgaste_actual_mm_km: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 8)))
    vida_util_restante_km: Optional[int] = Field(default=None)
    fecha_ultimo_reencauche: Optional[date] = Field(default=None)
    activo: Optional[bool] = Field(default=True, sa_column=Column(Boolean, server_default=text("true")))
    proxima_inspeccion_fecha: Optional[date] = Field(default=None, sa_column=Column(Date))
    proxima_inspeccion_km: Optional[int] = Field(default=None, sa_column=Column(Integer))
    profundidad_inicio_vida_actual_mm: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5, 2)))
    
    # Campos de IA para predicciones - Sprint 1
    prediccion_fecha_reemplazo: Optional[date] = Field(default=None, sa_column=Column(Date))
    confianza_prediccion: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(3, 2)))
    fecha_ultima_prediccion: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP))
    modelo_prediccion_version: Optional[str] = Field(default=None, sa_column=Column(String(50)))
    
    __table_args__ = (
        # Constraints exactos según ESQUEMA_COMPLETO_BD.md líneas 1344-1375
        CheckConstraint('vida_actual >= 1 AND vida_actual <= 11', name='neumaticos_vida_actual_check'),
        CheckConstraint('costo_compra IS NULL OR costo_compra >= 0', name='neumaticos_costo_compra_check'),
        CheckConstraint('kilometraje_acumulado >= 0', name='neumaticos_kilometraje_acumulado_check'),
        CheckConstraint('kilometraje_vida_actual >= 0', name='neumaticos_kilometraje_vida_actual_check'),
        CheckConstraint('reencauches_realizados >= 0', name='neumaticos_reencauches_realizados_check'),
        CheckConstraint('profundidad_inicial_mm IS NULL OR profundidad_inicial_mm > 0', name='neumaticos_profundidad_inicial_mm_check'),
        CheckConstraint('profundidad_remanente_actual_mm IS NULL OR (profundidad_remanente_actual_mm >= 0 AND profundidad_remanente_actual_mm <= 50)', name='neumaticos_profundidad_remanente_check'),
        CheckConstraint('tasa_desgaste_actual_mm_km IS NULL OR tasa_desgaste_actual_mm_km > 0', name='neumaticos_tasa_desgaste_actual_check'),
        CheckConstraint('vida_util_restante_km IS NULL OR vida_util_restante_km >= 0', name='neumaticos_vida_util_restante_check'),
        CheckConstraint('fecha_fabricacion IS NULL OR fecha_fabricacion <= fecha_compra', name='neumaticos_fechas_check'),
        CheckConstraint('confianza_prediccion IS NULL OR (confianza_prediccion >= 0.0 AND confianza_prediccion <= 1.0)', name='neumaticos_confianza_prediccion_check'),
        # Constraint complejo de ubicación mutuamente exclusiva según línea 1360
        CheckConstraint(
            '''((ubicacion_almacen_id IS NOT NULL AND ubicacion_actual_vehiculo_id IS NULL AND ubicacion_actual_posicion_id IS NULL AND estado_actual != 'INSTALADO') OR 
               (ubicacion_almacen_id IS NULL AND ubicacion_actual_vehiculo_id IS NOT NULL AND ubicacion_actual_posicion_id IS NOT NULL AND estado_actual = 'INSTALADO') OR 
               (ubicacion_almacen_id IS NULL AND ubicacion_actual_vehiculo_id IS NULL AND ubicacion_actual_posicion_id IS NULL AND estado_actual != 'INSTALADO'))''',
            name='chk_ubicacion_mutuamente_exclusiva'
        ),
        # Índices según esquema real
        Index('idx_neumaticos_modelo', 'modelo_id'),
        Index('idx_neumaticos_estado', 'estado_actual'),
        Index('idx_neumaticos_estado_actual', 'estado_actual', postgresql_where=text("estado_actual <> 'DESECHADO'::estado_neumatico_enum")),
        Index('idx_neumaticos_activos', 'estado_actual', postgresql_where=text("estado_actual <> 'DESECHADO'::estado_neumatico_enum")),
        Index('idx_neumaticos_estado_ubicacion', 'estado_actual', 'ubicacion_actual_vehiculo_id', 'ubicacion_actual_posicion_id', postgresql_where=text("estado_actual = 'INSTALADO'::estado_neumatico_enum")),
        Index('idx_neumaticos_fechas_compra', 'fecha_compra'),
        Index('idx_neumaticos_modelo_id', 'modelo_id'),
        Index('idx_neumaticos_prox_inspeccion', 'proxima_inspeccion_fecha', postgresql_where=text('proxima_inspeccion_fecha IS NOT NULL')),
        Index('idx_neumaticos_proximos_desecho', 'estado_actual', 'fecha_fabricacion', postgresql_where=text("estado_actual <> 'DESECHADO'::estado_neumatico_enum")),
        Index('idx_neumaticos_sensor_id', 'sensor_id', postgresql_where=text('sensor_id IS NOT NULL')),
        Index('idx_neumaticos_serie', 'numero_serie', postgresql_where=text('numero_serie IS NOT NULL')),
        Index('idx_neumaticos_tasa_desgaste', 'tasa_desgaste_actual_mm_km', postgresql_where=text('tasa_desgaste_actual_mm_km IS NOT NULL')),
        Index('idx_neumaticos_ubicacion', 'ubicacion_actual_vehiculo_id', 'ubicacion_actual_posicion_id', postgresql_where=text('ubicacion_actual_vehiculo_id IS NOT NULL')),
        Index('idx_neumaticos_ubicacion_almacen', 'ubicacion_almacen_id', postgresql_where=text('ubicacion_almacen_id IS NOT NULL')),
        Index('idx_neumaticos_vida_util_restante', 'vida_util_restante_km', postgresql_where=text('vida_util_restante_km IS NOT NULL')),
        Index('idx_neumaticos_dot', 'dot', postgresql_where=text('dot IS NOT NULL')),
        Index('uq_idx_neumatico_dot_vida', 'dot', 'vida_actual', unique=True, postgresql_where=text('dot IS NOT NULL')),
    )

class EspecificacionesDesgaste(SQLModel, table=True):
    """Especificaciones de desgaste por modelo y posición - Esquema exacto ESQUEMA_BD_REAL.md"""
    __tablename__ = 'especificaciones_desgaste'
    
    # Campos exactos del esquema real
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    modelo_neumatico_id: UUID = Field(foreign_key="modelos_neumatico.id", nullable=False)
    tipo_posicion: str = Field(sa_column=Column(String(50), nullable=False))
    vida_util_km_min: int = Field(sa_column=Column(Integer, nullable=False))
    vida_util_km_max: int = Field(sa_column=Column(Integer, nullable=False))
    descripcion_estado: str = Field(sa_column=Column(String(100), nullable=False))
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    )
    creado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP, onupdate=text("now()")))
    actualizado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")
    
    __table_args__ = (
        CheckConstraint('vida_util_km_min < vida_util_km_max', name='especificaciones_desgaste_km_check'),
        Index('idx_especificaciones_modelo', 'modelo_neumatico_id'),
    )

class ParametrosRendimientoEsperadoModelo(SQLModel, table=True):
    """Parámetros de rendimiento esperado por modelo - Esquema exacto ESQUEMA_BD_REAL.md"""
    __tablename__ = 'parametros_rendimiento_esperado_modelo'
    
    # Campos exactos del esquema real
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    modelo_id: UUID = Field(foreign_key="modelos_neumatico.id", nullable=False)
    tipo_eje_aplicacion: str = Field(sa_column=Column(String(20), nullable=False))
    km_esperado_vida_original_min: Optional[int] = Field(default=None, sa_column=Column(Integer))
    km_esperado_vida_original_max: Optional[int] = Field(default=None, sa_column=Column(Integer))
    activo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text("true")))
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    )
    creado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP, onupdate=text("now()")))
    actualizado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")
    
    __table_args__ = (
        CheckConstraint('km_esperado_vida_original_min >= 0', name='parametros_rendimiento_km_min_check'),
        CheckConstraint('km_esperado_vida_original_max >= km_esperado_vida_original_min', name='parametros_rendimiento_km_max_check'),
        UniqueConstraint('modelo_id', 'tipo_eje_aplicacion', name='uq_parametros_rendimiento_modelo_eje'),
        Index('idx_parametros_rendimiento_modelo', 'modelo_id'),
    )

class ModelosPosicionesPermitidas(SQLModel, table=True):
    """Posiciones permitidas por modelo de neumático - Alineado exactamente con ESQUEMA_COMPLETO_BD.md líneas 1228-1252"""
    __tablename__ = 'modelos_posiciones_permitidas'
    
    # Campos exactos según esquema real - Composite Primary Key
    modelo_neumatico_id: UUID = Field(foreign_key="modelos_neumatico.id", primary_key=True, nullable=False)
    posicion_neumatico_id: UUID = Field(foreign_key="posiciones_neumatico.id", primary_key=True, nullable=False)
    es_recomendado: bool = Field(default=False, sa_column=Column(Boolean, nullable=False, server_default=text("false")))
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    )
    creado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")

# Modelos completamente independientes sin relaciones SQLModel para evitar conflictos de metadata