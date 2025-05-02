# schemas/tipo_vehiculo.py
import uuid
from datetime import datetime
from typing import Optional
from pydantic import field_validator, Field # Importar Field
from sqlmodel import SQLModel

# Schema Base: Campos comunes para creación y lectura
class TipoVehiculoBase(SQLModel):
    nombre: str = Field(max_length=100, index=True) # Asumiendo índice en nombre
    descripcion: Optional[str] = None
    categoria_principal: Optional[str] = Field(default=None, max_length=50)
    subtipo: Optional[str] = Field(default=None, max_length=50)
    # Usar Field para añadir validación ge/le (mayor/igual, menor/igual)
    ejes_standard: int = Field(default=2, ge=1, le=10) # Valida entre 1 y 10
    activo: bool = True

    # Validador adicional (opcional, Field(ge=1, le=10) ya lo hace)
    # @field_validator('ejes_standard')
    # def check_ejes_standard(cls, v):
    #     if not (1 <= v <= 10):
    #         raise ValueError('El número de ejes estándar debe estar entre 1 y 10')
    #     return v

# Schema para Crear: Hereda de Base
class TipoVehiculoCreate(TipoVehiculoBase):
    pass # No necesita campos adicionales por ahora

# Schema para Leer: Hereda de Base y añade campos de solo lectura
class TipoVehiculoRead(TipoVehiculoBase):
    id: uuid.UUID
    creado_en: datetime
    actualizado_en: Optional[datetime] = None
    # Podrías añadir creado_por / actualizado_por si necesitas mostrar datos del usuario

# Schema para Actualizar: Campos opcionales
class TipoVehiculoUpdate(SQLModel):
    nombre: Optional[str] = Field(default=None, max_length=100)
    descripcion: Optional[str] = None
    categoria_principal: Optional[str] = Field(default=None, max_length=50)
    subtipo: Optional[str] = Field(default=None, max_length=50)
    ejes_standard: Optional[int] = Field(default=None, ge=1, le=10) # Mantener validación
    activo: Optional[bool] = None
    # No incluir campos de auditoría (id, creado*, actualizado*)