from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Text, DateTime, Date, Numeric, Boolean, Integer, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

class Neumaticos(SQLModel, table=True):
    """Modelo para tabla neumaticos - Alineado exactamente con esquema real"""
    __tablename__ = "neumaticos"
    __table_args__ = {'extend_existing': True}

    # Campos exactos del esquema PostgreSQL
    id: UUID = Field(default_factory=uuid4, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')))
    numero_serie: str = Field(sa_column=Column(String(100), nullable=False, unique=True))
    modelo_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), nullable=False))
    proveedor_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
    almacen_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
    vehiculo_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
    posicion_neumatico_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
    estado_neumatico: str = Field(default='EN_STOCK', sa_column=Column(String(20), nullable=False))
    fecha_compra: Optional[date] = Field(default=None, sa_column=Column(Date))
    fecha_instalacion: Optional[date] = Field(default=None, sa_column=Column(Date))
    fecha_desmontaje: Optional[date] = Field(default=None, sa_column=Column(Date))
    kilometraje_instalacion: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    kilometraje_desmontaje: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    profundidad_inicial_mm: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5, 2)))
    profundidad_actual_mm: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5, 2)))
    presion_recomendada_psi: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5, 2)))
    presion_actual_psi: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5, 2)))
    numero_reencauches: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    numero_reparaciones: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    costo_compra: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    observaciones: Optional[str] = Field(default=None, sa_column=Column(Text))
    activo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False))
    creado_en: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text('now()')))
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    actualizado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True)))
