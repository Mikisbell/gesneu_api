"""Modelos del modulo de inventario - Alineados con esquema real PostgreSQL"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4
from decimal import Decimal

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Numeric, CheckConstraint, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import Enum as SQLAlchemyEnum, text, UniqueConstraint, Index, ForeignKey

if TYPE_CHECKING:
    from ..auth.models import Usuario
    from ..catalogos.models import Almacen
    from ..neumaticos.models import ModeloNeumatico, Neumatico

# Enums exactos del esquema real - tipo_parametro_inventario_gesneu_enum
class TipoParametroInventarioEnum(str, Enum):
    STOCK_MINIMO = "STOCK_MINIMO"
    STOCK_MAXIMO = "STOCK_MAXIMO"
    PROFUNDIDAD_MINIMA_RETIRO_MM = "PROFUNDIDAD_MINIMA_RETIRO_MM"
    PROFUNDIDAD_MINIMA_REENCAUCHE_MM = "PROFUNDIDAD_MINIMA_REENCAUCHE_MM"
    TIEMPO_MAXIMO_VIDA_MESES = "TIEMPO_MAXIMO_VIDA_MESES"
    MAX_ROTACIONES_PERIODO = "MAX_ROTACIONES_PERIODO"
    MAX_REPARACIONES_PERIODO = "MAX_REPARACIONES_PERIODO"
    VIDA_MAXIMA_ESTANTE_MESES_SIN_USO = "VIDA_MAXIMA_ESTANTE_MESES_SIN_USO"

# ============================================================================
# PARÁMETROS INVENTARIO (tabla real en BD)
# ============================================================================

class ParametrosInventario(SQLModel, table=True):
    """Parámetros de inventario por modelo y almacén - Tabla real en BD."""
    __tablename__ = 'parametros_inventario'
    
    # Campos exactos del esquema real
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    )
    parametro_tipo: str = Field(sa_column=Column(String(50), nullable=False))  # USER-DEFINED type según esquema
    modelo_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("modelos_neumatico.id"), nullable=False))
    ubicacion_almacen_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("almacenes.id")))
    valor_numerico: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    valor_texto: Optional[str] = Field(default=None, sa_column=Column(Text))
    notas: Optional[str] = Field(default=None, sa_column=Column(Text))
    activo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text("true")))
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    )
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id")))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP))
    actualizado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id")))
    
    # Constraints exactos del esquema real - merged with extend_existing
    __table_args__ = (
        UniqueConstraint('parametro_tipo', 'modelo_id', 'ubicacion_almacen_id', name='uq_parametro_inventario'),
        UniqueConstraint('parametro_tipo', 'modelo_id', 'ubicacion_almacen_id', name='uq_parametro_inventario_gesneu'),
        Index('idx_param_inv_tipo_modelo_ubicacion', 'parametro_tipo', 'modelo_id', 'ubicacion_almacen_id'),
        {'extend_existing': True}
    )

# ============================================================================
# VISTA DE INVENTARIO (basada en tabla neumaticos)
# ============================================================================

class InventarioView(SQLModel):
    """Vista de inventario basada en neumáticos y parámetros."""
    modelo_id: UUID
    modelo_nombre: str
    almacen_id: UUID
    almacen_nombre: str
    cantidad_en_stock: int
    cantidad_instalados: int
    cantidad_total: int
    stock_minimo: Optional[Decimal]
    stock_maximo: Optional[Decimal]
    punto_reorden: Optional[Decimal]
    estado_stock: str  # 'BAJO', 'NORMAL', 'ALTO'
    
class ResumenInventario(SQLModel):
    """Resumen de inventario por modelo."""
    modelo_id: UUID
    modelo_nombre: str
    total_neumaticos: int
    en_stock: int
    instalados: int
    en_mantenimiento: int
    desechados: int
    almacenes: List[dict]
