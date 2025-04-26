# models/evento_neumatico.py
import uuid
from models.proveedor import Proveedor
from datetime import datetime
from typing import Optional #, List (List ya no es necesario si quitaste eventos_siguientes)
from sqlmodel import Field, SQLModel # No Relationship
from sqlalchemy import Column, text, TIMESTAMP, ForeignKey
# No imports de sqlalchemy.orm
# from schemas.evento_neumatico import EventoNeumaticoBase # Si volviste a usarla
from models.common import TimestampTZ, utcnow_aware

# --- ¡¡ASEGÚRATE DE QUE ESTOS IMPORTS ESTÉN!! ---
from models.neumatico import Neumatico
from models.usuario import Usuario
from models.vehiculo import Vehiculo
from models.posicion_neumatico import PosicionNeumatico
from models.motivo_desecho import MotivoDesecho
# --- FIN IMPORTS ---

# Si volviste a la herencia de Base, descomenta esto:
from schemas.evento_neumatico import EventoNeumaticoBase

# Heredamos de Base, definimos tabla y añadimos campos específicos + FK problemática
class EventoNeumatico(EventoNeumaticoBase, table=True):
    __tablename__ = "eventos_neumaticos"
    # Si EventoNeumaticoBase NO tiene table=True:
    __table_args__ = {'extend_existing': True}

    # ID y Timestamps específicos
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    timestamp_evento: datetime = Field(
        default_factory=utcnow_aware,
        sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()"))
    )
    creado_en: datetime = Field(
        default_factory=utcnow_aware,
        sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()"))
    )

    # --- Columna FK Auto-Referenciada (Definición Correcta) ---
    # Definimos el campo mapeado a la columna de BD y su FK.
    relacion_evento_anterior: Optional[uuid.UUID] = Field(
        default=None,
        sa_column=Column("relacion_evento_anterior", ForeignKey("eventos_neumaticos.id"), nullable=True)
    )
    # --- FIN FK ---

    # --- Relationships ELIMINADAS ---
    # evento_anterior: Optional["EventoNeumatico"] = Relationship(...) # BORRADO
    # eventos_siguientes: List["EventoNeumatico"] = Relationship(...) # BORRADO
    # --- FIN Relationships ---

    # Los demás campos (neumatico_id, usuario_id, etc.) se heredan de EventoNeumaticoBase