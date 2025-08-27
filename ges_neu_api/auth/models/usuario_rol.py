from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Column, DateTime, text, ForeignKey, Index, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import SQLModel, Field, Relationship

# Use TYPE_CHECKING for model imports to avoid circular imports
if TYPE_CHECKING:
    from .usuario import Usuario
    from .rol import Rol

class UsuarioRol(SQLModel, table=True):
    """Tabla de unión entre usuarios y roles (relación muchos a muchos)."""
    __tablename__ = "usuarios_roles"
    
    usuario_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("usuarios.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
            index=True
        ),
        description="ID del usuario"
    )
    
    rol_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("roles.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
            index=True
        ),
        description="ID del rol"
    )
    
    # Campos de auditoría
    asignado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=text("now()"), nullable=False),
        description="Fecha y hora en que se asignó el rol al usuario"
    )
    
    asignado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
        description="ID del usuario que realizó la asignación"
    )
    
    # Relaciones
    usuario: "Usuario" = Relationship(back_populates="roles_rel")
    rol: "Rol" = Relationship(back_populates="usuarios_rel")
    asignado_por_usuario: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[UsuarioRol.asignado_por]"},
        back_populates="asignaciones_roles"
    )
    
    __table_args__ = (
        PrimaryKeyConstraint('usuario_id', 'rol_id', name='pk_usuarios_roles'),
        Index('idx_usuarios_roles_rol_id', 'rol_id', postgresql_using='btree'),
        {
            'comment': 'Relación muchos a muchos entre usuarios y roles',
            'schema': 'public'
        }
    )
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            UUID: lambda v: str(v) if v else None,
            datetime: lambda v: v.isoformat() if v else None
        }

# Importaciones condicionales al final para evitar dependencias circulares
if not TYPE_CHECKING:
    from .usuario import Usuario
    from .rol import Rol
