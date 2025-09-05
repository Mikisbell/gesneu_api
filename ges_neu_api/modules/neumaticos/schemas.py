"""
Esquemas Pydantic para el módulo de neumáticos.
"""
from datetime import date, datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field

# Esquemas para Neumáticos (alineados con el esquema real de PostgreSQL)
class NeumaticoCreate(BaseModel):
    """Esquema para crear un neumático (Database-First)."""
    modelo_id: UUID = Field(..., description="ID del modelo de neumático")
    fecha_compra: date = Field(..., description="Fecha de compra del neumático")
    profundidad_remanente_actual_mm: Decimal = Field(..., description="Profundidad remanente actual en mm")

    # Opcionales según tabla real
    numero_serie: Optional[str] = Field(None, max_length=100)
    dot: Optional[str] = None
    fecha_fabricacion: Optional[date] = None
    costo_compra: Optional[Decimal] = Field(None, ge=0)
    moneda_compra: Optional[str] = Field(None, max_length=3)
    proveedor_compra_id: Optional[UUID] = None
    es_reencauchado: Optional[bool] = None
    vida_actual: Optional[int] = Field(None, ge=1)
    estado_actual: Optional[str] = Field(None, description="Estado actual del neumático")
    ubicacion_actual_vehiculo_id: Optional[UUID] = None
    ubicacion_actual_posicion_id: Optional[UUID] = None
    fecha_ultimo_evento: Optional[datetime] = None
    profundidad_inicial_mm: Optional[Decimal] = None
    kilometraje_acumulado: Optional[int] = Field(None, ge=0)
    reencauches_realizados: Optional[int] = Field(None, ge=0)
    fecha_desecho: Optional[date] = None
    motivo_desecho_id: Optional[UUID] = None
    ubicacion_almacen_id: Optional[UUID] = None
    sensor_id: Optional[str] = Field(None, max_length=100)
    fecha_ultima_medicion_profundidad: Optional[datetime] = None
    kilometraje_vida_actual: Optional[int] = Field(None, ge=0)
    fecha_inicio_vida_actual: Optional[date] = None
    odometro_instalacion_vida_actual: Optional[int] = Field(None, ge=0)
    tasa_desgaste_actual_mm_km: Optional[Decimal] = None
    vida_util_restante_km: Optional[int] = Field(None, ge=0)
    fecha_ultimo_reencauche: Optional[date] = None
    activo: Optional[bool] = None
    proxima_inspeccion_fecha: Optional[date] = None
    proxima_inspeccion_km: Optional[int] = Field(None, ge=0)
    profundidad_inicio_vida_actual_mm: Optional[Decimal] = None


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


class NeumaticoResponse(BaseModel):
    """Esquema de respuesta para neumáticos - Alineado con modelo BD real + campos IA."""
    id: UUID
    numero_serie: Optional[str]
    dot: Optional[str]
    modelo_id: UUID
    fecha_compra: date
    fecha_fabricacion: Optional[date]
    costo_compra: Optional[Decimal]
    moneda_compra: Optional[str]
    proveedor_compra_id: Optional[UUID]
    es_reencauchado: bool
    vida_actual: int
    estado_actual: str
    ubicacion_actual_vehiculo_id: Optional[UUID]
    ubicacion_actual_posicion_id: Optional[UUID]
    fecha_ultimo_evento: Optional[datetime]
    profundidad_inicial_mm: Optional[Decimal]
    kilometraje_acumulado: int
    reencauches_realizados: int
    fecha_desecho: Optional[date]
    motivo_desecho_id: Optional[UUID]
    ubicacion_almacen_id: Optional[UUID]
    sensor_id: Optional[str]
    profundidad_remanente_actual_mm: Decimal
    fecha_ultima_medicion_profundidad: Optional[datetime]
    kilometraje_vida_actual: Optional[int]
    fecha_inicio_vida_actual: Optional[date]
    odometro_instalacion_vida_actual: Optional[int]
    tasa_desgaste_actual_mm_km: Optional[Decimal]
    vida_util_restante_km: Optional[int]
    fecha_ultimo_reencauche: Optional[date]
    activo: Optional[bool]
    proxima_inspeccion_fecha: Optional[date]
    proxima_inspeccion_km: Optional[int]
    profundidad_inicio_vida_actual_mm: Optional[Decimal]
    
    # Campos de IA para predicciones - Sprint 1
    prediccion_fecha_reemplazo: Optional[date] = Field(None, description="Fecha predicha para reemplazo del neumático")
    confianza_prediccion: Optional[Decimal] = Field(None, ge=0, le=1, description="Confianza de la predicción (0.0-1.0)")
    fecha_ultima_prediccion: Optional[datetime] = Field(None, description="Fecha de la última predicción realizada")
    modelo_prediccion_version: Optional[str] = Field(None, description="Versión del modelo ML utilizado")
    
    # Campos de auditoría
    creado_en: datetime
    creado_por: Optional[UUID]
    actualizado_en: Optional[datetime]
    actualizado_por: Optional[UUID]
    
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
