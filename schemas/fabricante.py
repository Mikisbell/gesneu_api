# schemas/fabricante.py
import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class FabricanteNeumaticoBase(SQLModel):
    nombre: str = Field(max_length=100, index=True) # Requerido
    codigo_abreviado: Optional[str] = Field(default=None, unique=True, max_length=10) # UNIQUE en DB
    pais_origen: Optional[str] = Field(default=None, max_length=50)
    # Añadimos sitio_web basado en tu script SQL Fase 3
    sitio_web: Optional[str] = Field(default=None, max_length=255)
    activo: bool = Field(default=True) # Especificar default explícito

class FabricanteNeumaticoCreate(FabricanteNeumaticoBase):
    # Usaremos esta para validar la entrada del POST
    pass

class FabricanteNeumaticoRead(FabricanteNeumaticoBase):
    # Usaremos esta como response_model para GET
    id: uuid.UUID
    creado_en: datetime
    actualizado_en: Optional[datetime] = None
    # Podríamos añadir aquí creado_por/actualizado_por si fuera necesario

class FabricanteNeumaticoUpdate(SQLModel):
    # Modelo para PUT/PATCH, todo opcional
    nombre: Optional[str] = None
    codigo_abreviado: Optional[str] = None
    pais_origen: Optional[str] = None
    sitio_web: Optional[str] = None
    activo: Optional[bool] = None