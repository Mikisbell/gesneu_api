# gesneu_api2/models/modelo.py
import uuid
from datetime import datetime, timezone # Asegurarse que timezone esté importado si se usa
from typing import Optional, List, TYPE_CHECKING, Any # Añadido List, TYPE_CHECKING, Any
from decimal import Decimal # Para campos numéricos precisos

from sqlmodel import Field, SQLModel, Relationship # Añadido Relationship
# Column, ForeignKey, text ya no son necesarios aquí para los campos de auditoría
# from sqlalchemy import Column, ForeignKey, text 

# --- Importar los mixins correctos desde .common ---
from .common import SQLModelTimestamp, EstadoItem # <--- CORREGIDO

# Para referencias adelantadas en relaciones
if TYPE_CHECKING:
    from .fabricante import FabricanteNeumatico # Para la relación con fabricante
    from .neumatico import Neumatico # Para la relación con neumáticos de este modelo
    from .parametro_inventario import ParametroInventario # Para parámetros de este modelo
    from .usuario import Usuario # Si se definen relaciones explícitas para creador/actualizador


# Definir una clase base para los campos específicos de ModeloNeumatico
class ModeloNeumaticoBase(SQLModel):
    fabricante_id: uuid.UUID = Field(foreign_key="fabricantes_neumatico.id", index=True) # Añadido index
    nombre_modelo: str = Field(max_length=100, index=True) # Añadido index y max_length
    
    # Campos que estaban en el modelo original, ajustados
    medida: Optional[str] = Field(default=None, max_length=50) # Ejemplo: 295/80R22.5
    descripcion: Optional[str] = Field(default=None, max_length=255) # Campo añadido para más detalles
    
    ancho_seccion_mm: Optional[int] = Field(default=None, gt=0, description="Ancho de sección en milímetros")
    relacion_aspecto: Optional[int] = Field(default=None, gt=0, description="Relación de aspecto (perfil)")
    tipo_construccion: Optional[str] = Field(default=None, max_length=20, description="Ej: Radial, Diagonal")
    diametro_llanta_pulgadas: Optional[Decimal] = Field(default=None, gt=0, decimal_places=1, description="Diámetro de la llanta en pulgadas")
    
    indice_carga: Optional[str] = Field(default=None, max_length=10) # Puede ser un número o un código
    indice_velocidad: Optional[str] = Field(default=None, max_length=5) # Código de velocidad
    
    profundidad_original_mm: Optional[Decimal] = Field(default=None, gt=0, decimal_places=2) # Usar Decimal para precisión
    presion_recomendada_psi: Optional[float] = Field(default=None, gt=0)
    
    permite_reencauche: bool = Field(default=False)
    reencauches_maximos: Optional[int] = Field(default=0, ge=0) # ge=0 para permitir 0
    
    # El campo 'activo' y los campos de timestamp vendrán de EstadoItem y SQLModelTimestamp

# Modelo de tabla ModeloNeumatico, heredando los campos de auditoría y estado
class ModeloNeumatico(SQLModelTimestamp, EstadoItem, ModeloNeumaticoBase, table=True):
    __tablename__ = "modelos_neumatico"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # Los campos 'activo', 'fecha_baja', 'creado_en', 'actualizado_en', 
    # 'creado_por', 'actualizado_por' son heredados de SQLModelTimestamp y EstadoItem.
    # Ya no es necesario definirlos explícitamente aquí.

    # --- Relaciones ---
    fabricante: Optional["FabricanteNeumatico"] = Relationship(back_populates="modelos")
    
    # Un modelo puede estar asociado a muchos neumáticos
    neumaticos: List["Neumatico"] = Relationship(back_populates="modelo")
    
    # Un modelo puede tener muchos parámetros de inventario asociados
    parametros_inventario: List["ParametroInventario"] = Relationship(back_populates="modelo")

    # Si quieres relacionar explícitamente con el usuario creador/actualizador más allá
    # de los campos UUID heredados de SQLModelTimestamp:
    # creador: Optional["Usuario"] = Relationship(
    #     sa_relationship_kwargs={'foreign_keys': '[ModeloNeumatico.creado_por]'}
    # )
    # actualizador: Optional["Usuario"] = Relationship(
    #     sa_relationship_kwargs={'foreign_keys': '[ModeloNeumatico.actualizado_por]'}
    # )

    class Config:
        from_attributes = True # Para Pydantic V2
        # orm_mode = True # Para Pydantic V1
