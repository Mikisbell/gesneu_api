# models/evento_neumatico.py (Contenido Correcto)
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any # Podrías necesitar Dict, Any si EventoNeumaticoBase no está completamente tipado

from sqlalchemy import Column, ForeignKey, TIMESTAMP, text
from sqlalchemy import Enum as SAEnum # Importar si EventoNeumaticoBase usa SAEnum aquí directamente (no lo hace ahora)
from sqlalchemy.dialects.postgresql import JSONB # Importar si EventoNeumaticoBase usa JSONB aquí directamente (no lo hace ahora)
from sqlmodel import Field, SQLModel

# --- IMPORTANTE: Importar la clase Base desde schemas ---
from schemas.evento_neumatico import EventoNeumaticoBase

# --- Importar Helpers (ajusta ruta si los moviste a models/common.py) ---
from models.common import TimestampTZ, utcnow_aware


class EventoNeumatico(EventoNeumaticoBase, table=True):
    __tablename__ = "eventos_neumaticos"
    __table_args__ = {'extend_existing': True} # FIX

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    # Hereda todos los campos mapeados a columnas desde EventoNeumaticoBase

    # --- Definir campos específicos de tabla que NO estén en Base ---
    #    (En este caso, timestamp_evento y creado_en están en la tabla,
    #     pero los definimos aquí con mapeo explícito para asegurar)
    timestamp_evento: Optional[datetime] = Field(
        default=None, # La BD tiene DEFAULT now()
        sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()"))
    )
    creado_en: datetime = Field(
        default_factory=utcnow_aware, # Python genera valor TZ-aware
        sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()")) # Mapeo explícito TZ-aware
    )
    # Relationship eliminada