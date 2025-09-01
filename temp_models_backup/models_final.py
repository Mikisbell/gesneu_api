"""
Modelos completos del módulo de neumáticos - Todas las 36 tablas de la BD ges_neu_bd
"""
from datetime import date, datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from uuid import UUID, uuid4
from decimal import Decimal
from enum import Enum

from ...core.base_models import BaseModel
from sqlalchemy import Column, String, Boolean, Text, Integer, Numeric, Date, SmallInteger, TIMESTAMP, BigInteger
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy import text

# ============================================================================
# FABRICANTES Y MODELOS DE NEUMÁTICOS
# ============================================================================

class FabricanteNeumatico(BaseModel, table=True):
    __tablename__ = "fabricantes_neumatico"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    nombre: str = Field(max_length=100)
    pais_origen: Optional[str] = Field(default=None, max_length=50)
    sitio_web: Optional[str] = Field(default=None, max_length=200)
    contacto_tecnico: Optional[str] = Field(default=None, max_length=200)
    activo: bool = Field(default=True)

class ModeloNeumatico(BaseModel, table=True):
    __tablename__ = "modelos_neumatico"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    fabricante_id: UUID = Field(foreign_key="fabricantes_neumatico.id")
    nombre_modelo: str = Field(max_length=100)
    medida: str = Field(max_length=50)
    tipo_construccion: Optional[str] = Field(default=None, max_length=50)
    indice_carga: Optional[str] = Field(default=None, max_length=10)
    indice_velocidad: Optional[str] = Field(default=None, max_length=5)
    profundidad_banda_nueva_mm: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    presion_recomendada_psi: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    peso_kg: Optional[Decimal] = Field(default=None, max_digits=6, decimal_places=2)
    diametro_externo_mm: Optional[int] = Field(default=None)
    ancho_banda_mm: Optional[int] = Field(default=None)
    diametro_rin_pulgadas: Optional[Decimal] = Field(default=None, max_digits=4, decimal_places=1)
    tipo_vehiculo_aplicacion: Optional[str] = Field(default=None, max_length=50)
    tipo_terreno_recomendado: Optional[str] = Field(default=None, max_length=100)
    temperatura_trabajo_min_c: Optional[int] = Field(default=None)
    temperatura_trabajo_max_c: Optional[int] = Field(default=None)
    capacidad_recauchutaje: Optional[int] = Field(default=None)
    precio_referencia: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    moneda_precio: Optional[str] = Field(default=None, max_length=3)
    observaciones_tecnicas: Optional[str] = Field(default=None)
    activo: bool = Field(default=True)

class Neumatico(BaseModel, table=True):
    __tablename__ = "neumaticos"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    numero_serie: Optional[str] = Field(default=None, max_length=100)
    modelo_id: UUID = Field(foreign_key="modelos_neumatico.id")
    estado: str = Field(max_length=50, default="EN_STOCK")
    fecha_compra: Optional[date] = Field(default=None)
    precio_compra: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    proveedor_id: Optional[UUID] = Field(default=None, foreign_key="proveedores.id")
    fecha_fabricacion: Optional[date] = Field(default=None)
    semana_fabricacion: Optional[str] = Field(default=None, max_length=10)
    lote_fabricacion: Optional[str] = Field(default=None, max_length=50)
    profundidad_actual_mm: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    presion_actual_psi: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    kilometraje_acumulado: Optional[int] = Field(default=None)
    numero_reencauches: Optional[int] = Field(default=0)
    posicion_actual_id: Optional[UUID] = Field(default=None, foreign_key="posiciones_neumatico.id")
    vehiculo_actual_id: Optional[UUID] = Field(default=None, foreign_key="vehiculos.id")
    almacen_actual_id: Optional[UUID] = Field(default=None, foreign_key="almacenes.id")
    fecha_instalacion_actual: Optional[datetime] = Field(default=None)
    fecha_desmontaje_previsto: Optional[date] = Field(default=None)
    costo_total_mantenimiento: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    observaciones: Optional[str] = Field(default=None)
    codigo_interno: Optional[str] = Field(default=None, max_length=50)
    garantia_activa: Optional[bool] = Field(default=None)
    fecha_vencimiento_garantia: Optional[date] = Field(default=None)
    vida_util_estimada_km: Optional[int] = Field(default=None)
    vida_util_restante_km: Optional[int] = Field(default=None)
    eficiencia_combustible_rating: Optional[str] = Field(default=None, max_length=5)
    resistencia_rodadura_rating: Optional[str] = Field(default=None, max_length=5)
    adherencia_humedo_rating: Optional[str] = Field(default=None, max_length=5)
    nivel_ruido_db: Optional[int] = Field(default=None)
    temperatura_trabajo_actual_c: Optional[int] = Field(default=None)
    indice_desgaste_irregular: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    requiere_inspeccion: Optional[bool] = Field(default=None)
    fecha_proxima_inspeccion: Optional[date] = Field(default=None)
    motivo_baja: Optional[str] = Field(default=None, max_length=200)
    fecha_baja: Optional[date] = Field(default=None)
    valor_residual_estimado: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)

