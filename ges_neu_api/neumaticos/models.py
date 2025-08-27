from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional, TYPE_CHECKING, Dict, Any
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, Date, text, ForeignKey, 
    Index, Integer, Numeric, Enum as SQLAlchemyEnum, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlmodel import SQLModel, Field, Relationship

# Import base model
from ges_neu_api.core.base_models import BaseModel

# Use TYPE_CHECKING for model imports to avoid circular imports
if TYPE_CHECKING:
    from ges_neu_api.catalogos.models import ModeloNeumatico, PosicionNeumatico, BitacoraOperaciones, Proveedor, MotivoDesecho, Almacen, TipoRuta
    from ges_neu_api.vehiculos.models import Vehiculo, PosicionNeumatico as VehiculoPosicionNeumatico
    from ges_neu_api.auth.models.usuario import Usuario

# Enums
class EstadoNeumaticoEnum(str, Enum):
    NUEVO = "NUEVO"
    EN_STOCK = "EN_STOCK"
    EN_USO = "EN_USO"
    ALMACENADO = "ALMACENADO"
    EN_REPARACION = "EN_REPARACION"
    PARA_DESECHAR = "PARA_DESECHAR"
    DESECHADO = "DESECHADO"

class TipoEventoNeumaticoEnum(str, Enum):
    INSTALACION = "INSTALACION"
    DESINSTALACION = "DESINSTALACION"
    ROTACION = "ROTACION"
    INSPECCION = "INSPECCION"
    REPARACION = "REPARACION"
    REENCAUCHE = "REENCAUCHE"
    BAJA = "BAJA"
    ACTUALIZACION_ESTADO = "ACTUALIZACION_ESTADO"
    ACTUALIZACION_UBICACION = "ACTUALIZACION_UBICACION"
    ACTUALIZACION_DATOS = "ACTUALIZACION_DATOS"
    OTRO = "OTRO"

