# gesneu_api2/schemas/motivo_desecho.py
from typing import Optional, ClassVar, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from .common import EstadoItem # Asumo que tienes EstadoItem en schemas/common.py

# Properties to receive via API on creation
class MotivoDesechoBase(BaseModel):
    descripcion: str = Field(..., min_length=3, max_length=255)
    # activo: bool = True # Se manejará a través de EstadoItem o por defecto en el modelo

class MotivoDesechoCreate(MotivoDesechoBase):
    pass

# Properties to receive via API on update, all optional
class MotivoDesechoUpdate(BaseModel):
    descripcion: Optional[str] = Field(None, min_length=3, max_length=255)
    activo: Optional[bool] = None # Para permitir activar/desactivar

# Properties shared by models stored in DB
class MotivoDesechoInDBBase(MotivoDesechoBase, EstadoItem):
    id: int

    # Configuración moderna usando model_config con ConfigDict
        

    model_config: ClassVar[Dict[str, Any]] = ConfigDict(
        

        from_attributes=True  # Reemplaza orm_mode=True
        

    )

# Additional properties to return via API
class MotivoDesecho(MotivoDesechoInDBBase):
    pass

class MotivoDesechoResponse(MotivoDesecho):
    """Schema para la respuesta de un motivo de desecho individual."""
    pass
