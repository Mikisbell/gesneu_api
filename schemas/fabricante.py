# schemas/fabricante.py
import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

# Base: Campos comunes que pueden venir del cliente o mostrarse
class FabricanteNeumaticoBase(SQLModel):
    nombre: str = Field(max_length=100, index=True) # Requerido
    codigo_abreviado: Optional[str] = Field(default=None, unique=True, max_length=10)
    pais_origen: Optional[str] = Field(default=None, max_length=50)
    sitio_web: Optional[str] = Field(default=None, max_length=255)
    activo: bool = True

# Crear: Lo que la API recibe para crear un fabricante
class FabricanteNeumaticoCreate(FabricanteNeumaticoBase):
    pass # Los campos base son suficientes por ahora

# Leer: Lo que la API devuelve al leer un fabricante
class FabricanteNeumaticoRead(FabricanteNeumaticoBase):
    id: uuid.UUID
    creado_en: datetime
    actualizado_en: Optional[datetime] = None

# Actualizar: Campos opcionales para actualizar un fabricante
class FabricanteNeumaticoUpdate(SQLModel):
    nombre: Optional[str] = None
    codigo_abreviado: Optional[str] = None
    pais_origen: Optional[str] = None
    sitio_web: Optional[str] = None
    activo: Optional[bool] = None