# ============================================================================
# EVENTOS Y BITÁCORAS
# ============================================================================

class EventoNeumatico(BaseModel, table=True):
    __tablename__ = "eventos_neumaticos"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    neumatico_id: UUID = Field(foreign_key="neumaticos.id")
    tipo_evento: str = Field(max_length=23)
    timestamp_evento: datetime = Field()
    usuario_id: UUID = Field(foreign_key="usuarios.id")
    vehiculo_id: Optional[UUID] = Field(default=None, foreign_key="vehiculos.id")
    posicion_id: Optional[UUID] = Field(default=None, foreign_key="posiciones_neumatico.id")
    odometro_vehiculo_en_evento: Optional[int] = Field(default=None)
    profundidad_remanente_mm: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    presion_psi: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    costo_evento: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    moneda_costo: Optional[str] = Field(default=None, max_length=3)
    proveedor_servicio_id: Optional[UUID] = Field(default=None, foreign_key="proveedores.id")
    notas: Optional[str] = Field(default=None)
    destino_desmontaje: Optional[str] = Field(default=None, max_length=13)
    motivo_desecho_id_evento: Optional[UUID] = Field(default=None, foreign_key="motivos_desecho.id")
    profundidad_post_reencauche_mm: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    datos_evento: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    relacion_evento_anterior: Optional[UUID] = Field(default=None, foreign_key="eventos_neumaticos.id")
    almacen_destino_id: Optional[UUID] = Field(default=None, foreign_key="almacenes.id")
    tipo_ruta_id: Optional[UUID] = Field(default=None, foreign_key="tipos_ruta.id")
    peso_carga_promedio_ton_evento: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    motivo_reparacion_texto: Optional[str] = Field(default=None)
    tipo_dano_detectado_texto: Optional[str] = Field(default=None)

class BitacoraMantenimiento(BaseModel, table=True):
    __tablename__ = "bitacora_mantenimiento"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    vehiculo_id: Optional[UUID] = Field(default=None, foreign_key="vehiculos.id")
    tipo_mantenimiento: str = Field(max_length=50)
    descripcion: str = Field()
    fecha_programada: Optional[date] = Field(default=None)
    fecha_realizada: Optional[datetime] = Field(default=None)
    usuario_responsable_id: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")
    proveedor_servicio_id: Optional[UUID] = Field(default=None, foreign_key="proveedores.id")
    costo_estimado: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    costo_real: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    estado: str = Field(max_length=20, default="PENDIENTE")
    observaciones: Optional[str] = Field(default=None)
    exito: Optional[bool] = Field(default=None)
    detalles: Optional[str] = Field(default=None)

class BitacoraOperaciones(BaseModel, table=True):
    __tablename__ = "bitacora_operaciones"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tipo_operacion: str = Field(max_length=18)
    descripcion: str = Field()
    fecha_operacion: datetime = Field()
    usuario_id: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")
    almacen_id: Optional[UUID] = Field(default=None, foreign_key="almacenes.id")
    vehiculo_id: Optional[UUID] = Field(default=None, foreign_key="vehiculos.id")
    estado_operacion: str = Field(max_length=10)
    duracion_minutos: Optional[int] = Field(default=None)
    costo_estimado: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    costo_real: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    proveedor_id: Optional[UUID] = Field(default=None, foreign_key="proveedores.id")
    observaciones: Optional[str] = Field(default=None)

