"""
Esquemas Pydantic para el módulo de neumáticos.
"""
from datetime import date, datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field

# from .models import EstadoNeumaticoEnum  # Comentado para evitar conflictos de metadata


# Esquemas para Neumáticos
class NeumaticoBase(BaseModel):
    """Esquema base para neumáticos."""
    numero_serie: str = Field(..., max_length=100, description="Número de serie único del neumático")
    estado: str = Field(default="EN_STOCK", description="Estado actual del neumático")
    medida: Optional[str] = Field(None, max_length=50, description="Medida del neumático (ej: 295/80R22.5)")
    marca: Optional[str] = Field(None, max_length=100, description="Marca del neumático")
    modelo: Optional[str] = Field(None, max_length=100, description="Modelo del neumático")
    fecha_compra: Optional[date] = Field(None, description="Fecha de compra del neumático")
    precio_compra: Optional[Decimal] = Field(None, ge=0, description="Precio de compra del neumático")
    kilometraje_actual: Optional[int] = Field(0, ge=0, description="Kilometraje actual del neumático")
    observaciones: Optional[str] = Field(None, description="Observaciones adicionales")


class NeumaticoCreate(NeumaticoBase):
    """Esquema para crear un neumático."""
    pass


class NeumaticoUpdate(BaseModel):
    """Esquema para actualizar un neumático."""
    numero_serie: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = None
    medida: Optional[str] = Field(None, max_length=50)
    marca: Optional[str] = Field(None, max_length=100)
    modelo: Optional[str] = Field(None, max_length=100)
    fecha_compra: Optional[date] = None
    precio_compra: Optional[Decimal] = Field(None, ge=0)
    kilometraje_actual: Optional[int] = Field(None, ge=0)
    observaciones: Optional[str] = None


class NeumaticoResponse(NeumaticoBase):
    """Esquema de respuesta para neumáticos."""
    id: UUID
    
    class Config:
        from_attributes = True


# Esquemas para Fabricantes
class FabricanteBase(BaseModel):
    """Esquema base para fabricantes - Alineado con BD real."""
    nombre: str = Field(..., max_length=100, description="Nombre del fabricante")
    codigo_abreviado: Optional[str] = Field(None, max_length=10, description="Código abreviado del fabricante")
    pais_origen: Optional[str] = Field(None, max_length=50, description="País de origen")
    sitio_web: Optional[str] = Field(None, max_length=255, description="Sitio web oficial")
    activo: Optional[bool] = Field(True, description="Estado activo del fabricante")


class FabricanteCreate(FabricanteBase):
    """Esquema para crear un fabricante."""
    pass


class FabricanteUpdate(BaseModel):
    """Esquema para actualizar un fabricante."""
    nombre: Optional[str] = Field(None, max_length=100)
    codigo_abreviado: Optional[str] = Field(None, max_length=10)
    pais_origen: Optional[str] = Field(None, max_length=50)
    sitio_web: Optional[str] = Field(None, max_length=255)
    activo: Optional[bool] = None


class FabricanteResponse(BaseModel):
    """Esquema de respuesta para fabricantes - Todos los campos de BD real."""
    id: UUID
    nombre: str
    codigo_abreviado: Optional[str] = None
    pais_origen: Optional[str] = None
    sitio_web: Optional[str] = None
    activo: bool
    creado_en: datetime
    creado_por: Optional[UUID] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = None
    
    class Config:
        from_attributes = True


# Esquemas para Modelos
class ModeloBase(BaseModel):
    """Esquema base para modelos de neumáticos."""
    fabricante_id: Optional[UUID] = Field(None, description="ID del fabricante")
    nombre: str = Field(..., max_length=100, description="Nombre del modelo")
    medida: str = Field(..., max_length=50, description="Medida del neumático")
    tipo_construccion: Optional[str] = Field(None, max_length=50, description="Tipo de construcción (radial, diagonal)")
    indice_carga: Optional[str] = Field(None, max_length=10, description="Índice de carga")
    indice_velocidad: Optional[str] = Field(None, max_length=5, description="Índice de velocidad")
    precio_referencia: Optional[Decimal] = Field(None, ge=0, description="Precio de referencia")


class ModeloCreate(ModeloBase):
    """Esquema para crear un modelo."""
    pass


class ModeloUpdate(BaseModel):
    """Esquema para actualizar un modelo."""
    fabricante_id: Optional[UUID] = None
    nombre: Optional[str] = Field(None, max_length=100)
    medida: Optional[str] = Field(None, max_length=50)
    tipo_construccion: Optional[str] = Field(None, max_length=50)
    indice_carga: Optional[str] = Field(None, max_length=10)
    indice_velocidad: Optional[str] = Field(None, max_length=5)
    precio_referencia: Optional[Decimal] = Field(None, ge=0)


class ModeloResponse(ModeloBase):
    """Esquema de respuesta para modelos."""
    id: UUID
    
    class Config:
        from_attributes = True


# Esquemas de estadísticas y reportes
class EstadisticasNeumaticoResponse(BaseModel):
    """Estadísticas generales de neumáticos."""
    total_neumaticos: int
    por_estado: dict[str, int]
    por_marca: dict[str, int]
    valor_total_inventario: Optional[Decimal]
    
    class Config:
        from_attributes = True
