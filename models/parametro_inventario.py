# models/parametro_inventario.py

import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, Enum as SAEnum, text, CheckConstraint, UniqueConstraint # Renombrar Enum a SAEnum para evitar conflicto
from models.common import TimestampTZ, utcnow_aware

# --- IMPORTAR EL ENUM DESDE COMMON ---
from schemas.common import TipoParametroEnum # <-- Nueva importación

# --- ELIMINAR LA DEFINICIÓN LOCAL ---
# import enum                          <-- Eliminar
# class TipoParametroEnum(str, enum.Enum): <-- Eliminar bloque completo
#    PROFUNDIDAD_MINIMA = "PROFUNDIDAD_MINIMA"
#    ...
# ------------------------------------

if TYPE_CHECKING:
    from .modelo import ModeloNeumatico
    from .almacen import Almacen
    from .usuario import Usuario

class ParametroInventario(SQLModel, table=True):
    __tablename__ = "parametros_inventario"
    __table_args__ = (
        # Constraint para asegurar que valor_numerico sea NOT NULL si es PROFUNDIDAD o STOCK, etc.
        # CheckConstraint(...), # Podrías añadir constraints aquí
        # Constraint único para combinación modelo/almacen/tipo
        UniqueConstraint('modelo_id', 'almacen_id', 'tipo_parametro', name='uq_parametro_inventario'),
    )

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    # FK a modelos_neumatico (NULL si es global)
    modelo_id: Optional[uuid.UUID] = Field(default=None, foreign_key="modelos_neumatico.id", index=True)
    # FK a almacenes (NULL si es global)
    almacen_id: Optional[uuid.UUID] = Field(default=None, foreign_key="almacenes.id", index=True)

    # Usar el Enum importado, usando SAEnum para la columna SQLAlchemy
    tipo_parametro: TipoParametroEnum = Field(
        sa_column=Column(SAEnum(TipoParametroEnum), nullable=False, index=True)
    )

    # Valor numérico del parámetro (ej: mm, unidades, km, años)
    valor_numerico: Optional[float] = Field(default=None)
    # Valor de texto (si algún parámetro lo necesita)
    valor_texto: Optional[str] = Field(default=None)

    activo: bool = Field(default=True, nullable=False)
    notas: Optional[str] = Field(default=None)

    # Campos de auditoría
    creado_en: datetime = Field(default_factory=utcnow_aware, sa_column=Column(TimestampTZ, nullable=False, server_default=text("now()")))
    creado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TimestampTZ, nullable=True))
    actualizado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")

    # Relaciones (opcional, si necesitas navegar desde el parámetro)
    # modelo: Optional["ModeloNeumatico"] = Relationship(back_populates="parametros")
    # almacen: Optional["Almacen"] = Relationship(back_populates="parametros")
    # creado_por_usuario: Optional["Usuario"] = Relationship(...)
    # actualizado_por_usuario: Optional["Usuario"] = Relationship(...)