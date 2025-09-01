from sqlalchemy import Column, String, Index, func, text, ForeignKey, Integer, Numeric, Boolean, Text, UniqueConstraint, Date, SmallInteger, TIMESTAMP
from ges_neu_api.core.base_models import BaseModel
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import SQLModel, Field, Relationship
from uuid import uuid4, UUID
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, date
from decimal import Decimal

if TYPE_CHECKING:
    from ..neumaticos.models import Neumatico
    from ..inventario.models import InventarioNeumaticos, MovimientosInventario
    from ..eventos.models import EventosNeumaticos
    from ..garantias.models import GarantiasNeumaticos
    from ..alertas.models import Alertas

# Fabricantes movidos a módulo neumaticos

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
    activo: Optional[bool] = None
    creado_en: Optional[datetime] = None
    creado_por: Optional[UUID] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = None
    
    __table_args__ = (
        Index(
            'idx_proveedores_nombre_unique',
            func.f_immutable_lower_unaccent(text('nombre')),
            unique=True,
            postgresql_where=text("activo = true")
        ),
    )
    
    # Relationships - removed to avoid SQLAlchemy metadata conflicts
    # neumaticos: handled at service layer
    # garantias_neumaticos: handled at service layer

# ============================================================================
# PROVEEDORES
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
    activo: Optional[bool] = None
    creado_en: Optional[datetime] = None
    creado_por: Optional[UUID] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = None

    __table_args__ = (
        Index(
            "idx_disenios_nombre_unique",
            func.f_immutable_lower_unaccent(text("nombre")),
            unique=True,
            postgresql_where=text("activo = true"),
        ),
    )

# ============================================================================
# PROVEEDORES
# ============================================================================

# Modelos de neumático movidos a módulo neumaticos

# ============================================================================
# PROVEEDORES
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

    # Inherited fields from BaseModel
    activo: Optional[bool] = None
    creado_en: Optional[datetime] = None
    creado_por: Optional[UUID] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = None

    __table_args__ = (
        Index(
            "idx_motivos_desecho_codigo_unique",
            func.f_immutable_lower_unaccent(text("codigo")),
            unique=True,
            postgresql_where=text("activo = true"),
        ),
    )
    
    # Relationships - removed to avoid SQLAlchemy metadata conflicts
    # eventos_neumaticos: handled at service layer

# ============================================================================
# PROVEEDORES
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
    direccion: Optional[str] = Field(None, sa_column=Column(String), description="Dirección física del almacén")
    responsable: Optional[str] = Field(None, sa_column=Column(String(200)), description="Persona a cargo del almacén")
    telefono: Optional[str] = Field(None, sa_column=Column(String(20)), description="Teléfono de contacto del almacén")
    email: Optional[str] = Field(None, sa_column=Column(String(100)), description="Correo electrónico de contacto")
    es_principal: bool = Field(False, sa_column=Column(Boolean, nullable=False, server_default=text("false")), description="Indica si es el almacén principal")

    # Inherited fields from BaseModel
    activo: Optional[bool] = None
    creado_en: Optional[datetime] = None
    creado_por: Optional[UUID] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = None

    __table_args__ = (
        Index(
            "idx_almacenes_codigo_unique",
            func.f_immutable_lower_unaccent(text("codigo")),
            unique=True,
            postgresql_where=text("activo = true"),
        ),
    )
    
    # Relationships - removed to avoid SQLAlchemy metadata conflicts
    # inventario_neumaticos: handled at service layer

# ============================================================================
# PROVEEDORES
# ============================================================================

class ParametroInventario(BaseModel, table=True):
    __tablename__ = 'parametros_inventario'
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único del parámetro de inventario"
    )
    parametro_tipo: str = Field(sa_column=Column(String(50), nullable=False), description="Tipo de parámetro de inventario") # Using String for now, will replace with Enum later
    modelo_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("modelos.id", ondelete="CASCADE"), nullable=False), description="ID del modelo de neumático asociado")
    ubicacion_almacen_id: Optional[UUID] = Field(None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("almacenes.id", ondelete="SET NULL")), description="ID de la ubicación del almacén asociado")
    valor_numerico: Optional[Decimal] = Field(None, sa_column=Column(Numeric(10,2)), description="Valor numérico del parámetro")
    valor_texto: Optional[str] = Field(None, sa_column=Column(Text), description="Valor de texto del parámetro")
    notas: Optional[str] = Field(None, sa_column=Column(Text), description="Notas adicionales sobre el parámetro")

    # Inherited fields from BaseModel
    activo: Optional[bool] = None
    creado_en: Optional[datetime] = None
    creado_por: Optional[UUID] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = None

    __table_args__ = (
        Index(
            "idx_param_inv_tipo_modelo_ubicacion",
            "parametro_tipo",
            "modelo_id",
            "ubicacion_almacen_id",
            unique=True,
            postgresql_where=text("activo = true"),
        ),
        UniqueConstraint(
            "parametro_tipo",
            "modelo_id",
            "ubicacion_almacen_id",
            name="uq_parametro_inventario"
        ),
        UniqueConstraint(
            "parametro_tipo",
            "modelo_id",
            "ubicacion_almacen_id",
            name="uq_parametro_inventario_gesneu",
            postgresql_nulls_not_distinct=True
        ),
    )
    
    # Relationships - removed to avoid SQLAlchemy metadata conflicts
    # alertas: handled at service layer

# Rebuild models for forward references
Proveedor.model_rebuild()
MotivoDesecho.model_rebuild()
Almacen.model_rebuild()
ParametroInventario.model_rebuild()