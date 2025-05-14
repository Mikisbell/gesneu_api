# gesneu_api2/models/alerta.py
import uuid
from datetime import datetime, timezone 
from typing import Optional, Dict, Any, List, TYPE_CHECKING, ClassVar
from pydantic import ConfigDict

import sqlalchemy # <--- IMPORTACIÓN AÑADIDA AQUÍ
from sqlmodel import Field, SQLModel, Relationship 
from sqlalchemy import Column, ForeignKey, text, JSON, TIMESTAMP 
# Eliminar Enum de sqlalchemy si no se usa directamente aquí para definir columnas Enum
# from sqlalchemy import Enum as SAEnum 

# --- Importar SQLModelTimestamp ---
from .common import SQLModelTimestamp 
# TipoAlertaEnum se importará desde schemas.common si se define un campo de tipo enum aquí.
from schemas.common import TipoAlertaEnum # Asumiendo que lo usarás para tipo_alerta

# Para referencias adelantadas en relaciones
if TYPE_CHECKING:
    from .usuario import Usuario
    from .neumatico import Neumatico
    from .vehiculo import Vehiculo
    from .modelo import ModeloNeumatico # Asumiendo que es ModeloNeumatico
    from .almacen import Almacen
    from .parametro_inventario import ParametroInventario


# Definir una clase base para los campos específicos de Alerta
class AlertaBase(SQLModel):
    tipo_alerta: TipoAlertaEnum = Field(index=True, max_length=50) # Usar el Enum
    descripcion: str = Field(sa_column=Column(sqlalchemy.Text, nullable=False)) # Renombrado de mensaje a descripcion y usando Text
    
    nivel_severidad: str = Field(default='INFO', max_length=20) # ('INFO', 'WARN', 'CRITICAL')
    
    resuelta: bool = Field(default=False, index=True, nullable=False)

    # Foreign Keys opcionales
    neumatico_id: Optional[uuid.UUID] = Field(default=None, foreign_key="neumaticos.id", index=True)
    vehiculo_id: Optional[uuid.UUID] = Field(default=None, foreign_key="vehiculos.id", index=True)
    modelo_id: Optional[uuid.UUID] = Field(default=None, foreign_key="modelos_neumatico.id", index=True)
    almacen_id: Optional[uuid.UUID] = Field(default=None, foreign_key="almacenes.id", index=True)
    parametro_id: Optional[uuid.UUID] = Field(default=None, foreign_key="parametros_inventario.id")

    datos_contexto: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))


# Modelo de tabla Alerta, heredando los campos de auditoría de SQLModelTimestamp
class Alerta(SQLModelTimestamp, AlertaBase, table=True):
    __tablename__ = "alertas"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, index=True) 

    # --- Campos heredados de AlertaBase ---
    # tipo_alerta, descripcion, nivel_severidad, resuelta, FKs, datos_contexto

    # --- Campos heredados de SQLModelTimestamp ---
    # creado_en (será el timestamp_generacion)
    # actualizado_en (será el timestamp_gestion si la alerta se actualiza/resuelve)
    # creado_por (quién/qué sistema generó la alerta, si es un usuario)
    # actualizado_por (será el usuario_gestion_id si un usuario la actualiza/resuelve)

    # --- Relaciones ---
    neumatico: Optional["Neumatico"] = Relationship() # back_populates="alertas"
    vehiculo: Optional["Vehiculo"] = Relationship()   # back_populates="alertas"
    modelo: Optional["ModeloNeumatico"] = Relationship() # back_populates="alertas"
    almacen: Optional["Almacen"] = Relationship()     # back_populates="alertas"
    parametro: Optional["ParametroInventario"] = Relationship() # back_populates="alertas"

    usuario_creador: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={'foreign_keys': '[Alerta.creado_por]'}
    )
    usuario_gestor: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={'foreign_keys': '[Alerta.actualizado_por]'}
    )
    
    # Configuración moderna usando model_config con ConfigDict
    model_config: ClassVar[Dict[str, Any]] = ConfigDict(
        from_attributes=True
    )