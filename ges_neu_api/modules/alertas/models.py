"""
Modelos del módulo de alertas - Exactos al esquema de backup_completo.dump
"""
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Numeric, CheckConstraint, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import Enum as SQLAlchemyEnum, text, Index

# BaseModel removed to avoid SQLAlchemy metadata conflicts

if TYPE_CHECKING:
    from ..auth.models import Usuario
    from ..neumaticos.models import Neumatico
    from ..catalogos.models import ParametroInventario

# Enums exactos del esquema real
class TipoAlertaEnum(str, Enum):
    STOCK_BAJO = "STOCK_BAJO"
    PROFUNDIDAD_CRITICA = "PROFUNDIDAD_CRITICA"
    VENCIMIENTO_GARANTIA = "VENCIMIENTO_GARANTIA"
    INSPECCION_PENDIENTE = "INSPECCION_PENDIENTE"
    ROTACION_RECOMENDADA = "ROTACION_RECOMENDADA"
    REENCAUCHE_RECOMENDADO = "REENCAUCHE_RECOMENDADO"
    DESECHO_RECOMENDADO = "DESECHO_RECOMENDADO"

class PrioridadAlertaEnum(str, Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"

class EstadoAlertaEnum(str, Enum):
    PENDIENTE = "PENDIENTE"
    VISTA = "VISTA"
    RESUELTA = "RESUELTA"
    IGNORADA = "IGNORADA"

# ============================================================================
# ALERTAS
# ============================================================================

class Alertas(SQLModel, table=True):
    """Sistema de alertas del sistema."""
    __tablename__ = 'alertas'
    
    # Campos exactos del esquema real
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    )
    tipo_alerta: str = Field(sa_column=Column(String(50), nullable=False))
    neumatico_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("neumaticos.id")))
    parametro_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("parametros_inventario.id")))
    mensaje: str = Field(sa_column=Column(Text, nullable=False))
    nivel_prioridad: str = Field(default="medium", sa_column=Column(String(20), nullable=False, server_default=text("'medium'")))
    fecha_generacion: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text('now()')))
    fecha_vencimiento: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    leida: bool = Field(default=False, sa_column=Column(Boolean, nullable=False, server_default=text('false')))
    activo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text('true')))
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    )
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL")))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP))
    actualizado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL")))
    estado: EstadoAlertaEnum = Field(default=EstadoAlertaEnum.PENDIENTE, sa_column=Column(SQLAlchemyEnum(EstadoAlertaEnum), nullable=False, server_default=text("'PENDIENTE'")))
    vista_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL")))
    fecha_vista: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    resuelta_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL")))
    fecha_resolucion: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    observaciones_resolucion: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # Constraints exactos del esquema real
    __table_args__ = (
        CheckConstraint("nivel_prioridad IN ('low', 'medium', 'high')", name='alertas_prioridad_check'),
        CheckConstraint("tipo_alerta IN ('STOCK_BAJO', 'PROFUNDIDAD_CRITICA', 'VENCIMIENTO_GARANTIA', 'INSPECCION_PENDIENTE', 'ROTACION_RECOMENDADA', 'REENCAUCHE_RECOMENDADO', 'DESECHO_RECOMENDADO')", name='alertas_tipo_check'),
        Index('idx_alertas_tipo', 'tipo_alerta'),
        Index('idx_alertas_prioridad', 'nivel_prioridad'),
        Index('idx_alertas_fecha_generacion', 'fecha_generacion'),
        Index('idx_alertas_neumatico', 'neumatico_id'),
    )
    
    # Relationships - removed to avoid circular imports
    # usuarios: handled at service layer

# Note: model_rebuild() removed to avoid SQLAlchemy metadata conflicts
