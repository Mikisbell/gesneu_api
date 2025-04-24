# models.py (Basado en tu código, con validadores formateados)
import uuid
from datetime import date, datetime, timezone
from typing import Optional, Dict, Any
from enum import Enum


# Importaciones SQLAlchemy/SQLModel necesarias
from pydantic import BaseModel, EmailStr, field_validator, ValidationInfo
from sqlalchemy import Column, ForeignKey, TIMESTAMP, text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel


# --- Helpers ---
utcnow_aware = lambda: datetime.now(timezone.utc)
TimestampTZ = TIMESTAMP(timezone=True)

# --- Modelos Base ---

class UsuarioBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: Optional[EmailStr] = Field(default=None, unique=True, index=True)
    nombre_completo: Optional[str] = None
    rol: str = Field(default="OPERADOR")
    activo: bool = True

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioRead(UsuarioBase):
    id: uuid.UUID
    creado_en: datetime
    actualizado_en: Optional[datetime] = None





# Vehículos (Base definida ANTES)
class VehiculoBase(SQLModel):
    tipo_vehiculo_id: uuid.UUID = Field(foreign_key="tipos_vehiculo.id")
    numero_economico: str = Field(max_length=50, index=True)
    placa: Optional[str] = Field(default=None, unique=True, index=True, max_length=15)
    vin: Optional[str] = Field(default=None, unique=True, max_length=17)
    marca: Optional[str] = Field(default=None, max_length=50)
    modelo_vehiculo: Optional[str] = Field(default=None, max_length=50)
    anio_fabricacion: Optional[int] = Field(default=None)
    fecha_alta: Optional[date] = Field(default_factory=date.today)
    activo: bool = True
    ubicacion_actual: Optional[str] = Field(default=None, max_length=100)
    notas: Optional[str] = None

    @field_validator('anio_fabricacion')
    def check_anio_fabricacion(cls, v):
        if v is not None and (v < 1900 or v > datetime.now(timezone.utc).year + 1):
            raise ValueError(f"Año de fabricación inválido: {v}")
        return v

class VehiculoCreate(VehiculoBase):
    pass

class VehiculoRead(VehiculoBase):
    id: uuid.UUID
    odometro_actual: Optional[int] = None
    fecha_ultimo_odometro: Optional[datetime] = None
    creado_en: datetime
    actualizado_en: Optional[datetime] = None

class VehiculoUpdate(SQLModel):
    tipo_vehiculo_id: Optional[uuid.UUID]=None; placa: Optional[str]=None; vin: Optional[str]=None; numero_economico: Optional[str]=None; marca: Optional[str]=None; modelo_vehiculo: Optional[str]=None; anio_fabricacion: Optional[int]=None; fecha_alta: Optional[date]=None; fecha_baja: Optional[date]=None; activo: Optional[bool]=None; ubicacion_actual: Optional[str]=None; notas: Optional[str]=None


# --- Modelos de Tabla ---

class Usuario(UsuarioBase, table=True):
    __tablename__ = "usuarios"; __table_args__ = {'extend_existing': True}
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    password_hash: Optional[str] = None
    creado_en: datetime = Field(default_factory=utcnow_aware, sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()")))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TimestampTZ, nullable=True))



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



class ModeloNeumatico(SQLModel, table=True):
    __tablename__ = "modelos_neumatico"
    # Formato limpio
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    fabricante_id: uuid.UUID = Field(foreign_key="fabricantes_neumatico.id")
    nombre_modelo: str
    medida: str
    indice_carga: Optional[str] = Field(default=None, max_length=5)
    indice_velocidad: Optional[str] = Field(default=None, max_length=2)
    profundidad_original_mm: float
    presion_recomendada_psi: Optional[float] = None
    permite_reencauche: bool = False
    reencauches_maximos: int = 0
    creado_en: datetime = Field(default_factory=utcnow_aware, sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()")))
    creado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TimestampTZ, nullable=True))
    actualizado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")

class TipoVehiculo(SQLModel, table=True):
    __tablename__ = "tipos_vehiculo"
    # Formato limpio
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    nombre: str = Field(index=True)
    categoria_principal: Optional[str] = Field(default=None, max_length=50)
    ejes_standard: int = 2
    activo: bool = True
    creado_en: datetime = Field(default_factory=utcnow_aware, sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()")))
    creado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TimestampTZ, nullable=True))
    actualizado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")





class Vehiculo(VehiculoBase, table=True):
    __tablename__ = "vehiculos"; __table_args__ = {'extend_existing': True}
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    fecha_baja: Optional[date] = Field(default=None)
    odometro_actual: Optional[int] = Field(default=None)
    fecha_ultimo_odometro: Optional[datetime] = Field(default=None, sa_column=Column(TimestampTZ, nullable=True))
    creado_en: datetime = Field(default_factory=utcnow_aware, sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()")))
    creado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TimestampTZ, nullable=True))
    actualizado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")





class RegistroOdometro(SQLModel, table=True):
    __tablename__ = "registros_odometro"
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    vehiculo_id: uuid.UUID = Field(foreign_key="vehiculos.id")
    odometro: int
    fecha_medicion: datetime = Field(default_factory=utcnow_aware, sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()")))
    fuente: Optional[str] = Field(default="manual", max_length=50)
    creado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    notas: Optional[str] = None

# --- Modelos Auth ---
class Token(BaseModel): access_token: str; token_type: str
class TokenData(BaseModel): username: Optional[str] = None