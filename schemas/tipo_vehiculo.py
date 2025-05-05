# schemas/tipo_vehiculo.py
# --- CÓDIGO CORREGIDO (IMPORTACIÓN DE FIELD) ---

import uuid
from datetime import datetime
from typing import Optional
# --- IMPORTAR Field DESDE sqlmodel ---
from pydantic import field_validator, ConfigDict # Field ya no se importa de pydantic
from sqlmodel import SQLModel, Field # <-- Asegurarse que Field viene de aquí

class TipoVehiculoBase(SQLModel):
    # --- El campo con sa_column_kwargs ahora usará sqlmodel.Field ---
    nombre: str = Field(
        ...,
        max_length=100,
        sa_column_kwargs={"index": True}
    )
    # -------------------------------------------------------------
    descripcion: Optional[str] = Field(default=None)
    categoria_principal: Optional[str] = Field(default=None, max_length=50)
    subtipo: Optional[str] = Field(default=None, max_length=50)
    # Las validaciones ge/le funcionan igual en sqlmodel.Field
    ejes_standard: int = Field(default=2, ge=1, le=10)
    activo: bool = Field(default=True)

    # Validador (opcional)
    # @field_validator('ejes_standard') ...

class TipoVehiculoCreate(TipoVehiculoBase):
    pass

class TipoVehiculoRead(TipoVehiculoBase):
    id: uuid.UUID
    creado_en: datetime
    actualizado_en: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True) # Esto ya estaba bien

class TipoVehiculoUpdate(SQLModel):
    nombre: Optional[str] = Field(default=None, max_length=100)
    descripcion: Optional[str] = Field(default=None)
    categoria_principal: Optional[str] = Field(default=None, max_length=50)
    subtipo: Optional[str] = Field(default=None, max_length=50)
    ejes_standard: Optional[int] = Field(default=None, ge=1, le=10)
    activo: Optional[bool] = Field(default=None)