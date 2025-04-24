# schemas/vehiculo.py
import uuid
from datetime import date, datetime, timezone
from typing import Optional
from pydantic import field_validator, ValidationInfo, EmailStr # Añadir EmailStr si es necesario por herencia indirecta? No en este caso.
from sqlmodel import SQLModel, Field
# Nota: Si VehiculoRead necesita referenciar TipoVehiculo, ajustaremos luego.

# Vehículos (Base definida ANTES)
class VehiculoBase(SQLModel):
    tipo_vehiculo_id: uuid.UUID = Field(foreign_key="tipos_vehiculo.id")
    numero_economico: str = Field(max_length=50, index=True)
    placa: Optional[str] = Field(default=None, unique=True, index=True, max_length=15)
    vin: Optional[str] = Field(default=None, unique=True, max_length=17)
    marca: Optional[str] = Field(default=None, max_length=50)
    modelo_vehiculo: Optional[str] = Field(default=None, max_length=50)
    anio_fabricacion: Optional[int] = Field(default=None)
    fecha_alta: Optional[date] = Field(default_factory=date.today)
    activo: bool = True
    ubicacion_actual: Optional[str] = Field(default=None, max_length=100)
    notas: Optional[str] = None

    @field_validator('anio_fabricacion')
    def check_anio_fabricacion(cls, v):
        if v is not None and (v < 1900 or v > datetime.now(timezone.utc).year + 1):
            raise ValueError(f"Año de fabricación inválido: {v}")
        return v

class VehiculoCreate(VehiculoBase):
    pass

class VehiculoRead(VehiculoBase):
    id: uuid.UUID
    odometro_actual: Optional[int] = None
    fecha_ultimo_odometro: Optional[datetime] = None
    creado_en: datetime
    actualizado_en: Optional[datetime] = None

class VehiculoUpdate(SQLModel):
    tipo_vehiculo_id: Optional[uuid.UUID] = None; placa: Optional[str] = None; vin: Optional[str] = None; numero_economico: Optional[str] = None; marca: Optional[str] = None; modelo_vehiculo: Optional[str] = None; anio_fabricacion: Optional[int] = None; fecha_alta: Optional[date] = None; fecha_baja: Optional[date] = None; activo: Optional[bool] = None; ubicacion_actual: Optional[str] = None; notas: Optional[str] = None

# --- Modelos de Tabla ---