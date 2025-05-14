# gesneu_api2/models/common.py
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel # Column y ForeignKey no son necesarios aquí para estos campos
from sqlalchemy import UUID as SQLAlchemyUUID # Importa el UUID genérico de SQLAlchemy
from pydantic import BaseModel # Para PageParams
from enum import Enum # Para los Enums

# Definición de la clase base para timestamps y auditoría
class SQLModelTimestamp(SQLModel):
    creado_en: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    actualizado_en: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
        nullable=False
    )
    # Para los campos de FK en un mixin, es mejor definir el foreign_key y el sa_type directamente en Field,
    # y no usar sa_column, para evitar que el mismo objeto Column sea asignado a múltiples tablas.
    creado_por: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="usuarios.id", # SQLModel usará esto para crear la FK en cada tabla que herede
        nullable=True,
        sa_type=SQLAlchemyUUID(as_uuid=True) # Especifica el tipo de la columna en la BD
    )
    actualizado_por: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="usuarios.id", # SQLModel usará esto para crear la FK en cada tabla que herede
        nullable=True,
        sa_type=SQLAlchemyUUID(as_uuid=True) # Especifica el tipo de la columna en la BD
    )

# Definición de la clase base para borrado lógico
class EstadoItem(SQLModel):
    activo: bool = Field(default=True, nullable=False)
    fecha_baja: Optional[datetime] = Field(default=None, nullable=True)

# Schema base para respuestas paginadas
class PageParams(BaseModel):
    page: int = Field(1, ge=1, description="Número de página")
    size: int = Field(10, ge=1, le=100, description="Tamaño de página")

# Enums comunes
class TipoEventoNeumaticoEnum(str, Enum):
    COMPRA = "COMPRA"
    INSTALACION = "INSTALACION"
    DESMONTAJE = "DESMONTAJE"
    ROTACION = "ROTACION"
    INSPECCION = "INSPECCION"
    REPARACION_ENTRADA = "REPARACION_ENTRADA"
    REPARACION_SALIDA = "REPARACION_SALIDA"
    REENCAUCHE_ENTRADA = "REENCAUCHE_ENTRADA"
    REENCAUCHE_SALIDA = "REENCAUCHE_SALIDA"
    DESECHO = "DESECHO"
    AJUSTE_INVENTARIO = "AJUSTE_INVENTARIO"
    TRANSFERENCIA_UBICACION = "TRANSFERENCIA_UBICACION"

class EstadoNeumaticoEnum(str, Enum):
    NUEVO = "NUEVO"
    EN_ALMACEN = "EN_ALMACEN"
    INSTALADO = "INSTALADO"
    EN_REPARACION = "EN_REPARACION"
    PARA_REENCAUCHE = "PARA_REENCAUCHE"
    REENCAUCHADO = "REENCAUCHADO"
    DESECHADO = "DESECHADO"

class TipoAlertaEnum(str, Enum):
    PRESION_BAJA = "PRESION_BAJA"
    PRESION_ALTA = "PRESION_ALTA"
    PROFUNDIDAD_BAJA = "PROFUNDIDAD_BAJA"
    DESGASTE_IRREGULAR = "DESGASTE_IRREGULAR"
    SOBRECARGA = "SOBRECARGA"
    FIN_VIDA_UTIL_ESTIMADO = "FIN_VIDA_UTIL_ESTIMADO"
    MANTENIMIENTO_PREVENTIVO = "MANTENIMIENTO_PREVENTIVO"
    LIMITE_REENCAUCHES = "LIMITE_REENCAUCHES"
    STOCK_MINIMO = "STOCK_MINIMO"
    STOCK_MAXIMO = "STOCK_MAXIMO"
    OTRO = "OTRO"

class TipoParametroEnum(str, Enum):
    PROFUNDIDAD_MINIMA = "PROFUNDIDAD_MINIMA"
    PRESION_OPTIMA_PSI = "PRESION_OPTIMA_PSI"
    PRESION_MINIMA_PSI = "PRESION_MINIMA_PSI"
    PRESION_MAXIMA_PSI = "PRESION_MAXIMA_PSI"
    KM_MAX_RECOMENDADO_CICLO = "KM_MAX_RECOMENDADO_CICLO"
    DIAS_MAX_USO_CICLO = "DIAS_MAX_USO_CICLO"
    COSTO_REPOSICION_USD = "COSTO_REPOSICION_USD"
    STOCK_MINIMO_UNIDADES = "STOCK_MINIMO_UNIDADES"
    STOCK_MAXIMO_UNIDADES = "STOCK_MAXIMO_UNIDADES"
