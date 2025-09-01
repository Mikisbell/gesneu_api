"""
Modelos consolidados del módulo de neumáticos - Sin conflictos de metadatos
"""
from datetime import date, datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from uuid import UUID, uuid4
from decimal import Decimal
from enum import Enum

from ges_neu_api.core.base_models import BaseModel, EstadoNeumaticoEnum
from sqlalchemy import Column, String, Boolean, Text, Integer, Numeric, Date, SmallInteger, TIMESTAMP, BigInteger, ForeignKey, Index, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy import text

# ============================================================================
# ENUMS ESPECÍFICOS DE NEUMÁTICOS
# ============================================================================

class TipoEventoNeumaticoEnum(str, Enum):
    INSTALACION = "INSTALACION"
    REMOCION = "REMOCION"
    ROTACION = "ROTACION"
    REPARACION = "REPARACION"
    INSPECCION = "INSPECCION"
    CAMBIO_POSICION = "CAMBIO_POSICION"
    DESECHO = "DESECHO"

class TipoMedicionEnum(str, Enum):
    PROFUNDIDAD_BANDA = "PROFUNDIDAD_BANDA"
    PRESION = "PRESION"
    TEMPERATURA = "TEMPERATURA"
    DESGASTE_IRREGULAR = "DESGASTE_IRREGULAR"

# ============================================================================
# FABRICANTES Y MODELOS DE NEUMÁTICOS
# ============================================================================

class FabricanteNeumaticoConsolidado(BaseModel, table=True):
    __tablename__ = "fabricantes_neumatico"
    
    nombre: str = Field(
        sa_column=Column(String(100), nullable=False, unique=True),
        description="Nombre del fabricante"
    )
    pais_origen: Optional[str] = Field(
        None, sa_column=Column(String(50)),
        description="País de origen del fabricante"
    )
    sitio_web: Optional[str] = Field(
        None, sa_column=Column(String(200)),
        description="Sitio web oficial"
    )
    contacto_tecnico: Optional[str] = Field(
        None, sa_column=Column(String(200)),
        description="Información de contacto técnico"
    )

    # Relationships
    modelos: List["ModeloNeumaticoConsolidado"] = Relationship(back_populates="fabricante")

class ModeloNeumaticoConsolidado(BaseModel, table=True):
    __tablename__ = "modelos_neumatico"
    
    fabricante_id: UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("fabricantes_neumatico.id", ondelete="CASCADE"), nullable=False),
        description="ID del fabricante"
    )
    nombre_modelo: str = Field(
        sa_column=Column(String(100), nullable=False),
        description="Nombre del modelo"
    )
    medida: str = Field(
        sa_column=Column(String(50), nullable=False),
        description="Medida del neumático (ej: 295/80R22.5)"
    )
    tipo_construccion: Optional[str] = Field(
        None, sa_column=Column(String(50)),
        description="Tipo de construcción (radial, diagonal, etc.)"
    )
    indice_carga: Optional[str] = Field(
        None, sa_column=Column(String(10)),
        description="Índice de carga"
    )
    indice_velocidad: Optional[str] = Field(
        None, sa_column=Column(String(5)),
        description="Índice de velocidad"
    )
    profundidad_banda_nueva_mm: Optional[Decimal] = Field(
        None, sa_column=Column(Numeric(5,2)),
        description="Profundidad de banda nueva en mm"
    )
    presion_recomendada_psi: Optional[Decimal] = Field(
        None, sa_column=Column(Numeric(5,2)),
        description="Presión recomendada en PSI"
    )
    peso_kg: Optional[Decimal] = Field(
        None, sa_column=Column(Numeric(6,2)),
        description="Peso en kilogramos"
    )
    diametro_externo_mm: Optional[int] = Field(
        None, sa_column=Column(Integer),
        description="Diámetro externo en mm"
    )
    ancho_banda_mm: Optional[int] = Field(
        None, sa_column=Column(Integer),
        description="Ancho de banda en mm"
    )
    diametro_rin_pulgadas: Optional[Decimal] = Field(
        None, sa_column=Column(Numeric(4,1)),
        description="Diámetro del rin en pulgadas"
    )
    tipo_vehiculo_aplicacion: Optional[str] = Field(
        None, sa_column=Column(String(50)),
        description="Tipo de vehículo de aplicación"
    )
    tipo_terreno_recomendado: Optional[str] = Field(
        None, sa_column=Column(String(100)),
        description="Tipo de terreno recomendado"
    )
    temperatura_trabajo_min_c: Optional[int] = Field(
        None, sa_column=Column(Integer),
        description="Temperatura mínima de trabajo en °C"
    )
    temperatura_trabajo_max_c: Optional[int] = Field(
        None, sa_column=Column(Integer),
        description="Temperatura máxima de trabajo en °C"
    )
    capacidad_recauchutaje: Optional[int] = Field(
        None, sa_column=Column(Integer),
        description="Número de recauchutajes posibles"
    )
    kilometraje_esperado: Optional[int] = Field(
        None, sa_column=Column(Integer),
        description="Kilometraje esperado"
    )
    costo_promedio: Optional[Decimal] = Field(
        None, sa_column=Column(Numeric(10,2)),
        description="Costo promedio"
    )

    # Relationships
    fabricante: Optional["FabricanteNeumaticoConsolidado"] = Relationship(back_populates="modelos")
    neumaticos: List["NeumaticoConsolidado"] = Relationship(back_populates="modelo")

    __table_args__ = (
        UniqueConstraint('fabricante_id', 'nombre_modelo', 'medida', name='uq_modelo_fabricante_medida'),
        Index('idx_modelos_neumatico_fabricante', 'fabricante_id'),
        Index('idx_modelos_neumatico_medida', 'medida'),
    )

