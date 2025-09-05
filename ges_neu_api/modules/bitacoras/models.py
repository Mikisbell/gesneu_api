"""
Modelos para bitácoras, auditoría y sistema de errores
"""
from datetime import date, datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from uuid import UUID, uuid4
from decimal import Decimal
import enum

from sqlalchemy import Column, String, Index, func, text, ForeignKey, Integer, Numeric, Boolean, Text, UniqueConstraint, Date, SmallInteger, TIMESTAMP, Enum, BigInteger
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB, INTERVAL

# ============================================================================
# ENUMS
# ============================================================================

class TipoOperacionEnum(str, enum.Enum):
    ROTACION = "ROTACION"
    BALANCEO = "BALANCEO"
    ALINEACION = "ALINEACION"
    REPARACION_GENERAL = "REPARACION_GENERAL"
    INSPECCION_GENERAL = "INSPECCION_GENERAL"
    CAMBIO_ACEITE = "CAMBIO_ACEITE"
    OTRO = "OTRO"
    DESMONTAJE = "DESMONTAJE"

class EstadoOperacionEnum(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    EN_PROCESO = "EN_PROCESO"
    COMPLETADA = "COMPLETADA"
    CANCELADA = "CANCELADA"
    VENCIDA = "VENCIDA"

class TipoAccionOperacionEnum(str, enum.Enum):
    INSTALACION = "INSTALACION"
    DESMONTAJE = "DESMONTAJE"
    ROTACION = "ROTACION"
    REPARACION_NEU = "REPARACION_NEU"
    INSPECCION_NEU = "INSPECCION_NEU"
    OTRO_NEU = "OTRO_NEU"

# ============================================================================
# BITÁCORAS DE OPERACIONES
# ============================================================================

class BitacoraMantenimiento(SQLModel, table=True):
    __tablename__ = "bitacora_mantenimiento"
    
    id: int = Field(sa_column=Column(Integer, primary_key=True))
    fecha_ejecucion: datetime = Field(sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")))
    tipo: str = Field(sa_column=Column(String(50), nullable=False))
    descripcion: str = Field(sa_column=Column(Text, nullable=False))
    ejecutado_por: str = Field(sa_column=Column(String, nullable=False, server_default=text("CURRENT_USER")))
    duracion: Optional[str] = Field(default=None, sa_column=Column(INTERVAL))
    exito: Optional[bool] = Field(default=True, sa_column=Column(Boolean, server_default=text("true")))
    detalles: Optional[str] = Field(default=None, sa_column=Column(Text))

class BitacoraOperaciones(SQLModel, table=True):
    __tablename__ = "bitacora_operaciones"
    
    id: UUID = Field(default_factory=uuid4, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")))
    tipo_operacion: TipoOperacionEnum = Field(
        sa_column=Column(Enum(TipoOperacionEnum, name="tipo_operacion_enum"), nullable=False),
        description="Tipo de operación"
    )
    descripcion: str = Field(sa_column=Column(Text, nullable=False))
    fecha_operacion: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")),
        description="Fecha de la operación"
    )
    usuario_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id")))
    almacen_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("almacenes.id")))
    vehiculo_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("vehiculos.id")))
    estado_operacion: EstadoOperacionEnum = Field(
        sa_column=Column(Enum(EstadoOperacionEnum, name="estado_operacion_enum"), nullable=False),
        description="Estado de la operación"
    )
    duracion_minutos: Optional[int] = Field(default=None, sa_column=Column(Integer))
    costo_estimado: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10,2)))
    costo_real: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10,2)))
    proveedor_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("proveedores.id")))
    observaciones: Optional[str] = Field(default=None, sa_column=Column(Text))
    creado_en: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")),
        description="Fecha de creación"
    )
    actualizado_en: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")),
        description="Fecha de actualización"
    )
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id")))
    actualizado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id")))

class BitacoraOperacionesNeumaticos(SQLModel, table=True):
    __tablename__ = "bitacora_operaciones_neumaticos"
    
    id: UUID = Field(default_factory=uuid4, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")))
    operacion_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("bitacora_operaciones.id"), nullable=False))
    neumatico_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("neumaticos.id"), nullable=False))
    tipo_accion: TipoAccionOperacionEnum = Field(
        sa_column=Column(Enum(TipoAccionOperacionEnum, name="tipo_accion_operacion_enum"), nullable=False),
        description="Tipo de acción en la operación"
    )
    posicion_neumatico_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("posiciones_neumatico.id")))
    profundidad_inicial_mm: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5,2)))
    profundidad_final_mm: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5,2)))
    presion_inicial_psi: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5,2)))
    presion_final_psi: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5,2)))
    kilometraje_vehiculo_km: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10,2)))
    observaciones: Optional[str] = Field(default=None, sa_column=Column(Text))
    creado_en: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")))
    actualizado_en: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")))
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id")))
    actualizado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id")))

# ============================================================================
# SISTEMA DE AUDITORÍA
# ============================================================================

