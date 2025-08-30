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
# Esquemas para el modelo Fabricante
# ---------------------------------------------------------------------------

class FabricanteBase(BaseModel):
    """Esquema base para Fabricante, con campos comunes."""
    nombre: str = Field(..., max_length=100)
    codigo_abreviado: Optional[str] = Field(None, max_length=10)
    pais_origen: Optional[str] = Field(None, max_length=50)
    sitio_web: Optional[str] = Field(None, max_length=255)

class FabricanteCreate(FabricanteBase):
    """Esquema para la creación de un nuevo Fabricante."""
    pass

class FabricanteUpdate(BaseModel):
    """Esquema para actualizar un Fabricante. Todos los campos son opcionales."""
    nombre: Optional[str] = Field(None, max_length=100)
    codigo_abreviado: Optional[str] = Field(None, max_length=10)
    pais_origen: Optional[str] = Field(None, max_length=50)
    sitio_web: Optional[str] = Field(None, max_length=255)
    activo: Optional[bool] = None

class FabricanteRead(FabricanteBase):
    id: UUID
    activo: bool
    creado_en: datetime
    actualizado_en: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------------------------------------------
# Esquemas para el modelo ModeloNeumatico
# ---------------------------------------------------------------------------

class ModeloNeumaticoBase(BaseModel):
    nombre_modelo: str = Field(..., max_length=100)
    medida: str = Field(..., max_length=20)
    indice_carga: Optional[str] = Field(None, max_length=5)
    indice_velocidad: Optional[str] = Field(None, max_length=2)
    profundidad_original_mm: Decimal = Field(..., decimal_places=2, max_digits=5)
    presion_recomendada_psi: Optional[Decimal] = Field(None, decimal_places=2, max_digits=5)
    permite_reencauche: bool = False
    reencauches_maximos: int = 0
    patron_dibujo: Optional[str] = Field(None, max_length=50)
    tipo_servicio: Optional[str] = Field(None, max_length=50)
    fabricante_id: UUID
    
    posicion_uso_recomendada: Optional[TipoEjeEnum] = None
    diseno_predominante_para_eje: Optional[TipoEjeEnum] = None
    vida_util_teorica_km: Optional[int] = None
    profundidad_minima_retiro_mm: Decimal = Field(Decimal('1.60'), decimal_places=2, max_digits=5)
    tasa_desgaste_esperada_mm_km: Optional[Decimal] = Field(
        None, decimal_places=8, max_digits=10, 
        description="Tasa de desgaste esperada en mm por kilómetro"
    )
    frecuencia_inspeccion_km: int = 5000
    max_vidas_utiles: int = 5
    porcentaje_desgaste_por_vida: Decimal = Field(
        Decimal('10.00'), decimal_places=2, max_digits=5,
        description="Porcentaje de desgaste por vida útil"
    )

class ModeloNeumaticoCreate(ModeloNeumaticoBase):
    pass

class ModeloNeumaticoUpdate(BaseModel):
    nombre_modelo: Optional[str] = Field(None, max_length=100)
    medida: Optional[str] = Field(None, max_length=20)
    indice_carga: Optional[str] = Field(None, max_length=5)
    indice_velocidad: Optional[str] = Field(None, max_length=2)
    profundidad_original_mm: Optional[Decimal] = Field(None, decimal_places=2, max_digits=5)
    presion_recomendada_psi: Optional[Decimal] = Field(None, decimal_places=2, max_digits=5)
    permite_reencauche: Optional[bool] = None
    reencauches_maximos: Optional[int] = None
    patron_dibujo: Optional[str] = Field(None, max_length=50)
    tipo_servicio: Optional[str] = Field(None, max_length=50)
    fabricante_id: Optional[UUID] = None
    posicion_uso_recomendada: Optional[TipoEjeEnum] = None
    diseno_predominante_para_eje: Optional[TipoEjeEnum] = None
    vida_util_teorica_km: Optional[int] = None
    profundidad_minima_retiro_mm: Optional[Decimal] = Field(None, decimal_places=2, max_digits=5)
    tasa_desgaste_esperada_mm_km: Optional[Decimal] = Field(
        None, decimal_places=8, max_digits=10
    )
    frecuencia_inspeccion_km: Optional[int] = None
    max_vidas_utiles: Optional[int] = None
    porcentaje_desgaste_por_vida: Optional[Decimal] = Field(
        None, decimal_places=2, max_digits=5
    )
    activo: Optional[bool] = None