# ============================================================================
# NEUMÁTICOS
# ============================================================================

class NeumaticoConsolidado(BaseModel, table=True):
    __tablename__ = "neumaticos"
    
    modelo_id: UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("modelos_neumatico.id", ondelete="CASCADE"), nullable=False),
        description="ID del modelo de neumático"
    )
    numero_serie: str = Field(
        sa_column=Column(String(100), nullable=False, unique=True),
        description="Número de serie único"
    )
    dot: Optional[str] = Field(
        None, sa_column=Column(String(20)),
        description="Código DOT (fecha de fabricación)"
    )
    fecha_fabricacion: Optional[date] = Field(
        None, sa_column=Column(Date),
        description="Fecha de fabricación"
    )
    fecha_compra: Optional[date] = Field(
        None, sa_column=Column(Date),
        description="Fecha de compra"
    )
    costo_compra: Optional[Decimal] = Field(
        None, sa_column=Column(Numeric(10,2)),
        description="Costo de compra"
    )
    proveedor_id: Optional[UUID] = Field(
        None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("proveedores.id", ondelete="SET NULL")),
        description="ID del proveedor"
    )
    estado: EstadoNeumaticoEnum = Field(
        default=EstadoNeumaticoEnum.EN_STOCK,
        sa_column=Column(String(20), nullable=False, server_default=text("'EN_STOCK'")),
        description="Estado actual del neumático"
    )
    kilometraje_actual: int = Field(
        default=0,
        sa_column=Column(Integer, nullable=False, server_default=text("0")),
        description="Kilometraje acumulado"
    )
    profundidad_actual_mm: Optional[Decimal] = Field(
        None, sa_column=Column(Numeric(5,2)),
        description="Profundidad actual de la banda en mm"
    )
    presion_actual_psi: Optional[Decimal] = Field(
        None, sa_column=Column(Numeric(5,2)),
        description="Presión actual en PSI"
    )
    posicion_actual: Optional[str] = Field(
        None, sa_column=Column(String(20)),
        description="Posición actual en el vehículo"
    )
    vehiculo_actual_id: Optional[UUID] = Field(
        None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("vehiculos.id", ondelete="SET NULL")),
        description="ID del vehículo donde está instalado"
    )
    fecha_instalacion: Optional[date] = Field(
        None, sa_column=Column(Date),
        description="Fecha de instalación actual"
    )
    numero_recauchutajes: int = Field(
        default=0,
        sa_column=Column(Integer, nullable=False, server_default=text("0")),
        description="Número de recauchutajes realizados"
    )
    observaciones: Optional[str] = Field(
        None, sa_column=Column(Text),
        description="Observaciones generales"
    )

    # Relationships
    modelo: Optional["ModeloNeumaticoConsolidado"] = Relationship(back_populates="neumaticos")
    eventos: List["EventoNeumaticoConsolidado"] = Relationship(back_populates="neumatico")
    mediciones: List["MedicionProfundidadConsolidado"] = Relationship(back_populates="neumatico")

    __table_args__ = (
        Index('idx_neumaticos_numero_serie', 'numero_serie', unique=True),
        Index('idx_neumaticos_estado', 'estado'),
        Index('idx_neumaticos_vehiculo', 'vehiculo_actual_id'),
        Index('idx_neumaticos_modelo', 'modelo_id'),
        CheckConstraint('kilometraje_actual >= 0', name='ck_neumaticos_kilometraje_positivo'),
        CheckConstraint('numero_recauchutajes >= 0', name='ck_neumaticos_recauchutajes_positivo'),
    )

