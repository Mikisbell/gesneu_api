"""
Esquemas Pydantic para el módulo de bitácoras
"""
from datetime import datetime, date
from typing import Optional, Dict, Any
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field


# ============================================================================
# BITÁCORA MANTENIMIENTO
# ============================================================================

class BitacoraMantenimientoBase(BaseModel):
    fecha_ejecucion: datetime
    tipo: str = Field(max_length=50)
    descripcion: str
    ejecutado_por: str
    duracion: Optional[str] = None
    exito: Optional[bool] = True
    detalles: Optional[str] = None

class BitacoraMantenimientoCreate(BitacoraMantenimientoBase):
    pass

class BitacoraMantenimientoUpdate(BaseModel):
    fecha_ejecucion: Optional[datetime] = None
    tipo: Optional[str] = None
    descripcion: Optional[str] = None
    ejecutado_por: Optional[str] = None
    duracion: Optional[str] = None
    exito: Optional[bool] = None
    detalles: Optional[str] = None

class BitacoraMantenimientoRead(BitacoraMantenimientoBase):
    id: int

    class Config:
        from_attributes = True


# ============================================================================
# BITÁCORA OPERACIONES
# ============================================================================

class BitacoraOperacionesBase(BaseModel):
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    descripcion: str
    activo: bool = True
    usuario_id: Optional[UUID] = None
    almacen_id: Optional[UUID] = None
    vehiculo_id: Optional[UUID] = None
    duracion_minutos: Optional[int] = None
    costo_estimado: Optional[Decimal] = None
    costo_real: Optional[Decimal] = None
    proveedor_id: Optional[UUID] = None
    observaciones: Optional[str] = None

class BitacoraOperacionesCreate(BitacoraOperacionesBase):
    creado_por: Optional[UUID] = None

class BitacoraOperacionesUpdate(BaseModel):
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None
    usuario_id: Optional[UUID] = None
    almacen_id: Optional[UUID] = None
    vehiculo_id: Optional[UUID] = None
    duracion_minutos: Optional[int] = None
    costo_estimado: Optional[Decimal] = None
    costo_real: Optional[Decimal] = None
    proveedor_id: Optional[UUID] = None
    observaciones: Optional[str] = None
    actualizado_por: Optional[UUID] = None

class BitacoraOperacionesRead(BitacoraOperacionesBase):
    id: UUID
    creado_en: datetime
    actualizado_en: datetime
    creado_por: Optional[UUID] = None
    actualizado_por: Optional[UUID] = None

    class Config:
        from_attributes = True


# ============================================================================
# BITÁCORA OPERACIONES NEUMÁTICOS
# ============================================================================

class BitacoraOperacionesNeumaticosBase(BaseModel):
    operacion_id: UUID
    neumatico_id: UUID
    accion_realizada: str = Field(max_length=100)
    posicion_anterior_id: Optional[UUID] = None
    posicion_nueva_id: Optional[UUID] = None
    observaciones: Optional[str] = None

class BitacoraOperacionesNeumaticosCreate(BitacoraOperacionesNeumaticosBase):
    creado_por: Optional[UUID] = None

class BitacoraOperacionesNeumaticosUpdate(BaseModel):
    accion_realizada: Optional[str] = None
    posicion_anterior_id: Optional[UUID] = None
    posicion_nueva_id: Optional[UUID] = None
    observaciones: Optional[str] = None

class BitacoraOperacionesNeumaticosRead(BitacoraOperacionesNeumaticosBase):
    id: UUID
    creado_en: datetime
    creado_por: Optional[UUID] = None

    class Config:
        from_attributes = True


# ============================================================================
# AUDITORÍA LOG
# ============================================================================

class AuditoriaLogBase(BaseModel):
    timestamp_log: datetime
    esquema_tabla: str = Field(max_length=63)
    nombre_tabla: str = Field(max_length=63)
    operacion: str = Field(max_length=10)
    usuario_db: str = Field(max_length=63)
    usuario_aplicacion_id: Optional[UUID] = None
    usuario_aplicacion_username: Optional[str] = Field(None, max_length=50)
    direccion_ip: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = None
    id_entidad: Optional[str] = None
    datos_antiguos: Optional[Dict[str, Any]] = None
    datos_nuevos: Optional[Dict[str, Any]] = None
    cambios: Optional[Dict[str, Any]] = None
    contexto_aplicacion: Optional[Dict[str, Any]] = None
    query_ejecutada: Optional[str] = None

class AuditoriaLogCreate(AuditoriaLogBase):
    pass

class AuditoriaLogRead(AuditoriaLogBase):
    id: int

    class Config:
        from_attributes = True


# ============================================================================
# CONFIGURACIÓN AUDITORÍA
# ============================================================================

class ConfiguracionAuditoriaBase(BaseModel):
    activo: bool
    prioridad: Optional[str] = Field(None, max_length=20)
    campos_excluidos: Optional[Dict[str, Any]] = None

class ConfiguracionAuditoriaCreate(ConfiguracionAuditoriaBase):
    nombre_tabla: str = Field(max_length=63)

class ConfiguracionAuditoriaUpdate(ConfiguracionAuditoriaBase):
    activo: Optional[bool] = None

class ConfiguracionAuditoriaRead(ConfiguracionAuditoriaBase):
    nombre_tabla: str
    creado_en: Optional[datetime] = None
    actualizado_en: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# ERRORES APLICACIÓN
# ============================================================================

class ErroresAplicacionBase(BaseModel):
    nombre_funcion: str
    mensaje_error: str
    detalles: Optional[Dict[str, Any]] = None
    creado_por: Optional[str] = None
    resuelto: Optional[bool] = None
    resuelto_por: Optional[str] = None
    resuelto_en: Optional[datetime] = None
    comentario_resolucion: Optional[str] = None

class ErroresAplicacionCreate(ErroresAplicacionBase):
    pass

class ErroresAplicacionUpdate(BaseModel):
    resuelto: Optional[bool] = None
    resuelto_por: Optional[str] = None
    resuelto_en: Optional[datetime] = None
    comentario_resolucion: Optional[str] = None

class ErroresAplicacionRead(ErroresAplicacionBase):
    id: UUID
    creado_en: datetime

    class Config:
        from_attributes = True


# ============================================================================
# NOTA: Los esquemas para auditoria_roles_usuarios están en el módulo auth
# según el esquema real de la base de datos
# ============================================================================