class Neumatico(BaseModel, table=True):
    """Modelo para los neumáticos del sistema."""
    __tablename__ = "neumaticos"
    __table_args__ = (
        # Restricciones CHECK
        CheckConstraint("costo_compra IS NULL OR costo_compra >= 0", name="neumaticos_costo_compra_check"),
        CheckConstraint("fecha_fabricacion IS NULL OR fecha_fabricacion <= fecha_compra", name="neumaticos_fechas_check"),
        CheckConstraint("kilometraje_acumulado >= 0", name="neumaticos_kilometraje_acumulado_check"),
        CheckConstraint("kilometraje_vida_actual >= 0", name="neumaticos_kilometraje_vida_actual_check"),
        CheckConstraint("profundidad_inicial_mm IS NULL OR profundidad_inicial_mm > 0", name="neumaticos_profundidad_inicial_mm_check"),
        CheckConstraint("profundidad_remanente_actual_mm IS NULL OR (profundidad_remanente_actual_mm >= 0 AND profundidad_remanente_actual_mm <= 50)", 
                      name="neumaticos_profundidad_remanente_check"),
        CheckConstraint("reencauches_realizados >= 0", name="neumaticos_reencauches_realizados_check"),
        CheckConstraint("tasa_desgaste_actual_mm_km IS NULL OR tasa_desgaste_actual_mm_km > 0", 
                      name="neumaticos_tasa_desgaste_actual_check"),
        CheckConstraint("vida_actual >= 1 AND vida_actual <= 11", name="neumaticos_vida_actual_check"),
        CheckConstraint("vida_util_restante_km IS NULL OR vida_util_restante_km >= 0", 
                      name="neumaticos_vida_util_restante_check"),
        # Restricción de ubicación mutuamente exclusiva
        CheckConstraint(
            "(ubicacion_almacen_id IS NOT NULL AND ubicacion_actual_vehiculo_id IS NULL AND "
            "ubicacion_actual_posicion_id IS NULL AND estado_actual != 'INSTALADO'::estado_neumatico_enum) OR "
            "(ubicacion_almacen_id IS NULL AND ubicacion_actual_vehiculo_id IS NOT NULL AND "
            "ubicacion_actual_posicion_id IS NOT NULL AND estado_actual = 'INSTALADO'::estado_neumatico_enum) OR "
            "(ubicacion_almacen_id IS NULL AND ubicacion_actual_vehiculo_id IS NULL AND "
            "ubicacion_actual_posicion_id IS NULL AND estado_actual NOT IN ('EN_STOCK', 'INSTALADO')::estado_neumatico_enum[])",
            name="check_ubicacion_estado"
        ),
        # Índices para consultas frecuentes
        Index("idx_neumaticos_estado_ubicacion", "estado_actual", "ubicacion_almacen_id", "ubicacion_actual_vehiculo_id"),
        Index("idx_neumaticos_fechas_compra_fabricacion", "fecha_compra", "fecha_fabricacion"),
        Index("idx_neumaticos_modelo_estado", "modelo_id", "estado_actual"),
        Index("idx_neumaticos_kilometraje", "kilometraje_acumulado"),
        Index("idx_neumaticos_profundidad", "profundidad_remanente_actual_mm"),
        
        # Índice funcional para búsqueda insensible a mayúsculas/minúsculas
        Index("idx_neumaticos_numero_serie_ci", text("lower(numero_serie)")),
        Index("idx_neumaticos_dot_ci", text("lower(dot)")),
        
        # Configuración de la tabla
        {
            "schema": "public",
            "comment": "Almacena información sobre neumáticos individuales, incluyendo su estado actual, ubicación y métricas de rendimiento",
            "extend_existing": True
        }
    )

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único del neumático"
    )
    
    # Relaciones con otras tablas
    modelo_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.modelos_neumatico.id", ondelete="RESTRICT"),
            nullable=False,
            index=True
        ),
        description="ID del modelo de neumático"
    )
    
    proveedor_compra_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.proveedores.id", ondelete="SET NULL"),
            index=True
        ),
        description="ID del proveedor de compra"
    )
    
    ubicacion_almacen_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.almacenes.id", ondelete="SET NULL"),
            index=True
        ),
        description="ID de la ubicación en almacén actual"
    )
    
    motivo_desecho_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.motivos_desecho.id", ondelete="SET NULL")
        ),
        description="ID del motivo de desecho (si aplica)"
    )
    
    # Datos básicos
    numero_serie: Optional[str] = Field(
        default=None,
        sa_column=Column(String(100), unique=True, index=True),
        description="Número de serie único del neumático"
    )
    
    dot: Optional[str] = Field(
        default=None,
        sa_column=Column(String(50)),  # Asumo que dot_code se maneja como string
        description="Código DOT del neumático"
    )
    
    # Fechas importantes
    fecha_compra: Optional[date] = Field(
        default=None,
        sa_column=Column(Date),
        description="Fecha de compra del neumático"
    )
    
    fecha_fabricacion: Optional[date] = Field(
        default=None,
        sa_column=Column(Date),
        description="Fecha de fabricación del neumático"
    )
    
    # Datos de compra
    costo_compra: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(10, 2)),
        description="Costo de compra del neumático"
    )
    
    moneda_compra: str = Field(
        default="PEN",
        sa_column=Column(String(3), server_default=text("'PEN'")),
        description="Moneda del costo de compra"
    )
    
    # Estado y ubicación actual
    es_reencauchado: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default=text("false")),
        description="Indica si el neumático es reencauchado"
    )
    
    vida_actual: int = Field(
        default=1,
        sa_column=Column(Integer, nullable=False, server_default=text("1")),
        description="Número de vida actual del neumático (1 = primera vida, 2 = primer reencauche, etc.)"
    )
    
    estado_actual: EstadoNeumaticoEnum = Field(
        default=EstadoNeumaticoEnum.EN_STOCK,
        sa_column=Column(
            SQLAlchemyEnum(EstadoNeumaticoEnum, name="estado_neumatico_enum"),
            nullable=False,
            server_default=text(f"'{EstadoNeumaticoEnum.EN_STOCK.value}'::estado_neumatico_enum")
        ),
        description="Estado actual del neumático"
    )
    
    # Ubicación actual
    ubicacion_actual_vehiculo_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.vehiculos.id", ondelete="SET NULL"),
            nullable=True
        ),
        description="ID del vehículo donde está instalado actualmente (si aplica)"
    )
    
    ubicacion_actual_posicion_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.posiciones_neumatico.id", ondelete="SET NULL"),
            nullable=True
        ),
        description="ID de la posición en el vehículo donde está instalado (si aplica)"
    )
    
    # Métricas de rendimiento
    profundidad_inicial_mm: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(5, 2)),
        description="Profundidad inicial de la banda de rodadura (en mm)"
    )
    
    profundidad_remanente_actual_mm: Decimal = Field(
        sa_column=Column(Numeric(5, 2), nullable=False),
        description="Profundidad actual de la banda de rodadura (en mm)"
    )
    
    kilometraje_acumulado: int = Field(
        default=0,
        sa_column=Column(Integer, nullable=False, server_default=text("0")),
        description="Kilometraje total acumulado por el neumático en todas sus vidas"
    )
    
    kilometraje_vida_actual: int = Field(
        default=0,
        sa_column=Column(Integer, server_default=text("0")),
        description="Kilometraje acumulado en la vida actual del neumático"
    )
    
    tasa_desgaste_actual_mm_km: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(10, 8)),
        description="Tasa de desgaste actual en mm/km"
    )
    
    vida_util_restante_km: Optional[int] = Field(
        default=None,
        description="Vida útil restante estimada en kilómetros"
    )
    
    # Reencauches
    reencauches_realizados: int = Field(
        default=0,
        sa_column=Column(Integer, nullable=False, server_default=text("0")),
        description="Número de reencauches realizados en este neumático"
    )
    
    fecha_ultimo_reencauche: Optional[date] = Field(
        default=None,
        description="Fecha del último reencauche realizado"
    )
    
    # Desecho
    fecha_desecho: Optional[date] = Field(
        default=None,
        description="Fecha en que el neumático fue dado de baja"
    )
    
    # Seguimiento
    fecha_ultimo_evento: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Fecha y hora del último evento registrado para este neumático"
    )
    
    fecha_ultima_medicion_profundidad: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Fecha de la última medición de profundidad"
    )
    
    fecha_inicio_vida_actual: Optional[date] = Field(
        default=None,
        sa_column=Column(Date),
        description="Fecha de inicio de la vida actual del neumático"
    )
    
    odometro_instalacion_vida_actual: Optional[int] = Field(
        default=None,
        description="Odómetro del vehículo al momento de instalar el neumático en su vida actual"
    )
    
    # Auditoría
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()")),
        description="Fecha y hora de creación del registro"
    )
    
    creado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.usuarios.id", ondelete="SET NULL"),
            nullable=True
        ),
        description="ID del usuario que creó el registro"
    )
    
    actualizado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Fecha y hora de la última actualización del registro"
    )
    
    actualizado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.usuarios.id", ondelete="SET NULL"),
            nullable=True
        ),
        description="ID del usuario que realizó la última actualización"
    )
    
    # Sensor
    sensor_id: Optional[str] = Field(
        default=None,
        sa_column=Column(String(100)),
        description="ID del sensor asociado al neumático (si tiene uno)"
    )
    
    # Inspecciones
    proxima_inspeccion_fecha: Optional[date] = Field(
        default=None,
        sa_column=Column(Date),
        description="Próxima fecha programada para inspección"
    )
    
    proxima_inspeccion_km: Optional[int] = Field(
        default=None,
        description="Próximo kilometraje programado para inspección"
    )
    
    profundidad_inicio_vida_actual_mm: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(5, 2)),
        description="Profundidad de la banda de rodadura al inicio de la vida actual"
    )
    
    # Relaciones
    modelo: "ModeloNeumatico" = Relationship(back_populates="neumaticos")
    proveedor_compra: Optional["Proveedor"] = Relationship(back_populates="neumaticos_comprados")
    ubicacion_almacen: Optional["Almacen"] = Relationship(back_populates="neumaticos_en_almacen")
    motivo_desecho: Optional["MotivoDesecho"] = Relationship(back_populates="neumaticos")
    eventos: List["EventoNeumatico"] = Relationship(back_populates="neumatico")
    garantias: List["GarantiasNeumaticos"] = Relationship(back_populates="neumatico")
    operaciones_detalladas: List["BitacoraOperacionNeumatico"] = Relationship(
        back_populates="neumatico",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "foreign_keys": "BitacoraOperacionNeumatico.neumatico_id"
        }
    )
    
    # Propiedad para acceder directamente a las operaciones
    @property
    def operaciones(self) -> List["BitacoraOperacion"]:
        return [op.operacion for op in self.operaciones_detalladas]
    
    activo: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true"), comment="Indica si el neumático está activo (soft delete)")
    )
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            UUID: lambda v: str(v) if v else None,
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v is not None else None
        }

