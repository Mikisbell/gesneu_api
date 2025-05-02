# models/parametro_inventario.py
import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, ForeignKey, text, Numeric # Asegurar Numeric para decimales

# Importar helpers comunes
from models.common import TimestampTZ, utcnow_aware

class ParametroInventario(SQLModel, table=True):
    __tablename__ = "parametros_inventario"

    # Columnas de la tabla (basado en tu esquema de BD)
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    parametro_tipo: str = Field(index=True, max_length=50) # Parte de la clave única lógica
    modelo_id: uuid.UUID = Field(foreign_key="modelos_neumatico.id", index=True) # Parte de la clave
    ubicacion_almacen_id: Optional[uuid.UUID] = Field(default=None, foreign_key="almacenes.id", index=True) # Parte de la clave (puede ser NULL)

    valor_numerico: Optional[float] = Field(default=None, sa_column=Column(Numeric(10, 2))) # Usar Numeric para precisión
    valor_texto: Optional[str] = Field(default=None)
    activo: bool = Field(default=True, index=True)
    notas: Optional[str] = Field(default=None)

    # Campos de auditoría
    creado_en: datetime = Field(
        default_factory=utcnow_aware,
        sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()"))
    )
    creado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(
        default=None,
        sa_column=Column(TimestampTZ, nullable=True)
    )
    actualizado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")

    # (Opcional) Definir relaciones si las necesitas directamente en el modelo
    # modelo: Optional["ModeloNeumatico"] = Relationship(back_populates="parametros")
    # almacen: Optional["Almacen"] = Relationship(back_populates="parametros")

    class Config:
        # Configuración para Pydantic/SQLModel si es necesaria
        orm_mode = True # Compatible con SQLAlchemy ORM si usas relaciones