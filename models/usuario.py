# models/usuario.py
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, text, TIMESTAMP
from schemas.usuario import UsuarioBase # Importar Base desde schemas
# --- Helpers ---
from models.common import TimestampTZ, utcnow_aware

class Usuario(UsuarioBase, table=True):
    __tablename__ = "usuarios"; __table_args__ = {'extend_existing': True}
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    password_hash: Optional[str] = None
    creado_en: datetime = Field(default_factory=utcnow_aware, sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()")))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TimestampTZ, nullable=True))

