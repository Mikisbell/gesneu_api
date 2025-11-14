"""
Modelos del módulo de eventos - Creados desde cero basados en ESQUEMA_COMPLETO_BD.md
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from decimal import Decimal

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, DateTime, Text, Integer, Numeric, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy import Enum as SQLAlchemyEnum, text, Index, CheckConstraint

# Enums exactos del esquema PostgreSQL
class TipoEventoNeumaticoEnum(str, Enum):
    COMPRA = "COMPRA"
    INSTALACION = "INSTALACION"
    DESMONTAJE = "DESMONTAJE"
    INSPECCION = "INSPECCION"
    ROTACION = "ROTACION"
    REPARACION_ENTRADA = "REPARACION_ENTRADA"
    REPARACION_SALIDA = "REPARACION_SALIDA"
    REENCAUCHE_ENTRADA = "REENCAUCHE_ENTRADA"
    REENCAUCHE_SALIDA = "REENCAUCHE_SALIDA"
    DESECHO = "DESECHO"
    AJUSTE_INVENTARIO = "AJUSTE_INVENTARIO"
    TRANSFERENCIA_UBICACION = "TRANSFERENCIA_UBICACION"

class EstadoNeumaticoEnumDestino(str, Enum):
    """Enum exacto según ESQUEMA_COMPLETO_BD.md - estadoneumaticoenum"""
    EN_STOCK = "EN_STOCK"
    INSTALADO = "INSTALADO"
    EN_REPARACION = "EN_REPARACION"
    EN_REENCAUCHE = "EN_REENCAUCHE"
    DESECHADO = "DESECHADO"
    BAJA = "BAJA"

class EventosNeumaticos(SQLModel, table=True):
    """Modelo para tabla eventos_neumaticos - Exacto al esquema PostgreSQL."""
    __tablename__ = 'eventos_neumaticos'
    
    # Campos obligatorios según esquema
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    )
    neumatico_id: UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("neumaticos.id"), nullable=False)
    )
    tipo_evento: TipoEventoNeumaticoEnum = Field(
        sa_column=Column(SQLAlchemyEnum(TipoEventoNeumaticoEnum), nullable=False)
    )
    timestamp_evento: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text('now()'))
    )
    usuario_id: UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    )
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    )
    
    # Campos opcionales según esquema
    vehiculo_id: Optional[UUID] = Field(
        default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("vehiculos.id"))
    )
    posicion_id: Optional[UUID] = Field(
        default=None, sa_column=Column(PG_UUID(as_uuid=True))
    )
    odometro_vehiculo_en_evento: Optional[int] = Field(
        default=None, sa_column=Column(Integer)
    )
    profundidad_remanente_mm: Optional[Decimal] = Field(
        default=None, sa_column=Column(Numeric(5, 2))
    )
    presion_psi: Optional[Decimal] = Field(
        default=None, sa_column=Column(Numeric(5, 2))
    )
    costo_evento: Optional[Decimal] = Field(
        default=None, sa_column=Column(Numeric(10, 2))
    )
    moneda_costo: Optional[str] = Field(
        default='PEN', sa_column=Column(String(3), server_default=text("'PEN'"))
    )
    proveedor_servicio_id: Optional[UUID] = Field(
        default=None, sa_column=Column(PG_UUID(as_uuid=True))
    )
    notas: Optional[str] = Field(
        default=None, sa_column=Column(Text)
    )
    destino_desmontaje: Optional[EstadoNeumaticoEnumDestino] = Field(
        default=None, sa_column=Column(SQLAlchemyEnum(EstadoNeumaticoEnumDestino))
    )
    motivo_desecho_id_evento: Optional[UUID] = Field(
        default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("motivos_desecho.id"))
    )
    profundidad_post_reencauche_mm: Optional[Decimal] = Field(
        default=None, sa_column=Column(Numeric(5, 2))
    )
    datos_evento: Optional[dict] = Field(
        default=None, sa_column=Column(JSONB)
    )
    relacion_evento_anterior: Optional[UUID] = Field(
        default=None, sa_column=Column(PG_UUID(as_uuid=True))
    )
    almacen_destino_id: Optional[UUID] = Field(
        default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("almacenes.id"))
    )
    tipo_ruta_id: Optional[UUID] = Field(
        default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("tipos_ruta.id"))
    )
    peso_carga_promedio_ton_evento: Optional[Decimal] = Field(
        default=None, sa_column=Column(Numeric(5, 2))
    )
    motivo_reparacion_texto: Optional[str] = Field(
        default=None, sa_column=Column(Text)
    )
    tipo_dano_detectado_texto: Optional[str] = Field(
        default=None, sa_column=Column(Text)
    )
    
    # Constraints e índices según esquema REAL
    __table_args__ = (
        # Check constraints según ESQUEMA_COMPLETO_BD.md
        CheckConstraint("id IS NOT NULL", name='2200_19601_1_not_null'),
        CheckConstraint("neumatico_id IS NOT NULL", name='2200_19601_2_not_null'),
        CheckConstraint("tipo_evento IS NOT NULL", name='2200_19601_3_not_null'),
        CheckConstraint("timestamp_evento IS NOT NULL", name='2200_19601_4_not_null'),
        CheckConstraint("usuario_id IS NOT NULL", name='2200_19601_5_not_null'),
        CheckConstraint("creado_en IS NOT NULL", name='2200_19601_20_not_null'),
        CheckConstraint("((tipo_evento <> 'DESMONTAJE'::tipo_evento_neumatico_enum) OR (destino_desmontaje IS NOT NULL))", name='chk_destino_desmontaje'),
        CheckConstraint("(((tipo_evento <> 'DESECHO'::tipo_evento_neumatico_enum) AND ((tipo_evento <> 'DESMONTAJE'::tipo_evento_neumatico_enum) OR (destino_desmontaje <> 'DESECHADO'::estado_neumatico_enum))) OR (motivo_desecho_id_evento IS NOT NULL))", name='chk_motivo_desecho'),
        CheckConstraint("((tipo_evento <> 'REENCAUCHE_SALIDA'::tipo_evento_neumatico_enum) OR (profundidad_post_reencauche_mm IS NOT NULL))", name='chk_profundidad_reencauche'),
        CheckConstraint("((costo_evento IS NULL) OR (costo_evento >= (0)::numeric))", name='eventos_neumaticos_costo_evento_check'),
        CheckConstraint("((odometro_vehiculo_en_evento IS NULL) OR (odometro_vehiculo_en_evento >= 0))", name='eventos_neumaticos_odometro_vehiculo_en_evento_check'),
        CheckConstraint("((presion_psi IS NULL) OR (presion_psi > (0)::numeric))", name='eventos_neumaticos_presion_psi_check'),
        CheckConstraint("((profundidad_post_reencauche_mm IS NULL) OR (profundidad_post_reencauche_mm > (0)::numeric))", name='eventos_neumaticos_profundidad_post_reencauche_mm_check'),
        CheckConstraint("((profundidad_remanente_mm IS NULL) OR (profundidad_remanente_mm >= (0)::numeric))", name='eventos_neumaticos_profundidad_remanente_mm_check'),
        # Índices según esquema real COMPLETO
        Index('idx_eventos_neumatico', 'neumatico_id'),
        Index('idx_eventos_neumatico_fecha', 'neumatico_id', 'timestamp_evento'),
        Index('idx_eventos_neumatico_tipo_fecha', 'neumatico_id', 'tipo_evento', 'timestamp_evento'),
        Index('idx_eventos_neumaticos_tipo_ruta_id', 'tipo_ruta_id'),
        Index('idx_eventos_timestamp', 'timestamp_evento'),
        Index('idx_eventos_tipo', 'tipo_evento'),
        Index('idx_eventos_usuario', 'usuario_id'),
    )
