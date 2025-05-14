# gesneu_api2/schemas/posicion_neumatico.py
from typing import Optional, ClassVar, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from .common import EstadoItem

# Properties to receive via API on creation
class PosicionNeumaticoBase(BaseModel):
    configuracion_eje_id: int
    codigo_posicion: str = Field(..., max_length=50)
    descripcion: Optional[str] = Field(None, max_length=255)
    indice_reemplazo_preferente: Optional[int] = None
    # activo: bool = True # Se manejará por defecto en el modelo o CRUD si es necesario

class PosicionNeumaticoCreate(PosicionNeumaticoBase):
    pass

# Properties to receive via API on update, all optional
class PosicionNeumaticoUpdate(BaseModel):
    configuracion_eje_id: Optional[int] = None
    codigo_posicion: Optional[str] = Field(None, max_length=50)
    descripcion: Optional[str] = Field(None, max_length=255)
    indice_reemplazo_preferente: Optional[int] = None
    # activo: Optional[bool] = None # Para permitir activar/desactivar

# Properties shared by models stored in DB
class PosicionNeumaticoInDBBase(PosicionNeumaticoBase, EstadoItem):
    id: int

    # Configuración moderna usando model_config con ConfigDict
        

    model_config: ClassVar[Dict[str, Any]] = ConfigDict(
        from_attributes=True
    )

# Additional properties to return via API
class PosicionNeumatico(PosicionNeumaticoInDBBase):
    # Aquí podrías añadir campos de relaciones si fueran necesarios para la respuesta
    # Por ejemplo, si quisieras devolver detalles de 'configuracion_eje':
    # configuracion_eje: Optional[ConfiguracionEjeSchema] = None # Necesitarías importar ConfiguracionEjeSchema
    pass

# Para listar múltiples posiciones
class PosicionNeumaticoResponse(PosicionNeumatico):
    pass