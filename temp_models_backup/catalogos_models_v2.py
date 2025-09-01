"""
Modelos limpios del módulo de catálogos - Sin conflictos de metadatos
"""
from sqlalchemy import Column, String, Index, func, text, ForeignKey, Integer, Numeric, Boolean, Text
from ges_neu_api.core.base_models import BaseModel
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import SQLModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime
from decimal import Decimal

# ============================================================================
# PROVEEDORES
# ============================================================================

class ProveedorCatalogo(BaseModel, table=True):
    __tablename__ = 'proveedores'
    
    nombre: str = Field(
        sa_column=Column(String(150), nullable=False, unique=True),
        description="Nombre completo del proveedor"
    )
    
    __table_args__ = (
        Index(
            'idx_proveedores_nombre_unique',
            func.f_immutable_lower_unaccent(text('nombre')),
            unique=True,
            postgresql_where=text("activo = true")
        ),
    )

# ============================================================================
# DISEÑOS
# ============================================================================

class DisenioCatalogo(BaseModel, table=True):
    __tablename__ = 'disenios'
    
    nombre: str = Field(
        sa_column=Column(String(100), nullable=False, unique=True),
        description="Nombre del diseño"
    )

    __table_args__ = (
        Index(
            "idx_disenios_nombre_unique",
            func.f_immutable_lower_unaccent(text("nombre")),
            unique=True,
            postgresql_where=text("activo = true"),
        ),
    )

# ============================================================================
# MOTIVOS DE DESECHO
# ============================================================================

class MotivoDesechoCatalogo(BaseModel, table=True):
    __tablename__ = 'motivos_desecho'
    
    codigo: str = Field(
        sa_column=Column(String(20), nullable=False, unique=True), 
        description="Código único del motivo de desecho"
    )
    descripcion: str = Field(
        sa_column=Column(String(255), nullable=False), 
        description="Descripción detallada del motivo"
    )
    requiere_evidencia: bool = Field(
        sa_column=Column(Boolean, nullable=False, server_default=text("false")), 
        description="Indica si requiere evidencia"
    )

    __table_args__ = (
        Index(
            "idx_motivos_desecho_codigo_unique",
            func.f_immutable_lower_unaccent(text("codigo")),
            unique=True,
            postgresql_where=text("activo = true"),
        ),
    )

# ============================================================================
# ALMACENES
# ============================================================================

class AlmacenCatalogo(BaseModel, table=True):
    __tablename__ = 'almacenes'
    
    codigo: str = Field(
        sa_column=Column(String(20), nullable=False, unique=True), 
        description="Código único del almacén"
    )
    nombre: str = Field(
        sa_column=Column(String(100), nullable=False), 
        description="Nombre descriptivo del almacén"
    )
    direccion: Optional[str] = Field(
        None, sa_column=Column(String), 
        description="Dirección física del almacén"
    )
    responsable: Optional[str] = Field(
        None, sa_column=Column(String(200)), 
        description="Persona a cargo del almacén"
    )
    telefono: Optional[str] = Field(
        None, sa_column=Column(String(20)), 
        description="Teléfono de contacto del almacén"
    )
    email: Optional[str] = Field(
        None, sa_column=Column(String(100)), 
        description="Correo electrónico de contacto"
    )
    es_principal: bool = Field(
        False, sa_column=Column(Boolean, nullable=False, server_default=text("false")), 
        description="Indica si es el almacén principal"
    )
    capacidad_maxima: Optional[int] = Field(
        None, sa_column=Column(Integer), 
        description="Capacidad máxima del almacén"
    )

    __table_args__ = (
        Index(
            "idx_almacenes_codigo_unique",
            func.f_immutable_lower_unaccent(text("codigo")),
            unique=True,
            postgresql_where=text("activo = true"),
        ),
    )

# ============================================================================
# RUTAS Y TIPOS DE RUTA
# ============================================================================

class TipoRutaCatalogo(BaseModel, table=True):
    __tablename__ = "tipos_ruta"
    
    nombre_ruta: str = Field(max_length=150)
    descripcion: Optional[str] = Field(default=None)
    distancia_total_km_ciclo: Optional[Decimal] = Field(default=None, max_digits=8, decimal_places=2)
    distancia_trocha_km_ciclo: Optional[Decimal] = Field(default=None, max_digits=8, decimal_places=2)
    distancia_asfalto_km_ciclo: Optional[Decimal] = Field(default=None, max_digits=8, decimal_places=2)
    distancia_otro_terreno_km_ciclo: Optional[Decimal] = Field(default=None, max_digits=8, decimal_places=2)
    porcentaje_promedio_con_carga: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)

class RutaCatalogo(BaseModel, table=True):
    __tablename__ = "rutas"
    
    codigo: str = Field(max_length=20)
    nombre: str = Field(max_length=100)
    descripcion: Optional[str] = Field(default=None)
    distancia_total_km: Decimal = Field(max_digits=10, decimal_places=2)
    ida_vuelta: bool = Field()

# ============================================================================
# PARÁMETROS DE SISTEMA Y TAREAS
# ============================================================================

class ParametroSistemaCatalogo(SQLModel, table=True):
    __tablename__ = "parametros_sistema"
    
    id: int = Field(primary_key=True)
    clave: str = Field(max_length=100)
    valor: str = Field()
    descripcion: Optional[str] = Field(default=None)
    creado_en: Optional[datetime] = Field(default=None)
    actualizado_en: Optional[datetime] = Field(default=None)
    creado_por: Optional[str] = Field(default=None, max_length=100)
    actualizado_por: Optional[str] = Field(default=None, max_length=100)

class TareaProgramadaCatalogo(SQLModel, table=True):
    __tablename__ = "tareas_programadas"
    
    id: int = Field(primary_key=True)
    nombre_tarea: str = Field(max_length=100)
    descripcion: Optional[str] = Field(default=None)
    frecuencia_dias: int = Field()
    ultima_ejecucion: Optional[datetime] = Field(default=None)
    proxima_ejecucion: Optional[datetime] = Field(default=None)
    activa: Optional[bool] = Field(default=None)
    script_sql: Optional[str] = Field(default=None)
    creado_en: Optional[datetime] = Field(default=None)
    creado_por: Optional[str] = Field(default=None, max_length=100)
    actualizado_en: Optional[datetime] = Field(default=None)
    actualizado_por: Optional[str] = Field(default=None, max_length=100)
