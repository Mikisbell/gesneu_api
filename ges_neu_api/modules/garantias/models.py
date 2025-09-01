"""
Modelos del modulo de garantias - Exactos al esquema de backup_completo.dump
"""
from datetime import datetime, date
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Numeric, Date, CheckConstraint, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import text, Index

# BaseModel removed to avoid SQLAlchemy metadata conflicts

if TYPE_CHECKING:
    from ..auth.models import Usuario
    from ..catalogos.models import Proveedor
    from ..neumaticos.models import Neumatico

# ============================================================================
# GARANTÍAS NEUMÁTICOS
# ============================================================================

class GarantiasNeumaticos(SQLModel, table=True):
    """Garantías de neumáticos con proveedores."""
    __tablename__ = 'garantias_neumaticos'
    
    # Campos exactos del esquema real
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    )
    neumatico_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("neumaticos.id"), nullable=False))
    proveedor_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("proveedores.id"), nullable=False))
    fecha_inicio: date = Field(sa_column=Column(Date, nullable=False))
    fecha_vencimiento: date = Field(sa_column=Column(Date, nullable=False))
    tipo_garantia: str = Field(sa_column=Column(String(50), nullable=False))
    cobertura_descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))
    activo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text('true')))
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    )
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL")))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP))
    actualizado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL")))
    
    # Constraints exactos del esquema real
    __table_args__ = (
        CheckConstraint('fecha_vencimiento > fecha_inicio', name='garantias_neumaticos_fechas_check'),
        Index('idx_garantias_neumaticos_neumatico', 'neumatico_id'),
        Index('idx_garantias_neumaticos_proveedor', 'proveedor_id'),
        Index('idx_garantias_neumaticos_vencimiento', 'fecha_vencimiento'),
    )
    
    # Relationships - removed to avoid circular imports

# Note: model_rebuild() removed to avoid SQLAlchemy metadata conflicts
