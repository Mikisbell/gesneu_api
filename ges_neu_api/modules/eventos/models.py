"""
Modelos del modulo de eventos - Exactos al esquema de backup_completo.dump
"""
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4
from decimal import Decimal

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Numeric, Date, CheckConstraint, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy import Enum as SQLAlchemyEnum, text, Index

# BaseModel removed to avoid SQLAlchemy metadata conflicts

if TYPE_CHECKING:
    from ..auth.models import Usuario
    from ..catalogos.models import Almacen, MotivoDesecho
    from ..neumaticos.models import Neumatico
    from ..vehiculos.models import Vehiculo
    from ..sistema.models import TiposRuta

# Enums exactos del esquema real
class TipoEventoNeumaticoEnum(str, Enum):
    COMPRA = "COMPRA"
    INSTALACION = "INSTALACION"
    DESMONTAJE = "DESMONTAJE"
    INSPECCION = "INSPECCION"
    ROTACION = "ROTACION"
    REPARACION_ENTRADA = "REPARACION_ENTRADA"
    REPARACION_SALIDA = "REPARACION_SALIDA"
    REENCAUCHE_ENTRADA = "REENCAUCHE_ENTRADA"
    REENCAUCHE_SALIDA = "REENCAUCHE_SALIDA"
    DESECHO = "DESECHO"
    AJUSTE_INVENTARIO = "AJUSTE_INVENTARIO"
    TRANSFERENCIA_UBICACION = "TRANSFERENCIA_UBICACION"

class EstadoNeumaticoEnum(str, Enum):
    EN_STOCK = "EN_STOCK"
    INSTALADO = "INSTALADO"
    EN_REPARACION = "EN_REPARACION"
    EN_REENCAUCHE = "EN_REENCAUCHE"
    DESECHADO = "DESECHADO"
    EN_TRANSITO = "EN_TRANSITO"

class MetodoMedicionEnum(str, Enum):
    MANUAL = "MANUAL"
    AUTOMATICO = "AUTOMATICO"
    DIGITAL = "DIGITAL"

# ============================================================================
# EVENTOS NEUMÁTICOS
# ============================================================================

class EventosNeumaticos(SQLModel, table=True):
    """Eventos de neumáticos con datos completos."""
    __tablename__ = 'eventos_neumaticos'
    
    # Campos exactos del esquema real
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    )
    neumatico_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("neumaticos.id"), nullable=False))
    tipo_evento: str = Field(sa_column=Column(String(50), nullable=False))
    timestamp_evento: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text('now()')))
    usuario_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False))
    vehiculo_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("vehiculos.id")))
    almacen_origen_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("almacenes.id")))
    almacen_destino_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("almacenes.id")))
    tipo_ruta_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("tipos_ruta.id")))
    motivos_desecho_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("motivos_desecho.id")))
    datos_evento: dict = Field(default_factory=dict, sa_column=Column(JSONB, nullable=False, server_default=text("'{}'")))
    observaciones: Optional[str] = Field(default=None, sa_column=Column(Text))
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    )
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL")))
    
    __table_args__ = (
        CheckConstraint("tipo_evento IN ('COMPRA', 'INSTALACION', 'DESMONTAJE', 'INSPECCION', 'ROTACION', 'REPARACION_ENTRADA', 'REPARACION_SALIDA', 'REENCAUCHE_ENTRADA', 'REENCAUCHE_SALIDA', 'DESECHO', 'AJUSTE_INVENTARIO', 'TRANSFERENCIA_UBICACION')", name='eventos_neumaticos_tipo_evento_check'),
        Index('idx_eventos_neumaticos_neumatico', 'neumatico_id'),
        Index('idx_eventos_neumaticos_tipo', 'tipo_evento'),
        Index('idx_eventos_neumaticos_timestamp', 'timestamp_evento'),
    )
    
    # Relationships - simplified to avoid circular imports
    # neumatico: handled at service layer
    # usuario: handled at service layer
    # vehiculo: handled at service layer
    # tipo_ruta: handled at service layer
    # motivos_desecho: handled at service layer

# ============================================================================
# HISTORIAL ESTADOS NEUMÁTICOS
# ============================================================================

class HistorialEstadosNeumaticos(SQLModel, table=True):
    """Historial de cambios de estado de neumáticos."""
    __tablename__ = 'historial_estados_neumaticos'
    
    # Campos exactos del esquema real
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    )
    neumatico_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("neumaticos.id"), nullable=False))
    estado_anterior: Optional[str] = Field(default=None, sa_column=Column(String(50)))
    estado_nuevo: str = Field(sa_column=Column(String(50), nullable=False))
    fecha_cambio: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text('now()')))
    motivo_cambio: Optional[str] = Field(default=None, sa_column=Column(Text))
    observaciones: Optional[str] = Field(default=None, sa_column=Column(Text))
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    )
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL")))
    
    # Índices exactos del esquema real
    __table_args__ = (
        Index('idx_historial_estados_neumatico', 'neumatico_id'),
        Index('idx_historial_estados_fecha', 'fecha_cambio'),
        Index('idx_historial_estados_estado_nuevo', 'estado_nuevo'),
    )
    
    # Relationships - removed to avoid circular imports

# ============================================================================
# MEDICIONES PROFUNDIDAD
# ============================================================================

class MedicionesProfundidad(SQLModel, table=True):
    """Mediciones de profundidad de neumáticos."""
    __tablename__ = 'mediciones_profundidad'
    
    # Campos exactos del esquema real
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    )
    neumatico_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("neumaticos.id"), nullable=False))
    fecha_medicion: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text('now()')))
    profundidad_mm: Decimal = Field(sa_column=Column(Numeric(5, 2), nullable=False))
    metodo_medicion: str = Field(default="MANUAL", sa_column=Column(String(50), server_default=text("'MANUAL'")))
    observaciones: Optional[str] = Field(default=None, sa_column=Column(Text))
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    )
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL")))
    
    # Constraints exactos del esquema real
    __table_args__ = (
        CheckConstraint('profundidad_mm >= 0 AND profundidad_mm <= 50', name='mediciones_profundidad_check'),
        Index('idx_mediciones_profundidad_neumatico', 'neumatico_id'),
        Index('idx_mediciones_profundidad_fecha', 'fecha_medicion'),
    )
    
    # Relationships - simplified to avoid circular imports
    # neumatico: handled at service layer

# Note: model_rebuild() removed to avoid SQLAlchemy metadata conflicts
