from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    Column, String, Text, text, ForeignKey, Integer, Numeric, Boolean, 
    DateTime, Date, CheckConstraint, Index, UniqueConstraint, Table, 
    event, DDL, func, and_, or_, not_, SmallInteger, Enum as SQLAlchemyEnum
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB, ENUM as SQLEnum
from sqlalchemy.orm import relationship
from sqlmodel import SQLModel, Field, Relationship

# Import base model
from ges_neu_api.core.base_models import BaseModel

# Use string literals for type hints to avoid circular imports
if TYPE_CHECKING:
    from ges_neu_api.vehiculos.models import PosicionNeumatico, Vehiculo
    from ges_neu_api.usuarios.models import Usuario
    from .models import ModeloNeumatico

class TipoAccionOperacion(str, Enum):
    """Tipo de acción realizada sobre el neumático durante la operación"""
    MONTAJE = "montaje"
    DESMONTAJE = "desmontaje"
    INSPECCION = "inspeccion"
    MANTENIMIENTO = "mantenimiento"
    REPARACION = "reparacion"

class TipoEjeEnum(str, Enum):
    DIRECCION = "DIRECCION"
    TRACCION = "TRACCION"
    LIBRE = "LIBRE"
    ARRASTRE = "ARRASTRE"
    TANDEMMOTRIZ = "TANDEMMOTRIZ"
    TANDEMARRASTRE = "TANDEMARRASTRE"
    TRIDEM = "TRIDEM"
    RETRACTIL = "RETRACTIL"
    OTRO = "OTRO"

class BitacoraOperacionNeumatico(BaseModel, table=True):
    """Tabla de unión para la relación muchos a muchos entre BitacoraOperacion y Neumatico"""
    __tablename__ = "bitacora_operaciones_neumaticos"
    __table_args__ = (
        # Restricción única compuesta
        UniqueConstraint('operacion_id', 'neumatico_id', 'tipo_accion', 
                       name='bitacora_operaciones_neumatic_operacion_id_neumatico_id_tip_key'),
        # Índices para búsquedas frecuentes
        Index('idx_bitacora_op_neu_neumatico', 'neumatico_id'),
        Index('idx_bitacora_op_neu_operacion', 'operacion_id'),
        Index('idx_bitacora_op_neu_posicion', 'posicion_neumatico_id', 
             postgresql_where=text("posicion_neumatico_id IS NOT NULL")),
        Index('idx_bitacora_op_neu_tipo_accion', 'tipo_accion'),
        {"schema": "public", "comment": "Relación muchos a muchos entre operaciones y neumáticos"}
    )
    
    # Sobrescribir campos heredados de BaseModel para asegurar consistencia
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único del registro"
    )
    
    activo: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
        description="Indica si el registro está activo"
    )
    
    operacion_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.bitacora_operaciones.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        ),
        description="ID de la operación en la bitácora"
    )
    
    neumatico_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.neumaticos.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        ),
        description="ID del neumático involucrado en la operación"
    )
    
    tipo_accion: TipoAccionOperacion = Field(
        sa_column=Column(String(50), nullable=False, index=True),
        description="Tipo de acción realizada sobre el neumático durante la operación"
    )
    
    posicion_neumatico_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.posiciones_neumatico.id", ondelete="SET NULL"),
            index=True
        ),
        description="ID de la posición del neumático durante esta operación"
    )
    
    vehiculo_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.vehiculos.id", ondelete="SET NULL"),
            index=True
        ),
        description="ID del vehículo relacionado con la operación"
    )
    
    profundidad_inicial_mm: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(5, 2)),
        description="Profundidad inicial del dibujo en milímetros"
    )
    
    profundidad_final_mm: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(5, 2)),
        description="Profundidad final del dibujo en milímetros"
    )
    
    presion_inicial_psi: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(5, 2)),
        description="Presión inicial en PSI"
    )
    
    presion_final_psi: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(5, 2)),
        description="Presión final en PSI"
    )
    
    kilometraje_vehiculo_km: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(10, 2)),
        description="Kilometraje del vehículo al momento de la operación"
    )
    
    observaciones: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description="Observaciones adicionales sobre la operación"
    )
    
    # Relaciones
    operacion: "BitacoraOperaciones" = Relationship(back_populates="neumaticos_relacionados")
    neumatico: "Neumatico" = Relationship(back_populates="operaciones_detalladas")
    posicion_neumatico: Optional["PosicionNeumatico"] = Relationship(
        back_populates="bitacora_operaciones",
        sa_relationship_kwargs={
            "foreign_keys": "[BitacoraOperacionNeumatico.posicion_neumatico_id]"
        }
    )
    
    vehiculo: Optional["Vehiculo"] = Relationship(
        back_populates="bitacora_operaciones_neumaticos",
        sa_relationship_kwargs={
            "foreign_keys": "[BitacoraOperacionNeumatico.vehiculo_id]"
        }
    )
    
    # Usuarios relacionados
    usuario_creador: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[BitacoraOperacionNeumatico.creado_por]"}
    )
    
    usuario_actualizador: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[BitacoraOperacionNeumatico.actualizado_por]"}
    )