class BitacoraOperacionesNeumaticos(BaseModel, table=True):
    __tablename__ = "bitacora_operaciones_neumaticos"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    operacion_id: UUID = Field(foreign_key="bitacora_operaciones.id")
    neumatico_id: UUID = Field(foreign_key="neumaticos.id")
    tipo_accion: str = Field(max_length=14)
    posicion_neumatico_id: Optional[UUID] = Field(default=None, foreign_key="posiciones_neumatico.id")
    profundidad_inicial_mm: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    profundidad_final_mm: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    presion_inicial_psi: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    presion_final_psi: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    kilometraje_vehiculo_km: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    observaciones: Optional[str] = Field(default=None)

# ============================================================================
# SISTEMA DE AUDITORÍA
# ============================================================================

class AuditoriaLog(SQLModel, table=True):
    __tablename__ = "auditoria_log"
    
    id: int = Field(sa_column=Column(BigInteger, primary_key=True))
    timestamp_log: datetime = Field()
    esquema_tabla: str = Field(max_length=63)
    nombre_tabla: str = Field(max_length=63)
    operacion: str = Field(max_length=10)
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

class ErrorAplicacion(SQLModel, table=True):
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
# MEDICIONES Y ESPECIFICACIONES
# ============================================================================

class MedicionProfundidad(BaseModel, table=True):
    __tablename__ = "mediciones_profundidad"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    neumatico_id: UUID = Field(foreign_key="neumaticos.id")
    fecha_medicion: datetime = Field()
    profundidad_mm: Decimal = Field(max_digits=5, decimal_places=2)
    ubicacion_medicion: str = Field()
    metodo_medicion: Optional[str] = Field(default=None)
    usuario_id: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")
    observaciones: Optional[str] = Field(default=None)

class EspecificacionDesgaste(BaseModel, table=True):
    __tablename__ = "especificaciones_desgaste"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    modelo_neumatico_id: UUID = Field(foreign_key="modelos_neumatico.id")
    tipo_posicion: str = Field(max_length=50)
    vida_util_km_min: int = Field()
    vida_util_km_max: int = Field()
    descripcion_estado: str = Field(max_length=100)

class HistorialEstadoNeumatico(BaseModel, table=True):
    __tablename__ = "historial_estados_neumaticos"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    neumatico_id: UUID = Field(foreign_key="neumaticos.id")
    estado_anterior: Optional[str] = Field(default=None, max_length=50)
    estado_nuevo: str = Field(max_length=50)
    fecha_cambio: datetime = Field()
    usuario_id: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")
    comentario: Optional[str] = Field(default=None)
    metadata: Optional[dict] = Field(default=None, sa_column=Column(JSONB))

# ============================================================================
# GARANTÍAS Y ALERTAS
# ============================================================================

class GarantiaNeumatico(BaseModel, table=True):
    __tablename__ = "garantias_neumaticos"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    neumatico_id: UUID = Field(foreign_key="neumaticos.id")
    proveedor_id: Optional[UUID] = Field(default=None, foreign_key="proveedores.id")
    tipo_garantia: str = Field(max_length=50)
    fecha_inicio: date = Field()
    fecha_fin: Optional[date] = Field(default=None)
    kilometraje_cubierto: Optional[int] = Field(default=None)
    meses_cobertura: Optional[int] = Field(default=None)
    condiciones_url: Optional[str] = Field(default=None)

