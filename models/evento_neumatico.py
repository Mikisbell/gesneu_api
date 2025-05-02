# models/evento_neumatico.py
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
import sqlalchemy # Importar sqlalchemy para tipos como Numeric, Text
from sqlmodel import Field, SQLModel
from sqlalchemy import (
    Column,
    text,
    TIMESTAMP,
    ForeignKey,
    Enum as SAEnum,
    JSON,
    Numeric # Importar Numeric explícitamente
)
from models.common import TimestampTZ, utcnow_aware # Tus helpers de timestamp
from schemas.common import TipoEventoNeumaticoEnum, EstadoNeumaticoEnum # Tus Enums

# --- Modelo de Tabla (SIN herencia de Base) ---
class EventoNeumatico(SQLModel, table=True):
    """
    Representa la tabla 'eventos_neumaticos' en la base de datos.
    Registra cada evento significativo en el ciclo de vida de un neumático.
    """
    __tablename__ = "eventos_neumaticos"

    # --- Columnas Principales ---
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    timestamp_evento: datetime = Field(
        description="Momento exacto en que ocurrió el evento.",
        default_factory=utcnow_aware,
        sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()"))
    )

    tipo_evento: TipoEventoNeumaticoEnum = Field(
        description="Tipo de evento registrado.",
        sa_column=Column(SAEnum(TipoEventoNeumaticoEnum, name="tipo_evento_neumatico_enum", create_type=False), nullable=False)
    )

    # --- Claves Foráneas ---
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
        nullable=False # Asumiendo que siempre se requiere un usuario
    )

    vehiculo_id: Optional[uuid.UUID] = Field(
        description="ID del vehículo involucrado (si aplica, ej. instalación, desmontaje).",
        default=None,
        foreign_key="vehiculos.id",
        index=True
    )

    posicion_id: Optional[uuid.UUID] = Field(
        description="ID de la posición del neumático en el vehículo (si aplica).",
        default=None,
        foreign_key="posiciones_neumatico.id",
        index=True
    )

    proveedor_servicio_id: Optional[uuid.UUID] = Field(
        description="ID del proveedor de servicio (si aplica, ej. reparación, reencauche).",
        default=None,
        foreign_key="proveedores.id",
        index=True
    )

    # --- CORRECCIÓN APLICADA AQUÍ ---
    motivo_desecho_id_evento: Optional[uuid.UUID] = Field(
        description="ID del motivo de desecho (si el evento es DESECHO o DESMONTAJE a desecho).",
        default=None,
        # Eliminado index=True de Field(), ya se especifica en sa_column.
        sa_column=Column(ForeignKey("motivos_desecho.id"), nullable=True, index=True)
    )
    # --------------------------------

    relacion_evento_anterior: Optional[uuid.UUID] = Field(
        description="ID del evento anterior relacionado (opcional, para trazabilidad causa-efecto).",
        default=None,
        sa_column=Column(ForeignKey("eventos_neumaticos.id"), nullable=True)
    )

    almacen_destino_id: Optional[uuid.UUID] = Field(
        description="ID del almacén destino (si aplica, ej. desmontaje a stock, transferencia).",
        default=None,
        foreign_key="almacenes.id"
        # Podrías añadir index=True si filtras frecuentemente por esto
    )

    # --- Campos Específicos del Evento ---
    destino_desmontaje: Optional[EstadoNeumaticoEnum] = Field(
        description="Estado al que pasa el neumático después de un desmontaje.",
        default=None,
        sa_column=Column(SAEnum(EstadoNeumaticoEnum, name="estado_neumatico_enum", create_type=False), nullable=True)
    )

    odometro_vehiculo_en_evento: Optional[int] = Field(
        description="Lectura del odómetro del vehículo en el momento del evento.",
        default=None
        # Añadir sa_column si el nombre difiere o necesitas constraints específicas
    )

    profundidad_remanente_mm: Optional[float] = Field(
        description="Profundidad del dibujo medida durante el evento (ej. inspección).",
        default=None,
        sa_column=Column(Numeric(5, 2)) # Usar Numeric para precisión
    )

    presion_psi: Optional[float] = Field(
        description="Presión medida durante el evento (ej. inspección).",
        default=None,
        sa_column=Column(Numeric(5, 2)) # Usar Numeric para precisión
    )

    costo_evento: Optional[float] = Field(
        description="Costo asociado al evento (ej. reparación, reencauche).",
        default=None,
        sa_column=Column(Numeric(10, 2)) # Usar Numeric para precisión
    )

    moneda_costo: Optional[str] = Field(
        description="Moneda del costo del evento.",
        default="PEN",
        max_length=3
    )

    notas: Optional[str] = Field(
        description="Notas adicionales o comentarios sobre el evento.",
        default=None,
        sa_column=Column(sqlalchemy.Text) # Usar Text para notas potencialmente largas
    )

    profundidad_post_reencauche_mm: Optional[float] = Field(
        description="Profundidad del dibujo después de un evento de salida de reencauche.",
        default=None,
        sa_column=Column(Numeric(5, 2)) # Usar Numeric para precisión
    )

    datos_evento: Optional[Dict[str, Any]] = Field(
        description="Campo JSON para almacenar datos estructurados adicionales específicos del evento.",
        default=None,
        sa_column=Column(JSON)
    )

    # --- Campos de Auditoría (Automáticos en DB) ---
    creado_en: datetime = Field(
        description="Timestamp de creación del registro en la BD.",
        default_factory=utcnow_aware,
        sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()"))
    )

    # Nota: No necesitas definir aquí explícitamente las relaciones inversas
    # (como 'neumatico' o 'usuario') a menos que las vayas a usar directamente
    # en lógica compleja dentro del backend que requiera el objeto relacionado.
    # Para respuestas API, normalmente construyes el DTO (Schema Read) con los datos necesarios.

    class Config:
        # Configuración de Pydantic/SQLModel si es necesaria
        # from_attributes = True # Pydantic v2 (SQLModel puede manejarlo implícitamente)
        # anystr_strip_whitespace = True # Opcional: limpiar espacios en strings
        pass