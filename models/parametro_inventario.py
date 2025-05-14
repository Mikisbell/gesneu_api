# gesneu_api2/models/parametro_inventario.py
import uuid
from pydantic import ConfigDict
from datetime import datetime, timezone # Asegurarse que timezone esté importado si se usa
from typing import Optional, List, TYPE_CHECKING, Any, ClassVar, Dict # Añadido ClassVar y Dict
from decimal import Decimal # Para campos numéricos precisos

from sqlmodel import Field, SQLModel, Relationship # Añadido Relationship
from sqlalchemy import Column, Enum as SAEnum, CheckConstraint, UniqueConstraint 
# text ya no es necesario aquí para los campos de auditoría
# from sqlalchemy import text 

# --- Importar los mixins correctos desde .common ---
from .common import SQLModelTimestamp, EstadoItem # <--- CORREGIDO

# --- Importar el Enum desde schemas.common ---
from schemas.common import TipoParametroEnum 

# Para referencias adelantadas en relaciones
if TYPE_CHECKING:
    from .modelo import ModeloNeumatico
    from .almacen import Almacen
    from .usuario import Usuario # Si se definen relaciones explícitas para creador/actualizador


# Definir una clase base para los campos específicos de ParametroInventario
class ParametroInventarioBase(SQLModel):
    # FK a modelos_neumatico (NULL si es global)
    modelo_id: Optional[uuid.UUID] = Field(default=None, foreign_key="modelos_neumatico.id", index=True)
    # FK a almacenes (NULL si es global)
    almacen_id: Optional[uuid.UUID] = Field(default=None, foreign_key="almacenes.id", index=True)

    tipo_parametro: TipoParametroEnum = Field(
        sa_column=Column(SAEnum(TipoParametroEnum, name="tipo_parametro_inventario_enum"), nullable=False, index=True) # Añadido name al SAEnum
    )

    # Valor numérico del parámetro (ej: mm, unidades, km, años)
    # Usar Decimal para precisión si es necesario, o float
    valor_numerico: Optional[Decimal] = Field(default=None, decimal_places=2) # Ejemplo con Decimal
    # valor_numerico: Optional[float] = Field(default=None) # Alternativa con float
    
    # Valor de texto (si algún parámetro lo necesita)
    valor_texto: Optional[str] = Field(default=None, max_length=255) # Añadido max_length
    
    unidad: Optional[str] = Field(default=None, max_length=50, description="Unidad del valor_numerico, ej: mm, psi, km, uds") # Campo añadido
    descripcion: Optional[str] = Field(default=None, max_length=255) # Campo notas renombrado y con max_length
    
    # El campo 'activo' y los campos de timestamp vendrán de EstadoItem y SQLModelTimestamp

# Modelo de tabla ParametroInventario, heredando los campos de auditoría y estado
class ParametroInventario(SQLModelTimestamp, EstadoItem, ParametroInventarioBase, table=True):
    __tablename__ = "parametros_inventario"
    __table_args__ = (
        # Constraint único para combinación modelo/almacen/tipo
        UniqueConstraint('modelo_id', 'almacen_id', 'tipo_parametro', name='uq_parametro_inventario_unico'), # Nombre de constraint ajustado
    )

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, index=True) # Añadido index=True

    # Los campos 'activo', 'fecha_baja', 'creado_en', 'actualizado_en', 
    # 'creado_por', 'actualizado_por' son heredados de SQLModelTimestamp y EstadoItem.
    # Ya no es necesario definirlos explícitamente aquí.

    # --- Relaciones ---
    modelo: Optional["ModeloNeumatico"] = Relationship(back_populates="parametros_inventario")
    almacen: Optional["Almacen"] = Relationship() # back_populates="parametros_inventario" si Almacen tiene esta relación

    # Si quieres relacionar explícitamente con el usuario creador/actualizador más allá
    # de los campos UUID heredados de SQLModelTimestamp:
    # creador: Optional["Usuario"] = Relationship(
    #     sa_relationship_kwargs={'foreign_keys': '[ParametroInventario.creado_por]'}
    # )
    # actualizador: Optional["Usuario"] = Relationship(
    #     sa_relationship_kwargs={'foreign_keys': '[ParametroInventario.actualizado_por]'}
    # )

    # Configuración moderna usando model_config con ConfigDict
    model_config: ClassVar[Dict[str, Any]] = ConfigDict(
        from_attributes=True  # Reemplaza orm_mode=True
    )
