# gesneu_api2/models/vehiculo.py
import uuid
from pydantic import ConfigDict, field_serializer, field_validator
from typing import Optional, List, TYPE_CHECKING, ClassVar, Dict, Any, Union, Annotated
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
    # Cambiado de int a str para evitar problemas de conversión
    tipo_vehiculo_id: str = Field(foreign_key="tipos_vehiculo.id")
    numero_economico: str = Field(max_length=50, unique=True, index=True)
    placa: Optional[str] = Field(default=None, max_length=20, unique=True, index=True, nullable=True)
    vin: Optional[str] = Field(default=None, max_length=50, unique=True, nullable=True) # Vehicle Identification Number
    marca: Optional[str] = Field(default=None, max_length=50)
    modelo_vehiculo: Optional[str] = Field(default=None, max_length=50) # Nombre del modelo del vehículo
    anio_fabricacion: Optional[int] = Field(default=None)
    # Almacenado como String para compatibilidad con SQLite en pruebas
    fecha_alta: Optional[str] = Field(default_factory=lambda: date.today().isoformat(), sa_column=Column(String))
    
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

    # Configuración moderna usando model_config con ConfigDict
    model_config: ClassVar[Dict[str, Any]] = ConfigDict(
        from_attributes=True,
        json_schema_extra={"example": {"id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"}}
    )
    
    # Serializadores para manejar conversiones de tipo
    @field_serializer('id', 'tipo_vehiculo_id')
    def serialize_uuid(self, value: Optional[Union[uuid.UUID, str]]) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return str(value)
        return value
    
    @field_serializer('fecha_alta', 'fecha_baja')
    def serialize_date(self, value: Optional[Union[date, str]]) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, date):
            return value.isoformat()
        return value