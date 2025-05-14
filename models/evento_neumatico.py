# gesneu_api2/models/evento_neumatico.py
import uuid
from pydantic import ConfigDict
import uuid
from datetime import datetime, timezone 
from typing import Optional, Dict, Any, TYPE_CHECKING , ClassVar, Dict, Any

import sqlalchemy 
from sqlmodel import Field, SQLModel, Relationship 
from sqlalchemy import (
    Column,
    text,
    TIMESTAMP, 
    ForeignKey,
    Enum as SAEnum,
    JSON,
    Numeric
)

from schemas.common import TipoEventoNeumaticoEnum, EstadoNeumaticoEnum 

# Para referencias adelantadas en relaciones
if TYPE_CHECKING:
    from .neumatico import Neumatico
    from .usuario import Usuario
    from .vehiculo import Vehiculo
    from .posicion_neumatico import PosicionNeumatico
    from .proveedor import Proveedor
    from .motivo_desecho import MotivoDesecho
    from .almacen import Almacen


class EventoNeumatico(SQLModel, table=True):
    """
    Representa la tabla 'eventos_neumaticos' en la base de datos.
    Registra cada evento significativo en el ciclo de vida de un neumático.
    """
    __tablename__ = "eventos_neumaticos"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    timestamp_evento: datetime = Field(
        description="Momento exacto en que ocurrió el evento.",
        default_factory=lambda: datetime.now(timezone.utc), 
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")) 
    )

    tipo_evento: TipoEventoNeumaticoEnum = Field(
        description="Tipo de evento registrado.",
        sa_column=Column(SAEnum(TipoEventoNeumaticoEnum, name="tipo_evento_neumatico_enum", create_type=False), nullable=False)
    )

    neumatico_id: uuid.UUID = Field(
        description="ID del neumático al que pertenece el evento.",
        foreign_key="neumaticos.id",
        index=True,
        nullable=False
    )

    usuario_id: uuid.UUID = Field(
        description="ID del usuario que registró el evento.",
        foreign_key="usuarios.id",
        index=True,
        nullable=False 
    )

    vehiculo_id: Optional[uuid.UUID] = Field(
        description="ID del vehículo involucrado (si aplica, ej. instalación, desmontaje).",
        default=None,
        foreign_key="vehiculos.id",
        index=True,
        nullable=True 
    )

    posicion_id: Optional[uuid.UUID] = Field(
        description="ID de la posición del neumático en el vehículo (si aplica).",
        default=None,
        foreign_key="posiciones_neumatico.id",
        index=True,
        nullable=True 
    )

    proveedor_servicio_id: Optional[uuid.UUID] = Field(
        description="ID del proveedor de servicio (si aplica, ej. reparación, reencauche).",
        default=None,
        foreign_key="proveedores.id",
        index=True,
        nullable=True 
    )

    motivo_desecho_id_evento: Optional[uuid.UUID] = Field(
        description="ID del motivo de desecho (si el evento es DESECHO o DESMONTAJE a desecho).",
        default=None,
        # foreign_key="motivos_desecho.id", # <--- ELIMINADO DE AQUÍ
        sa_column=Column(
            ForeignKey("motivos_desecho.id", name="fk_evento_motivo_desecho"), # Añadido nombre a FK
            nullable=True, 
            index=True
        ) 
    )
    
    relacion_evento_anterior: Optional[uuid.UUID] = Field(
        description="ID del evento anterior relacionado (opcional, para trazabilidad causa-efecto).",
        default=None,
        # foreign_key="eventos_neumaticos.id", # <--- ELIMINADO DE AQUÍ si se usa sa_column para FK
        sa_column=Column(
            ForeignKey("eventos_neumaticos.id", name="fk_evento_relacion_anterior"), # Añadido nombre a FK
            nullable=True
        ) 
    )

    almacen_destino_id: Optional[uuid.UUID] = Field(
        description="ID del almacén destino (si aplica, ej. desmontaje a stock, transferencia).",
        default=None,
        foreign_key="almacenes.id",
        index=True, 
        nullable=True 
    )

    destino_desmontaje: Optional[EstadoNeumaticoEnum] = Field(
        description="Estado al que pasa el neumático después de un desmontaje.",
        default=None,
        sa_column=Column(SAEnum(EstadoNeumaticoEnum, name="estado_neumatico_enum_destino", create_type=False), nullable=True) # Nombre del enum type diferente si es necesario
    )

    odometro_vehiculo_en_evento: Optional[int] = Field(
        description="Lectura del odómetro del vehículo en el momento del evento.",
        default=None,
        nullable=True 
    )

    profundidad_remanente_mm: Optional[float] = Field(
        description="Profundidad del dibujo medida durante el evento (ej. inspección).",
        default=None,
        sa_column=Column(Numeric(5, 2), nullable=True) 
    )

    presion_psi: Optional[float] = Field(
        description="Presión medida durante el evento (ej. inspección).",
        default=None,
        sa_column=Column(Numeric(5, 2), nullable=True) 
    )

    costo_evento: Optional[float] = Field(
        description="Costo asociado al evento (ej. reparación, reencauche).",
        default=None,
        sa_column=Column(Numeric(10, 2), nullable=True) 
    )

    moneda_costo: Optional[str] = Field(
        description="Moneda del costo del evento.",
        default="PEN",
        max_length=3,
        nullable=True 
    )

    notas: Optional[str] = Field(
        description="Notas adicionales o comentarios sobre el evento.",
        default=None,
        sa_column=Column(sqlalchemy.Text, nullable=True) 
    )

    profundidad_post_reencauche_mm: Optional[float] = Field(
        description="Profundidad del dibujo después de un evento de salida de reencauche.",
        default=None,
        sa_column=Column(Numeric(5, 2), nullable=True) 
    )

    datos_evento: Optional[Dict[str, Any]] = Field(
        description="Campo JSON para almacenar datos estructurados adicionales específicos del evento.",
        default=None,
        sa_column=Column(JSON, nullable=True) 
    )

    creado_en: datetime = Field(
        description="Timestamp de creación del registro en la BD.",
        default_factory=lambda: datetime.now(timezone.utc), 
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")) 
    )

    # --- Relaciones ---
    neumatico: Optional["Neumatico"] = Relationship(back_populates="eventos_neumatico")
    usuario: Optional["Usuario"] = Relationship() 
    vehiculo: Optional["Vehiculo"] = Relationship()
    posicion: Optional["PosicionNeumatico"] = Relationship()
    proveedor_servicio: Optional["Proveedor"] = Relationship()
    motivo_desecho: Optional["MotivoDesecho"] = Relationship(
        sa_relationship_kwargs={'foreign_keys': '[EventoNeumatico.motivo_desecho_id_evento]'}
        # back_populates="eventos_asociados" # Si MotivoDesecho tiene esta relación
    ) 
    evento_anterior: Optional["EventoNeumatico"] = Relationship(
        sa_relationship_kwargs=dict(
            foreign_keys="[EventoNeumatico.relacion_evento_anterior]",
            remote_side="[EventoNeumatico.id]" 
        )
    )
    almacen_destino: Optional["Almacen"] = Relationship()

    # Configuración moderna usando model_config con ConfigDict
        

    model_config: ClassVar[Dict[str, Any]] = ConfigDict(
        from_attributes=True
    )