class EventoNeumatico(SQLModel, table=True):
    """Eventos relacionados con los neumáticos."""
    __tablename__ = "eventos_neumaticos"
    __table_args__ = (
        {
            "schema": "public", 
            "comment": "Registro de eventos que afectan el ciclo de vida de los neumáticos"
        }
    )
    
    # Sobrescribir el campo activo para que coincida con la base de datos
    activo: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
        description="Indica si el registro está activo"
    )
    
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único del evento"
    )
    
    neumatico_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.neumaticos.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        ),
        description="ID del neumático relacionado"
    )
    
    tipo_evento: 'TipoEventoNeumaticoEnum' = Field(
        sa_column=Column(
            SQLAlchemyEnum(TipoEventoNeumaticoEnum, name="tipo_evento_neumatico_enum"),
            nullable=False
        ),
        description="Tipo de evento"
    )
    
    timestamp_evento: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()")),
        description="Fecha y hora en que ocurrió el evento"
    )
    
    usuario_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.usuarios.id", ondelete="RESTRICT"),
            nullable=False
        ),
        description="ID del usuario que registró el evento"
    )
    
    vehiculo_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.vehiculos.id", ondelete="SET NULL")
        ),
        description="ID del vehículo relacionado (si aplica)"
    )
    
    posicion_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.posiciones_neumatico.id", ondelete="SET NULL")
        ),
        description="ID de la posición del neumático (si aplica)"
    )
    
    odometro_vehiculo_en_evento: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, CheckConstraint("odometro_vehiculo_en_evento >= 0")),
        description="Odómetro del vehículo en el momento del evento"
    )
    
    profundidad_remanente_mm: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(5, 2), CheckConstraint("profundidad_remanente_mm >= 0")),
        description="Profundidad remanente de la banda de rodadura en mm"
    )
    
    presion_psi: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(5, 2), CheckConstraint("presion_psi > 0")),
        description="Presión del neumático en PSI"
    )
    
    costo_evento: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(10, 2), CheckConstraint("costo_evento >= 0")),
        description="Costo asociado al evento"
    )
    
    moneda_costo: str = Field(
        "PEN",
        sa_column=Column(String(3), server_default=text("'PEN'::character varying")),
        description="Código de moneda para el costo (ej. PEN, USD)"
    )
    
    proveedor_servicio_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.proveedores.id", ondelete="SET NULL")
        ),
        description="ID del proveedor de servicio (si aplica)"
    )
    
    notas: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description="Notas adicionales sobre el evento"
    )
    
    destino_desmontaje: Optional['EstadoNeumaticoEnum'] = Field(
        default=None,
        sa_column=Column(SQLAlchemyEnum(EstadoNeumaticoEnum, name="estado_neumatico_enum")),
        description="Destino del neumático después del desmontaje (si aplica)"
    )
    
    motivo_desecho_id_evento: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.motivos_desecho.id", ondelete="RESTRICT")
        ),
        description="ID del motivo de desecho (si aplica)"
    )
    
    profundidad_post_reencauche_mm: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(5, 2), CheckConstraint("profundidad_post_reencauche_mm > 0")),
        description="Profundidad después del reencauche (si aplica)"
    )
    
    datos_evento: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB),
        description="Datos adicionales del evento en formato JSON"
    )
    
    relacion_evento_anterior: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.eventos_neumaticos.id", ondelete="SET NULL")
        ),
        description="ID de un evento relacionado anterior (si aplica)"
    )
    
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()")),
        description="Fecha y hora de creación del registro"
    )
    
    almacen_destino_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.almacenes.id", ondelete="SET NULL")
        ),
        description="ID del almacén de destino (si aplica)"
    )
    
    tipo_ruta_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("public.tipos_ruta.id", ondelete="RESTRICT")
        ),
        description="Tipo de ruta predominante durante el periodo cubierto hasta este evento"
    )
    
    peso_carga_promedio_ton_evento: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(5, 2)),
        description="Peso promedio de carga estimado durante el uso hasta este evento"
    )
    
    motivo_reparacion_texto: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description="Descripción del motivo o síntoma que llevó a la reparación"
    )
    
    tipo_dano_detectado_texto: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description="Descripción del tipo de daño encontrado en la reparación"
    )
    
    # Relaciones
    neumatico: "Neumatico" = Relationship(back_populates="eventos")
    usuario: "Usuario" = Relationship()
    vehiculo: Optional["Vehiculo"] = Relationship()
    posicion: Optional["PosicionNeumatico"] = Relationship()
    proveedor_servicio: Optional["Proveedor"] = Relationship()
    motivo_desecho: Optional["MotivoDesecho"] = Relationship()
    almacen_destino: Optional["Almacen"] = Relationship()
    tipo_ruta: Optional["TipoRuta"] = Relationship()
    
    # Relación auto-referencial
    evento_anterior: Optional["EventoNeumatico"] = Relationship(
        sa_relationship_kwargs={
            "remote_side": "EventoNeumatico.id",
            "foreign_keys": "EventoNeumatico.relacion_evento_anterior"
        },
        back_populates="evento_siguiente"
    )
    
    evento_siguiente: Optional["EventoNeumatico"] = Relationship(
        back_populates="evento_anterior"
    )
    
    # Configuración del modelo
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None,
            UUID: lambda v: str(v) if v else None,
            Decimal: lambda v: float(v) if v is not None else None
        }
    )
    
