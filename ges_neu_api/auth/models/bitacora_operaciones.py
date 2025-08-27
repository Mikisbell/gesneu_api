from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING, List, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import Column, Text, DateTime, String, ForeignKey, text, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ENUM as PG_ENUM, JSONB
from sqlmodel import SQLModel, Field, Relationship

# Enumeraciones que coinciden con los tipos ENUM de PostgreSQL
class TipoOperacionEnum(str, Enum):
    BALANCEO = "balanceo"
    ROTACION = "rotacion"
    ALINEACION = "alineacion"
    MANTENIMIENTO = "mantenimiento"
    REVISION = "revision"
    REENCAUCHE = "reencauche"
    REPARACION = "reparacion"
    REVISION_PRESION = "revision_presion"
    OTRO = "otro"

class EstadoOperacionEnum(str, Enum):
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"
    RECHAZADA = "rechazada"

class BitacoraOperacionesBase(SQLModel):
    tipo_operacion: TipoOperacionEnum = Field(
        sa_column=Column(String(50), nullable=False),
        description="Tipo de operación realizada"
    )
    
    descripcion: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Descripción detallada de la operación"
    )
    
    fecha_operacion: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()")),
        description="Fecha y hora en que se realizó la operación"
    )
    
    estado: EstadoOperacionEnum = Field(
        default=EstadoOperacionEnum.PENDIENTE,
        sa_column=Column(String(20), nullable=False, server_default=text("'pendiente'"))
    )
    
    metadata_adicional: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True),
        description="Metadatos adicionales en formato JSON"
    )

class BitacoraOperaciones(BitacoraOperacionesBase, table=True):
    __tablename__ = "bitacora_operaciones"
    __table_args__ = (
        Index('idx_bitacora_operaciones_estado', 'estado'),
        Index('idx_bitacora_operaciones_fecha', 'fecha_operacion'),
        {'schema': 'public', 'comment': 'Registro de operaciones realizadas en el sistema'}
    )

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único de la operación"
    )
    
    # Relación con Usuario
    usuario_id: UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        description="ID del usuario que realizó la operación"
    )
    
    # Relaciones
    usuario: "Usuario" = Relationship(back_populates="bitacora_operaciones")

# Configuración de modelos para relaciones circulares
if not TYPE_CHECKING:
    from .usuario import Usuario
    BitacoraOperaciones.model_rebuild()