# ============================================================================
# EVENTOS DE NEUMÁTICOS
# ============================================================================

class EventoNeumaticoConsolidado(BaseModel, table=True):
    __tablename__ = "eventos_neumaticos"
    
    neumatico_id: UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("neumaticos.id", ondelete="CASCADE"), nullable=False),
        description="ID del neumático"
    )
    vehiculo_id: Optional[UUID] = Field(
        None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("vehiculos.id", ondelete="SET NULL")),
        description="ID del vehículo relacionado"
    )
    tipo_evento: TipoEventoNeumaticoEnum = Field(
        sa_column=Column(String(20), nullable=False),
        description="Tipo de evento"
    )
    fecha_evento: datetime = Field(
        sa_column=Column(TIMESTAMP, nullable=False, server_default=text("now()")),
        description="Fecha y hora del evento"
    )
    kilometraje_vehiculo: Optional[int] = Field(
        None, sa_column=Column(Integer),
        description="Kilometraje del vehículo al momento del evento"
    )
    posicion_anterior: Optional[str] = Field(
        None, sa_column=Column(String(20)),
        description="Posición anterior del neumático"
    )
    posicion_nueva: Optional[str] = Field(
        None, sa_column=Column(String(20)),
        description="Nueva posición del neumático"
    )
    motivo: Optional[str] = Field(
        None, sa_column=Column(Text),
        description="Motivo del evento"
    )
    observaciones: Optional[str] = Field(
        None, sa_column=Column(Text),
        description="Observaciones del evento"
    )
    costo_evento: Optional[Decimal] = Field(
        None, sa_column=Column(Numeric(10,2)),
        description="Costo asociado al evento"
    )
    realizado_por: Optional[str] = Field(
        None, sa_column=Column(String(100)),
        description="Persona que realizó el evento"
    )

    # Relationships
    neumatico: Optional["NeumaticoConsolidado"] = Relationship(back_populates="eventos")

    __table_args__ = (
        Index('idx_eventos_neumaticos_neumatico', 'neumatico_id'),
        Index('idx_eventos_neumaticos_fecha', 'fecha_evento'),
        Index('idx_eventos_neumaticos_tipo', 'tipo_evento'),
        Index('idx_eventos_neumaticos_vehiculo', 'vehiculo_id'),
    )

# ============================================================================
# MEDICIONES DE PROFUNDIDAD
# ============================================================================

class MedicionProfundidadConsolidado(BaseModel, table=True):
    __tablename__ = "mediciones_profundidad"
    
    neumatico_id: UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("neumaticos.id", ondelete="CASCADE"), nullable=False),
        description="ID del neumático"
    )
    fecha_medicion: datetime = Field(
        sa_column=Column(TIMESTAMP, nullable=False, server_default=text("now()")),
        description="Fecha y hora de la medición"
    )
    kilometraje_vehiculo: Optional[int] = Field(
        None, sa_column=Column(Integer),
        description="Kilometraje del vehículo al momento de la medición"
    )
    profundidad_exterior_mm: Decimal = Field(
        sa_column=Column(Numeric(5,2), nullable=False),
        description="Profundidad en el exterior en mm"
    )
    profundidad_centro_mm: Decimal = Field(
        sa_column=Column(Numeric(5,2), nullable=False),
        description="Profundidad en el centro en mm"
    )
    profundidad_interior_mm: Decimal = Field(
        sa_column=Column(Numeric(5,2), nullable=False),
        description="Profundidad en el interior en mm"
    )
    presion_psi: Optional[Decimal] = Field(
        None, sa_column=Column(Numeric(5,2)),
        description="Presión medida en PSI"
    )
    temperatura_c: Optional[Decimal] = Field(
        None, sa_column=Column(Numeric(5,2)),
        description="Temperatura medida en °C"
    )
    observaciones: Optional[str] = Field(
        None, sa_column=Column(Text),
        description="Observaciones de la medición"
    )
    medido_por: Optional[str] = Field(
        None, sa_column=Column(String(100)),
        description="Persona que realizó la medición"
    )

    # Relationships
    neumatico: Optional["NeumaticoConsolidado"] = Relationship(back_populates="mediciones")

    __table_args__ = (
        Index('idx_mediciones_profundidad_neumatico', 'neumatico_id'),
        Index('idx_mediciones_profundidad_fecha', 'fecha_medicion'),
        CheckConstraint('profundidad_exterior_mm >= 0', name='ck_mediciones_prof_exterior_positiva'),
        CheckConstraint('profundidad_centro_mm >= 0', name='ck_mediciones_prof_centro_positiva'),
        CheckConstraint('profundidad_interior_mm >= 0', name='ck_mediciones_prof_interior_positiva'),
    )