class ModeloNeumatico(BaseModel, table=True):
    """Modelo para los modelos de neumáticos."""
    __tablename__ = "modelos_neumatico"
    __table_args__ = (
        # Índice único para el nombre del modelo por fabricante
        Index('idx_modelos_unique', 
              'fabricante_id',
              func.f_immutable_lower_unaccent(func.text("nombre_modelo")), 
              'medida',
              unique=True,
              postgresql_where=text("fabricante_id IS NOT NULL")),
        {"schema": "public", "comment": "Modelos de neumáticos disponibles en el sistema"}
    )
    
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único del modelo de neumático"
    )
    
    fabricante_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.fabricantes_neumatico.id", ondelete="RESTRICT"),
            nullable=False,
            index=True
        ),
        description="ID del fabricante del neumático"
    )
    
    nombre_modelo: str = Field(
        sa_column=Column(String(100), nullable=False, index=True),
        description="Nombre del modelo de neumático"
    )
    
    medida: str = Field(
        sa_column=Column(String(20), nullable=False),
        description="Medida del neumático (ej: 11R22.5)"
    )
    
    indice_carga: Optional[str] = Field(
        default=None,
        sa_column=Column(String(5)),
        description="Índice de carga del neumático"
    )
    
    indice_velocidad: Optional[str] = Field(
        default=None,
        sa_column=Column(String(2)),
        description="Índice de velocidad del neumático"
    )
    
    profundidad_original_mm: Decimal = Field(
        sa_column=Column(Numeric, nullable=False),
        description="Profundidad original del dibujo en milímetros"
    )
    
    presion_recomendada_psi: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric, CheckConstraint("presion_recomendada_psi IS NULL OR presion_recomendada_psi > 0")),
        description="Presión recomendada en PSI"
    )
    
    permite_reencauche: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default=text("false")),
        description="Indica si el neumático permite reencauche"
    )
    
    reencauches_maximos: int = Field(
        default=0,
        sa_column=Column(SmallInteger, server_default=text("0")),
        description="Número máximo de reencauches permitidos"
    )
    
    patron_dibujo: Optional[str] = Field(
        default=None,
        sa_column=Column(String(50)),
        description="Patrón de dibujo del neumático"
    )
    
    tipo_servicio: Optional[str] = Field(
        default=None,
        sa_column=Column(String(50)),
        description="Tipo de servicio del neumático"
    )
    
    posicion_uso_recomendada: Optional[TipoEjeEnum] = Field(
        default=None,
        sa_column=Column(String(20)),
        description="Tipo de eje/posición para la cual este modelo es recomendado"
    )
    
    diseno_predominante_para_eje: Optional[TipoEjeEnum] = Field(
        default=None,
        sa_column=Column(String(20)),
        description="Indica si el diseño del neumático es específicamente para dirección, tracción o libre/arrastre"
    )
    
    vida_util_teorica_km: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, CheckConstraint("vida_util_teorica_km IS NULL OR vida_util_teorica_km > 0")),
        description="Vida útil teórica del neumático en kilómetros según el fabricante (Lt)"
    )
    
    profundidad_minima_retiro_mm: Decimal = Field(
        default=1.6,
        sa_column=Column(Numeric, nullable=False, server_default=text("1.6")),
        description="Profundidad mínima del dibujo (en mm) antes de que el neumático deba ser retirado"
    )
    
    tasa_desgaste_esperada_mm_km: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric, CheckConstraint("tasa_desgaste_esperada_mm_km IS NULL OR tasa_desgaste_esperada_mm_km > 0")),
        description="Tasa de desgaste esperada en mm por kilómetro"
    )
    
    frecuencia_inspeccion_km: int = Field(
        default=5000,
        sa_column=Column(Integer, server_default=text("5000")),
        description="Frecuencia recomendada de inspección en kilómetros"
    )
    
    max_vidas_utiles: int = Field(
        default=5,
        sa_column=Column(Integer, server_default=text("5")),
        description="Número máximo de vidas útiles permitidas para este modelo"
    )
    
    porcentaje_desgaste_por_vida: Decimal = Field(
        default=10.0,
        sa_column=Column(Numeric, server_default=text("10.0")),
        description="Porcentaje de desgaste por vida útil"
    )
    
    activo: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
        description="Indica si el registro está activo"
    )
    
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()")),
        description="Fecha y hora de creación del registro"
    )
    
    creado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("public.usuarios.id", ondelete="SET NULL")),
        description="Usuario que creó el registro"
    )
    
    actualizado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Fecha y hora de la última actualización"
    )
    
    actualizado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("public.usuarios.id", ondelete="SET NULL")),
        description="Usuario que realizó la última actualización"
    )
    
    # Relaciones
    fabricante: "Fabricante" = Relationship(back_populates="modelos")
    neumaticos: List["Neumatico"] = Relationship(back_populates="modelo")
    
    # Usuarios relacionados
    usuario_creador: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[ModeloNeumatico.creado_por]"}
    )
    
    usuario_actualizador: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[ModeloNeumatico.actualizado_por]"}
    )

