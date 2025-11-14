"""
Modelos del módulo de sistema - Rutas y parámetros del sistema
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, SmallInteger, Numeric
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

class PrioridadAuditoriaEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

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

class TiposRuta(SQLModel, table=True):
    """Tipos de rutas para clasificación - Alineado exactamente con ESQUEMA_COMPLETO_BD.md líneas 1970-1994"""
    __tablename__ = 'tipos_ruta'
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    nombre_ruta: str = Field(sa_column=Column(String(150), nullable=False, unique=True))
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))
    distancia_total_km_ciclo: Optional[float] = Field(default=None, sa_column=Column(Numeric(8, 2)))
    distancia_trocha_km_ciclo: Optional[float] = Field(default=0, sa_column=Column(Numeric(8, 2), server_default=text('0')))
    distancia_asfalto_km_ciclo: Optional[float] = Field(default=0, sa_column=Column(Numeric(8, 2), server_default=text('0')))
    distancia_otro_terreno_km_ciclo: Optional[float] = Field(default=0, sa_column=Column(Numeric(8, 2), server_default=text('0')))
    porcentaje_promedio_con_carga: Optional[float] = Field(default=None, sa_column=Column(Numeric(5, 2)))
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    )
    creado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    actualizado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")

class Rutas(SQLModel, table=True):
    """Rutas de operación de vehículos - Alineado exactamente con ESQUEMA_COMPLETO_BD.md líneas 1890-1914"""
    __tablename__ = 'rutas'
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    codigo: str = Field(sa_column=Column(String(20), nullable=False, unique=True))
    nombre: str = Field(sa_column=Column(String(100), nullable=False))
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))
    distancia_total_km: float = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    ida_vuelta: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text('true')))
    activa: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text('true')))
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    )
    creado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    actualizado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")

# ============================================================================
# PARÁMETROS DEL SISTEMA
# ============================================================================

class ParametrosSistema(SQLModel, table=True):
    """Parámetros de configuración del sistema - Alineado exactamente con ESQUEMA_COMPLETO_BD.md líneas 1585-1609"""
    __tablename__ = 'parametros_sistema'
    
    id: int = Field(sa_column=Column(Integer, primary_key=True))
    clave: str = Field(sa_column=Column(String(100), nullable=False, unique=True))
    valor: str = Field(sa_column=Column(Text, nullable=False))
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))
    creado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True, server_default=text("now()"))
    )
    actualizado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True, server_default=text("now()"))
    )
    creado_por: Optional[str] = Field(
        default="SISTEMA", 
        sa_column=Column(String(100), server_default=text("'SISTEMA'::character varying"))
    )
    actualizado_por: Optional[str] = Field(
        default="SISTEMA", 
        sa_column=Column(String(100), server_default=text("'SISTEMA'::character varying"))
    )

class TareasProgramadas(SQLModel, table=True):
    """Tareas programadas del sistema - Alineado exactamente con ESQUEMA_COMPLETO_BD.md líneas 1935-1959"""
    __tablename__ = 'tareas_programadas'
    
    id: int = Field(sa_column=Column(Integer, primary_key=True))
    nombre_tarea: str = Field(sa_column=Column(String(100), nullable=False))
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))
    frecuencia_dias: int = Field(default=1, sa_column=Column(Integer, nullable=False, server_default=text('1')))
    ultima_ejecucion: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    proxima_ejecucion: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    activa: Optional[bool] = Field(default=True, sa_column=Column(Boolean, server_default=text('true')))
    script_sql: Optional[str] = Field(default=None, sa_column=Column(Text))
    creado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True, server_default=text("now()"))
    )
    creado_por: Optional[str] = Field(
        default="SISTEMA", 
        sa_column=Column(String(100), server_default=text("'SISTEMA'::character varying"))
    )
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    actualizado_por: Optional[str] = Field(default=None, sa_column=Column(String(100)))

# ============================================================================
# ERRORES DE APLICACIÓN
# ============================================================================

class ErroresAplicacion(SQLModel, table=True):
    """Errores de aplicación - Alineado exactamente con ESQUEMA_COMPLETO_BD.md líneas 750-792"""
    __tablename__ = 'errores_aplicacion'
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    nombre_funcion: str = Field(sa_column=Column(Text, nullable=False))
    mensaje_error: str = Field(sa_column=Column(Text, nullable=False))
    detalles: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    creado_por: Optional[str] = Field(default="SISTEMA", sa_column=Column(Text, server_default=text("'SISTEMA'::text")))
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    )
    resuelto: Optional[bool] = Field(default=False, sa_column=Column(Boolean, server_default=text("false")))
    resuelto_por: Optional[str] = Field(default=None, sa_column=Column(Text))
    resuelto_en: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    comentario_resolucion: Optional[str] = Field(default=None, sa_column=Column(Text))

# ============================================================================
# CONFIGURACIÓN DE AUDITORÍA
# ============================================================================

class ConfiguracionAuditoria(SQLModel, table=True):
    """Configuración de auditoría - Alineado exactamente con ESQUEMA_COMPLETO_BD.md líneas 664-688"""
    __tablename__ = 'configuracion_auditoria'
    
    nombre_tabla: str = Field(sa_column=Column(String(63), nullable=False, primary_key=True))
    activo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text("true")))
    prioridad: Optional[PrioridadAuditoriaEnum] = Field(
        default=None, 
        sa_column=Column(SQLAlchemyEnum(PrioridadAuditoriaEnum), nullable=True)
    )
    campos_excluidos: Optional[dict] = Field(
        default_factory=dict, 
        sa_column=Column(JSONB, server_default=text("'{}'::jsonb"))
    )
    creado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True, server_default=text("now()"))
    )
    actualizado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True, server_default=text("now()"))
    )

    class Config:
        from_attributes = True

# Rebuild models for forward references
TiposRuta.model_rebuild()
Rutas.model_rebuild()
ParametrosSistema.model_rebuild()
TareasProgramadas.model_rebuild()
ErroresAplicacion.model_rebuild()
ConfiguracionAuditoria.model_rebuild()
