# gesneu_api2/models/vehiculo.py
import uuid
from typing import Optional, List, TYPE_CHECKING # <--- TYPE_CHECKING AÑADIDO
from datetime import date, datetime
from sqlmodel import Field, SQLModel, Relationship, Column
from sqlalchemy import UUID as SQLAlchemyUUID, Date as SQLAlchemyDate, String
from .common import SQLModelTimestamp, EstadoItem

# Bloque para importaciones solo visibles por analizadores de tipo (Pylance, MyPy)
# Esto ayuda a resolver las advertencias de "UndefinedVariable" para referencias adelantadas
# sin causar importaciones circulares en tiempo de ejecución.
if TYPE_CHECKING:
    from .tipo_vehiculo import TipoVehiculo
    from .registro_odometro import RegistroOdometro
    from .neumatico import Neumatico
    # Si SQLModelTimestamp o EstadoItem tuvieran relaciones complejas que necesitaran
    # referencias adelantadas a Usuario, también se importarían aquí.
    # from .usuario import Usuario # Ejemplo, si fuera necesario para SQLModelTimestamp

class VehiculoBase(SQLModel):
    tipo_vehiculo_id: int = Field(foreign_key="tipos_vehiculo.id")
    numero_economico: str = Field(max_length=50, unique=True, index=True)
    placa: Optional[str] = Field(default=None, max_length=20, unique=True, index=True, nullable=True)
    vin: Optional[str] = Field(default=None, max_length=50, unique=True, nullable=True) # Vehicle Identification Number
    marca: Optional[str] = Field(default=None, max_length=50)
    modelo_vehiculo: Optional[str] = Field(default=None, max_length=50) # Nombre del modelo del vehículo
    anio_fabricacion: Optional[int] = Field(default=None)
    fecha_alta: Optional[date] = Field(default_factory=date.today, sa_column=Column(String)) # Cambiado a String para compatibilidad con SQLite en pruebas
    
    ubicacion_actual: Optional[str] = Field(default=None, max_length=255)
    notas: Optional[str] = Field(default=None, max_length=1000)


class Vehiculo(VehiculoBase, SQLModelTimestamp, EstadoItem, table=True):
    __tablename__ = "vehiculos"

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, # Default para el modelo Pydantic/SQLModel
        sa_column=Column( # Definición explícita para SQLAlchemy
            SQLAlchemyUUID(as_uuid=True), 
            primary_key=True, 
            default=uuid.uuid4, # Default a nivel de base de datos
            unique=True,
            nullable=False,
            index=True
        )
    )
    
    odometro_actual: Optional[int] = Field(default=None, nullable=True)
    fecha_ultimo_odometro: Optional[datetime] = Field(default=None, nullable=True)

    # Relaciones con referencias adelantadas (strings)
    # Pylance ahora debería poder encontrar estas clases gracias al bloque TYPE_CHECKING
    tipo_vehiculo: Optional["TipoVehiculo"] = Relationship(back_populates="vehiculos") 
    registros_odometro: List["RegistroOdometro"] = Relationship(back_populates="vehiculo")
    neumaticos_instalados: List["Neumatico"] = Relationship(back_populates="vehiculo_instalado")

    class Config:
        from_attributes = True # Para Pydantic V2
