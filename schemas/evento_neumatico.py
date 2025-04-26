# schemas/evento_neumatico.py

import uuid
from datetime import date, datetime, timezone
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, EmailStr, field_validator, ValidationInfo
from sqlalchemy import Column, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

# <<<--- AÑADIR ESTA IMPORTACIÓN AQUÍ ---<<<
from models.proveedor import Proveedor
# >>>------------------------------------>>>

# Importar Enums (si aplica)
from schemas.common import EstadoNeumaticoEnum, TipoEventoNeumaticoEnum

# ---------------------------------------------------------------------------
# Clase Base: Define la estructura y las columnas FK
# IMPORTANTE: Esta clase NO debe tener table=True
# ---------------------------------------------------------------------------
class EventoNeumaticoBase(SQLModel):

    # --- Foreign Keys ---
    neumatico_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("neumaticos.id"), index=True, nullable=False)
    )
    usuario_id: Optional[uuid.UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("usuarios.id"), index=True, nullable=False) # Asumiendo que siempre debe haber un usuario
    )
    vehiculo_id: Optional[uuid.UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("vehiculos.id"), index=True, nullable=True)
    )
    posicion_id: Optional[uuid.UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("posiciones_neumatico.id"), index=True, nullable=True)
    )
    proveedor_servicio_id: Optional[uuid.UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("proveedores.id"), index=True, nullable=True)
    )
    motivo_desecho_id_evento: Optional[uuid.UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("motivos_desecho.id"), index=True, nullable=True)
    )

   # --- Otros Campos ---
    tipo_evento: TipoEventoNeumaticoEnum = Field(
        sa_column=Column(SAEnum(TipoEventoNeumaticoEnum, name="tipo_evento_neumatico_enum", create_type=False), nullable=False)
    )
    destino_desmontaje: Optional[EstadoNeumaticoEnum] = Field(
        default=None,
        sa_column=Column(SAEnum(EstadoNeumaticoEnum, name="estado_neumatico_enum", create_type=False), nullable=True)
    )
    odometro_vehiculo_en_evento: Optional[int] = Field(default=None, ge=0)
    profundidad_remanente_mm: Optional[float] = Field(default=None, ge=0)
    presion_psi: Optional[float] = Field(default=None, gt=0)
    costo_evento: Optional[float] = Field(default=None, ge=0)
    moneda_costo: Optional[str] = Field(default="PEN", max_length=3)
    notas: Optional[str] = None
    profundidad_post_reencauche_mm: Optional[float] = Field(default=None, gt=0)
    datos_evento: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))


# ---------------------------------------------------------------------------
# Schema para Crear: Hereda de Base y añade validaciones
# ---------------------------------------------------------------------------
class EventoNeumaticoCreate(EventoNeumaticoBase):
    # Asegúrate que los campos requeridos en la API estén aquí si no están en Base
    # Ejemplo: neumatico_id y tipo_evento ya están en Base y son requeridos allí.

    # --- Validadores (los que tenías antes, adaptados si es necesario) ---

    @field_validator('destino_desmontaje', mode='before')
    def check_destino_desmontaje(cls, v: Optional[str], info: ValidationInfo):
        enum_member = None
        # Acceder al tipo de evento desde los datos de validación
        tipo_evento_val = info.data.get('tipo_evento')

        if v is not None:
            try:
                enum_member = EstadoNeumaticoEnum(v)
            except ValueError:
                raise ValueError(f"Valor inválido para destino_desmontaje: {v}. Valores permitidos: {[e.value for e in EstadoNeumaticoEnum]}")

        # Convertir tipo_evento a Enum para comparación segura
        tipo_enum = None
        if isinstance(tipo_evento_val, str):
            try:
                tipo_enum = TipoEventoNeumaticoEnum(tipo_evento_val)
            except ValueError:
                 # No lanzar error aquí, dejar que falle la validación de tipo_evento si es inválido
                 pass
        elif isinstance(tipo_evento_val, TipoEventoNeumaticoEnum):
            tipo_enum = tipo_evento_val

        # Validar requerimiento solo si tipo_evento es válido
        if tipo_enum == TipoEventoNeumaticoEnum.DESMONTAJE and enum_member is None:
            raise ValueError('destino_desmontaje es requerido para eventos de tipo DESMONTAJE')

        return enum_member # Devolver el miembro Enum o None

    @field_validator('motivo_desecho_id_evento', mode='before')
    def check_motivo_desecho(cls, v: Optional[str | uuid.UUID], info: ValidationInfo):
        tipo_evento_val = info.data.get('tipo_evento')
        destino_val = info.data.get('destino_desmontaje')

        # Convertir tipo_evento a Enum
        tipo_enum: Optional[TipoEventoNeumaticoEnum] = None
        if isinstance(tipo_evento_val, str):
            try: tipo_enum = TipoEventoNeumaticoEnum(tipo_evento_val)
            except ValueError: pass
        elif isinstance(tipo_evento_val, TipoEventoNeumaticoEnum):
            tipo_enum = tipo_evento_val

        # Convertir destino desmontaje a Enum si existe
        destino_enum: Optional[EstadoNeumaticoEnum] = None
        if isinstance(destino_val, str):
            try: destino_enum = EstadoNeumaticoEnum(destino_val)
            except ValueError: pass
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

        return motivo_uuid # Devolver el UUID validado o None

    @field_validator('profundidad_post_reencauche_mm', mode='before')
    def check_profundidad_reencauche(cls, v: Optional[float], info: ValidationInfo):
        tipo_evento_val = info.data.get('tipo_evento')

        # Convertir tipo_evento a Enum
        tipo_enum: Optional[TipoEventoNeumaticoEnum] = None
        if isinstance(tipo_evento_val, str):
            try: tipo_enum = TipoEventoNeumaticoEnum(tipo_evento_val)
            except ValueError: pass
        elif isinstance(tipo_evento_val, TipoEventoNeumaticoEnum):
            tipo_enum = tipo_evento_val

        # Verificar requerimiento
        if tipo_enum == TipoEventoNeumaticoEnum.REENCAUCHE_SALIDA and v is None:
            raise ValueError('profundidad_post_reencauche_mm es requerida para eventos REENCAUCHE_SALIDA')

        # Verificar > 0
        if v is not None and v <= 0:
            raise ValueError('profundidad_post_reencauche_mm debe ser un valor positivo')

        return v # Devuelve el valor validado


# ---------------------------------------------------------------------------
# Schema para Leer: Hereda de Base y añade campos de auditoría/ID
# ---------------------------------------------------------------------------
class EventoNeumaticoRead(EventoNeumaticoBase):
    id: uuid.UUID
    timestamp_evento: datetime # Asumiendo que este viene del modelo de tabla
    creado_en: datetime      # Asumiendo que este viene del modelo de tabla
    # usuario_id: uuid.UUID # Descomenta si quieres asegurar que siempre se muestre en la lectura