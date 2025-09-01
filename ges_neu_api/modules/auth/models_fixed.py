from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Text, DateTime, Boolean, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

class Usuario(SQLModel, table=True):
    """Modelo para tabla usuarios - Alineado exactamente con esquema real"""
    __tablename__ = "usuarios"
    __table_args__ = {'extend_existing': True}

    # Campos exactos del esquema PostgreSQL
    id: UUID = Field(default_factory=uuid4, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')))
    username: str = Field(sa_column=Column(String(50), nullable=False, unique=True))
    email: Optional[str] = Field(default=None, sa_column=Column(String(100), unique=True))
    password_hash: Optional[str] = Field(default=None, sa_column=Column(Text))
    nombre_completo: Optional[str] = Field(default=None, sa_column=Column(String(200)))
    activo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False))
    ultimo_login: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    creado_en: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text('now()')))
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    actualizado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
