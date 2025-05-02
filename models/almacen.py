# models/almacen.py
import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, ForeignKey, text

# Importar helpers comunes
from models.common import TimestampTZ, utcnow_aware

class Almacen(SQLModel, table=True):
    __tablename__ = "almacenes"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    codigo: str = Field(unique=True, index=True, max_length=20)
    nombre: str = Field(max_length=150)
    tipo: Optional[str] = Field(default=None, max_length=50)
    direccion: Optional[str] = Field(default=None)
    activo: bool = Field(default=True, index=True)

    # Campos de auditoría
    creado_en: datetime = Field(
        default_factory=utcnow_aware,
        sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()"))
    )
    creado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(TimestampTZ, nullable=True)
    )
    actualizado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")

    class Config:
        orm_mode = True