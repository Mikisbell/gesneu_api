#schemas/neumatico.py
import uuid
from datetime import date, datetime
from typing import Optional
from sqlmodel import SQLModel, Field
# Importar Enums (Ajusta ruta si es necesario)
from schemas.common import EstadoNeumaticoEnum, TipoEventoNeumaticoEnum # <-- Existita

class NeumaticoBase(SQLModel):
    numero_serie: Optional[str] = Field(default=None, index=True)
    dot: Optional[str] = Field(default=None)
    modelo_id: uuid.UUID = Field(foreign_key="modelos_neumatico.id")
    fecha_compra: date
    fecha_fabricacion: Optional[date] = None
    costo_compra: Optional[float] = Field(default=None, ge=0)
    moneda_compra: Optional[str] = Field(default="PEN", max_length=3)
    proveedor_compra_id: Optional[uuid.UUID] = Field(default=None, foreign_key="proveedores.id")

class NeumaticoCreate(NeumaticoBase):
    profundidad_inicial_mm: Optional[float] = Field(default=None, gt=0)

class NeumaticoRead(NeumaticoBase):
    id: uuid.UUID
    estado_actual: EstadoNeumaticoEnum
    ubicacion_actual_vehiculo_id: Optional[uuid.UUID] = None
    ubicacion_actual_posicion_id: Optional[uuid.UUID] = None
    fecha_ultimo_evento: Optional[datetime] = None
    profundidad_inicial_mm: Optional[float] = None
    kilometraje_acumulado: int
    reencauches_realizados: int
    vida_actual: int
    es_reencauchado: bool
    fecha_desecho: Optional[date] = None
    motivo_desecho_id: Optional[uuid.UUID] = None
    creado_en: datetime
    actualizado_en: Optional[datetime] = None

# --- Modelos para Vistas (Ejemplo) ---
class HistorialNeumaticoItem(SQLModel):
    # Formato limpio
    evento_id: uuid.UUID
    tipo_evento: TipoEventoNeumaticoEnum
    timestamp_evento: datetime
    usuario_registra: Optional[str] = None
    placa: Optional[str] = None
    numero_economico: Optional[str] = None
    codigo_posicion: Optional[str] = None
    odometro_vehiculo_en_evento: Optional[int] = None
    profundidad_remanente_mm: Optional[float] = None
    presion_psi: Optional[float] = None
    costo_evento: Optional[float] = None
    moneda_costo: Optional[str] = None
    proveedor_servicio: Optional[str] = None
    motivo_desecho: Optional[str] = None
    notas: Optional[str] = None

class NeumaticoInstaladoItem(SQLModel):
    # Formato limpio
    neumatico_id: uuid.UUID
    numero_serie: Optional[str] = None
    dot: Optional[str] = None
    nombre_modelo: Optional[str] = None
    medida: Optional[str] = None
    fabricante: Optional[str] = None
    placa: Optional[str] = None
    numero_economico: Optional[str] = None
    tipo_vehiculo: Optional[str] = None
    codigo_posicion: Optional[str] = None
    profundidad_actual_mm: Optional[float] = None
    presion_actual_psi: Optional[float] = None
    kilometraje_neumatico_acumulado: Optional[int] = None
    vida_actual: Optional[int] = None
    reencauches_realizados: Optional[int] = None
