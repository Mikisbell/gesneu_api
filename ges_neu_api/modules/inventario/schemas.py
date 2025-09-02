"""
Esquemas Pydantic para el módulo de inventario - Alineados con esquema real PostgreSQL.
"""
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel

from .models import TipoParametroInventarioEnum

# ============================================================================
# ESQUEMAS PARA PARÁMETROS INVENTARIO
# ============================================================================

class ParametroInventarioBase(BaseModel):
    """Esquema base para parámetros de inventario."""
    parametro_tipo: TipoParametroInventarioEnum
    modelo_id: UUID
    ubicacion_almacen_id: Optional[UUID] = None
    valor_numerico: Optional[Decimal] = None
    valor_texto: Optional[str] = None
    notas: Optional[str] = None
    activo: bool = True

class ParametroInventarioCreate(ParametroInventarioBase):
    """Esquema para crear parámetro de inventario."""
    pass

class ParametroInventarioUpdate(BaseModel):
    """Esquema para actualizar parámetro de inventario."""
    parametro_tipo: Optional[TipoParametroInventarioEnum] = None
    valor_numerico: Optional[Decimal] = None
    valor_texto: Optional[str] = None
    notas: Optional[str] = None
    activo: Optional[bool] = None

class ParametroInventarioResponse(ParametroInventarioBase):
    """Esquema de respuesta para parámetros de inventario."""
    id: UUID
    creado_en: datetime
    creado_por: Optional[UUID] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = None

    class Config:
        from_attributes = True

# ============================================================================
# ESQUEMAS PARA VISTAS DE INVENTARIO
# ============================================================================

class InventarioViewResponse(BaseModel):
    """Esquema de respuesta para vista de inventario."""
    modelo_id: UUID
    modelo_nombre: str
    almacen_id: UUID
    almacen_nombre: str
    cantidad_en_stock: int
    cantidad_instalados: int
    cantidad_total: int
    stock_minimo: Optional[Decimal] = None
    stock_maximo: Optional[Decimal] = None
    punto_reorden: Optional[Decimal] = None
    estado_stock: str

    class Config:
        from_attributes = True

class ResumenInventarioResponse(BaseModel):
    """Esquema de respuesta para resumen de inventario."""
    modelo_id: UUID
    modelo_nombre: str
    total_neumaticos: int

    class Config:
        from_attributes = True