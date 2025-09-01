"""
Modelos limpios del módulo de catálogos - Sin duplicados
"""
from sqlalchemy import Column, String, Index, func, text, ForeignKey, Integer, Numeric, Boolean, Text, UniqueConstraint
from ges_neu_api.core.base_models import BaseModel
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import SQLModel, Field
from uuid import uuid4, UUID
from typing import Optional
from datetime import datetime, date
from decimal import Decimal

# ============================================================================
# FABRICANTES
# ============================================================================

class FabricanteNeumatico(BaseModel, table=True):
    __tablename__ = 'fabricantes_neumatico'
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único del fabricante"
    )
    nombre: str = Field(
        sa_column=Column(String(100), nullable=False, unique=True),
        description="Nombre completo del fabricante"
    )
    pais_origen: Optional[str] = Field(None, sa_column=Column(String(50)), description="País de origen")
    sitio_web: Optional[str] = Field(None, sa_column=Column(String(200)), description="Sitio web oficial")
    contacto_tecnico: Optional[str] = Field(None, sa_column=Column(String(200)), description="Contacto técnico")
    
    __table_args__ = (
        Index(
            "idx_fabricantes_nombre_unique",
            func.f_immutable_lower_unaccent(text("nombre")),
            unique=True,
            postgresql_where=text("activo = true"),
        ),
    )

# ============================================================================
# PROVEEDORES
# ============================================================================

class Proveedor(BaseModel, table=True):
    __tablename__ = 'proveedores'
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único del proveedor"
    )
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

class Disenio(BaseModel, table=True):
    __tablename__ = 'disenios'
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único del diseño"
    )
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
# MODELOS DE NEUMÁTICO
# ============================================================================

class ModeloNeumatico(BaseModel, table=True):
    __tablename__ = 'modelos_neumatico'
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único del modelo de neumático"
    )
    nombre_modelo: str = Field(sa_column=Column(String(100), nullable=False), description="Nombre del modelo de neumático")
    medida: str = Field(sa_column=Column(String(20), nullable=False), description="Medida del neumático")
    fabricante_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("fabricantes_neumatico.id"), nullable=False), description="ID del fabricante")

    __table_args__ = (
        Index(
            "idx_modelos_neumatico_nombre_medida_unique",
            func.f_immutable_lower_unaccent(text("nombre_modelo")),
            func.f_immutable_lower_unaccent(text("medida")),
            unique=True,
            postgresql_where=text("activo = true"),
        ),
    )

# ============================================================================
# MOTIVOS DE DESECHO
# ============================================================================

class MotivoDesecho(BaseModel, table=True):
    __tablename__ = 'motivos_desecho'
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único del motivo de desecho"
    )
    codigo: str = Field(sa_column=Column(String(20), nullable=False, unique=True), description="Código único del motivo de desecho")
    descripcion: str = Field(sa_column=Column(String(255), nullable=False), description="Descripción detallada del motivo")

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

class Almacen(BaseModel, table=True):
    __tablename__ = 'almacenes'
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único del almacén"
    )
    codigo: str = Field(sa_column=Column(String(20), nullable=False, unique=True), description="Código único del almacén")
    nombre: str = Field(sa_column=Column(String(100), nullable=False), description="Nombre descriptivo del almacén")

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

class TipoRuta(BaseModel, table=True):
    __tablename__ = "tipos_ruta"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    nombre_ruta: str = Field(max_length=150)
    descripcion: Optional[str] = Field(default=None)

class Ruta(BaseModel, table=True):
    __tablename__ = "rutas"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    codigo: str = Field(max_length=20)
    nombre: str = Field(max_length=100)
    descripcion: Optional[str] = Field(default=None)
    distancia_total_km: Decimal = Field(max_digits=10, decimal_places=2)
    ida_vuelta: bool = Field()
    activa: bool = Field(default=True)

# ============================================================================
# PARÁMETROS DE SISTEMA Y TAREAS
# ============================================================================

class ParametroSistema(SQLModel, table=True):
    __tablename__ = "parametros_sistema"
    
    id: int = Field(primary_key=True)
    clave: str = Field(max_length=100)
    valor: str = Field()
    descripcion: Optional[str] = Field(default=None)
    creado_en: Optional[datetime] = Field(default=None)
    actualizado_en: Optional[datetime] = Field(default=None)
    creado_por: Optional[str] = Field(default=None, max_length=100)
    actualizado_por: Optional[str] = Field(default=None, max_length=100)

class TareaProgramada(SQLModel, table=True):
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

# ============================================================================
# PARÁMETROS DE INVENTARIO
# ============================================================================

class ParametroInventario(BaseModel, table=True):
    __tablename__ = 'parametros_inventario'
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único del parámetro de inventario"
    )
    parametro_tipo: str = Field(sa_column=Column(String(50), nullable=False), description="Tipo de parámetro de inventario")
    modelo_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("modelos_neumatico.id", ondelete="CASCADE"), nullable=False), description="ID del modelo de neumático asociado")
    ubicacion_almacen_id: Optional[UUID] = Field(None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("almacenes.id", ondelete="SET NULL")), description="ID de la ubicación del almacén asociado")
    valor_numerico: Optional[Decimal] = Field(None, sa_column=Column(Numeric(10,2)), description="Valor numérico del parámetro")
    valor_texto: Optional[str] = Field(None, sa_column=Column(Text), description="Valor de texto del parámetro")
    notas: Optional[str] = Field(None, sa_column=Column(Text), description="Notas adicionales sobre el parámetro")

    __table_args__ = (
        Index(
            "idx_param_inv_tipo_modelo_ubicacion",
            "parametro_tipo",
            "modelo_id",
            "ubicacion_almacen_id",
            unique=True,
            postgresql_where=text("activo = true"),
        ),
    )
