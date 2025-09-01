from datetime import datetime
from typing import Optional, Dict
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Text, DateTime, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB

class Alertas(SQLModel, table=True):
    """Modelo para tabla alertas - Alineado exactamente con esquema real"""
    __tablename__ = "alertas"
    __table_args__ = {'extend_existing': True}

    # Campos exactos del esquema PostgreSQL
    id: UUID = Field(default_factory=uuid4, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')))
    tipo_alerta: str = Field(sa_column=Column(String(50), nullable=False))
    mensaje: str = Field(sa_column=Column(Text, nullable=False))
    nivel_severidad: str = Field(default='INFO', sa_column=Column(String(20), nullable=False))
    estado_alerta: str = Field(default='NUEVA', sa_column=Column(String(20), nullable=False))
    timestamp_generacion: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text('now()')))
    timestamp_gestion: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    usuario_gestion_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
    neumatico_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
    vehiculo_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
    modelo_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
    almacen_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
    parametro_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
    datos_contexto: Optional[Dict] = Field(default=None, sa_column=Column(JSONB))
