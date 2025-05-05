# models/neumatico.py
import uuid
from datetime import date, datetime # Asegurar que 'date' esté importado
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, text, TIMESTAMP, ForeignKey, Numeric, Date # <-- Importar Date
from sqlalchemy import Enum as SAEnum
# --- Importar Base y Enum desde schemas ---
from schemas.neumatico import NeumaticoBase
from schemas.common import EstadoNeumaticoEnum
# --- Importar Helpers desde common ---
from models.common import TimestampTZ, utcnow_aware

class Neumatico(NeumaticoBase, table=True):
    __tablename__ = "neumaticos"
    # Permitir extender si ya existe (útil en algunos contextos, pero revisar si es necesario)
    __table_args__ = {'extend_existing': True}

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    # Hereda campos base:
    # numero_serie: Optional[str] = Field(default=None, index=True)
    # dot: Optional[str] = Field(default=None)
    # modelo_id: uuid.UUID = Field(foreign_key="modelos_neumatico.id")
    # fecha_compra: date
    # fecha_fabricacion: Optional[date] = None
    # costo_compra: Optional[float] = Field(default=None, ge=0)
    # moneda_compra: Optional[str] = Field(default="PEN", max_length=3)
    # proveedor_compra_id: Optional[uuid.UUID] = Field(default=None, foreign_key="proveedores.id")

    # --- Campos específicos tabla con mapeo/defaults ---
    estado_actual: EstadoNeumaticoEnum = Field(
        default=EstadoNeumaticoEnum.EN_STOCK,
        sa_column=Column(SAEnum(EstadoNeumaticoEnum, name="estado_neumatico_enum", create_type=False),
                         nullable=False,
                         default=EstadoNeumaticoEnum.EN_STOCK)
    )
    ubicacion_actual_vehiculo_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="vehiculos.id", index=True, nullable=True # Permitir nulo explícitamente
    )
    ubicacion_actual_posicion_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="posiciones_neumatico.id", index=True, nullable=True # Permitir nulo explícitamente
    )
    ubicacion_almacen_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="almacenes.id", index=True, nullable=True
    )

    # --- CAMPOS AÑADIDOS ---
    km_instalacion: Optional[int] = Field(default=None, nullable=True)
    fecha_instalacion: Optional[date] = Field(default=None, sa_column=Column(Date, nullable=True))
    # ------------------------

    fecha_ultimo_evento: Optional[datetime] = Field(
        default=None, sa_column=Column(TimestampTZ, nullable=True)
    )
    # Usar Numeric para precisión decimal en BD, permitir nulo
    profundidad_inicial_mm: Optional[float] = Field(
        default=None, sa_column=Column(Numeric(5, 2), nullable=True)
    )
    kilometraje_acumulado: int = Field(default=0) # Este es el campo principal para KM totales
    reencauches_realizados: int = Field(default=0)
    vida_actual: int = Field(default=1) # Considerar si se calcula o se almacena
    es_reencauchado: bool = Field(default=False)
    fecha_desecho: Optional[date] = Field(default=None, nullable=True)
    motivo_desecho_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="motivos_desecho.id", nullable=True
    )

    # Campos de auditoría
    creado_en: datetime = Field(
        default_factory=utcnow_aware,
        sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()"))
    )
    creado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(
        default=None, sa_column=Column(TimestampTZ, nullable=True)
    )
    actualizado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")

    # class Config: # No es necesario si ya está en NeumaticoBase
    #     from_attributes = True