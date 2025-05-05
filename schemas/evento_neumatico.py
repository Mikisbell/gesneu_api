# schemas/evento_neumatico.py
# --- CÓDIGO CORREGIDO ---

import uuid
from datetime import date, datetime, timezone
from typing import Optional, Dict, Any
from pydantic import field_validator, ValidationInfo, ConfigDict # <-- AÑADIR ConfigDict
from sqlmodel import SQLModel, Field
from .common import TipoEventoNeumaticoEnum, EstadoNeumaticoEnum # Ajustado a relativo

class EventoNeumaticoBase(SQLModel):
    # Los campos aquí no usaban index/unique directamente en Field,
    # por lo que no necesitan sa_column_kwargs para esos warnings.
    # Los foreign_key los maneja SQLModel.
    neumatico_id: uuid.UUID = Field(foreign_key="neumaticos.id") # FK está bien aquí
    usuario_id: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    vehiculo_id: Optional[uuid.UUID] = Field(default=None, foreign_key="vehiculos.id")
    posicion_id: Optional[uuid.UUID] = Field(default=None, foreign_key="posiciones_neumatico.id")
    proveedor_servicio_id: Optional[uuid.UUID] = Field(default=None, foreign_key="proveedores.id")
    motivo_desecho_id_evento: Optional[uuid.UUID] = Field(default=None, foreign_key="motivos_desecho.id")
    almacen_destino_id: Optional[uuid.UUID] = Field(default=None, foreign_key="almacenes.id") # Asumiendo FK a 'almacenes'

    tipo_evento: TipoEventoNeumaticoEnum
    destino_desmontaje: Optional[EstadoNeumaticoEnum] = Field(default=None) # Añadir default=None
    odometro_vehiculo_en_evento: Optional[int] = Field(default=None, ge=0)
    profundidad_remanente_mm: Optional[float] = Field(default=None, ge=0)
    presion_psi: Optional[float] = Field(default=None, gt=0)
    costo_evento: Optional[float] = Field(default=None, ge=0)
    moneda_costo: Optional[str] = Field(default="PEN", max_length=3)
    notas: Optional[str] = Field(default=None) # Añadir default=None
    profundidad_post_reencauche_mm: Optional[float] = Field(default=None, gt=0)
    # datos_evento necesita sa_column=Column(JSON) en el MODELO, no aquí en el schema base.
    datos_evento: Optional[Dict[str, Any]] = Field(default=None)
    relacion_evento_anterior: Optional[uuid.UUID] = Field(default=None, foreign_key="eventos_neumatico.id")


class EventoNeumaticoCreate(EventoNeumaticoBase):
    # Validadores (se mantienen igual que tu código original)
    @field_validator('destino_desmontaje', mode='before')
    def check_destino_desmontaje(cls, v: Optional[str], info: ValidationInfo):
        # Tu lógica...
        enum_member = None
        tipo_evento_val = info.data.get('tipo_evento')
        if v is not None:
            try: enum_member = EstadoNeumaticoEnum(v)
            except ValueError: raise ValueError(f"Valor inválido para destino_desmontaje: {v}")
        tipo_enum = None
        if isinstance(tipo_evento_val, str):
            try: tipo_enum = TipoEventoNeumaticoEnum(tipo_evento_val)
            except ValueError: pass
        elif isinstance(tipo_evento_val, TipoEventoNeumaticoEnum): tipo_enum = tipo_evento_val
        if tipo_enum == TipoEventoNeumaticoEnum.DESMONTAJE and enum_member is None:
            raise ValueError('destino_desmontaje es requerido para eventos de tipo DESMONTAJE')
        return enum_member

    @field_validator('motivo_desecho_id_evento', mode='before')
    def check_motivo_desecho(cls, v: Optional[str | uuid.UUID], info: ValidationInfo):
        # Tu lógica...
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
        return motivo_uuid

    @field_validator('profundidad_post_reencauche_mm', mode='before')
    def check_profundidad_reencauche(cls, v: Optional[float], info: ValidationInfo):
        # Tu lógica...
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

    # No necesita 'from_attributes'

class EventoNeumaticoRead(EventoNeumaticoBase):
    id: uuid.UUID
    timestamp_evento: datetime # Este campo viene del MODELO, no de la Base
    creado_en: datetime # Este campo viene del MODELO

    # --- CORRECCIÓN: Añadir model_config ---
    model_config = ConfigDict(from_attributes=True)
    # ------------------------------------