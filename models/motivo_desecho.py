# gesneu_api2/models/motivo_desecho.py
import uuid
from datetime import datetime, timezone # Asegurarse que timezone esté importado si se usa
from typing import Optional, List, TYPE_CHECKING # Añadir List y TYPE_CHECKING para relaciones

from sqlmodel import Field, SQLModel, Relationship # Añadir Relationship
# Column, ForeignKey, text ya no son necesarios aquí si heredamos SQLModelTimestamp
# from sqlalchemy import Column, ForeignKey, text 

# --- Importar los mixins correctos desde .common ---
from .common import SQLModelTimestamp, EstadoItem # <--- CORREGIDO

# Para referencias adelantadas en relaciones
if TYPE_CHECKING:
    from .neumatico import Neumatico
    from .usuario import Usuario # Si se usa para creador/actualizador en relaciones explícitas


# Definir una clase base para los campos específicos de MotivoDesecho
class MotivoDesechoBase(SQLModel):
    codigo: str = Field(unique=True, index=True, max_length=20) # Añadido index=True
    descripcion: str = Field(max_length=255) # Especificar max_length
    requiere_evidencia: bool = Field(default=False)
    # El campo 'activo' y los campos de timestamp vendrán de EstadoItem y SQLModelTimestamp

# Modelo de tabla MotivoDesecho, heredando los campos de auditoría y estado
class MotivoDesecho(SQLModelTimestamp, EstadoItem, MotivoDesechoBase, table=True):
    __tablename__ = "motivos_desecho"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, index=True) # Añadido index=True

    # Los campos 'activo', 'fecha_baja', 'creado_en', 'actualizado_en', 
    # 'creado_por', 'actualizado_por' son heredados de SQLModelTimestamp y EstadoItem.
    # Ya no es necesario definirlos explícitamente aquí.

    # --- Relaciones ---
    # Un motivo de desecho puede estar asociado a muchos neumáticos desechados
    # Esta relación asume que Neumatico tiene un campo 'motivo_desecho_id'
    neumaticos_desechados: List["Neumatico"] = Relationship(back_populates="motivo_desecho")
    
    # Si quieres relacionar explícitamente con el usuario creador/actualizador más allá
    # de los campos UUID heredados de SQLModelTimestamp:
    # creador: Optional["Usuario"] = Relationship(
    #     sa_relationship_kwargs={'foreign_keys': '[MotivoDesecho.creado_por]'}
    # )
    # actualizador: Optional["Usuario"] = Relationship(
    #     sa_relationship_kwargs={'foreign_keys': '[MotivoDesecho.actualizado_por]'}
    # )

    class Config:
        from_attributes = True # Para Pydantic V2 (reemplaza orm_mode)
        # orm_mode = True # Para Pydantic V1
