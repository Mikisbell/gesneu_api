# schemas/vehiculo.py
# --- CÓDIGO CORREGIDO ---

import uuid
from datetime import date, datetime, timezone
from typing import Optional, Union, Any
# --- AÑADIR IMPORT PARA ConfigDict y field_validator ---
from pydantic import ConfigDict, field_validator, ValidationInfo, BeforeValidator
from typing_extensions import Annotated
from sqlmodel import SQLModel, Field

# Función para convertir UUID a str si es necesario
def convert_uuid_to_str(v: Any) -> str:
    if isinstance(v, uuid.UUID):
        return str(v)
    return v

# Función para convertir date a str si es necesario
def convert_date_to_str(v: Any) -> str:
    if isinstance(v, date):
        return v.isoformat()
    return v

class VehiculoBase(SQLModel):
    # Foreign key con conversión UUID a str
    tipo_vehiculo_id: Annotated[str, BeforeValidator(convert_uuid_to_str)] = Field(foreign_key="tipos_vehiculo.id")

    # --- CAMPOS CORREGIDOS ---
    numero_economico: str = Field(
        ..., # Obligatorio
        max_length=50,
        sa_column_kwargs={"index": True} # <-- CORRECCIÓN
    )
    placa: Optional[str] = Field(
        default=None,
        max_length=15,
        sa_column_kwargs={"unique": True, "index": True} # <-- CORRECCIÓN
    )
    vin: Optional[str] = Field(
        default=None,
        max_length=17,
        sa_column_kwargs={"unique": True} # <-- CORRECCIÓN
    )
    # -------------------------

    marca: Optional[str] = Field(default=None, max_length=50)
    modelo_vehiculo: Optional[str] = Field(default=None, max_length=50)
    anio_fabricacion: Optional[int] = Field(default=None)
    # Conversión automática de date a str
    fecha_alta: Optional[Annotated[str, BeforeValidator(convert_date_to_str)]] = Field(default=None) 
    activo: bool = Field(default=True) # Especificar default explícito
    ubicacion_actual: Optional[str] = Field(default=None, max_length=100)
    notas: Optional[str] = Field(default=None) # Permitir explícitamente None por defecto

    @field_validator('anio_fabricacion')
    def check_anio_fabricacion(cls, v):
        if v is not None and (v < 1900 or v > datetime.now(timezone.utc).year + 1):
            raise ValueError(f"Año de fabricación inválido: {v}")
        return v

class VehiculoCreate(VehiculoBase):
    pass # No necesita 'from_attributes'

class VehiculoRead(VehiculoBase):
    id: Annotated[str, BeforeValidator(convert_uuid_to_str)]  # Conversión automática de UUID a str
    # Estos campos vienen del modelo de tabla, no de la base
    odometro_actual: Optional[int] = None
    fecha_ultimo_odometro: Optional[datetime] = None
    creado_en: datetime
    actualizado_en: Optional[datetime] = None
    # Podrías añadir relaciones aquí si las defines en el modelo y las quieres leer
    # tipo_vehiculo: Optional["TipoVehiculoRead"] = None # Ejemplo

    # --- CORRECCIÓN: Añadir model_config ---
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    # ------------------------------------


class VehiculoUpdate(SQLModel): # Todos opcionales para PATCH/PUT
    tipo_vehiculo_id: Optional[Annotated[str, BeforeValidator(convert_uuid_to_str)]] = Field(default=None)
    numero_economico: Optional[str] = Field(default=None, max_length=50) # Mantener max_length
    placa: Optional[str] = Field(default=None, max_length=15)
    vin: Optional[str] = Field(default=None, max_length=17)
    marca: Optional[str] = Field(default=None, max_length=50)
    modelo_vehiculo: Optional[str] = Field(default=None, max_length=50)
    anio_fabricacion: Optional[int] = Field(default=None)
    fecha_alta: Optional[Annotated[str, BeforeValidator(convert_date_to_str)]] = Field(default=None)
    activo: Optional[bool] = Field(default=None)
    ubicacion_actual: Optional[str] = Field(default=None, max_length=100)
    notas: Optional[str] = Field(default=None)
    # Campos específicos del modelo de tabla también opcionales para actualizar
    fecha_baja: Optional[Annotated[str, BeforeValidator(convert_date_to_str)]] = Field(default=None)
    odometro_actual: Optional[int] = Field(default=None)
    fecha_ultimo_odometro: Optional[datetime] = Field(default=None)
    # Configuración para permitir conversión de atributos
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)