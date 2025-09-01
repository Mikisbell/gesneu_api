from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Union, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from enum import Enum, auto

# Enums para validación
class TipoEjeEnum(str, Enum):
    DIRECCION = "DIRECCION"
    TRACCION = "TRACCION"
    ARRASTRE = "ARRASTRE"
    ELEVADOR = "ELEVADOR"
    RETRACTIL = "RETRACTIL"
    OTRO = "OTRO"

class TipoEventoNeumaticoEnum(str, Enum):
    INSTALACION = "INSTALACION"
    DESMONTAJE = "DESMONTAJE"
    INSPECCION = "INSPECCION"
    REPARACION = "REPARACION"
    ROTACION = "ROTACION"
    REENCAUCHE_ENTRADA = "REENCAUCHE_ENTRADA"
    REENCAUCHE_SALIDA = "REENCAUCHE_SALIDA"
    ALMACENAMIENTO = "ALMACENAMIENTO"
    DESECHO = "DESECHO"
    AJUSTE = "AJUSTE"
    OTRO = "OTRO"

class EstadoNeumaticoEnum(str, Enum):
    NUEVO = "NUEVO"
    EN_USO = "EN_USO"
    ALMACENADO = "ALMACENADO"
    EN_REPARACION = "EN_REPARACION"
    EN_REENCAUCHE = "EN_REENCAUCHE"
    DESECHADO = "DESECHADO"
    BAJA = "BAJA"
    VENDIDO = "VENDIDO"
    ROBADO = "ROBADO"
    PERDIDO = "PERDIDO"
    DONADO = "DONADO"
    DANADO = "DANADO"
    EN_TRANSITO = "EN_TRANSITO"
    EN_REVISION = "EN_REVISION"

# ---------------------------------------------------------------------------
# Esquemas para Proveedor
# ---------------------------------------------------------------------------

class ProveedorBase(BaseModel):
    """Esquema base para Proveedor."""
    nombre: str = Field(..., max_length=150, description="Nombre completo del proveedor")

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "nombre": "PROVEEDOR EJEMPLO S.A.C."
            }
        }
    )

class ProveedorCreate(ProveedorBase):
    """Esquema para la creación de un nuevo proveedor."""
    pass

class ProveedorUpdate(BaseModel):
    """Esquema para actualizar un proveedor existente."""
    nombre: Optional[str] = Field(None, max_length=150, description="Nombre completo del proveedor")
    activo: Optional[bool] = Field(None, description="Indica si el proveedor está activo")

class ProveedorRead(ProveedorBase):
    """Esquema para leer los datos de un proveedor."""
    id: UUID
    activo: bool
    creado_en: datetime
    creado_por: Optional[UUID] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------------------------------------------
# Esquemas para MotivoDesecho
# ---------------------------------------------------------------------------

class MotivoDesechoBase(BaseModel):
    """Esquema base para MotivoDesecho."""
    codigo: str = Field(..., max_length=20, description="Código único del motivo de desecho")
    descripcion: str = Field(..., max_length=255, description="Descripción detallada del motivo")

class MotivoDesechoCreate(MotivoDesechoBase):
    """Esquema para la creación de un nuevo motivo de desecho."""
    pass

class MotivoDesechoUpdate(BaseModel):
    """Esquema para actualizar un motivo de desecho existente."""
    codigo: Optional[str] = Field(None, max_length=20, description="Código único del motivo de desecho")
    descripcion: Optional[str] = Field(None, max_length=255, description="Descripción detallada del motivo")
    activo: Optional[bool] = Field(None, description="Indica si el motivo está activo o no")

class MotivoDesechoRead(MotivoDesechoBase):
    """Esquema para leer los datos de un motivo de desecho."""
    id: UUID
    activo: bool
    creado_en: datetime
    creado_por: Optional[UUID] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------------------------------------------
# Esquemas para Almacen
# ---------------------------------------------------------------------------

class AlmacenBase(BaseModel):
    """Esquema base para Almacen."""
    codigo: str = Field(..., max_length=20, description="Código único del almacén")
    nombre: str = Field(..., max_length=100, description="Nombre descriptivo del almacén")
    direccion: Optional[str] = Field(None, description="Dirección física del almacén")
    responsable: Optional[str] = Field(None, max_length=200, description="Persona a cargo del almacén")
    telefono: Optional[str] = Field(None, max_length=20, description="Teléfono de contacto del almacén")
    email: Optional[str] = Field(None, max_length=100, description="Correo electrónico de contacto")
    es_principal: bool = Field(False, description="Indica si es el almacén principal")

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "codigo": "ALM-001",
                "nombre": "Almacén Central",
                "direccion": "Av. Principal 123",
                "responsable": "Juan Pérez",
                "telefono": "+51987654321",
                "email": "almacen@empresa.com",
                "es_principal": True
            }
        }
    )