class Fabricante(BaseModel, table=True):
    """Modelo para los fabricantes de neumáticos."""
    __tablename__ = "fabricantes_neumatico"
    __table_args__ = (
        # Índice único para el nombre del fabricante (case-insensitive, sin acentos)
        Index('idx_fabricantes_nombre_unique', 
              func.f_immutable_lower_unaccent(func.text("nombre")), 
              unique=True,
              postgresql_where=text("activo = true")),
        {"schema": "public", "comment": "Fabricantes de neumáticos registrados en el sistema"}
    )
    
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único del fabricante"
    )
    
    nombre: str = Field(
        sa_column=Column(String(100), nullable=False, index=True),
        description="Nombre completo del fabricante"
    )
    
    codigo_abreviado: Optional[str] = Field(
        default=None,
        sa_column=Column(String(10), unique=True, index=True),
        description="Código abreviado del fabricante (opcional)"
    )
    
    pais_origen: Optional[str] = Field(
        default=None,
        sa_column=Column(String(50)),
        description="País de origen del fabricante"
    )
    
    sitio_web: Optional[str] = Field(
        default=None,
        sa_column=Column(String(255)),
        description="Sitio web del fabricante"
    )
    
    activo: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
        description="Indica si el registro está activo"
    )
    
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), nullable=False, server_default=text("now()")),
        description="Fecha y hora de creación del registro"
    )
    
    creado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("public.usuarios.id", ondelete="SET NULL")),
        description="Usuario que creó el registro"
    )
    
    actualizado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=False)),
        description="Fecha y hora de la última actualización"
    )
    
    actualizado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("public.usuarios.id", ondelete="SET NULL")),
        description="Usuario que realizó la última actualización"
    )
    
    # Relaciones
    modelos: List["ModeloNeumatico"] = Relationship(back_populates="fabricante")
    
    # Usuarios relacionados
    usuario_creador: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Fabricante.creado_por]"}
    )
    
    usuario_actualizador: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Fabricante.actualizado_por]"}
    )

