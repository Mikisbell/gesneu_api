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
    """Esquema base para modelos de neumáticos - Alineado con BD real."""
    fabricante_id: UUID = Field(..., description="ID del fabricante")
    nombre_modelo: str = Field(..., max_length=100, description="Nombre del modelo")
    medida: str = Field(..., max_length=20, description="Medida del neumático")
    profundidad_original_mm: Decimal = Field(..., gt=0, description="Profundidad original de la banda de rodadura en mm")
    tipo_construccion: str = Field("RADIAL", max_length=20, description="Tipo de construcción (RADIAL, DIAGONAL)")
    indice_carga: Optional[str] = Field(None, max_length=5, description="Índice de carga")
    indice_velocidad: Optional[str] = Field(None, max_length=2, description="Índice de velocidad")
    max_vidas_utiles: Optional[int] = Field(3, gt=0, description="Máximo de vidas útiles (reencauches)")
    porcentaje_desgaste_por_vida: Optional[Decimal] = Field(Decimal('33.33'), ge=0, le=100, description="Porcentaje de desgaste por vida útil")
    tasa_desgaste_esperada_mm_km: Optional[Decimal] = Field(None, description="Tasa de desgaste esperada en mm/km")
    vida_util_teorica_km: Optional[int] = Field(None, ge=0, description="Vida útil teórica en km")
    activo: Optional[bool] = Field(True, description="Estado activo del modelo")


class ModeloCreate(ModeloBase):
    """Esquema para crear un modelo."""
    pass


class ModeloUpdate(BaseModel):
    """Esquema para actualizar un modelo (todos los campos son opcionales)."""
    fabricante_id: Optional[UUID] = None
    nombre_modelo: Optional[str] = Field(None, max_length=100)
    medida: Optional[str] = Field(None, max_length=20)
    profundidad_original_mm: Optional[Decimal] = Field(None, gt=0)
    tipo_construccion: Optional[str] = Field(None, max_length=20)
    indice_carga: Optional[str] = Field(None, max_length=5)
    indice_velocidad: Optional[str] = Field(None, max_length=2)
    max_vidas_utiles: Optional[int] = Field(None, gt=0)
    porcentaje_desgaste_por_vida: Optional[Decimal] = Field(None, ge=0, le=100)
    tasa_desgaste_esperada_mm_km: Optional[Decimal] = None
    vida_util_teorica_km: Optional[int] = Field(None, ge=0)
    activo: Optional[bool] = None


class ModeloResponse(BaseModel):
    """Esquema de respuesta para modelos - Todos los campos de BD real."""
    id: UUID
    fabricante_id: UUID
    nombre_modelo: str
    medida: str
    indice_carga: Optional[str]
    indice_velocidad: Optional[str]
    profundidad_original_mm: Decimal
    presion_recomendada_psi: Optional[Decimal]
    permite_reencauche: bool
    reencauches_maximos: Optional[int]
    patron_dibujo: Optional[str]
    tipo_servicio: Optional[str]
    posicion_uso_recomendada: Optional[str]
    diseno_predominante_para_eje: Optional[str]
    vida_util_teorica_km: Optional[int]
    profundidad_minima_retiro_mm: Decimal
    tasa_desgaste_esperada_mm_km: Decimal
    activo: Optional[bool]
    frecuencia_inspeccion_km: Optional[int]
    max_vidas_utiles: Optional[int]
    porcentaje_desgaste_por_vida: Optional[Decimal]
    creado_en: datetime
    creado_por: Optional[UUID] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = None

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
