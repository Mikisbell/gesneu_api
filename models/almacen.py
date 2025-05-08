# gesneu_api2/models/almacen.py
import uuid
from datetime import datetime, timezone # Asegurarse que timezone esté importado si se usa
from typing import Optional, List, TYPE_CHECKING # Añadir List y TYPE_CHECKING para relaciones

from sqlmodel import Field, SQLModel, Relationship # Añadir Relationship
# Column y text ya no son necesarios aquí si heredamos SQLModelTimestamp
# from sqlalchemy import Column, ForeignKey, text 

# --- Importar los mixins correctos desde .common ---
from .common import SQLModelTimestamp, EstadoItem # <--- CORREGIDO

# Para referencias adelantadas en relaciones
if TYPE_CHECKING:
    from .neumatico import Neumatico
    from .usuario import Usuario # Si se usa para creador/actualizador en relaciones explícitas


# Definir una clase base para los campos específicos de Almacen
class AlmacenBase(SQLModel):
    codigo: str = Field(unique=True, index=True, max_length=20)
    nombre: str = Field(max_length=150)
    tipo: Optional[str] = Field(default=None, max_length=50) # Ej: Principal, Taller, Transito
    direccion: Optional[str] = Field(default=None, max_length=255)
    # El campo 'activo' y los campos de timestamp vendrán de EstadoItem y SQLModelTimestamp

# Modelo de tabla Almacen, heredando los campos de auditoría y estado
class Almacen(SQLModelTimestamp, EstadoItem, AlmacenBase, table=True):
    __tablename__ = "almacenes"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, index=True) # Añadido index=True

    # Los campos 'activo', 'fecha_baja', 'creado_en', 'actualizado_en', 
    # 'creado_por', 'actualizado_por' son heredados de SQLModelTimestamp y EstadoItem.
    # Ya no es necesario definirlos explícitamente aquí.

    # --- Relaciones ---
    # Un almacén puede tener muchos neumáticos (si se rastrea el stock así)
    # Esta relación asume que Neumatico tiene un campo 'ubicacion_almacen_id'
    neumaticos_en_almacen: List["Neumatico"] = Relationship(back_populates="almacen_actual")

    # Si quieres relacionar explícitamente con el usuario creador/actualizador más allá
    # de los campos UUID heredados de SQLModelTimestamp:
    # creador: Optional["Usuario"] = Relationship(
    #     sa_relationship_kwargs={'foreign_keys': '[Almacen.creado_por]'}
    # )
    # actualizador: Optional["Usuario"] = Relationship(
    #     sa_relationship_kwargs={'foreign_keys': '[Almacen.actualizado_por]'}
    # )

    class Config:
        from_attributes = True # Para Pydantic V2 (reemplaza orm_mode)
        # orm_mode = True # Para Pydantic V1