class AlmacenCreate(AlmacenBase):
    """Esquema para la creación de un nuevo almacén."""
    pass

class AlmacenUpdate(BaseModel):
    """Esquema para actualizar un almacén existente."""
    codigo: Optional[str] = Field(None, max_length=20, description="Código único del almacén")
    nombre: Optional[str] = Field(None, max_length=100, description="Nombre descriptivo del almacén")
    direccion: Optional[str] = Field(None, description="Dirección física del almacén")
    responsable: Optional[str] = Field(None, max_length=200, description="Persona a cargo del almacén")
    telefono: Optional[str] = Field(None, max_length=20, description="Teléfono de contacto del almacén")
    email: Optional[str] = Field(None, max_length=100, description="Correo electrónico de contacto")
    es_principal: Optional[bool] = Field(None, description="Indica si es el almacén principal")
    activo: Optional[bool] = Field(None, description="Indica si el almacén está activo")

class AlmacenRead(AlmacenBase):
    """Esquema para leer los datos de un almacén."""
    id: UUID
    activo: bool
    creado_en: datetime
    creado_por: Optional[UUID] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------------------------------------------
# Esquemas para ParametroInventario
# ---------------------------------------------------------------------------

class ParametroInventarioBase(BaseModel):
    """Esquema base para Parámetros de Inventario."""
    parametro_tipo: str = Field(..., max_length=50, description="Tipo de parámetro de inventario")
    modelo_id: UUID = Field(..., description="ID del modelo de neumático asociado")
    ubicacion_almacen_id: Optional[UUID] = Field(None, description="ID de la ubicación del almacén asociado")
    valor_numerico: Optional[Decimal] = Field(None, description="Valor numérico del parámetro")
    valor_texto: Optional[str] = Field(None, description="Valor de texto del parámetro")
    notas: Optional[str] = Field(None, description="Notas adicionales sobre el parámetro")

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "parametro_tipo": "STOCK_MINIMO",
                "modelo_id": "550e8400-e29b-41d4-a716-446655440000",
                "valor_numerico": 5,
                "notas": "Cantidad mínima de neumáticos que debe haber en inventario"
            }
        }
    )

class ParametroInventarioCreate(ParametroInventarioBase):
    """Esquema para la creación de un nuevo parámetro de inventario."""
    pass

class ParametroInventarioUpdate(BaseModel):
    """Esquema para actualizar un parámetro de inventario existente."""
    parametro_tipo: Optional[str] = Field(None, max_length=50, description="Tipo de parámetro de inventario")
    modelo_id: Optional[UUID] = Field(None, description="ID del modelo de neumático asociado")
    ubicacion_almacen_id: Optional[UUID] = Field(None, description="ID de la ubicación del almacén asociado")
    valor_numerico: Optional[Decimal] = Field(None, description="Valor numérico del parámetro")
    valor_texto: Optional[str] = Field(None, description="Valor de texto del parámetro")
    notas: Optional[str] = Field(None, description="Notas adicionales sobre el parámetro")
    activo: Optional[bool] = Field(None, description="Indica si el parámetro está activo")

class ParametroInventarioRead(ParametroInventarioBase):
    """Esquema para leer los datos de un parámetro de inventario."""
    id: UUID
    activo: bool
    creado_en: datetime
    creado_por: Optional[UUID] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------------------------------------------
# Esquemas Polimórficos / Genéricos para el Router
# ---------------------------------------------------------------------------

CatalogoItemCreate = Union[ProveedorCreate, MotivoDesechoCreate, AlmacenCreate, ParametroInventarioCreate]

CatalogoItemRead = Union[ProveedorRead, MotivoDesechoRead, AlmacenRead, ParametroInventarioRead]

class CatalogoItemUpdate(BaseModel):
    """
    Esquema genérico para actualizaciones. La lógica de servicio determinará
    a qué modelo concreto aplicar estos cambios.
    """
    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)
    activo: Optional[bool] = None

# NOTA: Se asume que los esquemas de lectura (Read) para cada tipo de catálogo
# ya incluyen los campos de auditoría (id, activo, creado_en, etc.)
# y que el campo 'nombre' es común a todos para la búsqueda genérica.