from sqlalchemy import Column, String, Index, func, text, ForeignKey, Integer, Numeric, Boolean, Text, UniqueConstraint
from ges_neu_api.core.base_models import BaseModel
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import Field
from uuid import uuid4, UUID
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Fabricante(BaseModel, table=True):
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
    activo: Optional[bool] = None
    creado_en: Optional[datetime] = None
    creado_por: Optional[UUID] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = None
    
    __table_args__ = (
        Index(
            "idx_fabricantes_nombre_unique",
            func.f_immutable_lower_unaccent(text("nombre")),
            unique=True,
            postgresql_where=text("activo = true"),
        ),
    )

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

class ModeloNeumatico(BaseModel, table=True):
    __tablename__ = 'modelos_neumatico'
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único del modelo de neumático"
    )
    nombre_modelo: str = Field(sa_column=Column(String(100), nullable=False), description="Nombre del modelo de neumático")
    medida: str = Field(sa_column=Column(String(20), nullable=False), description="Medida del neumático (ej. 205/55R16)")
    indice_carga: Optional[str] = Field(None, sa_column=Column(String(5)), description="Índice de carga del neumático")
    indice_velocidad: Optional[str] = Field(None, sa_column=Column(String(2)), description="Índice de velocidad del neumático")
    profundidad_original_mm: Decimal = Field(sa_column=Column(Numeric(5, 2), nullable=False), description="Profundidad original de la banda de rodadura en mm")
    presion_recomendada_psi: Optional[Decimal] = Field(None, sa_column=Column(Numeric(5, 2)), description="Presión de aire recomendada en PSI")
    permite_reencauche: bool = Field(False, sa_column=Column(Boolean, nullable=False, server_default=text("false")), description="Indica si el modelo permite reencauche")
    reencauches_maximos: int = Field(0, sa_column=Column(Integer, nullable=False, server_default=text("0")), description="Número máximo de reencauches permitidos")
    patron_dibujo: Optional[str] = Field(None, sa_column=Column(String(50)), description="Patrón de dibujo de la banda de rodadura")
    tipo_servicio: Optional[str] = Field(None, sa_column=Column(String(50)), description="Tipo de servicio (ej. Carretera, Off-Road)")
    fabricante_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("fabricantes_neumatico.id"), nullable=False), description="ID del fabricante del neumático")

    # Inherited fields from BaseModel
    activo: Optional[bool] = None
    creado_en: Optional[datetime] = None
    creado_por: Optional[UUID] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = None

    # Additional fields from schema
    posicion_uso_recomendada: Optional[str] = Field(None, sa_column=Column(String(50)), description="Posición de uso recomendada (ej. Dirección, Tracción)")
    diseno_predominante_para_eje: Optional[str] = Field(None, sa_column=Column(String(50)), description="Diseño predominante para tipo de eje")
    vida_util_teorica_km: Optional[int] = Field(None, sa_column=Column(Integer), description="Vida útil teórica en kilómetros")
    profundidad_minima_retiro_mm: Decimal = Field(Decimal('1.60'), sa_column=Column(Numeric(5, 2), nullable=False, server_default=text("1.60")), description="Profundidad mínima de la banda de rodadura para retiro en mm")
    tasa_desgaste_esperada_mm_km: Optional[Decimal] = Field(
        None, sa_column=Column(Numeric(10, 8)),
        description="Tasa de desgaste esperada en mm por kilómetro"
    )
    frecuencia_inspeccion_km: int = Field(5000, sa_column=Column(Integer, nullable=False, server_default=text("5000")), description="Frecuencia de inspección recomendada en kilómetros")
    max_vidas_utiles: int = Field(5, sa_column=Column(Integer, nullable=False, server_default=text("5")), description="Número máximo de vidas útiles (reencauches + vida original)")
    porcentaje_desgaste_por_vida: Decimal = Field(
        Decimal('10.00'), sa_column=Column(Numeric(5, 2), nullable=False, server_default=text("10.00")),
        description="Porcentaje de desgaste por vida útil"
    )

    __table_args__ = (
        Index(
            "idx_modelos_neumatico_nombre_medida_unique",
            func.f_immutable_lower_unaccent(text("nombre_modelo")),
            func.f_immutable_lower_unaccent(text("medida")),
            unique=True,
            postgresql_where=text("activo = true"),
        ),
    )

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

class ParametroInventario(BaseModel, table=True):
    __tablename__ = 'parametros_inventario'
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único del parámetro de inventario"
    )
    parametro_tipo: str = Field(sa_column=Column(String(50), nullable=False), description="Tipo de parámetro de inventario") # Using String for now, will replace with Enum later
    modelo_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("modelos_neumatico.id", ondelete="CASCADE"), nullable=False), description="ID del modelo de neumático asociado")
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