class TipoProveedorEnum(str, Enum):
    FABRICANTE = "FABRICANTE"
    DISTRIBUIDOR = "DISTRIBUIDOR"
    SERVICIO_REPARACION = "SERVICIO_REPARACION"
    SERVICIO_REENCAUCHE = "SERVICIO_REENCAUCHE"
    OTRO = "OTRO"

class Proveedor(BaseModel, table=True):
    """Modelo para los proveedores de neumáticos y servicios."""
    __tablename__ = "proveedores"
    __table_args__ = (
        # Índice único para el nombre del proveedor (case-insensitive, sin acentos)
        Index('idx_proveedores_nombre_unique', 
              func.f_immutable_lower_unaccent(func.text("nombre")), 
              unique=True,
              postgresql_where=text("activo = true")),
        {"schema": "public", "comment": "Proveedores de neumáticos y servicios registrados en el sistema"}
    )

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único del proveedor"
    )
    nombre: str = Field(
        sa_column=Column(String(150), nullable=False, index=True),
        description="Nombre completo del proveedor"
    )
    tipo: TipoProveedorEnum = Field(
        sa_column=Column(String(20), nullable=False),
        description="Tipo de proveedor (fabricante, distribuidor, etc.)"
    )
    ruc: Optional[str] = Field(
        default=None,
        sa_column=Column(String(11), unique=True, index=True),
        description="RUC del proveedor (formato: 10-20 dígitos)"
    )
    contacto_principal: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description="Nombre de la persona de contacto principal"
    )
    telefono: Optional[str] = Field(
        default=None,
        sa_column=Column(String(50)),
        description="Número de teléfono de contacto"
    )
    email: Optional[str] = Field(
        default=None,
        sa_column=Column(String(100)),
        description="Correo electrónico de contacto"
    )
    direccion: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description="Dirección física del proveedor"
    )
    activo: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
        description="Indica si el registro está activo"
    )
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()")),
        description="Fecha y hora de creación del registro"
    )
    creado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("public.usuarios.id", ondelete="SET NULL")),
        description="Usuario que creó el registro"
    )
    actualizado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Fecha y hora de la última actualización"
    )
    actualizado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("public.usuarios.id", ondelete="SET NULL")),
        description="Usuario que realizó la última actualización"
    )
    
    # Relaciones
    usuario_creador: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Proveedor.creado_por]"}
    )
    usuario_actualizador: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Proveedor.actualizado_por]"}
    )
    garantias_neumaticos: List["GarantiasNeumaticos"] = Relationship(back_populates="proveedor")
    
    # Relación con las operaciones de bitácora donde este proveedor está involucrado
    bitacora_operaciones: List["BitacoraOperaciones"] = Relationship(
        back_populates="proveedor",
        sa_relationship_kwargs={"foreign_keys": "[BitacoraOperaciones.proveedor_id]"}
    )
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            UUID: lambda v: str(v) if v else None,
            datetime: lambda v: v.isoformat() if v else None
        }

class Almacen(BaseModel, table=True):
    """Modelo para los almacenes de neumáticos."""
    __tablename__ = "almacenes"
    __table_args__ = (
        {"schema": "public", "comment": "Catálogo de almacenes para el inventario de neumáticos"}
    )

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único del almacén"
    )
    
    codigo: str = Field(
        sa_column=Column(String(20), nullable=False, unique=True),
        description="Código único del almacén"
    )
    
    nombre: str = Field(
        sa_column=Column(String(150), nullable=False),
        description="Nombre descriptivo del almacén"
    )
    
    tipo: Optional[str] = Field(
        default=None,
        sa_column=Column(String(50)),
        description="Tipo de almacén (ej: principal, sucursal, bodega, etc.)"
    )
    
    direccion: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description="Dirección física del almacén"
    )
    
    activo: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
        description="Indica si el almacén está activo en el sistema"
    )
    
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()")),
        description="Fecha y hora de creación del registro"
    )
    
    creado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("public.usuarios.id", ondelete="SET NULL")),
        description="Usuario que creó el registro"
    )
    
    actualizado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Fecha y hora de la última actualización"
    )
    
    actualizado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("public.usuarios.id", ondelete="SET NULL")),
        description="Usuario que realizó la última actualización"
    )
    
    # Relaciones
    usuario_creador: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Almacen.creado_por]"}
    )
    
    usuario_actualizador: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Almacen.actualizado_por]"}
    )
    
    # Relación con las operaciones de bitácora donde este almacén está involucrado
    bitacora_operaciones: List["BitacoraOperaciones"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[BitacoraOperaciones.almacen_id]"},
        back_populates="almacen"
    )

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            UUID: lambda v: str(v) if v else None,
            datetime: lambda v: v.isoformat() if v else None
        }

