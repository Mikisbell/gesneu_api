# models/usuario.py
import uuid
from datetime import datetime
from typing import Optional
# --- Importar Text y los otros tipos necesarios ---
from sqlalchemy import Column, String, Boolean, text, ForeignKey, Text
# -------------------------------------------------
from sqlmodel import Field, SQLModel
from pydantic import EmailStr
# Modificado: Importa UsuarioBase desde schemas, asumiendo que está ahí
# (Si UsuarioBase está en models, ajusta el import)
# from models.usuario import UsuarioBase <-- Original (posiblemente incorrecto)
from schemas.usuario import UsuarioBase # <-- Asumiendo que UsuarioBase está en schemas
from models.common import TimestampTZ, utcnow_aware

class Usuario(UsuarioBase, table=True):
    __tablename__ = "usuarios"
    # __table_args__ = {'extend_existing': True} # Puedes quitar extend_existing si no es necesario

    # Este campo está bien, usa default_factory
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # --- CAMPO USERNAME ---
    # TU CÓDIGO ACTUAL: Ya está bien. Define unique e index dentro de Column.
    username: str = Field(
        max_length=50,
        sa_column=Column(String(50), unique=True, index=True, nullable=False)
    )

    # --- CAMPO EMAIL ---
    # TU CÓDIGO ACTUAL: Ya está bien. Define unique e index dentro de Column.
    email: Optional[EmailStr] = Field(
        default=None,
        max_length=100,
        sa_column=Column(String(100), unique=True, index=True)
    )

    # Estos campos no tenían unique/index, están bien como están
    nombre_completo: Optional[str] = Field(default=None, max_length=200, sa_column=Column(String(200)))
    rol: str = Field(default="OPERADOR", max_length=50, sa_column=Column(String(50), default="OPERADOR", nullable=False))
    activo: bool = Field(default=True, sa_column=Column(Boolean, default=True, nullable=False))

    # Este campo está bien, usa Text correctamente
    password_hash: Optional[str] = Field(default=None, sa_column=Column(Text))

    # Timestamps y FKs están bien
    creado_en: datetime = Field(default_factory=utcnow_aware, sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()")))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TimestampTZ, nullable=True))
    creado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")