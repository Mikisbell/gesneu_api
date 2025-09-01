"""
Modelos limpios de neumáticos - Usando nombres únicos para evitar conflictos
"""
from datetime import date, datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from uuid import UUID, uuid4
from decimal import Decimal
from enum import Enum

from sqlalchemy import Column, String, Boolean, Text, Integer, Numeric, Date, SmallInteger, TIMESTAMP, BigInteger, ForeignKey, Index, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy import text

# ============================================================================
# ENUMS ESPECÍFICOS DE NEUMÁTICOS
# ============================================================================

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

class TipoEventoNeumaticoEnum(str, Enum):
    INSTALACION = "INSTALACION"
    REMOCION = "REMOCION"
    ROTACION = "ROTACION"
    REPARACION = "REPARACION"
    INSPECCION = "INSPECCION"
    CAMBIO_POSICION = "CAMBIO_POSICION"
    DESECHO = "DESECHO"

# ============================================================================
# MODELO BASE SIMPLE PARA NEUMÁTICOS
# ============================================================================

class BaseNeumaticoModel(SQLModel):
    """Base model simple para neumáticos sin campos de auditoría automáticos"""
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único"
    )
    activo: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
        description="Indica si el registro está activo"
    )
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP, nullable=False, server_default=text("now()")),
        description="Fecha de creación"
    )
    actualizado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(TIMESTAMP, onupdate=text("now()")),
        description="Fecha de última actualización"
    )

# ============================================================================
# FABRICANTES DE NEUMÁTICOS
# ============================================================================

class FabricanteNeumaticoClean(BaseNeumaticoModel, table=True):
    __tablename__ = "fabricantes_neumatico_clean"
    
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
    modelos: List["ModeloNeumaticoClean"] = Relationship(back_populates="fabricante")

    __table_args__ = (
        Index('idx_fabricantes_neumatico_clean_nombre', 'nombre', unique=True),
    )

# ============================================================================
# MODELOS DE NEUMÁTICOS
# ============================================================================

class ModeloNeumaticoClean(BaseNeumaticoModel, table=True):
    __tablename__ = "modelos_neumatico_clean"
    
    fabricante_id: UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("fabricantes_neumatico_clean.id", ondelete="CASCADE"), nullable=False),
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
    kilometraje_esperado: Optional[int] = Field(
        None, sa_column=Column(Integer),
        description="Kilometraje esperado"
    )
    costo_promedio: Optional[Decimal] = Field(
        None, sa_column=Column(Numeric(10,2)),
        description="Costo promedio"
    )

    # Relationships
    fabricante: Optional["FabricanteNeumaticoClean"] = Relationship(back_populates="modelos")
    neumaticos: List["NeumaticoClean"] = Relationship(back_populates="modelo")

    __table_args__ = (
        UniqueConstraint('fabricante_id', 'nombre_modelo', 'medida', name='uq_modelo_clean_fabricante_medida'),
        Index('idx_modelos_neumatico_clean_fabricante', 'fabricante_id'),
        Index('idx_modelos_neumatico_clean_medida', 'medida'),
    )

# ============================================================================
# NEUMÁTICOS
# ============================================================================

class NeumaticoClean(BaseNeumaticoModel, table=True):
    __tablename__ = "neumaticos_clean"
    
    modelo_id: UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("modelos_neumatico_clean.id", ondelete="CASCADE"), nullable=False),
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
    modelo: Optional["ModeloNeumaticoClean"] = Relationship(back_populates="neumaticos")
    eventos: List["EventoNeumaticoClean"] = Relationship(back_populates="neumatico")

    __table_args__ = (
        Index('idx_neumaticos_clean_numero_serie', 'numero_serie', unique=True),
        Index('idx_neumaticos_clean_estado', 'estado'),
        Index('idx_neumaticos_clean_modelo', 'modelo_id'),
        CheckConstraint('kilometraje_actual >= 0', name='ck_neumaticos_clean_kilometraje_positivo'),
        CheckConstraint('numero_recauchutajes >= 0', name='ck_neumaticos_clean_recauchutajes_positivo'),
    )

# ============================================================================
# EVENTOS DE NEUMÁTICOS
# ============================================================================

class EventoNeumaticoClean(BaseNeumaticoModel, table=True):
    __tablename__ = "eventos_neumaticos_clean"
    
    neumatico_id: UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("neumaticos_clean.id", ondelete="CASCADE"), nullable=False),
        description="ID del neumático"
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
    neumatico: Optional["NeumaticoClean"] = Relationship(back_populates="eventos")

    __table_args__ = (
        Index('idx_eventos_neumaticos_clean_neumatico', 'neumatico_id'),
        Index('idx_eventos_neumaticos_clean_fecha', 'fecha_evento'),
        Index('idx_eventos_neumaticos_clean_tipo', 'tipo_evento'),
    )