class Alerta(BaseModel, table=True):
    __tablename__ = "alertas"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tipo_alerta: str = Field(max_length=50)
    mensaje: str = Field()
    nivel_severidad: str = Field(max_length=20)
    estado_alerta: str = Field(max_length=20)
    timestamp_generacion: datetime = Field()
    timestamp_gestion: Optional[datetime] = Field(default=None)
    usuario_gestion_id: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")
    neumatico_id: Optional[UUID] = Field(default=None, foreign_key="neumaticos.id")
    vehiculo_id: Optional[UUID] = Field(default=None, foreign_key="vehiculos.id")
    modelo_id: Optional[UUID] = Field(default=None, foreign_key="modelos_neumatico.id")
    almacen_id: Optional[UUID] = Field(default=None, foreign_key="almacenes.id")
    parametro_id: Optional[UUID] = Field(default=None, foreign_key="parametros_inventario.id")
    datos_contexto: Optional[dict] = Field(default=None, sa_column=Column(JSONB))

# ============================================================================
# CONFIGURACIÓN AVANZADA
# ============================================================================

class ParametroRendimientoEsperadoModelo(BaseModel, table=True):
    __tablename__ = "parametros_rendimiento_esperado_modelo"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    modelo_id: UUID = Field(foreign_key="modelos_neumatico.id")
    tipo_eje_aplicacion: str = Field(max_length=9)
    km_esperado_vida_original_min: Optional[int] = Field(default=None)
    km_esperado_vida_original_max: Optional[int] = Field(default=None)
    notas: Optional[str] = Field(default=None)

class ModeloPosicionPermitida(SQLModel, table=True):
    __tablename__ = "modelos_posiciones_permitidas"
    
    modelo_neumatico_id: UUID = Field(foreign_key="modelos_neumatico.id", primary_key=True)
    posicion_neumatico_id: UUID = Field(foreign_key="posiciones_neumatico.id", primary_key=True)
    es_recomendado: bool = Field()
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    creado_por: Optional[UUID] = Field(default=None, foreign_key="usuarios.id")

class MotivoDesecho(BaseModel, table=True):
    __tablename__ = "motivos_desecho"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    codigo: str = Field(max_length=20)
    descripcion: str = Field()
    requiere_evidencia: bool = Field()
    activo: bool = Field(default=True)

# ============================================================================
# ALMACENES Y POSICIONES
# ============================================================================

class Almacen(BaseModel, table=True):
    __tablename__ = "almacenes"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    nombre: str = Field(max_length=100)
    codigo: str = Field(max_length=20)
    ubicacion: Optional[str] = Field(default=None, max_length=200)
    capacidad_maxima: Optional[int] = Field(default=None)
    activo: bool = Field(default=True)

class PosicionNeumatico(BaseModel, table=True):
    __tablename__ = "posiciones_neumatico"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    configuracion_eje_id: UUID = Field(foreign_key="configuraciones_eje.id")
    codigo_posicion: str = Field(max_length=10)
    etiqueta_posicion: Optional[str] = Field(default=None, max_length=50)
    lado: str = Field(max_length=13)
    posicion_relativa: int = Field(sa_column=Column(SmallInteger))
    es_interna: bool = Field()
    es_direccion: bool = Field()
    es_traccion: bool = Field()
    requiere_neumatico_especifico: bool = Field()

class ConfiguracionEje(BaseModel, table=True):
    __tablename__ = "configuraciones_eje"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tipo_vehiculo_id: UUID = Field(foreign_key="tipos_vehiculo.id")
    numero_eje: int = Field(sa_column=Column(SmallInteger))
    tipo_eje: str = Field(max_length=20)
    neumaticos_por_lado: int = Field(sa_column=Column(SmallInteger))
    peso_maximo_eje_kg: Optional[Decimal] = Field(default=None, max_digits=8, decimal_places=2)
    presion_recomendada_psi: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=2)
    observaciones: Optional[str] = Field(default=None)
    activo: bool = Field(default=True)

class ParametroInventario(BaseModel, table=True):
    __tablename__ = "parametros_inventario"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    parametro_tipo: str = Field(max_length=33)
    modelo_id: UUID = Field(foreign_key="modelos_neumatico.id")
    ubicacion_almacen_id: Optional[UUID] = Field(default=None, foreign_key="almacenes.id")
    valor_numerico: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    valor_texto: Optional[str] = Field(default=None)
    activo: bool = Field(default=True)
    notas: Optional[str] = Field(default=None)
