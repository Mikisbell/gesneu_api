# gesneu_api2/schemas/parametro_inventario.py
from typing import Optional, ClassVar, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from .common import EstadoItem, TipoParametroEnum # Asegúrate que TipoParametroEnum esté en common.py

# Properties to receive via API on creation
class ParametroInventarioBase(BaseModel):
    modelo_id: Optional[int] = None # Puede ser un parámetro global o específico de un modelo
    tipo_parametro: TipoParametroEnum
    valor_numerico: Optional[Decimal] = Field(None, decimal_places=2)
    valor_texto: Optional[str] = Field(None, max_length=255)
    unidad: Optional[str] = Field(None, max_length=50)
    descripcion: Optional[str] = Field(None, max_length=255)

class ParametroInventarioCreate(ParametroInventarioBase):
    pass

# Properties to receive via API on update, all optional
class ParametroInventarioUpdate(BaseModel):
    modelo_id: Optional[int] = None
    tipo_parametro: Optional[TipoParametroEnum] = None
    valor_numerico: Optional[Decimal] = Field(None, decimal_places=2)
    valor_texto: Optional[str] = Field(None, max_length=255)
    unidad: Optional[str] = Field(None, max_length=50)
    descripcion: Optional[str] = Field(None, max_length=255)
    # activo: Optional[bool] = None # Si quieres poder actualizarlo directamente

# Properties shared by models stored in DB
class ParametroInventarioInDBBase(ParametroInventarioBase, EstadoItem):
    id: int

    # Configuración moderna usando model_config con ConfigDict
        

    model_config: ClassVar[Dict[str, Any]] = ConfigDict(
        

        from_attributes=True  # Reemplaza orm_mode=True, from_attributes=True
        

    )

# Additional properties to return via API
class ParametroInventario(ParametroInventarioInDBBase):
    # Si necesitas devolver el modelo relacionado, lo definirías aquí
    # modelo: Optional[ModeloNeumaticoSchema] = None # Necesitarías un ModeloNeumaticoSchema
    pass

class ParametroInventarioResponse(ParametroInventario):
    pass