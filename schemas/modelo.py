# gesneu_api2/schemas/modelo.py
from typing import Optional, List, ClassVar, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from .common import EstadoItem # Asumo que tienes EstadoItem en schemas/common.py
# Si necesitas devolver información detallada del fabricante,
# necesitarás importar su respectivo schema.
# from .fabricante import FabricanteResponse # O el schema que corresponda

# Properties to receive via API on creation
class ModeloBase(BaseModel):
    fabricante_id: int
    nombre_modelo: str = Field(..., max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)
    ancho_seccion_mm: Optional[int] = Field(None, gt=0)
    relacion_aspecto: Optional[int] = Field(None, gt=0)
    tipo_construccion: Optional[str] = Field(None, max_length=20) # Ejemplo: Radial, Diagonal
    diametro_llanta_pulgadas: Optional[Decimal] = Field(None, gt=0, decimal_places=1)
    indice_carga: Optional[int] = Field(None, gt=0)
    simbolo_velocidad: Optional[str] = Field(None, max_length=5)
    profundidad_original_mm: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    presion_maxima_psi: Optional[int] = Field(None, gt=0)
    reencauches_maximos: Optional[int] = Field(None, ge=0, default=0) # ge=0 para permitir 0 reencauches
    permite_reencauche: bool = False
    # activo: bool = True # Se manejará a través de EstadoItem o por defecto en el modelo

class ModeloCreate(ModeloBase):
    pass

# Properties to receive via API on update, all optional
class ModeloUpdate(BaseModel):
    fabricante_id: Optional[int] = None
    nombre_modelo: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)
    ancho_seccion_mm: Optional[int] = Field(None, gt=0)
    relacion_aspecto: Optional[int] = Field(None, gt=0)
    tipo_construccion: Optional[str] = Field(None, max_length=20)
    diametro_llanta_pulgadas: Optional[Decimal] = Field(None, gt=0, decimal_places=1)
    indice_carga: Optional[int] = Field(None, gt=0)
    simbolo_velocidad: Optional[str] = Field(None, max_length=5)
    profundidad_original_mm: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    presion_maxima_psi: Optional[int] = Field(None, gt=0)
    reencauches_maximos: Optional[int] = Field(None, ge=0)
    permite_reencauche: Optional[bool] = None
    activo: Optional[bool] = None # Para permitir activar/desactivar

# Properties shared by models stored in DB
class ModeloInDBBase(ModeloBase, EstadoItem):
    id: int

    # Configuración moderna usando model_config con ConfigDict
        

    model_config: ClassVar[Dict[str, Any]] = ConfigDict(
        

        from_attributes=True  # Reemplaza orm_mode=True
        

    )

# Additional properties to return via API
class Modelo(ModeloInDBBase):
    # Aquí puedes incluir los schemas de las relaciones si quieres que se devuelvan
    # Por ejemplo, para el fabricante:
    # from .fabricante import Fabricante  # Asegúrate de tener este schema
    # fabricante: Optional[Fabricante] = None
    pass

class ModeloResponse(Modelo):
    """Schema para la respuesta de un modelo individual."""
    # Si quieres incluir relaciones por defecto en la respuesta, defínelas aquí.
    # Por ejemplo, para incluir el fabricante asociado:
    # from .fabricante import FabricanteResponse # Asegúrate de tener este schema
    # fabricante: Optional[FabricanteResponse] = None
    pass

class ModeloConDetallesResponse(Modelo):
    """
    Schema extendido para respuestas de modelo que podrían incluir detalles de relaciones.
    """
    # from .fabricante import FabricanteResponse
    # fabricante: Optional[FabricanteResponse] = None
    # Podrías también querer listar los parámetros de inventario asociados a este modelo:
    # from .parametro_inventario import ParametroInventarioResponse
    # parametros_inventario: List[ParametroInventarioResponse] = []
    pass
