from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Column, DateTime, text, ForeignKey, Index, String, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ENUM as PG_ENUM
from sqlmodel import SQLModel, Field, Relationship

# Use TYPE_CHECKING for model imports to avoid circular imports
if TYPE_CHECKING:
    from .usuario import Usuario
    from .rol import Rol

class AccionAuditoria(str, Enum):
    """Enumeración de acciones de auditoría."""
    ASIGNACION = 'ASIGNACION'
    ELIMINACION = 'ELIMINACION'
    MODIFICACION = 'MODIFICACION'

class AuditoriaRolUsuario(SQLModel, table=True):
    """Modelo para auditar cambios en la asignación de roles a usuarios."""
    __tablename__ = "auditoria_roles_usuarios"
    
    # Identificador único del registro de auditoría
    id: UUID = Field(
        default_factory=UUID,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()")
        ),
        description="Identificador único del registro de auditoría"
    )
    
    # Referencia al usuario afectado
    usuario_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("usuarios.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        ),
        description="ID del usuario afectado"
    )
    
    # Referencia al rol afectado
    rol_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("roles.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        ),
        description="ID del rol afectado"
    )
    
    # Acción realizada (ASIGNACION, ELIMINACION, MODIFICACION)
    accion: AccionAuditoria = Field(
        sa_column=Column(
            PG_ENUM(
                AccionAuditoria,
                name="accion_auditoria_enum",
                create_type=True
            ),
            nullable=False
        ),
        description="Tipo de acción realizada"
    )
    
    # Detalles adicionales de la acción (opcional)
    detalles: Optional[str] = Field(
        default=None,
        sa_column=Column(String(500), nullable=True),
        description="Detalles adicionales sobre la acción realizada"
    )
    
    # Fecha y hora del evento
    fecha_evento: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=text("now()"), nullable=False),
        description="Fecha y hora en que ocurrió el evento"
    )
    
    # Usuario que realizó la acción
    realizado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
        description="ID del usuario que realizó la acción"
    )
    
    # Dirección IP desde donde se realizó la acción
    ip_origen: Optional[str] = Field(
        default=None,
        sa_column=Column(String(50), nullable=True),
        description="Dirección IP desde donde se realizó la acción"
    )
    
    # Relaciones
    usuario: "Usuario" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[AuditoriaRolUsuario.usuario_id]"},
        back_populates="auditorias_rol"
    )
    
    rol: "Rol" = Relationship(
        back_populates="auditorias"
    )
    
    usuario_que_realizo: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[AuditoriaRolUsuario.realizado_por]"},
        back_populates="auditorias_realizadas"
    )
    
    __table_args__ = (
        Index('idx_auditoria_roles_usuarios_usuario_id', 'usuario_id', postgresql_using='btree'),
        Index('idx_auditoria_roles_usuarios_rol_id', 'rol_id', postgresql_using='btree'),
        Index('idx_auditoria_roles_usuarios_fecha', 'fecha_evento', postgresql_using='btree'),
        {
            'comment': 'Registro de auditoría para cambios en la asignación de roles a usuarios',
            'schema': 'public'
        }
    )
    
    # Configuración del modelo
    model_config = {
        'arbitrary_types_allowed': True,
        'json_encoders': {
            UUID: lambda v: str(v) if v else None,
            datetime: lambda v: v.isoformat() if v else None,
            AccionAuditoria: lambda v: v.value if v else None
        }
    }

# Importaciones condicionales al final para evitar dependencias circulares
if not TYPE_CHECKING:
    from .usuario import Usuario
    from .rol import Rol
