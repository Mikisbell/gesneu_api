from sqlalchemy import Column, String, Index, func, text, ForeignKey, Integer, Numeric, Boolean, Text, UniqueConstraint, Date, SmallInteger, TIMESTAMP, Enum
from ges_neu_api.core.base_models import BaseModel
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import SQLModel, Field, Relationship
from uuid import uuid4, UUID
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, date
from decimal import Decimal
import enum

if TYPE_CHECKING:
    from ..neumaticos.models import Neumatico
    from ..inventario.models import InventarioNeumaticos, MovimientosInventario
    from ..eventos.models import EventosNeumaticos
    from ..garantias.models import GarantiasNeumaticos
    from ..alertas.models import Alertas

# Fabricantes movidos a módulo neumaticos

# ============================================================================
# ENUMS
# ============================================================================

class TipoProveedorEnum(str, enum.Enum):
    FABRICANTE = "FABRICANTE"
    DISTRIBUIDOR = "DISTRIBUIDOR"
    SERVICIO_REPARACION = "SERVICIO_REPARACION"
    SERVICIO_REENCAUCHE = "SERVICIO_REENCAUCHE"
    OTRO = "OTRO"

class TipoParametroInventarioEnum(str, enum.Enum):
    PROFUNDIDAD_MINIMA = "PROFUNDIDAD_MINIMA"
    STOCK_MINIMO = "STOCK_MINIMO"
    STOCK_MAXIMO = "STOCK_MAXIMO"
    VIDA_UTIL_KM = "VIDA_UTIL_KM"
    VIDA_UTIL_ANIOS = "VIDA_UTIL_ANIOS"
    TIEMPO_DE_ENTREGA = "TIEMPO_DE_ENTREGA"

# NOTA: FabricanteNeumatico se encuentra en el módulo neumaticos según ESQUEMA_COMPLETO_BD.md
# Los fabricantes de neumáticos no pertenecen al módulo de catálogos

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
        sa_column=Column(String(150), nullable=False),
        description="Nombre completo del proveedor"
    )
    tipo: Optional[TipoProveedorEnum] = Field(
        default=None,
        sa_column=Column(Enum(TipoProveedorEnum, name="tipoproveedorenum"), nullable=True),
        description="Tipo de proveedor"
    )
    ruc: Optional[str] = Field(
        default=None,
        sa_column=Column(String(11), nullable=True, unique=True),
        description="RUC del proveedor"
    )
    contacto_principal: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
        description="Contacto principal del proveedor"
    )
    telefono: Optional[str] = Field(
        default=None,
        sa_column=Column(String(50), nullable=True),
        description="Teléfono del proveedor"
    )
    email: Optional[str] = Field(
        default=None,
        sa_column=Column(String(100), nullable=True),
        description="Email del proveedor"
    )
    direccion: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
        description="Dirección del proveedor"
    )
    activo: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
        description="Estado activo del proveedor"
    )
    creado_en: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")),
        description="Fecha de creación"
    )
    creado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True),
        description="Usuario que creó el registro"
    )
    actualizado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=True),
        description="Fecha de última actualización"
    )
    actualizado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True),
        description="Usuario que actualizó el registro"
    )
    
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
# ALMACENES
# ============================================================================

class MotivoDesecho(BaseModel, table=True):
    __tablename__ = 'motivos_desecho'
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único del motivo de desecho"
    )
    codigo: str = Field(
        sa_column=Column(String(20), nullable=False, unique=True), 
        description="Código único del motivo de desecho"
    )
    descripcion: str = Field(
        sa_column=Column(Text, nullable=False), 
        description="Descripción detallada del motivo"
    )
    requiere_evidencia: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default=text("false")),
        description="Indica si requiere evidencia"
    )
    activo: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
        description="Estado activo del motivo"
    )
    creado_en: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")),
        description="Fecha de creación"
    )
    creado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True),
        description="Usuario que creó el registro"
    )
    actualizado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=True),
        description="Fecha de última actualización"
    )
    actualizado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True),
        description="Usuario que actualizó el registro"
    )

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
    codigo: str = Field(
        sa_column=Column(String(20), nullable=False, unique=True), 
        description="Código único del almacén"
    )
    nombre: str = Field(
        sa_column=Column(String(150), nullable=False), 
        description="Nombre descriptivo del almacén"
    )
    tipo: Optional[str] = Field(
        default=None,
        sa_column=Column(String(50), nullable=True),
        description="Tipo de almacén"
    )
    direccion: Optional[str] = Field(
        default=None, 
        sa_column=Column(Text, nullable=True), 
        description="Dirección física del almacén"
    )
    activo: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
        description="Estado activo del almacén"
    )
    creado_en: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")),
        description="Fecha de creación"
    )
    creado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True),
        description="Usuario que creó el registro"
    )
    actualizado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=True),
        description="Fecha de última actualización"
    )
    actualizado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True),
        description="Usuario que actualizó el registro"
    )

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
    parametro_tipo: TipoParametroInventarioEnum = Field(
        sa_column=Column(Enum(TipoParametroInventarioEnum, name="tipo_parametro_inventario_enum"), nullable=False),
        description="Tipo de parámetro de inventario"
    )
    modelo_id: UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("modelos_neumatico.id", ondelete="CASCADE"), nullable=False),
        description="ID del modelo de neumático asociado"
    )
    ubicacion_almacen_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("almacenes.id", ondelete="SET NULL"), nullable=True),
        description="ID de la ubicación del almacén asociado"
    )
    valor_numerico: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(10,2), nullable=True),
        description="Valor numérico del parámetro"
    )
    valor_texto: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
        description="Valor de texto del parámetro"
    )
    activo: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
        description="Estado activo del parámetro"
    )
    notas: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
        description="Notas adicionales sobre el parámetro"
    )
    creado_en: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")),
        description="Fecha de creación"
    )
    creado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True),
        description="Usuario que creó el registro"
    )
    actualizado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(TIMESTAMP(timezone=True), nullable=True),
        description="Fecha de última actualización"
    )
    actualizado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True),
        description="Usuario que actualizó el registro"
    )

    __table_args__ = (
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
            name="uq_parametro_inventario_gesneu"
        ),
    )

# Rebuild models for forward references
Proveedor.model_rebuild()
MotivoDesecho.model_rebuild()
Almacen.model_rebuild()
ParametroInventario.model_rebuild()