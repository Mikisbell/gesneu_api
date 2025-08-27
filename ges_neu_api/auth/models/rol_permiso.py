from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import SQLModel, Field, Relationship

# Use TYPE_CHECKING for model imports to avoid circular imports
if TYPE_CHECKING:
    from .rol import Rol
    from .permiso import Permiso
    from .usuario import Usuario

class RolPermiso(SQLModel, table=True):
    """Tabla de unión entre roles y permisos (relación muchos a muchos)."""
    __tablename__ = "roles_permisos"
    
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
    
    permiso_id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True),
            ForeignKey("permisos.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
            index=True
        ),
        description="ID del permiso"
    )
    
    asignado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=text("now()"), nullable=False),
        description="Fecha en que se asignó el permiso al rol"
    )
    
    asignado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
        description="ID del usuario que asignó el permiso al rol"
    )
    
    # Relaciones
    rol: "Rol" = Relationship(back_populates="permisos_rel")
    permiso: "Permiso" = Relationship(back_populates="roles_rel")
    asignado_por_usuario: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[RolPermiso.asignado_por]"},
        back_populates="auditorias_roles_permisos"
    )
    
    __table_args__ = (
        Index('idx_roles_permisos_permiso_id', 'permiso_id', postgresql_using='btree'),
        {
            'comment': 'Relación muchos a muchos entre roles y permisos',
            'schema': 'public'
        }
    )
    
    # Configuración del modelo
    model_config = {
        'arbitrary_types_allowed': True,
        'json_encoders': {
            UUID: lambda v: str(v) if v else None,
            datetime: lambda v: v.isoformat() if v else None
        }
    }

# Importaciones condicionales al final para evitar dependencias circulares
if not TYPE_CHECKING:
    from .rol import Rol
    from .permiso import Permiso
    from .usuario import Usuario
