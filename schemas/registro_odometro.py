# gesneu_api2/schemas/registro_odometro.py
from typing import Optional
from datetime import date, datetime # datetime para campos de timestamp si los usas
from pydantic import BaseModel, Field
# Si necesitas devolver información detallada del vehículo,
# necesitarás importar su respectivo schema.
# from .vehiculo import VehiculoResponse # O el schema que corresponda

# Properties to receive via API on creation
class RegistroOdometroBase(BaseModel):
    vehiculo_id: int
    kilometraje: int = Field(..., gt=0) # Kilometraje debe ser positivo
    fecha_registro: Optional[date] = Field(default_factory=date.today) # Permite enviarlo o usa la fecha actual
    observaciones: Optional[str] = Field(None, max_length=500)

class RegistroOdometroCreate(RegistroOdometroBase):
    pass

# Properties to receive via API on update
# Generalmente, los registros de odómetro son inmutables una vez creados,
# pero podrías querer permitir la corrección de observaciones.
class RegistroOdometroUpdate(BaseModel):
    # vehiculo_id: Optional[int] = None # No suele cambiarse
    # kilometraje: Optional[int] = Field(None, gt=0) # No suele cambiarse
    # fecha_registro: Optional[date] = None # No suele cambiarse
    observaciones: Optional[str] = Field(None, max_length=500)
    # Considera si realmente necesitas actualizar otros campos o si es mejor crear un nuevo registro.

# Properties shared by models stored in DB
class RegistroOdometroInDBBase(RegistroOdometroBase):
    id: int
    # Si tu modelo base (SQLModel) añade timestamps automáticos y quieres exponerlos:
    # created_at: datetime
    # updated_at: datetime

    class Config:
        from_attributes = True # Para Pydantic V2 (reemplaza orm_mode)
        # orm_mode = True # Para Pydantic V1

# Additional properties to return via API
class RegistroOdometro(RegistroOdometroInDBBase):
    # Aquí puedes incluir los schemas de las relaciones si quieres que se devuelvan
    # Por ejemplo, para el vehículo:
    # from .vehiculo import Vehiculo  # Asegúrate de tener este schema
    # vehiculo: Optional[Vehiculo] = None
    pass

class RegistroOdometroResponse(RegistroOdometro):
    """Schema para la respuesta de un registro de odómetro individual."""
    # Si quieres incluir relaciones por defecto en la respuesta, defínelas aquí.
    # Por ejemplo, para incluir el vehículo asociado:
    # from .vehiculo import VehiculoResponse # Asegúrate de tener este schema
    # vehiculo: Optional[VehiculoResponse] = None
    pass
