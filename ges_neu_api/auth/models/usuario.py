from datetime import datetime
from typing import List, Optional, TYPE_CHECKING, ForwardRef
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import SQLModel, Field, Relationship, text

# Use TYPE_CHECKING for model imports to avoid circular imports
if TYPE_CHECKING:
    from .usuario_rol import UsuarioRol
    from .rol import Rol
    from .bitacora_operaciones import BitacoraOperaciones

# No importar UsuarioRol aquí para evitar importación circular
# En su lugar, usaremos cadenas para las relaciones

class Usuario(SQLModel, table=True):
    """Modelo para los usuarios del sistema."""
    __tablename__ = "usuarios"
    
    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()")
        ),
        description="Identificador único del usuario"
    )
    
    username: str = Field(
        max_length=50,
        sa_column=Column(String(50), unique=True, nullable=False, index=True),
        description="Nombre de usuario único para autenticación"
    )
    
    nombre_completo: Optional[str] = Field(
        default=None,
        max_length=200,
        nullable=True,
        description="Nombre completo del usuario"
    )
    
    email: Optional[str] = Field(
        default=None,
        max_length=100,
        sa_column=Column(String(100), unique=True, nullable=True),
        description="Correo electrónico del usuario"
    )
    
    password_hash: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
        description="Hash de la contraseña del usuario"
    )
    
    activo: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
        description="Indica si el usuario está activo en el sistema"
    )
    
    ultimo_login: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
        description="Fecha y hora del último inicio de sesión exitoso"
    )
    
    # Campos de auditoría
    creado_en: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=text("now()"), nullable=False),
        description="Fecha de creación del usuario"
    )
    
    creado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
        description="ID del usuario que creó este registro"
    )
    
    actualizado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
        description="Fecha de última actualización del usuario"
    )
    
    actualizado_por: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
        description="ID del usuario que actualizó este registro por última vez"
    )
    
    # Relaciones
    roles_rel: List["UsuarioRol"] = Relationship(
        back_populates="usuario"
    )
    
    # Propiedad para acceder a los roles directamente
    @property
    def roles(self) -> List["Rol"]:
        return [rel.rol for rel in self.roles_rel] if hasattr(self, 'roles_rel') else []
    
    # Relación con las operaciones de bitácora
    bitacora_operaciones: List["BitacoraOperaciones"] = Relationship(
        back_populates="usuario",
        sa_relationship_kwargs={"foreign_keys": "BitacoraOperaciones.usuario_id"}
    )
    
    # Relación con las asignaciones de roles hechas por este usuario
    asignaciones_roles: List["UsuarioRol"] = Relationship(
        back_populates="asignado_por_usuario"
    )
    
    # Relación con el usuario creador
    creado_por_usuario: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={
            "remote_side": "[Usuario.id]",
            "foreign_keys": "[Usuario.creado_por]"
        }
    )
    
    # Relación con el usuario que actualizó
    actualizado_por_usuario: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={
            "remote_side": "[Usuario.id]",
            "foreign_keys": "[Usuario.actualizado_por]"
        }
    )

# Configuración de actualización de modelos al final del archivo
if not TYPE_CHECKING:
    from .rol import Rol
    from .bitacora_operaciones import BitacoraOperaciones
    from .usuario_rol import UsuarioRol
    
    # Actualizar referencias circulares
    Usuario.model_rebuild()
    
    # Actualizar campos con referencias circulares
    if hasattr(Usuario, 'model_fields'):
        Usuario.model_fields.update({
            'creado_por_usuario': 'Optional[Usuario]',
            'actualizado_por_usuario': 'Optional[Usuario]',
            'roles_rel': 'List[UsuarioRol]',
            'bitacora_operaciones': 'List[BitacoraOperaciones]',
            'asignaciones_roles': 'List[UsuarioRol]'
        })
