"""
Modelos del módulo de alertas - Exactos al esquema de backup_completo.dump
"""
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Numeric, CheckConstraint, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import Enum as SQLAlchemyEnum, text, Index

# BaseModel removed to avoid SQLAlchemy metadata conflicts

if TYPE_CHECKING:
    from ..auth.models import Usuario
    from ..neumaticos.models import Neumatico
    from ..catalogos.models import ParametroInventario

# Enums exactos del esquema real
class NivelSeveridadEnum(str, Enum):
    INFO = "INFO"
    WARN = "WARN"
    CRITICAL = "CRITICAL"

class EstadoAlertaEnum(str, Enum):
    NUEVA = "NUEVA"
    VISTA = "VISTA"
    GESTIONADA = "GESTIONADA"

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
    mensaje: str = Field(sa_column=Column(Text, nullable=False))
    nivel_severidad: NivelSeveridadEnum = Field(
        default=NivelSeveridadEnum.INFO, 
        sa_column=Column(String(20), nullable=False, server_default=text("'INFO'"))
    )
    estado_alerta: EstadoAlertaEnum = Field(
        default=EstadoAlertaEnum.NUEVA, 
        sa_column=Column(String(20), nullable=False, server_default=text("'NUEVA'"))
    )
    timestamp_generacion: datetime = Field(
        default_factory=datetime.utcnow, 
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text('now()'))
    )
    timestamp_gestion: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    usuario_gestion_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id")))
    neumatico_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("neumaticos.id")))
    vehiculo_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("vehiculos.id")))
    modelo_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("modelos_neumatico.id")))
    almacen_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("almacenes.id")))
    parametro_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("parametros_inventario.id")))
    datos_contexto: Optional[dict] = Field(default=None, sa_column=Column("datos_contexto", JSON))
    
    # Constraints exactos del esquema real
    __table_args__ = (
        CheckConstraint("nivel_severidad IN ('INFO', 'WARN', 'CRITICAL')", name='alertas_nivel_severidad_check'),
        CheckConstraint("estado_alerta IN ('NUEVA', 'VISTA', 'GESTIONADA')", name='alertas_estado_alerta_check'),
        Index('idx_alertas_estado_ts', 'estado_alerta', 'timestamp_generacion'),
    )
    
    # Relationships - removed to avoid circular imports
    # usuarios: handled at service layer

# Note: model_rebuild() removed to avoid SQLAlchemy metadata conflicts