class ModeloNeumaticoRead(ModeloNeumaticoBase):
    id: UUID
    activo: bool
    creado_en: datetime
    creado_por: Optional[UUID] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = None
    fabricante: FabricanteRead
    
    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------------------------------------------
# Esquemas para Proveedor
# ---------------------------------------------------------------------------

class ProveedorBase(BaseModel):
    """Esquema base para Proveedor."""
    ruc: str = Field(..., max_length=20, description="RUC del proveedor")
    razon_social: str = Field(..., max_length=200, description="Razón social del proveedor")
    nombre_comercial: Optional[str] = Field(None, max_length=200, description="Nombre comercial del proveedor")
    direccion: Optional[str] = Field(None, description="Dirección del proveedor")
    telefono: Optional[str] = Field(None, max_length=20, description="Teléfono de contacto")
    email: Optional[str] = Field(None, max_length=100, description="Correo electrónico de contacto")
    contacto: Optional[str] = Field(None, max_length=100, description="Persona de contacto")
    tipo: str = Field(..., max_length=50, description="Tipo de proveedor (ej: neumáticos, servicios, etc.)")

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "ruc": "20123456781",
                "razon_social": "PROVEEDOR EJEMPLO S.A.C.",
                "nombre_comercial": "PROVEE EJEMPLO",
                "direccion": "Av. Ejemplo 123",
                "telefono": "+51987654321",
                "email": "contacto@proveedorejemplo.com",
                "contacto": "Juan Pérez",
                "tipo": "NEUMATICOS"
            }
        }
    )

class ProveedorCreate(ProveedorBase):
    """Esquema para la creación de un nuevo proveedor."""
    pass

class ProveedorUpdate(BaseModel):
    """Esquema para actualizar un proveedor existente."""
    ruc: Optional[str] = Field(None, max_length=20, description="RUC del proveedor")
    razon_social: Optional[str] = Field(None, max_length=200, description="Razón social del proveedor")
    nombre_comercial: Optional[str] = Field(None, max_length=200, description="Nombre comercial del proveedor")
    direccion: Optional[str] = Field(None, description="Dirección del proveedor")
    telefono: Optional[str] = Field(None, max_length=20, description="Teléfono de contacto")
    email: Optional[str] = Field(None, max_length=100, description="Correo electrónico de contacto")
    contacto: Optional[str] = Field(None, max_length=100, description="Persona de contacto")
    tipo: Optional[str] = Field(None, max_length=50, description="Tipo de proveedor")
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
    codigo: str = Field(..., max_length=50, description="Código único del parámetro")
    nombre: str = Field(..., max_length=100, description="Nombre descriptivo del parámetro")
    valor: str = Field(..., description="Valor del parámetro")
    descripcion: Optional[str] = Field(None, description="Descripción detallada del parámetro")

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "codigo": "STOCK_MINIMO",
                "nombre": "Stock Mínimo de Neumáticos",
                "valor": "5",
                "descripcion": "Cantidad mínima de neumáticos que debe haber en inventario"
            }
        }
    )

class ParametroInventarioCreate(ParametroInventarioBase):
    """Esquema para la creación de un nuevo parámetro de inventario."""
    pass

class ParametroInventarioUpdate(BaseModel):
    """Esquema para actualizar un parámetro de inventario existente."""
    codigo: Optional[str] = Field(None, max_length=50, description="Código único del parámetro")
    nombre: Optional[str] = Field(None, max_length=100, description="Nombre descriptivo del parámetro")
    valor: Optional[str] = Field(None, description="Valor del parámetro")
    descripcion: Optional[str] = Field(None, description="Descripción detallada del parámetro")
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

CatalogoItemCreate = Union[FabricanteCreate, ModeloNeumaticoCreate, ProveedorCreate, MotivoDesechoCreate, AlmacenCreate, ParametroInventarioCreate]


CatalogoItemRead = Union[FabricanteRead, ModeloNeumaticoRead, ProveedorRead, MotivoDesechoRead, AlmacenRead, ParametroInventarioRead]


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