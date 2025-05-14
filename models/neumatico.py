# gesneu_api2/models/neumatico.py
import uuid
from pydantic import ConfigDict
import uuid
from datetime import date, datetime, timezone 
from typing import Optional, List, TYPE_CHECKING , ClassVar, Dict, Any

from sqlmodel import Field, SQLModel, Relationship 
from sqlalchemy import Column, text, TIMESTAMP, ForeignKey, Numeric, Date
from sqlalchemy import Enum as SAEnum

# --- Importar Base y Enum desde schemas ---
# NeumaticoSchemaBase (de schemas.neumatico) ya es un SQLModel.
# Lo usaremos como la base para nuestra tabla Neumatico.
from schemas.neumatico import NeumaticoBase as NeumaticoSchemaBase 
from schemas.common import EstadoNeumaticoEnum 

# Para referencias adelantadas en relaciones
if TYPE_CHECKING:
    from .modelo import ModeloNeumatico
    from .proveedor import Proveedor
    from .vehiculo import Vehiculo
    from .posicion_neumatico import PosicionNeumatico
    from .almacen import Almacen
    from .motivo_desecho import MotivoDesecho
    from .usuario import Usuario
    from .evento_neumatico import EventoNeumatico


# La clase Neumatico hereda de NeumaticoSchemaBase (que ya es un SQLModel)
# y se define como una tabla.
class Neumatico(NeumaticoSchemaBase, table=True): # <--- CORREGIDO: Quitado SQLModel explícito de aquí
    __tablename__ = "neumaticos"
    # __table_args__ = {'extend_existing': True} # Usar con precaución

    # --- Clave Primaria ---
    # NeumaticoSchemaBase (de schemas/neumatico.py) NO define 'id'.
    # Lo definimos aquí para la tabla.
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False)

    # --- Campos Heredados de NeumaticoSchemaBase ---
    # numero_serie: Optional[str]
    # dot: Optional[str]
    # modelo_id: uuid.UUID 
    # fecha_compra: date
    # fecha_fabricacion: Optional[date]
    # costo_compra: Optional[float]
    # moneda_compra: Optional[str]
    # proveedor_compra_id: Optional[uuid.UUID]
    
    # --- Asegurar que los campos FK de NeumaticoSchemaBase se definan correctamente para SQLModel ---
    # En NeumaticoSchemaBase (schemas/neumatico.py), modelo_id y proveedor_compra_id ya tienen
    # el argumento foreign_key, lo cual es correcto para SQLModel.
    # modelo_id: uuid.UUID = Field(foreign_key="modelos_neumatico.id")
    # proveedor_compra_id: Optional[uuid.UUID] = Field(default=None, foreign_key="proveedores.id")


    # --- Campos específicos de la tabla Neumatico que no están en NeumaticoSchemaBase ---
    estado_actual: EstadoNeumaticoEnum = Field(
        default=EstadoNeumaticoEnum.EN_STOCK, 
        sa_column=Column(SAEnum(EstadoNeumaticoEnum, name="estado_neumatico_enum", create_type=False),
                         nullable=False,
                         default=EstadoNeumaticoEnum.EN_STOCK) 
    )
    ubicacion_actual_vehiculo_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="vehiculos.id", index=True, nullable=True
    )
    ubicacion_actual_posicion_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="posiciones_neumatico.id", index=True, nullable=True
    )
    ubicacion_almacen_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="almacenes.id", index=True, nullable=True
    )

    km_instalacion: Optional[int] = Field(default=None, nullable=True)
    fecha_instalacion: Optional[date] = Field(default=None, sa_column=Column(Date, nullable=True))

    fecha_ultimo_evento: Optional[datetime] = Field(
        default=None, 
        sa_column=Column(TIMESTAMP(timezone=True), nullable=True)
    )
    # profundidad_inicial_mm ya está en NeumaticoCreate (schema), ¿debería estar aquí también?
    # Si es un campo de la tabla, sí. Si solo es para la creación, no.
    # Asumiendo que es un campo de la tabla:
    profundidad_inicial_mm: Optional[float] = Field( 
        default=None, sa_column=Column(Numeric(5, 2), nullable=True)
    )
    kilometraje_acumulado: int = Field(default=0, nullable=False)
    reencauches_realizados: int = Field(default=0, nullable=False)
    vida_actual: int = Field(default=1, nullable=False)
    es_reencauchado: bool = Field(default=False, nullable=False)
    fecha_desecho: Optional[date] = Field(default=None, sa_column=Column(Date, nullable=True))
    motivo_desecho_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="motivos_desecho.id", nullable=True
    )

    # Campos de auditoría 
    # Si queremos consistencia, Neumatico también debería heredar de SQLModelTimestamp y EstadoItem
    # como otros modelos, y estos campos se definirían allí.
    # Por ahora, se mantienen como estaban definidos explícitamente aquí.
    creado_en: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), 
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")) 
    )
    creado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id", nullable=True)
    
    actualizado_en: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc), 
        sa_column=Column(TIMESTAMP(timezone=True), nullable=True, onupdate=lambda: datetime.now(timezone.utc))
    )
    actualizado_por: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id", nullable=True)

    # --- Relaciones ---
    # 'modelo_id' y 'proveedor_compra_id' son campos FK definidos en NeumaticoSchemaBase.
    # Las relaciones correspondientes se definen aquí.
    modelo: Optional["ModeloNeumatico"] = Relationship(back_populates="neumaticos") 
    proveedor_compra: Optional["Proveedor"] = Relationship(back_populates="neumaticos_comprados") 
    
    vehiculo_instalado: Optional["Vehiculo"] = Relationship(
        sa_relationship_kwargs={'foreign_keys': '[Neumatico.ubicacion_actual_vehiculo_id]'},
        back_populates="neumaticos_instalados"
    )
    posicion_instalado: Optional["PosicionNeumatico"] = Relationship(
         sa_relationship_kwargs={'foreign_keys': '[Neumatico.ubicacion_actual_posicion_id]'}
        # back_populates="neumatico_actual" # Asegurar que exista en PosicionNeumatico
    )
    almacen_actual: Optional["Almacen"] = Relationship(
        sa_relationship_kwargs={'foreign_keys': '[Neumatico.ubicacion_almacen_id]'}
        # back_populates="neumaticos_en_almacen" # Asegurar que exista en Almacen
    )
    motivo_desecho: Optional["MotivoDesecho"] = Relationship(back_populates="neumaticos_desechados")

    creador: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={'foreign_keys': '[Neumatico.creado_por]'}
        # back_populates="neumaticos_creados_por_mi" # Ejemplo, si Usuario tiene esta relación
    )
    actualizador: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={'foreign_keys': '[Neumatico.actualizado_por]'}
        # back_populates="neumaticos_actualizados_por_mi" # Ejemplo
    )
    
    eventos_neumatico: List["EventoNeumatico"] = Relationship(back_populates="neumatico")

    # Configuración moderna usando model_config con ConfigDict
        

    model_config: ClassVar[Dict[str, Any]] = ConfigDict(
        from_attributes=True
    )