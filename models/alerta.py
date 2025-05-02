# models/alerta.py
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, ForeignKey, text, JSON # Usar JSON estándar

# Importar helpers comunes
from models.common import TimestampTZ, utcnow_aware

class Alerta(SQLModel, table=True):
    __tablename__ = "alertas" # Nombre de la tabla creada

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    tipo_alerta: str = Field(index=True, max_length=50)
    mensaje: str
    nivel_severidad: str = Field(default='INFO', max_length=20) # ('INFO', 'WARN', 'CRITICAL')
    estado_alerta: str = Field(default='NUEVA', index=True, max_length=20) # ('NUEVA', 'VISTA', 'GESTIONADA')

    timestamp_generacion: datetime = Field(
        default_factory=utcnow_aware,
        sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()"))
    )
    timestamp_gestion: Optional[datetime] = Field(
        default=None,
        sa_column=Column(TimestampTZ, nullable=True)
    )
    usuario_gestion_id: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")

    # Foreign Keys opcionales
    neumatico_id: Optional[uuid.UUID] = Field(default=None, foreign_key="neumaticos.id", index=True)
    vehiculo_id: Optional[uuid.UUID] = Field(default=None, foreign_key="vehiculos.id", index=True)
    modelo_id: Optional[uuid.UUID] = Field(default=None, foreign_key="modelos_neumatico.id", index=True)
    almacen_id: Optional[uuid.UUID] = Field(default=None, foreign_key="almacenes.id", index=True)
    parametro_id: Optional[uuid.UUID] = Field(default=None, foreign_key="parametros_inventario.id")

    datos_contexto: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

    class Config:
        orm_mode = True