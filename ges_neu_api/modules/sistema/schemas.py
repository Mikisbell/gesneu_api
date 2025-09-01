"""
Esquemas Pydantic para el módulo de sistema
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field


# ============================================================================
# PARÁMETROS SISTEMA
# ============================================================================

class ParametrosSistemaBase(BaseModel):
    clave: str = Field(max_length=100)
    valor: str
    descripcion: Optional[str] = None

class ParametrosSistemaCreate(ParametrosSistemaBase):
    creado_por: Optional[str] = "SISTEMA"

class ParametrosSistemaUpdate(BaseModel):
    valor: Optional[str] = None
    descripcion: Optional[str] = None
    actualizado_por: Optional[str] = "SISTEMA"

class ParametrosSistemaRead(ParametrosSistemaBase):
    id: int
    creado_en: Optional[datetime] = None
    actualizado_en: Optional[datetime] = None
    creado_por: Optional[str] = None
    actualizado_por: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================================
# TAREAS PROGRAMADAS
# ============================================================================

class TareasProgramadasBase(BaseModel):
    nombre_tarea: str = Field(max_length=100)
    frecuencia_dias: int = Field(default=1, ge=1)
    descripcion: Optional[str] = None
    activa: Optional[bool] = True
    script_sql: Optional[str] = None

class TareasProgramadasCreate(TareasProgramadasBase):
    creado_por: Optional[str] = "SISTEMA"

class TareasProgramadasUpdate(BaseModel):
    nombre_tarea: Optional[str] = None
    frecuencia_dias: Optional[int] = Field(None, ge=1)
    descripcion: Optional[str] = None
    activa: Optional[bool] = None
    script_sql: Optional[str] = None
    ultima_ejecucion: Optional[datetime] = None
    proxima_ejecucion: Optional[datetime] = None
    actualizado_por: Optional[str] = None

class TareasProgramadasRead(TareasProgramadasBase):
    id: int
    ultima_ejecucion: Optional[datetime] = None
    proxima_ejecucion: Optional[datetime] = None
    creado_en: Optional[datetime] = None
    creado_por: Optional[str] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================================
# RUTAS
# ============================================================================

class RutasBase(BaseModel):
    codigo: str = Field(max_length=20)
    nombre: str = Field(max_length=100)
    descripcion: Optional[str] = None
    activo: bool = True

class RutasCreate(RutasBase):
    creado_por: Optional[UUID] = None

class RutasUpdate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=20)
    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = None
    activo: Optional[bool] = None
    actualizado_por: Optional[UUID] = None

class RutasRead(RutasBase):
    id: UUID
    creado_en: datetime
    creado_por: Optional[UUID] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = None

    class Config:
        from_attributes = True


# ============================================================================
# TIPOS RUTA
# ============================================================================

class TiposRutaBase(BaseModel):
    nombre: str = Field(max_length=100)
    descripcion: Optional[str] = None
    porcentaje_promedio_con_carga: Optional[Decimal] = Field(None, ge=0, le=100)
    activo: bool = True

class TiposRutaCreate(TiposRutaBase):
    creado_por: Optional[UUID] = None

class TiposRutaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = None
    porcentaje_promedio_con_carga: Optional[Decimal] = Field(None, ge=0, le=100)
    activo: Optional[bool] = None
    actualizado_por: Optional[UUID] = None

class TiposRutaRead(TiposRutaBase):
    id: UUID
    creado_en: datetime
    creado_por: Optional[UUID] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = None

    class Config:
        from_attributes = True
