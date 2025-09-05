"""
Modelos SQLModel para el módulo de vehículos - Alineados exactamente con PostgreSQL
Basado en ESQUEMA_COMPLETO_BD.md - Tablas: vehiculos, tipos_vehiculo, configuraciones_eje, posiciones_neumatico
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, String, SmallInteger, Integer, Boolean, Date, DateTime, Text, Numeric, ForeignKey, CheckConstraint, UniqueConstraint, Index, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import text
from sqlmodel import SQLModel, Field
from sqlalchemy import Enum as SQLAlchemyEnum

from .enums import TipoEjeEnum, LadoVehiculoEnum

class TiposVehiculo(SQLModel, table=True):
    __tablename__ = 'tipos_vehiculo'

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    nombre: str = Field(max_length=100)
    descripcion: Optional[str] = Field(default=None)
    categoria_principal: Optional[str] = Field(default=None, max_length=50)
    subtipo: Optional[str] = Field(default=None, max_length=50)
    ejes_standard: int = Field(default=2)
    activo: bool = Field(default=True)
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    creado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(default=None)
    actualizado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")
    
    __table_args__ = (
        CheckConstraint('(ejes_standard >= 1) AND (ejes_standard <= 10)', name='tipos_vehiculo_ejes_standard_check'),
        {'extend_existing': True}
    )


class ConfiguracionesEje(SQLModel, table=True):
    __tablename__ = 'configuraciones_eje'

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tipo_vehiculo_id: UUID = Field(foreign_key="tipos_vehiculo.id")
    numero_eje: int
    nombre_eje: str = Field(max_length=50)
    tipo_eje: TipoEjeEnum
    numero_posiciones: int
    posiciones_duales: bool = Field(default=False)
    permite_reencauchados: bool = Field(default=True)
    neumaticos_por_posicion: int = Field(default=1)
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    creado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(default=None)
    actualizado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")

    # Relationships comentadas para evitar conflictos de metadata
    # tipo_vehiculo: "TiposVehiculo" = Relationship(back_populates="configuraciones_eje")
    # posiciones_neumatico: List["PosicionesNeumatico"] = Relationship(back_populates="configuracion_eje")


class PosicionesNeumatico(SQLModel, table=True):
    __tablename__ = 'posiciones_neumatico'

    id: UUID = Field(default_factory=uuid4, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text('public.gen_random_uuid()')))
    configuracion_eje_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("configuraciones_eje.id"), nullable=False))
    codigo_posicion: str = Field(sa_column=Column(String(10), nullable=False))
    lado: LadoVehiculoEnum = Field(sa_column=Column(SQLAlchemyEnum(LadoVehiculoEnum), nullable=False))
    posicion_relativa: int = Field(sa_column=Column(SmallInteger, nullable=False))
    es_interna: bool = Field(sa_column=Column(Boolean, nullable=False, server_default=text('false')))
    es_direccion: bool = Field(sa_column=Column(Boolean, nullable=False, server_default=text('false')))
    es_traccion: bool = Field(sa_column=Column(Boolean, nullable=False, server_default=text('false')))
    requiere_neumatico_especifico: bool = Field(sa_column=Column(Boolean, nullable=False, server_default=text('false')))
    creado_en: datetime = Field(sa_column=Column(TIMESTAMP, nullable=False, server_default=text('now()')))
    etiqueta_posicion: Optional[str] = Field(default=None, sa_column=Column(String(50)))
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id")))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP))
    actualizado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id")))

    # Relationships comentadas para evitar conflictos de metadata
    # configuracion_eje: "ConfiguracionesEje" = Relationship(back_populates="posiciones_neumatico")


class Vehiculos(SQLModel, table=True):
    __tablename__ = 'vehiculos'
    __table_args__ = (
    CheckConstraint('anio_fabricacion >= 1900 AND anio_fabricacion::numeric <= (EXTRACT(year FROM CURRENT_DATE) + 1::numeric)', name='vehiculos_anio_fabricacion_check'),
        CheckConstraint('fecha_baja IS NULL OR fecha_baja >= fecha_alta', name='vehiculos_fecha_baja_check'),
        CheckConstraint('odometro_actual IS NULL OR odometro_actual >= 0', name='vehiculos_odometro_actual_check'),
        Index('idx_vehiculos_activos', 'activo', postgresql_where=text('activo = true')),
        Index('idx_vehiculos_numero_economico', func.lower(text('numero_economico::text')), postgresql_where=text('activo = true')),
        Index('idx_vehiculos_placa', 'placa', postgresql_where=text('placa IS NOT NULL AND activo = true')),
        Index('idx_vehiculos_tipo', 'tipo_vehiculo_id', postgresql_where=text('activo = true')),
        UniqueConstraint('numero_economico', name='vehiculos_numero_economico_key'),
        UniqueConstraint('placa', name='vehiculos_placa_key'),
        UniqueConstraint('vin', name='vehiculos_vin_key'),
        {'extend_existing': True}
    )

    id: UUID = Field(default_factory=uuid4, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text('public.gen_random_uuid()')))
    tipo_vehiculo_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("tipos_vehiculo.id"), nullable=False))
    placa: Optional[str] = Field(default=None, max_length=15)
    vin: Optional[str] = Field(default=None, sa_column=Column(String(17)))
    numero_economico: str = Field(sa_column=Column(String(50), nullable=False))
    marca: Optional[str] = Field(default=None, sa_column=Column(String(50)))
    modelo_vehiculo: Optional[str] = Field(default=None, sa_column=Column(String(50)))
    anio_fabricacion: Optional[int] = Field(default=None, sa_column=Column(SmallInteger))
    fecha_alta: date = Field(sa_column=Column(Date, nullable=False, server_default=text('CURRENT_DATE')))
    fecha_baja: Optional[date] = Field(default=None, sa_column=Column(Date))
    activo: bool = Field(sa_column=Column(Boolean, nullable=False, server_default=text('true')))
    odometro_actual: Optional[int] = Field(default=None, sa_column=Column(Integer))
    fecha_ultimo_odometro: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP))
    ubicacion_actual: Optional[str] = Field(default=None, sa_column=Column(String(100)))
    notas: Optional[str] = Field(default=None, sa_column=Column(Text))
    creado_en: datetime = Field(sa_column=Column(TIMESTAMP, nullable=False, server_default=text('now()')))
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id")))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP))
    actualizado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL")))
    peso_carga_maxima_diseno_ton: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5, 2)))

    # Relationships comentadas para evitar conflictos de metadata
    # tipo_vehiculo: "TiposVehiculo" = Relationship(back_populates="vehiculos")
    # neumaticos: List["Neumatico"] = Relationship(back_populates="ubicacion_actual_vehiculo")
    # registros_odometro: List["RegistrosOdometro"] = Relationship(back_populates="vehiculo")
    # eventos_neumaticos: List["EventosNeumaticos"] = Relationship(back_populates="vehiculo")


class RegistrosOdometro(SQLModel, table=True):
    __tablename__ = 'registros_odometro'
    __table_args__ = (
        CheckConstraint("fuente::text <> ''::text", name='registros_odometro_fuente_check'),
        CheckConstraint('odometro >= 0', name='registros_odometro_odometro_check'),
        {'comment': 'Registros históricos de lecturas de odómetro de los vehículos'}
    )

    id: UUID = Field(default_factory=uuid4, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text('public.gen_random_uuid()')))
    vehiculo_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("vehiculos.id"), nullable=False))
    odometro: int = Field(sa_column=Column(Integer, nullable=False))
    fecha_medicion: datetime = Field(sa_column=Column(TIMESTAMP, nullable=False, server_default=text('now()')))
    fuente: Optional[str] = Field(default=None, sa_column=Column(String(50), server_default=text("'manual'::character varying")))
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id")))
    notas: Optional[str] = Field(default=None, sa_column=Column(Text))

    # Relationships comentadas para evitar conflictos de metadata
    # vehiculo: "Vehiculos" = Relationship(back_populates="registros_odometro")


# Rebuild models for forward references
TiposVehiculo.model_rebuild()
ConfiguracionesEje.model_rebuild()
PosicionesNeumatico.model_rebuild()
Vehiculos.model_rebuild()
RegistrosOdometro.model_rebuild()