class AuditoriaLog(SQLModel, table=True):
    __tablename__ = "auditoria_log"
    
    id: int = Field(sa_column=Column(BigInteger, primary_key=True))
    timestamp_log: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")),
        description="Timestamp del log"
    )
    esquema_tabla: str = Field(
        sa_column=Column(String(63), nullable=False),
        description="Esquema de la tabla"
    )
    nombre_tabla: str = Field(
        sa_column=Column(String(63), nullable=False),
        description="Nombre de la tabla"
    )
    operacion: str = Field(
        sa_column=Column(String(10), nullable=False),
        description="Operación realizada (INSERT, UPDATE, DELETE)"
    )
    usuario_db: str = Field(
        sa_column=Column(String(63), nullable=False, server_default=text("CURRENT_USER")),
        description="Usuario de base de datos"
    )
    usuario_aplicacion_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True),
        description="ID del usuario de aplicación"
    )
    usuario_aplicacion_username: Optional[str] = Field(
        default=None,
        sa_column=Column(String(50), nullable=True),
        description="Username del usuario de aplicación"
    )
    direccion_ip: Optional[str] = Field(
        default=None,
        sa_column=Column(String(45), nullable=True),
        description="Dirección IP"
    )
    user_agent: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
        description="User agent"
    )
    id_entidad: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
        description="ID de la entidad afectada"
    )
    datos_antiguos: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True),
        description="Datos antes del cambio"
    )
    datos_nuevos: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True),
        description="Datos después del cambio"
    )
    cambios: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True),
        description="Cambios realizados"
    )
    contexto_aplicacion: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True),
        description="Contexto de la aplicación"
    )
    query_ejecutada: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
        description="Query SQL ejecutada"
    )

class ConfiguracionAuditoria(SQLModel, table=True):
    __tablename__ = "configuracion_auditoria"
    
    nombre_tabla: str = Field(sa_column=Column(String(63), primary_key=True, nullable=False))
    activo: bool = Field(sa_column=Column(Boolean, nullable=False, server_default=text("true")))
    prioridad: Optional[str] = Field(default=None, sa_column=Column(String(20)))
    campos_excluidos: Optional[dict] = Field(default=None, sa_column=Column(JSONB, server_default=text("'{}'")))
    creado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP(timezone=True), server_default=text("now()")))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP(timezone=True), server_default=text("now()")))

class ErroresAplicacion(SQLModel, table=True):
    __tablename__ = "errores_aplicacion"
    
    id: UUID = Field(default_factory=uuid4, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")))
    nombre_funcion: str = Field(sa_column=Column(Text, nullable=False))
    mensaje_error: str = Field(sa_column=Column(Text, nullable=False))
    detalles: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    creado_por: Optional[str] = Field(default="SISTEMA", sa_column=Column(Text, server_default=text("'SISTEMA'")))
    creado_en: datetime = Field(sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")))
    resuelto: Optional[bool] = Field(default=False, sa_column=Column(Boolean, server_default=text("false")))
    resuelto_por: Optional[str] = Field(default=None, sa_column=Column(Text))
    resuelto_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP(timezone=True)))
    comentario_resolucion: Optional[str] = Field(default=None, sa_column=Column(Text))


# ============================================================================
# SISTEMA
# ============================================================================

class ParametrosSistema(SQLModel, table=True):
    __tablename__ = "parametros_sistema"
    
    id: int = Field(sa_column=Column(Integer, primary_key=True))
    clave: str = Field(sa_column=Column(String(100), nullable=False, unique=True))
    valor: str = Field(sa_column=Column(Text, nullable=False))
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))
    creado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP, server_default=text("now()")))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP, server_default=text("now()")))
    creado_por: Optional[str] = Field(default="SISTEMA", sa_column=Column(String(100), server_default=text("'SISTEMA'")))
    actualizado_por: Optional[str] = Field(default="SISTEMA", sa_column=Column(String(100), server_default=text("'SISTEMA'")))

class TareasProgramadas(SQLModel, table=True):
    __tablename__ = "tareas_programadas"
    
    id: int = Field(sa_column=Column(Integer, primary_key=True))
    nombre_tarea: str = Field(sa_column=Column(String(100), nullable=False))
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))
    frecuencia_dias: int = Field(default=1, sa_column=Column(Integer, nullable=False, server_default=text("1")))
    ultima_ejecucion: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP(timezone=True)))
    proxima_ejecucion: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP(timezone=True)))
    activa: Optional[bool] = Field(default=True, sa_column=Column(Boolean, server_default=text("true")))
    script_sql: Optional[str] = Field(default=None, sa_column=Column(Text))
    creado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP(timezone=True), server_default=text("now()")))
    creado_por: Optional[str] = Field(default="SISTEMA", sa_column=Column(String(100), server_default=text("'SISTEMA'")))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP(timezone=True)))
    actualizado_por: Optional[str] = Field(default=None, sa_column=Column(String(100)))

class Rutas(SQLModel, table=True):
    __tablename__ = "rutas"
    
    id: UUID = Field(default_factory=uuid4, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")))
    codigo: str = Field(sa_column=Column(String(20), nullable=False, unique=True))
    nombre: str = Field(sa_column=Column(String(100), nullable=False))
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))
    distancia_total_km: Decimal = Field(sa_column=Column(Numeric(10,2), nullable=False))
    ida_vuelta: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text("true")))
    activa: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text("true")))
    creado_en: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")))
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id")))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP(timezone=True)))
    actualizado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id")))

class TiposRuta(SQLModel, table=True):
    __tablename__ = "tipos_ruta"
    
    id: UUID = Field(default_factory=uuid4, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")))
    nombre_ruta: str = Field(sa_column=Column(String(150), nullable=False, unique=True))
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))
    distancia_total_km_ciclo: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(8,2)))
    distancia_trocha_km_ciclo: Optional[Decimal] = Field(default=0, sa_column=Column(Numeric(8,2), server_default=text("0")))
    distancia_asfalto_km_ciclo: Optional[Decimal] = Field(default=0, sa_column=Column(Numeric(8,2), server_default=text("0")))
    distancia_otro_terreno_km_ciclo: Optional[Decimal] = Field(default=0, sa_column=Column(Numeric(8,2), server_default=text("0")))
    porcentaje_promedio_con_carga: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5,2)))
    creado_en: datetime = Field(sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")))
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id")))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP(timezone=True)))
    actualizado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id")))
