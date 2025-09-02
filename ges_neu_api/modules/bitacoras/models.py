"""
Modelos para bitácoras, auditoría y sistema de errores
"""
from datetime import date, datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from uuid import UUID, uuid4
from decimal import Decimal

from sqlalchemy import Column, String, Boolean, Text, Integer, Numeric, Date, SmallInteger, TIMESTAMP, BigInteger
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB, INTERVAL
from sqlalchemy import text, ForeignKey

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
    fecha_inicio: datetime = Field(sa_column=Column(TIMESTAMP(timezone=True), nullable=False))
    fecha_fin: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP(timezone=True)))
    descripcion: str = Field(sa_column=Column(Text, nullable=False))
    activo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text("true")))
    creado_en: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")))
    actualizado_en: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")))
    usuario_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id")))
    almacen_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("almacenes.id")))
    vehiculo_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("vehiculos.id")))
    duracion_minutos: Optional[int] = Field(default=None, sa_column=Column(Integer))
    costo_estimado: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10,2)))
    costo_real: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10,2)))
    proveedor_id: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("proveedores.id")))
    observaciones: Optional[str] = Field(default=None, sa_column=Column(Text))
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id")))
    actualizado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id")))

class BitacoraOperacionesNeumaticos(SQLModel, table=True):
    __tablename__ = "bitacora_operaciones_neumaticos"
    
    id: UUID = Field(default_factory=uuid4, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")))
    operacion_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("bitacora_operaciones.id"), nullable=False))
    neumatico_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("neumaticos.id"), nullable=False))
    tipo_accion: str = Field(sa_column=Column(String(50), nullable=False))  # Enum como string según esquema
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
    timestamp_log: datetime = Field()
    esquema_tabla: str = Field(max_length=63)
    nombre_tabla: str = Field(max_length=63)
    operacion: str = Field(max_length=10)  # INSERT, UPDATE, DELETE
    usuario_db: str = Field(max_length=63)
    usuario_aplicacion_id: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")
    usuario_aplicacion_username: Optional[str] = Field(default=None, max_length=50)
    direccion_ip: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None)
    id_entidad: Optional[str] = Field(default=None)
    datos_antiguos: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    datos_nuevos: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    cambios: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    contexto_aplicacion: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    query_ejecutada: Optional[str] = Field(default=None)

class ConfiguracionAuditoria(SQLModel, table=True):
    __tablename__ = "configuracion_auditoria"
    
    nombre_tabla: str = Field(max_length=63, primary_key=True)
    activo: bool = Field()
    prioridad: Optional[str] = Field(default=None, max_length=20)
    campos_excluidos: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    creado_en: Optional[datetime] = Field(default=None)
    actualizado_en: Optional[datetime] = Field(default=None)

class ErroresAplicacion(SQLModel, table=True):
    __tablename__ = "errores_aplicacion"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    nombre_funcion: str = Field()
    mensaje_error: str = Field()
    detalles: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    creado_por: Optional[str] = Field(default=None)
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    resuelto: Optional[bool] = Field(default=None)
    resuelto_por: Optional[str] = Field(default=None)
    resuelto_en: Optional[datetime] = Field(default=None)
    comentario_resolucion: Optional[str] = Field(default=None)

# ============================================================================
# NOTA: auditoria_roles_usuarios está definida en el módulo auth/models.py
# según el esquema real de la base de datos
# ============================================================================

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
    frecuencia_dias: int = Field(default=1, sa_column=Column(Integer, nullable=False, server_default=text("1")))
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))
    ultima_ejecucion: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP))
    proxima_ejecucion: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP))
    activa: Optional[bool] = Field(default=True, sa_column=Column(Boolean, server_default=text("true")))
    script_sql: Optional[str] = Field(default=None, sa_column=Column(Text))
    creado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP, server_default=text("now()")))
    creado_por: Optional[str] = Field(default="SISTEMA", sa_column=Column(String(100), server_default=text("'SISTEMA'")))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP))
    actualizado_por: Optional[str] = Field(default=None, sa_column=Column(String(100)))

class Rutas(SQLModel, table=True):
    __tablename__ = "rutas"
    
    id: UUID = Field(default_factory=uuid4, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")))
    codigo: str = Field(sa_column=Column(String(20), nullable=False, unique=True))
    nombre: str = Field(sa_column=Column(String(100), nullable=False))
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))
    activo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text("true")))
    creado_en: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")))
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id")))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP(timezone=True)))
    actualizado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id")))

class TiposRuta(SQLModel, table=True):
    __tablename__ = "tipos_ruta"
    
    id: UUID = Field(default_factory=uuid4, sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")))
    nombre: str = Field(sa_column=Column(String(100), nullable=False, unique=True))
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))
    porcentaje_promedio_con_carga: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5,2)))
    activo: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, server_default=text("true")))
    creado_en: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")))
    creado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id")))
    actualizado_en: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP(timezone=True)))
    actualizado_por: Optional[UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id")))