class MotivoDesecho(BaseModel, table=True):
    """Modelo para los motivos de desecho de neumáticos."""
    __tablename__ = "motivos_desecho"
    __table_args__ = (
        {"schema": "public", "comment": "Catálogo de motivos por los cuales un neumático puede darse de baja"}
    )

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único del motivo de desecho"
    )
    
    codigo: str = Field(
        sa_column=Column(String(20), nullable=False, unique=True),
        description="Código único del motivo de desecho"
    )
    
    descripcion: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Descripción detallada del motivo de desecho"
    )
    
    requiere_evidencia: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default=text("false")),
        description="Indica si este motivo requiere evidencia fotográfica o documental"
    )
    
    activo: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
        description="Indica si el motivo de desecho está activo en el sistema"
    )
    
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()")),
        description="Fecha y hora de creación del registro"
    )
    
    creado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("public.usuarios.id", ondelete="SET NULL")),
        description="Usuario que creó el registro"
    )
    
    actualizado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Fecha y hora de la última actualización"
    )
    
    actualizado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("public.usuarios.id", ondelete="SET NULL")),
        description="Usuario que realizó la última actualización"
    )
    
    # Relaciones
    usuario_creador: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[MotivoDesecho.creado_por]"}
    )
    
    usuario_actualizador: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[MotivoDesecho.actualizado_por]"}
    )

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            UUID: lambda v: str(v) if v else None,
            datetime: lambda v: v.isoformat() if v else None
        }

class TipoParametroInventarioEnum(str, Enum):
    """Enumeración de tipos de parámetros de inventario."""
    STOCK_MINIMO = "STOCK_MINIMO"
    STOCK_MAXIMO = "STOCK_MAXIMO"
    PUNTO_REORDEN = "PUNTO_REORDEN"
    TIEMPO_REABASTECIMIENTO = "TIEMPO_REABASTECIMIENTO"
    VIDA_UTIL = "VIDA_UTIL"
    PRESION_OPTIMA = "PRESION_OPTIMA"
    PROFUNDIDAD_MINIMA = "PROFUNDIDAD_MINIMA"
    OTRO = "OTRO"

class ParametroInventario(BaseModel, table=True):
    """Modelo para los parámetros de inventario de neumáticos."""
    __tablename__ = "parametros_inventario"
    __table_args__ = (
        {"schema": "public", "comment": "Parámetros de configuración para el inventario de neumáticos"}
    )

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único del parámetro de inventario"
    )
    
    parametro_tipo: TipoParametroInventarioEnum = Field(
        sa_column=Column(
            SQLEnum(TipoParametroInventarioEnum, name="tipo_parametro_inventario_gesneu_enum"),
            nullable=False
        ),
        description="Tipo de parámetro de inventario"
    )
    
    modelo_id: UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("public.modelos_neumatico.id", ondelete="CASCADE"), nullable=False),
        description="ID del modelo de neumático al que aplica el parámetro"
    )
    
    ubicacion_almacen_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("public.almacenes.id", ondelete="SET NULL")),
        description="ID de la ubicación de almacén específica (opcional)"
    )
    
    valor_numerico: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(10, 2)),
        description="Valor numérico del parámetro (si aplica)"
    )
    
    valor_texto: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description="Valor de texto del parámetro (si aplica)"
    )
    
    activo: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
        description="Indica si el parámetro está activo"
    )
    
    notas: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description="Notas adicionales sobre el parámetro"
    )
    
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()")),
        description="Fecha y hora de creación del registro"
    )
    
    creado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("public.usuarios.id", ondelete="SET NULL")),
        description="Usuario que creó el registro"
    )
    
    actualizado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Fecha y hora de la última actualización"
    )
    
    actualizado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("public.usuarios.id", ondelete="SET NULL")),
        description="Usuario que realizó la última actualización"
    )
    
    # Relaciones
    modelo: "ModeloNeumatico" = Relationship()
    ubicacion_almacen: Optional["Almacen"] = Relationship()
    usuario_creador: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[ParametroInventario.creado_por]"}
    )
    usuario_actualizador: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[ParametroInventario.actualizado_por]"}
    )

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            UUID: lambda v: str(v) if v else None,
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v is not None else None
        }