# Import models with circular dependencies at the bottom
# This helps avoid circular imports while still providing type hints
if not TYPE_CHECKING:
    from ges_neu_api.catalogos.models import (
        ModeloNeumatico, PosicionNeumatico, BitacoraOperaciones, 
        Proveedor, MotivoDesecho, Almacen, TipoRuta
    )
    from ges_neu_api.vehiculos.models import Vehiculo
    from ges_neu_api.auth.models.usuario import Usuario
    
    # Rebuild models to handle forward references
    Neumatico.model_rebuild()
    EventoNeumatico.model_rebuild()
    
    # Update relationship types using model_fields
    if hasattr(Neumatico, 'model_fields'):
        Neumatico.model_fields.update({
            'modelo': "ModeloNeumatico",
            'proveedor_compra': "Optional[Proveedor]",
            'ubicacion_almacen': "Optional[Almacen]",
            'motivo_desecho': "Optional[MotivoDesecho]",
            'eventos': "List[EventoNeumatico]",
            'garantias': "List[GarantiasNeumaticos]",
            'operaciones_detalladas': "List[BitacoraOperacionNeumatico]"
        })
    
    if hasattr(EventoNeumatico, 'model_fields'):
        EventoNeumatico.model_fields.update({
            'neumatico': "Neumatico",
            'usuario': "Usuario",
            'vehiculo': "Optional[Vehiculo]",
            'posicion': "Optional[PosicionNeumatico]",
            'proveedor_servicio': "Optional[Proveedor]",
            'motivo_desecho': "Optional[MotivoDesecho]",
            'evento_anterior': "Optional['EventoNeumatico']",
            'evento_siguiente': "Optional['EventoNeumatico']",
            'almacen_destino': "Optional[Almacen]",
            'tipo_ruta': "Optional[TipoRuta]"
        })
