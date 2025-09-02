"""
Schemas Pydantic para el módulo de garantías de neumáticos.
Alineados exactamente con ESQUEMA_COMPLETO_BD.md
"""
from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class GarantiaNeumaticoBase(BaseModel):
    """Schema base para garantías de neumáticos."""
    neumatico_id: UUID
    proveedor_id: Optional[UUID] = None
    tipo_garantia: str
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    kilometraje_cubierto: Optional[int] = None
    meses_cobertura: Optional[int] = None
    condiciones_url: Optional[str] = None


class GarantiaNeumaticoCreate(GarantiaNeumaticoBase):
    """Schema para crear garantía de neumático."""
    pass


class GarantiaNeumaticoUpdate(BaseModel):
    """Schema para actualizar garantía de neumático."""
    proveedor_id: Optional[UUID] = None
    tipo_garantia: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    kilometraje_cubierto: Optional[int] = None
    meses_cobertura: Optional[int] = None
    condiciones_url: Optional[str] = None


class GarantiaNeumaticoResponse(GarantiaNeumaticoBase):
    """Schema para respuesta de garantía de neumático."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    creado_en: datetime
    actualizado_en: Optional[datetime] = None
    creado_por: Optional[UUID] = None
    actualizado_por: Optional[UUID] = None
