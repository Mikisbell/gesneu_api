from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .models import TipoEjeEnum, LadoVehiculoEnum # Import enums from models

# Base Schemas
class TiposVehiculoBase(BaseModel):
    nombre: str
    ejes_standard: int
    activo: bool
    descripcion: Optional[str] = None
    categoria_principal: Optional[str] = None
    subtipo: Optional[str] = None

class ConfiguracionesEjeBase(BaseModel):
    tipo_vehiculo_id: UUID
    numero_eje: int
    nombre_eje: str
    tipo_eje: TipoEjeEnum
    numero_posiciones: int
    posiciones_duales: bool
    permite_reencauchados: bool
    neumaticos_por_posicion: int
    etiqueta_posicion: Optional[str] = None

class PosicionesNeumaticoBase(BaseModel):
    configuracion_eje_id: UUID
    codigo_posicion: str
    lado: LadoVehiculoEnum
    posicion_relativa: int
    es_interna: bool
    es_direccion: bool
    es_traccion: bool
    requiere_neumatico_especifico: bool
    etiqueta_posicion: Optional[str] = None

class VehiculoBase(BaseModel):
    tipo_vehiculo_id: UUID
    numero_economico: str
    fecha_alta: date
    activo: bool
    placa: Optional[str] = None
    vin: Optional[str] = None
    marca: Optional[str] = None
    modelo_vehiculo: Optional[str] = None
    anio_fabricacion: Optional[int] = None
    fecha_baja: Optional[date] = None
    odometro_actual: Optional[int] = None
    fecha_ultimo_odometro: Optional[datetime] = None
    ubicacion_actual: Optional[str] = None
    notas: Optional[str] = None
    peso_carga_maxima_diseno_ton: Optional[Decimal] = None

class RegistrosOdometroBase(BaseModel):
    vehiculo_id: UUID
    odometro: int
    fecha_medicion: datetime
    fuente: Optional[str] = None
    notas: Optional[str] = None

# Create Schemas
class TiposVehiculoCreate(TiposVehiculoBase):
    pass

class ConfiguracionesEjeCreate(ConfiguracionesEjeBase):
    pass

class PosicionesNeumaticoCreate(PosicionesNeumaticoBase):
    pass

class VehiculoCreate(VehiculoBase):
    pass

class RegistrosOdometroCreate(RegistrosOdometroBase):
    pass

# Update Schemas
class TiposVehiculoUpdate(TiposVehiculoBase):
    nombre: Optional[str] = None
    ejes_standard: Optional[int] = None
    activo: Optional[bool] = None

class ConfiguracionesEjeUpdate(ConfiguracionesEjeBase):
    tipo_vehiculo_id: Optional[UUID] = None
    numero_eje: Optional[int] = None
    nombre_eje: Optional[str] = None
    tipo_eje: Optional[TipoEjeEnum] = None
    numero_posiciones: Optional[int] = None
    posiciones_duales: Optional[bool] = None
    permite_reencauchados: Optional[bool] = None
    neumaticos_por_posicion: Optional[int] = None

class PosicionesNeumaticoUpdate(PosicionesNeumaticoBase):
    configuracion_eje_id: Optional[UUID] = None
    codigo_posicion: Optional[str] = None
    lado: Optional[LadoVehiculoEnum] = None
    posicion_relativa: Optional[int] = None
    es_interna: Optional[bool] = None
    es_direccion: Optional[bool] = None
    es_traccion: Optional[bool] = None
    requiere_neumatico_especifico: Optional[bool] = None

class VehiculoUpdate(VehiculoBase):
    tipo_vehiculo_id: Optional[UUID] = None
    numero_economico: Optional[str] = None
    fecha_alta: Optional[date] = None
    activo: Optional[bool] = None

class RegistrosOdometroUpdate(RegistrosOdometroBase):
    vehiculo_id: Optional[UUID] = None
    odometro: Optional[int] = None
    fecha_medicion: Optional[datetime] = None

# Read Schemas (for API responses)
class TiposVehiculoRead(TiposVehiculoBase):
    id: UUID
    creado_en: datetime
    creado_por: Optional[UUID] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)

class ConfiguracionesEjeRead(ConfiguracionesEjeBase):
    id: UUID
    creado_en: datetime
    creado_por: Optional[UUID] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = None
    
    tipo_vehiculo: TiposVehiculoRead # Nested read model

    model_config = ConfigDict(from_attributes=True)

class PosicionesNeumaticoRead(PosicionesNeumaticoBase):
    id: UUID
    creado_en: datetime
    creado_por: Optional[UUID] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = None
    
    configuracion_eje: ConfiguracionesEjeRead # Nested read model

    model_config = ConfigDict(from_attributes=True)

class VehiculoRead(VehiculoBase):
    id: UUID
    creado_en: datetime
    creado_por: Optional[UUID] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = None
    
    tipo_vehiculo: TiposVehiculoRead # Nested read model

    model_config = ConfigDict(from_attributes=True)

class RegistrosOdometroRead(RegistrosOdometroBase):
    id: UUID
    creado_por: Optional[UUID] = None
    
    vehiculo: VehiculoRead # Nested read model

    model_config = ConfigDict(from_attributes=True)
