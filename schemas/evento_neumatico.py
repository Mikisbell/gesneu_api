# schemas/evento_neumatico.py
import uuid
from datetime import date, datetime, timezone # Asegurar todos los necesarios
from typing import Optional, Dict, Any
from enum import Enum

from pydantic import BaseModel, EmailStr, field_validator, ValidationInfo
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

# Importar Enums (Ajusta si están en schemas/common.py)
from schemas.common import EstadoNeumaticoEnum, TipoEventoNeumaticoEnum
# Importar Enums (Asumiendo que siguen en models.py principal o los moviste a schemas/common.py)
class EventoNeumaticoBase(SQLModel):
    # FKs con sa_column
    neumatico_id: uuid.UUID = Field(sa_column=Column(ForeignKey("neumaticos.id"), index=True, nullable=False))
    usuario_id: Optional[uuid.UUID] = Field(default=None, sa_column=Column(ForeignKey("usuarios.id"), index=True, nullable=False))
    vehiculo_id: Optional[uuid.UUID] = Field(default=None, sa_column=Column(ForeignKey("vehiculos.id"), index=True, nullable=True))
    posicion_id: Optional[uuid.UUID] = Field(default=None, sa_column=Column(ForeignKey("posiciones_neumatico.id"), index=True, nullable=True))
    proveedor_servicio_id: Optional[uuid.UUID] = Field(default=None, sa_column=Column(ForeignKey("proveedores.id"), index=True, nullable=True))
    motivo_desecho_id_evento: Optional[uuid.UUID] = Field(default=None, sa_column=Column(ForeignKey("motivos_desecho.id"), index=True, nullable=True))
    # ENUM tipo_evento mapeado
    tipo_evento: TipoEventoNeumaticoEnum = Field(sa_column=Column(SAEnum(TipoEventoNeumaticoEnum, name="tipo_evento_neumatico_enum", create_type=False), nullable=False))
    # ENUM destino_desmontaje mapeado
    destino_desmontaje: Optional[EstadoNeumaticoEnum] = Field(default=None, sa_column=Column(SAEnum(EstadoNeumaticoEnum, name="estado_neumatico_enum", create_type=False), nullable=True))
    # Otros campos
    odometro_vehiculo_en_evento: Optional[int] = Field(default=None, ge=0)
    profundidad_remanente_mm: Optional[float] = Field(default=None, ge=0)
    presion_psi: Optional[float] = Field(default=None, gt=0)
    costo_evento: Optional[float] = Field(default=None, ge=0)
    moneda_costo: Optional[str] = Field(default="PEN", max_length=3)
    notas: Optional[str] = None
    profundidad_post_reencauche_mm: Optional[float] = Field(default=None, gt=0)
    datos_evento: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    relacion_evento_anterior: Optional[uuid.UUID] = Field(default=None, sa_column=Column(ForeignKey("eventos_neumaticos.id"), nullable=True))


