"""
Modelos del módulo de sistema - Rutas y parámetros del sistema
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, SmallInteger
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy import Enum as SQLAlchemyEnum, text

from ...core.base_models import BaseModel

if TYPE_CHECKING:
    from ..auth.models import Usuario

# Enums para rutas
class TipoRutaEnum(str, Enum):
    URBANA = "URBANA"
    CARRETERA = "CARRETERA"
    MIXTA = "MIXTA"
    ESPECIAL = "ESPECIAL"

class EstadoRutaEnum(str, Enum):
    ACTIVA = "ACTIVA"
    INACTIVA = "INACTIVA"
    EN_MANTENIMIENTO = "EN_MANTENIMIENTO"

# Enums para parámetros sistema
class TipoParametroEnum(str, Enum):
    CONFIGURACION = "CONFIGURACION"
    LIMITE = "LIMITE"
    UMBRAL = "UMBRAL"
    NOTIFICACION = "NOTIFICACION"

class TipoTareaEnum(str, Enum):
    MANTENIMIENTO = "MANTENIMIENTO"
    BACKUP = "BACKUP"
    LIMPIEZA = "LIMPIEZA"
    REPORTE = "REPORTE"
    NOTIFICACION = "NOTIFICACION"

class EstadoTareaEnum(str, Enum):
    PENDIENTE = "PENDIENTE"
    EJECUTANDO = "EJECUTANDO"
    COMPLETADA = "COMPLETADA"
    ERROR = "ERROR"
    CANCELADA = "CANCELADA"

# ============================================================================
# RUTAS
# ============================================================================

class TiposRuta(BaseModel, table=True):
    """Tipos de rutas para clasificación."""
    __tablename__ = 'tipos_ruta'
    
    nombre: str = Field(sa_column=Column(String(50), nullable=False, unique=True))
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))
    factor_desgaste: Optional[float] = Field(default=1.0, sa_column=Column(Integer))
    
    # Relationships
    rutas: List["Rutas"] = Relationship(back_populates="tipo_ruta")

class Rutas(BaseModel, table=True):
    """Rutas de operación de vehículos."""
    __tablename__ = 'rutas'
    
    codigo: str = Field(sa_column=Column(String(20), nullable=False, unique=True))
    nombre: str = Field(sa_column=Column(String(100), nullable=False))
    tipo_ruta_id: UUID = Field(foreign_key="tipos_ruta.id", nullable=False)
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))
    distancia_km: Optional[float] = Field(default=None, sa_column=Column(Integer))
    tiempo_estimado_minutos: Optional[int] = Field(default=None, sa_column=Column(Integer))
    punto_origen: Optional[str] = Field(default=None, sa_column=Column(String(200)))
    punto_destino: Optional[str] = Field(default=None, sa_column=Column(String(200)))
    estado: EstadoRutaEnum = Field(default=EstadoRutaEnum.ACTIVA, sa_column=Column(SQLAlchemyEnum(EstadoRutaEnum), nullable=False))
    observaciones: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # Relationships
    tipo_ruta: "TiposRuta" = Relationship(back_populates="rutas")

# ============================================================================
# PARÁMETROS DEL SISTEMA
# ============================================================================

class ParametrosSistema(BaseModel, table=True):
    """Parámetros de configuración del sistema."""
    __tablename__ = 'parametros_sistema'
    
    clave: str = Field(sa_column=Column(String(100), nullable=False, unique=True))
    valor: str = Field(sa_column=Column(Text, nullable=False))
    tipo_parametro: TipoParametroEnum = Field(sa_column=Column(SQLAlchemyEnum(TipoParametroEnum), nullable=False))
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))
    es_editable: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text('true')))
    valor_por_defecto: Optional[str] = Field(default=None, sa_column=Column(Text))
    validacion_regex: Optional[str] = Field(default=None, sa_column=Column(String(500)))
    grupo_parametro: Optional[str] = Field(default=None, sa_column=Column(String(50)))

class TareasProgramadas(BaseModel, table=True):
    """Tareas programadas del sistema."""
    __tablename__ = 'tareas_programadas'
    
    nombre: str = Field(sa_column=Column(String(100), nullable=False, unique=True))
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))
    tipo_tarea: TipoTareaEnum = Field(sa_column=Column(SQLAlchemyEnum(TipoTareaEnum), nullable=False))
    expresion_cron: str = Field(sa_column=Column(String(100), nullable=False))
    comando_ejecutar: str = Field(sa_column=Column(Text, nullable=False))
    estado: EstadoTareaEnum = Field(default=EstadoTareaEnum.PENDIENTE, sa_column=Column(SQLAlchemyEnum(EstadoTareaEnum), nullable=False))
    ultima_ejecucion: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    proxima_ejecucion: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    intentos_fallidos: int = Field(default=0, sa_column=Column(Integer, nullable=False, server_default=text('0')))
    max_intentos: int = Field(default=3, sa_column=Column(Integer, nullable=False, server_default=text('3')))
    timeout_segundos: Optional[int] = Field(default=None, sa_column=Column(Integer))
    resultado_ultima_ejecucion: Optional[str] = Field(default=None, sa_column=Column(Text))
    log_ejecucion: Optional[dict] = Field(default=None, sa_column=Column(JSONB))

# Rebuild models for forward references
TiposRuta.model_rebuild()
Rutas.model_rebuild()
ParametrosSistema.model_rebuild()
TareasProgramadas.model_rebuild()
