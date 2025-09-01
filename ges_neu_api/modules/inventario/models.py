"""
Modelos del modulo de inventario - Exactos al esquema de backup_completo.dump
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4
from decimal import Decimal

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Numeric, CheckConstraint, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import Enum as SQLAlchemyEnum, text, UniqueConstraint, Index, ForeignKey

# BaseModel removed to avoid SQLAlchemy metadata conflicts

if TYPE_CHECKING:
    from ..auth.models import Usuario
    from ..catalogos.models import Almacen
    from ..neumaticos.models import ModeloNeumatico, Neumatico

# Enums exactos del esquema real
class TipoMovimientoEnum(str, Enum):
    ENTRADA = "ENTRADA"
    SALIDA = "SALIDA"
    TRANSFERENCIA = "TRANSFERENCIA"
    AJUSTE = "AJUSTE"

# ============================================================================
# INVENTARIO NEUMÁTICOS
# ============================================================================

class InventarioNeumaticos(SQLModel, table=True):
    """Inventario de neumáticos por modelo y almacén."""
    __tablename__ = 'inventario_neumaticos'
    
    # Campos exactos del esquema real
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    )
    modelo_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("modelos_neumatico.id"), nullable=False))
    almacen_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("almacenes.id"), nullable=False))
    cantidad_stock: int = Field(default=0, sa_column=Column(Integer, nullable=False, server_default=text('0')))
    stock_minimo: int = Field(default=0, sa_column=Column(Integer, server_default=text('0')))
    stock_maximo: Optional[int] = Field(default=None, sa_column=Column(Integer))
    activo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text("true")))
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    )
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL")))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP, onupdate=text("now()")))
    actualizado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL")))
    
    # Constraints exactos del esquema real
    __table_args__ = (
        CheckConstraint('cantidad_stock >= 0', name='inventario_neumaticos_cantidad_stock_check'),
        CheckConstraint('stock_minimo >= 0', name='inventario_neumaticos_stock_minimo_check'),
        CheckConstraint('stock_maximo IS NULL OR stock_maximo >= stock_minimo', name='inventario_neumaticos_stock_maximo_check'),
        UniqueConstraint('modelo_id', 'almacen_id', name='uq_inventario_modelo_almacen'),
        Index('idx_inventario_neumaticos_modelo', 'modelo_id'),
        Index('idx_inventario_neumaticos_almacen', 'almacen_id'),
    )
    
    # Relationships - simplified to avoid circular imports
    # modelo: handled at service layer
    # almacen: handled at service layer

# ============================================================================
# MOVIMIENTOS INVENTARIO
# ============================================================================

class MovimientosInventario(SQLModel, table=True):
    """Movimientos de inventario de neumáticos."""
    __tablename__ = 'movimientos_inventario'
    
    # Campos exactos del esquema real
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    )
    neumatico_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("neumaticos.id"), nullable=False))
    tipo_movimiento: str = Field(sa_column=Column(String(20), nullable=False))
    almacen_origen_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("almacenes.id")))
    almacen_destino_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("almacenes.id")))
    cantidad: int = Field(sa_column=Column(Integer, nullable=False))
    motivo: str = Field(sa_column=Column(String(200), nullable=False))
    observaciones: Optional[str] = Field(default=None, sa_column=Column(Text))
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    )
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL")))
    
    __table_args__ = (
        CheckConstraint('cantidad > 0', name='movimientos_inventario_cantidad_check'),
        CheckConstraint("tipo_movimiento IN ('ENTRADA', 'SALIDA', 'TRANSFERENCIA', 'AJUSTE')", name='movimientos_inventario_tipo_check'),
        Index('idx_movimientos_inventario_neumatico', 'neumatico_id'),
        Index('idx_movimientos_inventario_tipo', 'tipo_movimiento'),
        Index('idx_movimientos_inventario_fecha', 'creado_en'),
    )
    
    # Relationships - simplified to avoid circular imports
    # neumatico: handled at service layer
    # almacenes: handled at service layer

# Note: model_rebuild() removed to avoid SQLAlchemy metadata conflicts
