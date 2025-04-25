# models/modelo.py
import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, ForeignKey, text
from models.common import TimestampTZ, utcnow_aware

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