class EventoNeumaticoCreate(EventoNeumaticoBase):
    neumatico_id: uuid.UUID
    tipo_evento: TipoEventoNeumaticoEnum
    destino_desmontaje: Optional[EstadoNeumaticoEnum] = None

    # --- Validador 1: Formato Corregido ---
    @field_validator('destino_desmontaje', mode='before')
    def check_destino_desmontaje(cls, v: Optional[str], info: ValidationInfo):
        enum_member = None
        tipo = info.data.get('tipo_evento') # Mejor en líneas separadas
        if v is not None:
            try: # Bloque try indentado
                enum_member = EstadoNeumaticoEnum(v)
            except ValueError: # Bloque except indentado
                raise ValueError(f"Valor inválido para destino_desmontaje: {v}")

        # Convertir tipo a Enum para comparación segura
        tipo_enum = None
        if isinstance(tipo, str):
             try: tipo_enum = TipoEventoNeumaticoEnum(tipo)
             except ValueError: raise ValueError(f"Tipo de evento inválido: {tipo}")
        elif isinstance(tipo, Enum):
            tipo_enum = tipo

        if tipo_enum == TipoEventoNeumaticoEnum.DESMONTAJE and enum_member is None:
            raise ValueError('destino_desmontaje es requerido para eventos DESMONTAJE')
        return enum_member

    # --- Validador 2: Formato Corregido ---
    @field_validator('motivo_desecho_id_evento', mode='before')
    def check_motivo_desecho(cls, v: Optional[str | uuid.UUID], info: ValidationInfo):
        # Obtener datos relevantes del contexto
        tipo_evento_val = info.data.get('tipo_evento')
        destino_val = info.data.get('destino_desmontaje')

        # Salir temprano si falta información esencial para la lógica
        if tipo_evento_val is None:
            return v # No podemos validar sin el tipo de evento

        # Convertir tipo_evento a Enum
        tipo_enum: Optional[TipoEventoNeumaticoEnum] = None
        if isinstance(tipo_evento_val, str):
            try: tipo_enum = TipoEventoNeumaticoEnum(tipo_evento_val)
            except ValueError: return v # Dejar que Pydantic falle por tipo_evento inválido
        elif isinstance(tipo_evento_val, TipoEventoNeumaticoEnum):
            tipo_enum = tipo_evento_val
        else:
             return v # Tipo inesperado

        # Convertir destino_desmontaje a Enum si existe
        destino_enum: Optional[EstadoNeumaticoEnum] = None
        if isinstance(destino_val, str):
            try: destino_enum = EstadoNeumaticoEnum(destino_val)
            except ValueError: pass # Ignorar destino inválido aquí
        elif isinstance(destino_val, EstadoNeumaticoEnum):
            destino_enum = destino_val

        # Validar/Convertir motivo_uuid
        motivo_uuid: Optional[uuid.UUID] = None
        if isinstance(v, str):
            try:
                motivo_uuid = uuid.UUID(v)
            except ValueError:
                raise ValueError(f"Formato UUID inválido para motivo_desecho_id_evento: {v}")
        elif isinstance(v, uuid.UUID):
            motivo_uuid = v
        elif v is not None:
             raise ValueError(f"Tipo inválido para motivo_desecho_id_evento: {type(v)}")

        # Verificar requerimiento
        is_evento_desecho = (tipo_enum == TipoEventoNeumaticoEnum.DESECHO)
        is_desmontaje_a_desecho = (tipo_enum == TipoEventoNeumaticoEnum.DESMONTAJE and destino_enum == EstadoNeumaticoEnum.DESECHADO)

        if (is_evento_desecho or is_desmontaje_a_desecho) and motivo_uuid is None:
            raise ValueError('motivo_desecho_id_evento (UUID válido) es requerido para eventos DESECHO o DESMONTAJE a DESECHADO')

        return motivo_uuid

    # --- Validador 3: Formato Corregido ---
    @field_validator('profundidad_post_reencauche_mm', mode='before')
    def check_profundidad_reencauche(cls, v: Optional[float], info: ValidationInfo):
        tipo_evento_val = info.data.get('tipo_evento')
        if tipo_evento_val is None: return v

        # Convertir tipo_evento a Enum
        tipo_enum: Optional[TipoEventoNeumaticoEnum] = None
        if isinstance(tipo_evento_val, str):
            try: tipo_enum = TipoEventoNeumaticoEnum(tipo_evento_val)
            except ValueError: return v
        elif isinstance(tipo_evento_val, TipoEventoNeumaticoEnum):
            tipo_enum = tipo_evento_val
        else:
             return v # Tipo inesperado

        # Verificar requerimiento
        if tipo_enum == TipoEventoNeumaticoEnum.REENCAUCHE_SALIDA and v is None:
            raise ValueError('profundidad_post_reencauche_mm es requerida para eventos REENCAUCHE_SALIDA')

        # Verificar > 0
        if v is not None and v <= 0:
             raise ValueError('profundidad_post_reencauche_mm debe ser un valor positivo')
        return v

class EventoNeumaticoRead(EventoNeumaticoBase):
    id: uuid.UUID
    timestamp_evento: datetime
    creado_en: datetime
    usuario_id: uuid.UUID