class GarantiasNeumaticos(BaseModel, table=True):
    """Modelo para el registro de garantías de neumáticos."""
    __tablename__ = "garantias_neumaticos"
    __table_args__ = (
        CheckConstraint("fecha_fin IS NULL OR fecha_fin >= fecha_inicio", name="chk_fechas_garantia"),
        {"schema": "public", "comment": "Almacena información detallada sobre las garantías de los neumáticos"}
    )

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único de la garantía"
    )
    
    neumatico_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.neumaticos.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        ),
        description="ID del neumático al que se aplica la garantía"
    )
    
    tipo_garantia: str = Field(
        sa_column=Column(String(50), nullable=False),
        description="Tipo de garantía (KILOMETRAJE, TIEMPO, AMBOS)"
    )
    
    fecha_inicio: date = Field(
        sa_column=Column(Date, nullable=False),
        description="Fecha de inicio de la garantía"
    )
    
    fecha_fin: Optional[date] = Field(
        default=None,
        sa_column=Column(Date),
        description="Fecha de fin de la garantía (si aplica)"
    )
    
    kilometraje_cubierto: Optional[int] = Field(
        default=None,
        description="Kilometraje cubierto por la garantía (si aplica)"
    )
    
    meses_cobertura: Optional[int] = Field(
        default=None,
        description="Meses de cobertura de la garantía (si aplica)"
    )
    
    condiciones_url: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description="URL a las condiciones de la garantía"
    )
    
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()")),
        description="Fecha y hora de creación del registro"
    )
    
    actualizado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Fecha y hora de la última actualización"
    )
    
    creado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("public.usuarios.id", ondelete="SET NULL")),
        description="Usuario que creó el registro"
    )
    
    actualizado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("public.usuarios.id", ondelete="SET NULL")),
        description="Usuario que realizó la última actualización"
    )
    
    proveedor_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.proveedores.id", ondelete="SET NULL"),
            index=True
        ),
        description="ID del proveedor que otorga la garantía"
    )
    
    # Relaciones
    neumatico: "Neumatico" = Relationship(back_populates="garantias")
    proveedor: Optional["Proveedor"] = Relationship(back_populates="garantias_neumaticos")
    usuario_creador: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[GarantiasNeumaticos.creado_por]"}
    )
    usuario_actualizador: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[GarantiasNeumaticos.actualizado_por]"}
    )
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            UUID: lambda v: str(v) if v else None,
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None
        }

# Importaciones condicionales para evitar dependencias circulares
if not TYPE_CHECKING:
    from ges_neu_api.vehiculos.models import Vehiculo
    from ges_neu_api.auth.models.bitacora_operaciones import BitacoraOperaciones
    # Eliminamos la importación de Neumatico y EventoNeumatico de aquí

# Agregamos las importaciones de Neumatico y EventoNeumatico al final del archivo
from ges_neu_api.neumaticos.models import Neumatico, EventoNeumatico
from ges_neu_api.auth.models.usuario import Usuario

if not TYPE_CHECKING:
    from ges_neu_api.auth.models.usuario import Usuario
    
    # Rebuild models to resolve forward references
    # BitacoraOperaciones.model_rebuild()
    
    # if hasattr(BitacoraOperaciones, 'model_fields'):
    #     BitacoraOperaciones.model_fields.update({
    #         'usuario': "Optional[Usuario]"
    #     })