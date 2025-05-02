# models/neumatico.py
import uuid
from datetime import date, datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, text, TIMESTAMP, ForeignKey, Numeric # <-- Asegurar Numeric
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
    # numero_serie: str
    # dot: Optional[str]
    # modelo_id: uuid.UUID (FK a modelos_neumatico)
    # fecha_compra: date
    # fecha_fabricacion: Optional[date]
    # costo_compra: Optional[float]
    # moneda_compra: Optional[str]
    # proveedor_compra_id: Optional[uuid.UUID] (FK a proveedores)

    # --- Campos específicos tabla con mapeo/defaults ---
    estado_actual: EstadoNeumaticoEnum = Field(
        default=EstadoNeumaticoEnum.EN_STOCK,
        sa_column=Column(SAEnum(EstadoNeumaticoEnum, name="estado_neumatico_enum", create_type=False),
                         nullable=False,
                         default=EstadoNeumaticoEnum.EN_STOCK)
    )
    ubicacion_actual_vehiculo_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="vehiculos.id", index=True # Añadir index=True
    )
    ubicacion_actual_posicion_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="posiciones_neumatico.id", index=True # Añadir index=True
    )
    fecha_ultimo_evento: Optional[datetime] = Field(
        default=None, sa_column=Column(TimestampTZ, nullable=True)
    )
    # Usar Numeric para precisión decimal en BD
    profundidad_inicial_mm: Optional[float] = Field(
        default=None, sa_column=Column(Numeric(5, 2))
    )
    kilometraje_acumulado: int = Field(default=0)
    reencauches_realizados: int = Field(default=0)
    vida_actual: int = Field(default=1)
    es_reencauchado: bool = Field(default=False)
    fecha_desecho: Optional[date] = Field(default=None)
    motivo_desecho_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="motivos_desecho.id"
    )

    # --- *** CAMPO AÑADIDO *** ---
    ubicacion_almacen_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="almacenes.id", index=True, nullable=True
    )
    # -----------------------------

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

    # Relationship eliminada (como indicaste en el comentario)

    # Añadir Config si no hereda de NeumaticoBase que ya la tenga
    # class Config:
    #     from_attributes = True # Para Pydantic v2
