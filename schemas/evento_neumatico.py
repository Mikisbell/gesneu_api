# schemas/evento_neumatico.py (Completo y Corregido v3)

import uuid
from datetime import date, datetime, timezone
from typing import Optional, Dict, Any
from decimal import Decimal
from pydantic import field_validator, ValidationInfo, ConfigDict
from sqlmodel import SQLModel, Field

# Importar Enums desde su ubicación correcta
# Asumiendo que EstadoNeumaticoEnum está en neumatico.py y el resto en evento_neumatico.py
# Ajusta según tu estructura final si es diferente
from models.neumatico import EstadoNeumaticoEnum
from models.evento_neumatico import TipoEventoNeumaticoEnum

# --- Schema Base con campos comunes a la mayoría de eventos ---
# (Dejamos aquí los campos que NO son específicos de un solo tipo de evento)
class EventoNeumaticoBase(SQLModel):
    # Identificadores Principales
    neumatico_id: Optional[uuid.UUID] = Field(default=None, foreign_key="neumaticos.id") # Neumático al que afecta
    tipo_evento: TipoEventoNeumaticoEnum # El tipo de evento siempre es obligatorio
    usuario_id: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id") # Quién registra (se asigna en endpoint)
    fecha_evento: Optional[date] = Field(default=None, description="Fecha explícita del evento si difiere del timestamp de registro")

    # Datos comunes opcionales
    odometro_vehiculo_en_evento: Optional[int] = Field(default=None, ge=0)
    notas: Optional[str] = Field(default=None)
    costo_evento: Optional[Decimal] = Field(default=None, ge=0) # Para servicios
    moneda_costo: Optional[str] = Field(default="PEN", max_length=3)
    proveedor_servicio_id: Optional[uuid.UUID] = Field(default=None, foreign_key="proveedores.id") # Reparación, Reencauche
    datos_evento: Optional[Dict[str, Any]] = Field(default=None) # Para JSON genérico
    relacion_evento_anterior: Optional[uuid.UUID] = Field(default=None, foreign_key="eventos_neumatico.id") # Para relacionar eventos

# --- Schema de Creación: Hereda de Base y añade TODOS los campos posibles como Opcionales ---
class EventoNeumaticoCreate(EventoNeumaticoBase):
    # --- Campos específicos añadidos aquí ---
    # Compra
    numero_serie: Optional[str] = None
    modelo_id: Optional[uuid.UUID] = None
    fecha_compra: Optional[date] = None
    costo_compra: Optional[Decimal] = None
    proveedor_compra_id: Optional[uuid.UUID] = None

    # Instalación / Rotación
    vehiculo_id: Optional[uuid.UUID] = None
    posicion_id: Optional[uuid.UUID] = None

    # Desmontaje
    motivo_desmontaje_destino: Optional[EstadoNeumaticoEnum] = None # Estado destino al desmontar

    # Destinos (Almacén) - Usado por COMPRA, DESMONTAJE(a stock), REPARACION/REENCAUCHE_SALIDA, AJUSTE
    destino_almacen_id: Optional[uuid.UUID] = None

    # Inspección
    profundidad_remanente_mm: Optional[float] = None
    presion_psi: Optional[float] = None

    # Desecho
    motivo_desecho_id_evento: Optional[uuid.UUID] = None # ID del motivo tabla MotivoDesecho

    # Reencauche Salida
    profundidad_post_reencauche_mm: Optional[float] = None

    # Ajuste Inventario
    estado_ajuste: Optional[EstadoNeumaticoEnum] = None # Nuevo estado a asignar

    # --- Validadores (Se aplican sobre los campos opcionales cuando son relevantes) ---
    @field_validator('motivo_desmontaje_destino', mode='before')
    def check_motivo_desmontaje_destino(cls, v: Optional[str], info: ValidationInfo):
        enum_member = cls._get_enum_from_val(v, EstadoNeumaticoEnum)
        tipo_enum = cls._get_enum_from_val(info.data.get('tipo_evento'), TipoEventoNeumaticoEnum)

        if tipo_enum == TipoEventoNeumaticoEnum.DESMONTAJE and enum_member is None:
            raise ValueError('motivo_desmontaje_destino es requerido para eventos de tipo DESMONTAJE')
        return enum_member

    @field_validator('motivo_desecho_id_evento', mode='before')
    def check_motivo_desecho(cls, v: Optional[str | uuid.UUID], info: ValidationInfo):
        motivo_uuid = cls._get_uuid_from_val(v)
        tipo_enum = cls._get_enum_from_val(info.data.get('tipo_evento'), TipoEventoNeumaticoEnum)
        destino_enum = cls._get_enum_from_val(info.data.get('motivo_desmontaje_destino'), EstadoNeumaticoEnum)

        is_evento_desecho = (tipo_enum == TipoEventoNeumaticoEnum.DESECHO)
        is_desmontaje_a_desecho = (tipo_enum == TipoEventoNeumaticoEnum.DESMONTAJE and destino_enum == EstadoNeumaticoEnum.DESECHADO)

        if (is_evento_desecho or is_desmontaje_a_desecho) and motivo_uuid is None:
            raise ValueError('motivo_desecho_id_evento es requerido para DESECHO o DESMONTAJE a DESECHADO')
        return motivo_uuid

    @field_validator('profundidad_post_reencauche_mm', mode='before')
    def check_profundidad_reencauche(cls, v: Optional[float], info: ValidationInfo):
        tipo_enum = cls._get_enum_from_val(info.data.get('tipo_evento'), TipoEventoNeumaticoEnum)

        if tipo_enum == TipoEventoNeumaticoEnum.REENCAUCHE_SALIDA and v is None:
            raise ValueError('profundidad_post_reencauche_mm es requerida para REENCAUCHE_SALIDA')
        if v is not None and v <= 0:
            raise ValueError('profundidad_post_reencauche_mm debe ser positivo')
        return v

    # Helpers para validadores (pueden ser métodos de clase)
    @classmethod
    def _get_enum_from_val(cls, val: Any, enum_cls: Any) -> Optional[Any]:
        if isinstance(val, str):
            try: return enum_cls(val)
            except ValueError: raise ValueError(f"Valor '{val}' inválido para {enum_cls.__name__}")
        elif isinstance(val, enum_cls): return val
        return None # Permite que sea None si el campo es opcional

    @classmethod
    def _get_uuid_from_val(cls, val: Any) -> Optional[uuid.UUID]:
         if isinstance(val, str):
             try: return uuid.UUID(val)
             except ValueError: raise ValueError(f"'{val}' no es un UUID válido")
         elif isinstance(val, uuid.UUID): return val
         return None # Permite que sea None si el campo es opcional


# --- Schema de Lectura (Respuesta de la API) ---
class EventoNeumaticoRead(EventoNeumaticoBase):
    # Hereda campos de EventoNeumaticoBase y añade los del modelo que no están en Base
    id: uuid.UUID
    timestamp_evento: datetime # Generado automáticamente por el modelo
    creado_en: datetime # Generado automáticamente por el modelo
    # Considera añadir aquí relaciones leídas si las necesitas (ej. nombre de usuario)
    # usuario: Optional[UsuarioRead] = None # Requeriría definir UsuarioRead

    # Configuración para permitir la lectura desde atributos del objeto modelo
    model_config = ConfigDict(from_attributes=True)