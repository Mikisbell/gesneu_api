"""
Modelos específicos para tests - Compatibles con SQLite.
Mantienen la estructura del esquema real pero adaptan tipos para SQLite.
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4
from enum import Enum

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, UniqueConstraint, MetaData, Integer, Date, Numeric, SmallInteger
from passlib.context import CryptContext

# Create separate metadata for test models
test_metadata = MetaData()

# Password context for test models
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Enums exactos según ESQUEMA_COMPLETO_BD.md
class EstadoNeumaticoEnum(str, Enum):
    EN_STOCK = "EN_STOCK"
    INSTALADO = "INSTALADO"
    EN_REPARACION = "EN_REPARACION"
    EN_REENCAUCHE = "EN_REENCAUCHE"
    DESECHADO = "DESECHADO"
    EN_TRANSITO = "EN_TRANSITO"

class EstadoAlertaEnum(str, Enum):
    NUEVA = "NUEVA"
    VISTA = "VISTA"
    GESTIONADA = "GESTIONADA"

class NivelSeveridadEnum(str, Enum):
    INFO = "INFO"
    WARN = "WARN"
    CRITICAL = "CRITICAL"

class EstadoOperacionEnum(str, Enum):
    PENDIENTE = "PENDIENTE"
    EN_PROCESO = "EN_PROCESO"
    COMPLETADA = "COMPLETADA"
    CANCELADA = "CANCELADA"
    VENCIDA = "VENCIDA"

class TipoEjeEnum(str, Enum):
    DIRECCION = "DIRECCION"
    TRACCION = "TRACCION"
    ARRASTRE = "ARRASTRE"
    ELEVADOR = "ELEVADOR"
    RETRACTIL = "RETRACTIL"
    OTRO = "OTRO"

class LadoVehiculoEnum(str, Enum):
    IZQUIERDO = "IZQUIERDO"
    DERECHO = "DERECHO"
    CENTRAL = "CENTRAL"
    INDETERMINADO = "INDETERMINADO"

class TipoEventoNeumaticoEnum(str, Enum):
    COMPRA = "COMPRA"
    INSTALACION = "INSTALACION"
    DESMONTAJE = "DESMONTAJE"
    INSPECCION = "INSPECCION"
    ROTACION = "ROTACION"
    REPARACION_ENTRADA = "REPARACION_ENTRADA"
    REPARACION_SALIDA = "REPARACION_SALIDA"
    REENCAUCHE_ENTRADA = "REENCAUCHE_ENTRADA"
    REENCAUCHE_SALIDA = "REENCAUCHE_SALIDA"
    DESECHO = "DESECHO"
    AJUSTE_INVENTARIO = "AJUSTE_INVENTARIO"
    TRANSFERENCIA_UBICACION = "TRANSFERENCIA_UBICACION"

class TipoAccionOperacionEnum(str, Enum):
    INSTALACION = "INSTALACION"
    DESMONTAJE = "DESMONTAJE"
    ROTACION = "ROTACION"
    REPARACION_NEU = "REPARACION_NEU"
    INSPECCION_NEU = "INSPECCION_NEU"
    OTRO_NEU = "OTRO_NEU"

class TipoOperacionEnum(str, Enum):
    ROTACION = "ROTACION"
    BALANCEO = "BALANCEO"
    ALINEACION = "ALINEACION"
    REPARACION_GENERAL = "REPARACION_GENERAL"
    INSPECCION_GENERAL = "INSPECCION_GENERAL"
    CAMBIO_ACEITE = "CAMBIO_ACEITE"
    OTRO = "OTRO"
    DESMONTAJE = "DESMONTAJE"

class Usuario(SQLModel, table=True):
    """Modelo Usuario para tests - Compatible con SQLite"""
    __tablename__ = "usuarios"
    __table_args__ = {'extend_existing': True}
    
    metadata = test_metadata

    # Campos exactos según esquema BD real, adaptados para SQLite
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(max_length=50, unique=True)
    nombre_completo: Optional[str] = Field(default=None, max_length=200)
    email: Optional[str] = Field(default=None, max_length=100, unique=True)
    password_hash: Optional[str] = Field(default=None)
    activo: bool = Field(default=True)
    ultimo_login: Optional[datetime] = Field(default=None)
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    creado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(default=None)
    actualizado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")
    
    def verify_password(self, password: str) -> bool:
        """Verifica si la contraseña proporcionada coincide con el hash almacenado."""
        if not self.password_hash:
            return False
        return pwd_context.verify(password, self.password_hash)

class Rol(SQLModel, table=True):
    """Modelo Rol para tests - Compatible con SQLite"""
    __tablename__ = "roles"
    __table_args__ = {'extend_existing': True}
    
    metadata = test_metadata

    # Campos exactos según esquema BD real, adaptados para SQLite
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    nombre: str = Field(max_length=100, unique=True)
    descripcion: Optional[str] = Field(default=None)
    es_rol_sistema: bool = Field(default=False)
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    creado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_en: Optional[datetime] = Field(default=None)
    actualizado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")

class Permiso(SQLModel, table=True):
    """Modelo Permiso para tests - Compatible con SQLite"""
    __tablename__ = "permisos"
    __table_args__ = (
        UniqueConstraint('nombre_recurso', 'accion'),
        {'extend_existing': True}
    )
    
    metadata = test_metadata

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    nombre_recurso: str = Field(max_length=100)
    accion: str = Field(max_length=100)
    descripcion: Optional[str] = Field(default=None)
    creado_en: datetime = Field(default_factory=datetime.utcnow)

class UsuariosRoles(SQLModel, table=True):
    """Modelo UsuariosRoles para tests - Compatible con SQLite"""
    __tablename__ = "usuarios_roles"
    __table_args__ = {'extend_existing': True}
    
    metadata = test_metadata

    usuario_id: UUID = Field(foreign_key="usuarios.id", primary_key=True)
    rol_id: UUID = Field(foreign_key="roles.id", primary_key=True)
    asignado_en: datetime = Field(default_factory=datetime.utcnow)
    asignado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")

class RolesPermisos(SQLModel, table=True):
    """Modelo RolesPermisos para tests - Compatible con SQLite"""
    __tablename__ = "roles_permisos"
    __table_args__ = {'extend_existing': True}
    
    metadata = test_metadata

    rol_id: UUID = Field(foreign_key="roles.id", primary_key=True)
    permiso_id: UUID = Field(foreign_key="permisos.id", primary_key=True)
    asignado_en: datetime = Field(default_factory=datetime.utcnow)
    asignado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")

# ============================================================================
# MODELOS DE NEUMÁTICOS PARA TESTS
# ============================================================================

class FabricanteNeumatico(SQLModel, table=True):
    """Fabricantes de neumáticos para tests - Exacto según esquema PostgreSQL"""
    __tablename__ = 'fabricantes_neumatico'
    __table_args__ = {'extend_existing': True}
    metadata = test_metadata
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    nombre: str = Field(max_length=100)  # NOT NULL
    codigo_abreviado: Optional[str] = Field(default=None, max_length=10)  # NULLABLE
    pais_origen: Optional[str] = Field(default=None, max_length=50)
    sitio_web: Optional[str] = Field(default=None, max_length=255)
    activo: bool = Field(default=True)  # NOT NULL
    creado_en: Optional[datetime] = Field(default_factory=datetime.utcnow)  # NOT NULL
    creado_por: Optional[UUID] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = None

class ModeloNeumatico(SQLModel, table=True):
    """Modelos de neumáticos para tests - Exacto según esquema PostgreSQL"""
    __tablename__ = 'modelos_neumatico'
    __table_args__ = {'extend_existing': True}
    metadata = test_metadata
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    fabricante_id: UUID = Field(foreign_key="fabricantes_neumatico.id")  # NOT NULL
    nombre_modelo: str = Field(max_length=100)  # NOT NULL
    medida: str = Field(max_length=20)  # NOT NULL, max 20 chars
    indice_carga: Optional[str] = Field(default=None, max_length=5)  # NULLABLE
    indice_velocidad: Optional[str] = Field(default=None, max_length=2)  # NULLABLE
    profundidad_original_mm: Decimal = Field(decimal_places=2)  # NOT NULL, NUMERIC(5,2)
    presion_recomendada_psi: Optional[Decimal] = Field(default=None, decimal_places=2)  # NULLABLE
    permite_reencauche: bool = Field(default=False)  # NOT NULL
    reencauches_maximos: Optional[int] = Field(default=0)  # NULLABLE, smallint
    patron_dibujo: Optional[str] = Field(default=None, max_length=50)
    tipo_servicio: Optional[str] = Field(default=None, max_length=50)
    vida_util_teorica_km: Optional[int] = None  # NULLABLE
    profundidad_minima_retiro_mm: Decimal = Field(default=Decimal("1.6"), decimal_places=2)  # NOT NULL
    tasa_desgaste_esperada_mm_km: Decimal = Field(decimal_places=8)  # NOT NULL, NUMERIC(10,8)
    activo: Optional[bool] = Field(default=True)  # NULLABLE
    frecuencia_inspeccion_km: Optional[int] = Field(default=5000)  # NULLABLE
    max_vidas_utiles: Optional[int] = Field(default=5)  # NULLABLE
    porcentaje_desgaste_por_vida: Optional[Decimal] = Field(default=Decimal("10.0"), decimal_places=2)  # NULLABLE
    creado_en: Optional[datetime] = Field(default_factory=datetime.utcnow)  # NOT NULL
    creado_por: Optional[UUID] = None
    actualizado_en: Optional[datetime] = None
    actualizado_por: Optional[UUID] = None

class Neumatico(SQLModel, table=True):
    """Modelo Neumatico para tests - Exacto según esquema PostgreSQL"""
    __tablename__ = 'neumaticos'
    __table_args__ = {'extend_existing': True}
    metadata = test_metadata
    
    # Campos obligatorios (NOT NULL)
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)  # uuid NOT NULL DEFAULT gen_random_uuid()
    modelo_id: UUID = Field(foreign_key="modelos_neumatico.id")  # uuid NOT NULL
    fecha_compra: date = Field()  # date NOT NULL
    es_reencauchado: bool = Field(default=False)  # boolean NOT NULL DEFAULT false
    vida_actual: int = Field(default=1, ge=1, le=11)  # smallint NOT NULL DEFAULT 1
    estado_actual: EstadoNeumaticoEnum = Field(default=EstadoNeumaticoEnum.EN_STOCK)  # estado_neumatico_enum NOT NULL DEFAULT 'EN_STOCK'
    kilometraje_acumulado: int = Field(default=0, ge=0)  # integer NOT NULL DEFAULT 0
    reencauches_realizados: int = Field(default=0, ge=0)  # smallint NOT NULL DEFAULT 0
    creado_en: Optional[datetime] = Field(default_factory=datetime.utcnow)  # timestamp with time zone NOT NULL DEFAULT now()
    profundidad_remanente_actual_mm: Decimal = Field(decimal_places=2, ge=0, le=50)  # numeric(5,2) NOT NULL
    
    # Campos opcionales (NULLABLE)
    numero_serie: Optional[str] = Field(default=None, max_length=100)  # character varying(100)
    dot: Optional[str] = None  # text
    fecha_fabricacion: Optional[date] = None  # date
    costo_compra: Optional[Decimal] = Field(default=None, decimal_places=2, ge=0)  # numeric(10,2)
    moneda_compra: Optional[str] = Field(default="PEN", max_length=3)  # character varying(3) DEFAULT 'PEN'
    proveedor_compra_id: Optional[UUID] = None  # uuid
    ubicacion_actual_vehiculo_id: Optional[UUID] = None  # uuid
    ubicacion_actual_posicion_id: Optional[UUID] = None  # uuid
    fecha_ultimo_evento: Optional[datetime] = None  # timestamp with time zone
    profundidad_inicial_mm: Optional[Decimal] = Field(default=None, decimal_places=2, gt=0)  # numeric(5,2)
    fecha_desecho: Optional[date] = None  # date
    motivo_desecho_id: Optional[UUID] = None  # uuid
    creado_por: Optional[UUID] = None  # uuid
    actualizado_en: Optional[datetime] = None  # timestamp with time zone
    actualizado_por: Optional[UUID] = None  # uuid
    ubicacion_almacen_id: Optional[UUID] = None  # uuid
    sensor_id: Optional[str] = Field(default=None, max_length=100)  # character varying(100)
    fecha_ultima_medicion_profundidad: Optional[datetime] = None  # timestamp with time zone
    kilometraje_vida_actual: Optional[int] = Field(default=0, ge=0)  # integer DEFAULT 0
    fecha_inicio_vida_actual: Optional[date] = None  # date
    odometro_instalacion_vida_actual: Optional[int] = None  # integer
    tasa_desgaste_actual_mm_km: Optional[Decimal] = Field(default=None, decimal_places=8, gt=0)  # numeric(10,8)
    vida_util_restante_km: Optional[int] = Field(default=None, ge=0)  # integer
    fecha_ultimo_reencauche: Optional[date] = None  # date
    activo: Optional[bool] = Field(default=True)  # boolean DEFAULT true
    proxima_inspeccion_fecha: Optional[date] = None  # date
    proxima_inspeccion_km: Optional[int] = None  # integer
    profundidad_inicio_vida_actual_mm: Optional[Decimal] = Field(default=None, decimal_places=2)  # numeric(5,2)
    
    # Campos AI agregados en Sprint 1
    prediccion_fecha_reemplazo: Optional[date] = None
    confianza_prediccion: Optional[Decimal] = Field(default=None, decimal_places=3, ge=0.0, le=1.0)
    fecha_ultima_prediccion: Optional[datetime] = None
    modelo_prediccion_version: Optional[str] = Field(default=None, max_length=50)

# MODELOS DE VEHÍCULOS PARA TESTS
# ============================================================================

class TiposVehiculo(SQLModel, table=True):
    """Tipos de vehículo para tests - Exacto según esquema PostgreSQL"""
    __tablename__ = 'tipos_vehiculo'
    __table_args__ = {'extend_existing': True}
    
    metadata = test_metadata
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)  # uuid NOT NULL
    nombre: str = Field(max_length=100)  # character varying(100) NOT NULL
    descripcion: Optional[str] = None  # text
    categoria_principal: Optional[str] = Field(default=None, max_length=50)  # character varying(50)
    subtipo: Optional[str] = Field(default=None, max_length=50)  # character varying(50)
    ejes_standard: int = Field(default=2)  # smallint NOT NULL DEFAULT 2
    activo: bool = Field(default=True)  # boolean NOT NULL DEFAULT true
    creado_en: Optional[datetime] = Field(default_factory=datetime.utcnow)  # timestamp with time zone NOT NULL DEFAULT now()
    creado_por: Optional[UUID] = None  # uuid
    actualizado_en: Optional[datetime] = None  # timestamp with time zone
    actualizado_por: Optional[UUID] = None  # uuid

class Vehiculos(SQLModel, table=True):
    """Modelo Vehiculos para tests - Exacto según esquema PostgreSQL"""
    __tablename__ = "vehiculos"
    __table_args__ = {'extend_existing': True}
    
    metadata = test_metadata
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)  # uuid NOT NULL
    tipo_vehiculo_id: UUID = Field(foreign_key="tipos_vehiculo.id")  # uuid NOT NULL
    placa: Optional[str] = Field(default=None, max_length=15)  # character varying(15)
    vin: Optional[str] = Field(default=None, max_length=17)  # character varying(17)
    numero_economico: str = Field(max_length=50)  # character varying(50) NOT NULL
    marca: Optional[str] = Field(default=None, max_length=50)  # character varying(50)
    modelo_vehiculo: Optional[str] = Field(default=None, max_length=50)  # character varying(50)
    anio_fabricacion: Optional[int] = None  # smallint
    fecha_alta: date = Field(default_factory=date.today)  # date NOT NULL DEFAULT CURRENT_DATE
    fecha_baja: Optional[date] = None  # date
    activo: bool = Field(default=True)  # boolean NOT NULL DEFAULT true
    odometro_actual: Optional[int] = None  # integer
    fecha_ultimo_odometro: Optional[datetime] = None  # timestamp with time zone
    ubicacion_actual: Optional[str] = Field(default=None, max_length=100)  # character varying(100)
    notas: Optional[str] = None  # text
    creado_en: Optional[datetime] = Field(default_factory=datetime.utcnow)  # timestamp with time zone NOT NULL DEFAULT now()
    creado_por: Optional[UUID] = None  # uuid
    actualizado_en: Optional[datetime] = None  # timestamp with time zone
    actualizado_por: Optional[UUID] = None  # uuid
    peso_carga_maxima_diseno_ton: Optional[Decimal] = Field(default=None, decimal_places=2)  # numeric(5,2)

class ConfiguracionesEje(SQLModel, table=True):
    """Configuraciones de eje para tests - Exacto según esquema PostgreSQL"""
    __tablename__ = 'configuraciones_eje'
    __table_args__ = {'extend_existing': True}
    
    metadata = test_metadata

    id: UUID = Field(default_factory=uuid4, primary_key=True)  # uuid NOT NULL
    tipo_vehiculo_id: UUID = Field(foreign_key="tipos_vehiculo.id")  # uuid NOT NULL
    numero_eje: int  # smallint NOT NULL
    tipo_eje: TipoEjeEnum  # tipo_eje_enum NOT NULL
    lado_vehiculo: LadoVehiculoEnum  # lado_vehiculo_enum NOT NULL
    activo: bool = Field(default=True)  # boolean NOT NULL DEFAULT true
    creado_en: Optional[datetime] = Field(default_factory=datetime.utcnow)  # timestamp with time zone NOT NULL DEFAULT now()
    creado_por: Optional[UUID] = None  # uuid
    actualizado_en: Optional[datetime] = None  # timestamp with time zone
    actualizado_por: Optional[UUID] = None  # uuid

class PosicionesNeumatico(SQLModel, table=True):
    """Posiciones de neumático para tests - Exacto según esquema PostgreSQL"""
    __tablename__ = 'posiciones_neumatico'
    __table_args__ = {'extend_existing': True}
    
    metadata = test_metadata

    id: UUID = Field(default_factory=uuid4, primary_key=True)  # uuid NOT NULL
    configuracion_eje_id: UUID = Field(foreign_key="configuraciones_eje.id")  # uuid NOT NULL
    posicion_en_eje: int  # smallint NOT NULL
    es_gemela: bool = Field(default=False)  # boolean NOT NULL DEFAULT false
    activo: bool = Field(default=True)  # boolean NOT NULL DEFAULT true
    creado_en: Optional[datetime] = Field(default_factory=datetime.utcnow)  # timestamp with time zone NOT NULL DEFAULT now()
    creado_por: Optional[UUID] = None  # uuid
    actualizado_en: Optional[datetime] = None  # timestamp with time zone
    actualizado_por: Optional[UUID] = None  # uuid

# ============================================================================
# MODELOS DE ALERTAS PARA TESTS
# ============================================================================

class Alertas(SQLModel, table=True):
    """Alertas para tests - Exactamente igual al esquema PostgreSQL"""
    __tablename__ = 'alertas'
    __table_args__ = {'extend_existing': True}
    
    metadata = test_metadata
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tipo_alerta: str = Field(max_length=50)
    mensaje: str = Field()
    nivel_severidad: str = Field(default="INFO", max_length=20)
    estado_alerta: str = Field(default="NUEVA", max_length=20)
    timestamp_generacion: datetime = Field(default_factory=datetime.utcnow)
    timestamp_gestion: Optional[datetime] = Field(default=None)
    usuario_gestion_id: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")
    neumatico_id: Optional[UUID] = Field(default=None, foreign_key="neumaticos.id")
    vehiculo_id: Optional[UUID] = Field(default=None, foreign_key="vehiculos.id")
    modelo_id: Optional[UUID] = Field(default=None, foreign_key="modelos_neumatico.id")
    almacen_id: Optional[UUID] = Field(default=None, foreign_key="almacenes.id")
    parametro_id: Optional[UUID] = Field(default=None, foreign_key="parametros_inventario.id")
    datos_contexto: Optional[str] = Field(default=None)  # JSON as text for SQLite

# ============================================================================
# MODELOS DE BITÁCORAS PARA TESTS
# ============================================================================

class BitacoraOperaciones(SQLModel, table=True):
    """Bitácora de operaciones para tests - Exactamente igual al esquema PostgreSQL"""
    __tablename__ = 'bitacora_operaciones'
    __table_args__ = {'extend_existing': True}
    
    metadata = test_metadata
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tipo_operacion: str = Field()  # USER-DEFINED enum en PostgreSQL
    descripcion: str = Field()
    fecha_operacion: datetime = Field(default_factory=datetime.utcnow)
    usuario_id: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")
    almacen_id: Optional[UUID] = Field(default=None, foreign_key="almacenes.id")
    vehiculo_id: Optional[UUID] = Field(default=None, foreign_key="vehiculos.id")
    estado_operacion: str = Field()  # USER-DEFINED enum en PostgreSQL
    duracion_minutos: Optional[int] = Field(default=None)
    costo_estimado: Optional[Decimal] = Field(default=None, decimal_places=2)
    costo_real: Optional[Decimal] = Field(default=None, decimal_places=2)
    proveedor_id: Optional[UUID] = Field(default=None, foreign_key="proveedores.id")
    observaciones: Optional[str] = Field(default=None)
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    actualizado_en: datetime = Field(default_factory=datetime.utcnow)
    creado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")
    actualizado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")

# ============================================================================
# MODELOS DE CATÁLOGOS PARA TESTS
# ============================================================================

class Almacenes(SQLModel, table=True):
    """Almacenes para tests - Exacto según esquema PostgreSQL"""
    __tablename__ = 'almacenes'
    __table_args__ = {'extend_existing': True}
    
    metadata = test_metadata
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)  # uuid NOT NULL
    codigo: str = Field(max_length=20, unique=True)  # character varying(20) NOT NULL UNIQUE
    nombre: str = Field(max_length=150)  # character varying(150) NOT NULL
    tipo: Optional[str] = Field(default=None, max_length=50)  # character varying(50)
    direccion: Optional[str] = Field(default=None)  # text
    activo: bool = Field(default=True)  # boolean NOT NULL DEFAULT true
    creado_en: datetime = Field(default_factory=datetime.utcnow)  # timestamp with time zone NOT NULL DEFAULT now()
    creado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")  # uuid
    actualizado_en: Optional[datetime] = Field(default=None)  # timestamp with time zone
    actualizado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")  # uuid

class Proveedores(SQLModel, table=True):
    """Proveedores para tests - Exacto según esquema PostgreSQL"""
    __tablename__ = 'proveedores'
    __table_args__ = {'extend_existing': True}
    
    metadata = test_metadata
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)  # uuid NOT NULL
    nombre: str = Field(max_length=200)  # character varying(200) NOT NULL
    codigo_proveedor: Optional[str] = Field(default=None, max_length=50, unique=True)  # character varying(50) UNIQUE
    tipo_proveedor: str = Field(max_length=50)  # character varying(50) NOT NULL
    ruc_dni: Optional[str] = Field(default=None, max_length=20)  # character varying(20)
    direccion: Optional[str] = Field(default=None)  # text
    telefono: Optional[str] = Field(default=None, max_length=20)  # character varying(20)
    email: Optional[str] = Field(default=None, max_length=100)  # character varying(100)
    contacto_principal: Optional[str] = Field(default=None, max_length=100)  # character varying(100)
    activo: bool = Field(default=True)  # boolean NOT NULL DEFAULT true
    creado_en: datetime = Field(default_factory=datetime.utcnow)  # timestamp with time zone NOT NULL DEFAULT now()
    creado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")  # uuid
    actualizado_en: Optional[datetime] = Field(default=None)  # timestamp with time zone
    actualizado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")  # uuid

class MotivosDesecho(SQLModel, table=True):
    """Motivos de desecho para tests - Exacto según esquema PostgreSQL"""
    __tablename__ = 'motivos_desecho'
    __table_args__ = {'extend_existing': True}
    
    metadata = test_metadata
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)  # uuid NOT NULL
    codigo: str = Field(max_length=20, unique=True)  # character varying(20) NOT NULL UNIQUE
    descripcion: str = Field(max_length=200)  # character varying(200) NOT NULL
    es_recuperable: bool = Field(default=False)  # boolean NOT NULL DEFAULT false
    requiere_inspeccion: bool = Field(default=False)  # boolean NOT NULL DEFAULT false
    activo: bool = Field(default=True)  # boolean NOT NULL DEFAULT true
    creado_en: datetime = Field(default_factory=datetime.utcnow)  # timestamp with time zone NOT NULL DEFAULT now()
    creado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")  # uuid
    actualizado_en: Optional[datetime] = Field(default=None)  # timestamp with time zone
    actualizado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")  # uuid

class ParametrosInventario(SQLModel, table=True):
    """Parámetros de inventario para tests - Exacto según esquema PostgreSQL"""
    __tablename__ = 'parametros_inventario'
    __table_args__ = {'extend_existing': True}
    
    metadata = test_metadata
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)  # uuid NOT NULL
    modelo_id: UUID = Field(foreign_key="modelos_neumatico.id")  # uuid NOT NULL
    ubicacion_almacen_id: UUID = Field(foreign_key="almacenes.id")  # uuid NOT NULL
    parametro_tipo: str = Field(max_length=50)  # character varying(50) NOT NULL
    valor_numerico: Optional[Decimal] = Field(default=None, decimal_places=2)  # numeric(10,2)
    valor_texto: Optional[str] = Field(default=None, max_length=100)  # character varying(100)
    unidad_medida: Optional[str] = Field(default=None, max_length=20)  # character varying(20)
    activo: bool = Field(default=True)  # boolean NOT NULL DEFAULT true
    creado_en: datetime = Field(default_factory=datetime.utcnow)  # timestamp with time zone NOT NULL DEFAULT now()
    creado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")  # uuid
    actualizado_en: Optional[datetime] = Field(default=None)  # timestamp with time zone
    actualizado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")  # uuid
