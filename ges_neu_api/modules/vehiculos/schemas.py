"""
Esquemas Pydantic para el módulo de vehículos - Alineados exactamente con PostgreSQL
Basado en ESQUEMA_COMPLETO_BD.md
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .enums import TipoEjeEnum, LadoVehiculoEnum


# ============================================================================
# ESQUEMAS BASE
# ============================================================================

class TiposVehiculoBase(BaseModel):
    """Esquema base para tipos de vehículo"""
    nombre: str = Field(..., max_length=100, description="Nombre del tipo de vehículo")
    descripcion: Optional[str] = Field(None, description="Descripción del tipo de vehículo")
    categoria_principal: Optional[str] = Field(None, max_length=50, description="Categoría principal")
    subtipo: Optional[str] = Field(None, max_length=50, description="Subtipo del vehículo")
    ejes_standard: int = Field(2, ge=1, le=10, description="Número estándar de ejes")
    activo: bool = Field(True, description="Estado activo del tipo de vehículo")


class ConfiguracionesEjeBase(BaseModel):
    """Esquema base para configuraciones de eje"""
    tipo_vehiculo_id: UUID = Field(..., description="ID del tipo de vehículo")
    numero_eje: int = Field(..., gt=0, description="Número del eje")
    nombre_eje: str = Field(..., max_length=50, description="Nombre del eje")
    tipo_eje: TipoEjeEnum = Field(..., description="Tipo de eje")
    numero_posiciones: int = Field(..., ge=1, le=6, description="Número de posiciones")
    posiciones_duales: bool = Field(False, description="Tiene posiciones duales")
    permite_reencauchados: bool = Field(True, description="Permite neumáticos reencauchados")
    neumaticos_por_posicion: int = Field(1, ge=1, le=2, description="Neumáticos por posición")


class PosicionesNeumaticoBase(BaseModel):
    """Esquema base para posiciones de neumático"""
    configuracion_eje_id: UUID = Field(..., description="ID de la configuración de eje")
    codigo_posicion: str = Field(..., max_length=10, description="Código de la posición")
    etiqueta_posicion: Optional[str] = Field(None, max_length=50, description="Etiqueta de la posición")
    lado: LadoVehiculoEnum = Field(..., description="Lado del vehículo")
    posicion_relativa: int = Field(..., gt=0, description="Posición relativa")
    es_interna: bool = Field(False, description="Es posición interna")
    es_direccion: bool = Field(False, description="Es posición de dirección")
    es_traccion: bool = Field(False, description="Es posición de tracción")
    requiere_neumatico_especifico: bool = Field(False, description="Requiere neumático específico")


class VehiculosBase(BaseModel):
    """Esquema base para vehículos"""
    tipo_vehiculo_id: UUID = Field(..., description="ID del tipo de vehículo")
    placa: Optional[str] = Field(None, max_length=15, description="Placa del vehículo")
    vin: Optional[str] = Field(None, max_length=17, description="VIN del vehículo")
    numero_economico: str = Field(..., max_length=50, description="Número económico")
    marca: Optional[str] = Field(None, max_length=50, description="Marca del vehículo")
    modelo_vehiculo: Optional[str] = Field(None, max_length=50, description="Modelo del vehículo")
    anio_fabricacion: Optional[int] = Field(None, ge=1900, description="Año de fabricación")
    fecha_alta: date = Field(..., description="Fecha de alta")
    fecha_baja: Optional[date] = Field(None, description="Fecha de baja")
    activo: bool = Field(True, description="Estado activo del vehículo")
    odometro_actual: Optional[int] = Field(None, ge=0, description="Odómetro actual")
    fecha_ultimo_odometro: Optional[datetime] = Field(None, description="Fecha último odómetro")
    ubicacion_actual: Optional[str] = Field(None, max_length=100, description="Ubicación actual")
    notas: Optional[str] = Field(None, description="Notas adicionales")
    peso_carga_maxima_diseno_ton: Optional[Decimal] = Field(None, description="Peso máximo de carga en toneladas")


class RegistrosOdometroBase(BaseModel):
    """Esquema base para registros de odómetro"""
    vehiculo_id: UUID = Field(..., description="ID del vehículo")
    odometro: int = Field(..., ge=0, description="Lectura del odómetro")
    fecha_medicion: datetime = Field(..., description="Fecha de medición")
    fuente: Optional[str] = Field("manual", max_length=50, description="Fuente de la medición")
    notas: Optional[str] = Field(None, description="Notas adicionales")


# ============================================================================
# ESQUEMAS DE CREACIÓN
# ============================================================================

class TiposVehiculoCreate(TiposVehiculoBase):
    """Esquema para crear tipos de vehículo"""
    pass


class ConfiguracionesEjeCreate(ConfiguracionesEjeBase):
    """Esquema para crear configuraciones de eje"""
    pass


class PosicionesNeumaticoCreate(PosicionesNeumaticoBase):
    """Esquema para crear posiciones de neumático"""
    pass


class VehiculosCreate(VehiculosBase):
    """Esquema para crear vehículos"""
    pass


class RegistrosOdometroCreate(RegistrosOdometroBase):
    """Esquema para crear registros de odómetro"""
    pass


# ============================================================================
# ESQUEMAS DE ACTUALIZACIÓN
# ============================================================================

class TiposVehiculoUpdate(BaseModel):
    """Esquema para actualizar tipos de vehículo"""
    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = Field(None)
    categoria_principal: Optional[str] = Field(None, max_length=50)
    subtipo: Optional[str] = Field(None, max_length=50)
    ejes_standard: Optional[int] = Field(None, ge=1, le=10)
    activo: Optional[bool] = Field(None)


class ConfiguracionesEjeUpdate(BaseModel):
    """Esquema para actualizar configuraciones de eje"""
    tipo_vehiculo_id: Optional[UUID] = Field(None)
    numero_eje: Optional[int] = Field(None, gt=0)
    nombre_eje: Optional[str] = Field(None, max_length=50)
    tipo_eje: Optional[TipoEjeEnum] = Field(None)
    numero_posiciones: Optional[int] = Field(None, ge=1, le=6)
    posiciones_duales: Optional[bool] = Field(None)
    permite_reencauchados: Optional[bool] = Field(None)
    neumaticos_por_posicion: Optional[int] = Field(None, ge=1, le=2)


class PosicionesNeumaticoUpdate(BaseModel):
    """Esquema para actualizar posiciones de neumático"""
    configuracion_eje_id: Optional[UUID] = Field(None)
    codigo_posicion: Optional[str] = Field(None, max_length=10)
    etiqueta_posicion: Optional[str] = Field(None, max_length=50)
    lado: Optional[LadoVehiculoEnum] = Field(None)
    posicion_relativa: Optional[int] = Field(None, gt=0)
    es_interna: Optional[bool] = Field(None)
    es_direccion: Optional[bool] = Field(None)
    es_traccion: Optional[bool] = Field(None)
    requiere_neumatico_especifico: Optional[bool] = Field(None)


class VehiculosUpdate(BaseModel):
    """Esquema para actualizar vehículos"""
    tipo_vehiculo_id: Optional[UUID] = Field(None)
    placa: Optional[str] = Field(None, max_length=15)
    vin: Optional[str] = Field(None, max_length=17)
    numero_economico: Optional[str] = Field(None, max_length=50)
    marca: Optional[str] = Field(None, max_length=50)
    modelo_vehiculo: Optional[str] = Field(None, max_length=50)
    anio_fabricacion: Optional[int] = Field(None, ge=1900)
    fecha_alta: Optional[date] = Field(None)
    fecha_baja: Optional[date] = Field(None)
    activo: Optional[bool] = Field(None)
    odometro_actual: Optional[int] = Field(None, ge=0)
    fecha_ultimo_odometro: Optional[datetime] = Field(None)
    ubicacion_actual: Optional[str] = Field(None, max_length=100)
    notas: Optional[str] = Field(None)
    peso_carga_maxima_diseno_ton: Optional[Decimal] = Field(None)


class RegistrosOdometroUpdate(BaseModel):
    """Esquema para actualizar registros de odómetro"""
    vehiculo_id: Optional[UUID] = Field(None)
    odometro: Optional[int] = Field(None, ge=0)
    fecha_medicion: Optional[datetime] = Field(None)
    fuente: Optional[str] = Field(None, max_length=50)
    notas: Optional[str] = Field(None)


# ============================================================================
# ESQUEMAS DE LECTURA
# ============================================================================

class TiposVehiculoRead(TiposVehiculoBase):
    """Esquema para leer tipos de vehículo"""
    id: UUID
    creado_en: datetime
    creado_por: Optional[UUID] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = None

    class Config:
        from_attributes = True


class ConfiguracionesEjeRead(ConfiguracionesEjeBase):
    """Esquema para leer configuraciones de eje"""
    id: UUID
    creado_en: datetime
    creado_por: Optional[UUID] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = None

    class Config:
        from_attributes = True


class PosicionesNeumaticoRead(PosicionesNeumaticoBase):
    """Esquema para leer posiciones de neumático"""
    id: UUID
    creado_en: datetime
    creado_por: Optional[UUID] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = None

    class Config:
        from_attributes = True


class VehiculosRead(VehiculosBase):
    """Esquema para leer vehículos"""
    id: UUID
    creado_en: datetime
    creado_por: Optional[UUID] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = None

    class Config:
        from_attributes = True


class RegistrosOdometroRead(RegistrosOdometroBase):
    """Esquema para leer registros de odómetro"""
    id: UUID
    creado_por: Optional[UUID] = None

    class Config:
        from_attributes = True
