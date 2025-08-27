from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Text, text, Index, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import SQLModel, Field, Relationship

# Use TYPE_CHECKING for model imports to avoid circular imports
if TYPE_CHECKING:
    from .rol_permiso import RolPermiso
    from .rol import Rol

class Permiso(SQLModel, table=True):
    """Modelo para los permisos del sistema."""
    __tablename__ = "permisos"
    
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")),
        description="Identificador único del permiso"
    )
    
    nombre_recurso: str = Field(
        max_length=100,
        sa_column=Column(String(100), nullable=False, index=True),
        description="Nombre del recurso al que aplica el permiso"
    )
    
    accion: str = Field(
        max_length=100,
        sa_column=Column(String(100), nullable=False, index=True),
        description="Acción que se puede realizar sobre el recurso"
    )
    
    descripcion: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description="Descripción detallada del permiso"
    )
    
    creado_en: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=text("now()"), nullable=False),
        description="Fecha de creación del permiso"
    )
    
    # Relaciones
    roles_rel: List["RolPermiso"] = Relationship(back_populates="permiso")
    
    # Propiedad para acceder a los roles directamente
    @property
    def roles(self) -> List["Rol"]:
        return [rel.rol for rel in self.roles_rel] if hasattr(self, 'roles_rel') else []
    
    __table_args__ = (
        Index('idx_permisos_recurso_accion', 'nombre_recurso', 'accion', postgresql_using='btree'),
        {
            'comment': 'Permisos del sistema que pueden ser asignados a los roles',
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
    from .rol_permiso import RolPermiso
    from .rol import Rol
