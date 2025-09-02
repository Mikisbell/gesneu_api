"""
Esquemas Pydantic para el módulo de eventos - Basados en ESQUEMA_COMPLETO_BD.md
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from .models import TipoEventoNeumaticoEnum, EstadoNeumaticoEnumDestino

# Esquemas de respuesta
class EventoNeumaticoResponse(BaseModel):
    """Esquema para respuesta de eventos de neumáticos."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    neumatico_id: UUID
    tipo_evento: TipoEventoNeumaticoEnum
    timestamp_evento: datetime
    usuario_id: UUID
    creado_en: datetime
    vehiculo_id: Optional[UUID] = None
    posicion_id: Optional[UUID] = None
    odometro_vehiculo_en_evento: Optional[int] = None
    profundidad_remanente_mm: Optional[Decimal] = None
    presion_psi: Optional[Decimal] = None
    costo_evento: Optional[Decimal] = None
    moneda_costo: Optional[str] = None
    proveedor_servicio_id: Optional[UUID] = None
    notas: Optional[str] = None
    destino_desmontaje: Optional[EstadoNeumaticoEnumDestino] = None
    motivo_desecho_id_evento: Optional[UUID] = None
    profundidad_post_reencauche_mm: Optional[Decimal] = None
    datos_evento: Optional[dict] = None
    relacion_evento_anterior: Optional[UUID] = None
    almacen_destino_id: Optional[UUID] = None
    tipo_ruta_id: Optional[UUID] = None
    peso_carga_promedio_ton_evento: Optional[Decimal] = None
    motivo_reparacion_texto: Optional[str] = None
    tipo_dano_detectado_texto: Optional[str] = None

# Esquemas de creación
class EventoNeumaticoCreate(BaseModel):
    """Esquema para crear eventos de neumáticos."""
    neumatico_id: UUID
    tipo_evento: TipoEventoNeumaticoEnum
    usuario_id: UUID
    vehiculo_id: Optional[UUID] = None
    posicion_id: Optional[UUID] = None
    odometro_vehiculo_en_evento: Optional[int] = None
    profundidad_remanente_mm: Optional[Decimal] = None
    presion_psi: Optional[Decimal] = None
    costo_evento: Optional[Decimal] = None
    moneda_costo: Optional[str] = "PEN"
    proveedor_servicio_id: Optional[UUID] = None
    notas: Optional[str] = None
    destino_desmontaje: Optional[EstadoNeumaticoEnumDestino] = None
    motivo_desecho_id_evento: Optional[UUID] = None
    profundidad_post_reencauche_mm: Optional[Decimal] = None
    datos_evento: Optional[dict] = None
    relacion_evento_anterior: Optional[UUID] = None
    almacen_destino_id: Optional[UUID] = None
    tipo_ruta_id: Optional[UUID] = None
    peso_carga_promedio_ton_evento: Optional[Decimal] = None
    motivo_reparacion_texto: Optional[str] = None
    tipo_dano_detectado_texto: Optional[str] = None
