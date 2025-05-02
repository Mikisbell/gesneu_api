# schemas/evento_neumatico.py
import uuid
from datetime import date, datetime, timezone
from typing import Optional, Dict, Any
from pydantic import field_validator, ValidationInfo # Quitar BaseModel si no se usa
from sqlmodel import SQLModel, Field # Quitar Column, ForeignKey, SAEnum, JSON si no se usan directamente aquí
from .common import TipoEventoNeumaticoEnum, EstadoNeumaticoEnum

# Schema Base: Para validación y datos comunes de API (SIN table=True)
class EventoNeumaticoBase(SQLModel):
    neumatico_id: uuid.UUID
    # Campos opcionales que pueden venir en la creación o mostrarse en lectura
    usuario_id: Optional[uuid.UUID] = None # Lo asignaremos en el endpoint
    vehiculo_id: Optional[uuid.UUID] = None
    posicion_id: Optional[uuid.UUID] = None
    proveedor_servicio_id: Optional[uuid.UUID] = None
    motivo_desecho_id_evento: Optional[uuid.UUID] = None
    tipo_evento: TipoEventoNeumaticoEnum
    destino_desmontaje: Optional[EstadoNeumaticoEnum] = None
    odometro_vehiculo_en_evento: Optional[int] = Field(default=None, ge=0)
    profundidad_remanente_mm: Optional[float] = Field(default=None, ge=0)
    presion_psi: Optional[float] = Field(default=None, gt=0)
    costo_evento: Optional[float] = Field(default=None, ge=0)
    moneda_costo: Optional[str] = Field(default="PEN", max_length=3)
    notas: Optional[str] = None
    profundidad_post_reencauche_mm: Optional[float] = Field(default=None, gt=0)
    datos_evento: Optional[Dict[str, Any]] = None
    relacion_evento_anterior: Optional[uuid.UUID] = None
    almacen_destino_id: Optional[uuid.UUID] = None

# Schema para Crear: Hereda de Base y añade validadores
class EventoNeumaticoCreate(EventoNeumaticoBase):
    # Hereda todos los campos de EventoNeumaticoBase
    # Los validadores se aplican a los datos de entrada

    # --- Tus Validadores (se mantienen igual) ---
    @field_validator('destino_desmontaje', mode='before')
    def check_destino_desmontaje(cls, v: Optional[str], info: ValidationInfo):
        # Tu lógica... (igual que antes)
        enum_member = None
        tipo_evento_val = info.data.get('tipo_evento')
        if v is not None:
            try: enum_member = EstadoNeumaticoEnum(v)
            except ValueError: raise ValueError(f"Valor inválido para destino_desmontaje: {v}")
        tipo_enum = None
        if isinstance(tipo_evento_val, str):
            try: tipo_enum = TipoEventoNeumaticoEnum(tipo_evento_val)
            except ValueError: pass # Dejar que la validación de tipo_evento lo maneje
        elif isinstance(tipo_evento_val, TipoEventoNeumaticoEnum): tipo_enum = tipo_evento_val
        if tipo_enum == TipoEventoNeumaticoEnum.DESMONTAJE and enum_member is None:
            raise ValueError('destino_desmontaje es requerido para eventos de tipo DESMONTAJE')
        return enum_member # Devuelve el Enum o None

    @field_validator('motivo_desecho_id_evento', mode='before')
    def check_motivo_desecho(cls, v: Optional[str | uuid.UUID], info: ValidationInfo):
        # Tu lógica... (igual que antes)
        motivo_uuid: Optional[uuid.UUID] = None
        if isinstance(v, str):
             try: motivo_uuid = uuid.UUID(v)
             except ValueError: raise ValueError("motivo_desecho_id_evento debe ser un UUID válido")
        elif isinstance(v, uuid.UUID): motivo_uuid = v

        tipo_evento_val = info.data.get('tipo_evento')
        destino_val = info.data.get('destino_desmontaje')
        tipo_enum = None
        destino_enum = None
        if isinstance(tipo_evento_val, str):
            try: tipo_enum = TipoEventoNeumaticoEnum(tipo_evento_val)
            except ValueError: pass
        elif isinstance(tipo_evento_val, TipoEventoNeumaticoEnum): tipo_enum = tipo_evento_val

        if isinstance(destino_val, str):
            try: destino_enum = EstadoNeumaticoEnum(destino_val)
            except ValueError: pass
        elif isinstance(destino_val, EstadoNeumaticoEnum): destino_enum = destino_val

        is_evento_desecho = (tipo_enum == TipoEventoNeumaticoEnum.DESECHO)
        is_desmontaje_a_desecho = (tipo_enum == TipoEventoNeumaticoEnum.DESMONTAJE and destino_enum == EstadoNeumaticoEnum.DESECHADO)

        if (is_evento_desecho or is_desmontaje_a_desecho) and motivo_uuid is None:
            raise ValueError('motivo_desecho_id_evento es requerido para DESECHO o DESMONTAJE a DESECHADO')
        return motivo_uuid # Devuelve el UUID o None


    @field_validator('profundidad_post_reencauche_mm', mode='before')
    def check_profundidad_reencauche(cls, v: Optional[float], info: ValidationInfo):
        # Tu lógica... (igual que antes)
        tipo_evento_val = info.data.get('tipo_evento')
        tipo_enum = None
        if isinstance(tipo_evento_val, str):
            try: tipo_enum = TipoEventoNeumaticoEnum(tipo_evento_val)
            except ValueError: pass
        elif isinstance(tipo_evento_val, TipoEventoNeumaticoEnum): tipo_enum = tipo_evento_val

        if tipo_enum == TipoEventoNeumaticoEnum.REENCAUCHE_SALIDA and v is None:
            raise ValueError('profundidad_post_reencauche_mm es requerida para REENCAUCHE_SALIDA')
        if v is not None and v <= 0: raise ValueError('profundidad_post_reencauche_mm debe ser positivo')
        return v

# Schema para Leer: Hereda de Base y añade campos de solo lectura
class EventoNeumaticoRead(EventoNeumaticoBase):
    id: uuid.UUID
    timestamp_evento: datetime
    creado_en: datetime
    # Puedes añadir aquí campos calculados o de relaciones si los necesitas en la respuesta API