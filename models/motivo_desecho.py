# models/motivo_desecho.py
import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, ForeignKey, text
from models.common import TimestampTZ, utcnow_aware


class MotivoDesecho(SQLModel, table=True):
    __tablename__ = "motivos_desecho"
    # Formato limpio
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    codigo: str = Field(unique=True, max_length=20)
    descripcion: str
    requiere_evidencia: bool = False
    activo: bool = True
    creado_en: datetime = Field(default_factory=utcnow_aware, sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()")))
    creado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TimestampTZ, nullable=True))
    actualizado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
