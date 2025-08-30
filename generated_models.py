from typing import Optional
import datetime
import decimal
import uuid

from sqlalchemy import BigInteger, Boolean, CheckConstraint, Column, Date, DateTime, Double, Enum, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, SmallInteger, String, TEXT, Table, Text, UniqueConstraint, Uuid, VARCHAR, text
from sqlalchemy.dialects.postgresql import DOMAIN, INTERVAL, JSONB, OID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class AuditoriaRolesUsuarios(Base):
    __tablename__ = 'auditoria_roles_usuarios'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='auditoria_roles_usuarios_pkey'),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    usuario_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    rol_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    accion: Mapped[str] = mapped_column(String(10), nullable=False)
    ejecutado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    ejecutado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    metadata_: Mapped[Optional[dict]] = mapped_column('metadata', JSONB)


class BitacoraMantenimiento(Base):
    __tablename__ = 'bitacora_mantenimiento'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='bitacora_mantenimiento_pkey'),
        Index('idx_bitacora_mantenimiento_exito', 'exito'),
        Index('idx_bitacora_mantenimiento_fecha', 'fecha_ejecucion'),
        Index('idx_bitacora_mantenimiento_tipo', 'tipo'),
        {'comment': 'Registra la ejecución de tareas de mantenimiento programadas o '
                'manuales.'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fecha_ejecucion: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    tipo: Mapped[str] = mapped_column(String(50), nullable=False, comment='Tipo de mantenimiento ejecutado (ej: DIARIO, REINDEX, VACUUM, ANALYZE)')
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    ejecutado_por: Mapped[str] = mapped_column(String, nullable=False, server_default=text('CURRENT_USER'))
    duracion: Mapped[Optional[datetime.timedelta]] = mapped_column(INTERVAL)
    exito: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))
    detalles: Mapped[Optional[str]] = mapped_column(Text)


class ConfiguracionAuditoria(Base):
    __tablename__ = 'configuracion_auditoria'
    __table_args__ = (
        CheckConstraint("prioridad::text = ANY (ARRAY['low'::character varying::text, 'medium'::character varying::text, 'high'::character varying::text])", name='configuracion_auditoria_prioridad_check'),
        PrimaryKeyConstraint('nombre_tabla', name='configuracion_auditoria_pkey'),
        {'comment': 'Configuración de auditoría para las tablas del sistema'}
    )

    nombre_tabla: Mapped[str] = mapped_column(String(63), primary_key=True, comment='Nombre de la tabla a auditar')
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'), comment='Indica si la auditoría está activa para esta tabla')
    prioridad: Mapped[Optional[str]] = mapped_column(String(20), comment='Nivel de prioridad de auditoría (low, medium, high)')
    campos_excluidos: Mapped[Optional[dict]] = mapped_column(JSONB, server_default=text("'{}'::jsonb"), comment='Campos que no se auditarán en esta tabla')
    creado_en: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'), comment='Fecha de creación del registro')
    actualizado_en: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'), comment='Fecha de última actualización del registro')


class ErroresAplicacion(Base):
    __tablename__ = 'errores_aplicacion'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='errores_aplicacion_pkey'),
        Index('idx_errores_aplicacion_creado_en', 'creado_en'),
        Index('idx_errores_aplicacion_nombre_funcion', 'nombre_funcion'),
        Index('idx_errores_aplicacion_resuelto', 'resuelto'),
        {'comment': 'Registro de errores de la aplicación para seguimiento y '
                'depuración'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'), comment='Identificador único del error')
    nombre_funcion: Mapped[str] = mapped_column(Text, nullable=False, comment='Nombre de la función o procedimiento donde ocurrió el error')
    mensaje_error: Mapped[str] = mapped_column(Text, nullable=False, comment='Mensaje de error generado')
    creado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'), comment='Fecha y hora en que se registró el error')
    detalles: Mapped[Optional[dict]] = mapped_column(JSONB, comment='Información adicional sobre el error en formato JSON')
    creado_por: Mapped[Optional[str]] = mapped_column(Text, server_default=text("'SISTEMA'::text"), comment='Usuario o sistema que generó el error')
    resuelto: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'), comment='Indica si el error ha sido resuelto')
    resuelto_por: Mapped[Optional[str]] = mapped_column(Text, comment='Usuario que marcó el error como resuelto')
    resuelto_en: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), comment='Fecha y hora en que se resolvió el error')
    comentario_resolucion: Mapped[Optional[str]] = mapped_column(Text, comment='Comentarios sobre la resolución del error')


t_mv_desempeno_modelos = Table(
    'mv_desempeno_modelos', Base.metadata,
    Column('modelo_id', Uuid),
    Column('modelo_nombre', String(100)),
    Column('fabricante_nombre', String(100)),
    Column('medida', String(20)),
    Column('indice_carga', String(5)),
    Column('indice_velocidad', String(2)),
    Column('profundidad_original_mm', Numeric(5, 2)),
    Column('tasa_desgaste_esperada_mm_km', Numeric(10, 8)),
    Column('vida_util_teorica_km', Integer),
    Column('modelo_activo', Boolean),
    Column('total_neumaticos', BigInteger),
    Column('instalados', BigInteger),
    Column('en_stock', BigInteger),
    Column('en_reparacion', BigInteger),
    Column('en_reencauche', BigInteger),
    Column('en_transito', BigInteger),
    Column('desechados', BigInteger),
    Column('vida_util_promedio_km', Numeric),
    Column('tasa_desgaste_promedio_mm_km', Numeric),
    Column('profundidad_promedio_mm', Numeric),
    Column('profundidad_minima_mm', Numeric),
    Column('profundidad_maxima_mm', Numeric),
    Column('kilometraje_vida_promedio', Numeric),
    Column('max_kilometraje_vida', Integer),
    Column('min_kilometraje_vida_no_cero', Integer),
    Column('vida_actual_promedio', Numeric),
    Column('fecha_actualizacion', DateTime(True)),
    Column('tiene_datos_rendimiento', Boolean),
    Index('idx_mv_desempeno_modelos_id', 'modelo_id', unique=True)
)


t_mv_eventos_recientes = Table(
    'mv_eventos_recientes', Base.metadata,
    Column('id', Uuid),
    Column('tipo_evento', Enum('COMPRA', 'INSTALACION', 'DESMONTAJE', 'INSPECCION', 'ROTACION', 'REPARACION_ENTRADA', 'REPARACION_SALIDA', 'REENCAUCHE_ENTRADA', 'REENCAUCHE_SALIDA', 'DESECHO', 'AJUSTE_INVENTARIO', 'TRANSFERENCIA_UBICACION', name='tipo_evento_neumatico_enum')),
    Column('timestamp_evento', DateTime(True)),
    Column('numero_serie', String(100)),
    Column('usuario_id', Uuid),
    Column('vehiculo_id', Uuid),
    Column('datos_evento', JSONB),
    Index('idx_mv_eventos_recientes_fecha', 'timestamp_evento'),
    Index('idx_mv_eventos_recientes_id', 'id', unique=True),
    Index('idx_mv_eventos_recientes_serie', 'numero_serie')
)


t_mv_permisos_usuario = Table(
    'mv_permisos_usuario', Base.metadata,
    Column('usuario_id', Uuid),
    Column('username', String(50)),
    Column('nombre_recurso', String(100)),
    Column('accion', String(100)),
    Column('descripcion', Text),
    Column('rol', String(100)),
    Column('rol_asignado_en', DateTime(True)),
    Index('idx_mv_permisos_usuario', 'usuario_id', 'nombre_recurso', 'accion', unique=True)
)


t_mv_resumen_neumaticos_estado = Table(
    'mv_resumen_neumaticos_estado', Base.metadata,
    Column('estado_actual', Enum('EN_STOCK', 'INSTALADO', 'EN_REPARACION', 'EN_REENCAUCHE', 'DESECHADO', 'EN_TRANSITO', name='estado_neumatico_enum')),
    Column('cantidad', BigInteger),
    Column('vida_util_promedio_km', Numeric),
    Column('profundidad_minima_mm', Numeric),
    Column('profundidad_maxima_mm', Numeric),
    Index('idx_mv_resumen_estado', 'estado_actual', unique=True)
)


t_neumaticos_vista_publica = Table(
    'neumaticos_vista_publica', Base.metadata,
    Column('id', Uuid),
    Column('numero_serie', String(100)),
    Column('dot', DOMAIN('dot_code', TEXT(), constraint_name='dot_code_check', not_null=False, check=text("VALUE ~ '^[A-Z0-9]{2,4}[A-Z0-9]{2}[A-Z0-9]{3,4}$'::text"))),
    Column('modelo_id', Uuid),
    Column('fecha_compra', Date),
    Column('fecha_fabricacion', Date),
    Column('estado_actual', Enum('EN_STOCK', 'INSTALADO', 'EN_REPARACION', 'EN_REENCAUCHE', 'DESECHADO', 'EN_TRANSITO', name='estado_neumatico_enum')),
    Column('es_reencauchado', Boolean),
    Column('vida_actual', SmallInteger),
    Column('ubicacion_actual_vehiculo_id', Uuid),
    Column('ubicacion_actual_posicion_id', Uuid),
    Column('ubicacion_almacen_id', Uuid),
    Column('fecha_ultimo_evento', DateTime(True)),
    Column('kilometraje_acumulado', Integer),
    Column('reencauches_realizados', SmallInteger)
)


class ParametrosSistema(Base):
    __tablename__ = 'parametros_sistema'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='parametros_sistema_pkey'),
        UniqueConstraint('clave', name='parametros_sistema_clave_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    clave: Mapped[str] = mapped_column(String(100), nullable=False)
    valor: Mapped[str] = mapped_column(Text, nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text)
    creado_en: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))
    actualizado_en: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))
    creado_por: Mapped[Optional[str]] = mapped_column(String(100), server_default=text("'SISTEMA'::character varying"))
    actualizado_por: Mapped[Optional[str]] = mapped_column(String(100), server_default=text("'SISTEMA'::character varying"))


class Permisos(Base):
    __tablename__ = 'permisos'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='permisos_pkey'),
        UniqueConstraint('nombre_recurso', 'accion', name='uq_permiso_recurso_accion'),
        Index('idx_permisos_recurso_accion', 'nombre_recurso', 'accion'),
        {'comment': 'Permisos granulares del sistema'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('public.gen_random_uuid()'))
    nombre_recurso: Mapped[str] = mapped_column(String(100), nullable=False)
    accion: Mapped[str] = mapped_column(String(100), nullable=False)
    creado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    descripcion: Mapped[Optional[str]] = mapped_column(Text)

    roles_permisos: Mapped[list['RolesPermisos']] = relationship('RolesPermisos', back_populates='permiso')


t_pg_stat_statements = Table(
    'pg_stat_statements', Base.metadata,
    Column('userid', OID),
    Column('dbid', OID),
    Column('toplevel', Boolean),
    Column('queryid', BigInteger),
    Column('query', Text),
    Column('plans', BigInteger),
    Column('total_plan_time', Double(53)),
    Column('min_plan_time', Double(53)),
    Column('max_plan_time', Double(53)),
    Column('mean_plan_time', Double(53)),
    Column('stddev_plan_time', Double(53)),
    Column('calls', BigInteger),
    Column('total_exec_time', Double(53)),
    Column('min_exec_time', Double(53)),
    Column('max_exec_time', Double(53)),
    Column('mean_exec_time', Double(53)),
    Column('stddev_exec_time', Double(53)),
    Column('rows', BigInteger),
    Column('shared_blks_hit', BigInteger),
    Column('shared_blks_read', BigInteger),
    Column('shared_blks_dirtied', BigInteger),
    Column('shared_blks_written', BigInteger),
    Column('local_blks_hit', BigInteger),
    Column('local_blks_read', BigInteger),
    Column('local_blks_dirtied', BigInteger),
    Column('local_blks_written', BigInteger),
    Column('temp_blks_read', BigInteger),
    Column('temp_blks_written', BigInteger),
    Column('shared_blk_read_time', Double(53)),
    Column('shared_blk_write_time', Double(53)),
    Column('local_blk_read_time', Double(53)),
    Column('local_blk_write_time', Double(53)),
    Column('temp_blk_read_time', Double(53)),
    Column('temp_blk_write_time', Double(53)),
    Column('wal_records', BigInteger),
    Column('wal_fpi', BigInteger),
    Column('wal_bytes', Numeric),
    Column('jit_functions', BigInteger),
    Column('jit_generation_time', Double(53)),
    Column('jit_inlining_count', BigInteger),
    Column('jit_inlining_time', Double(53)),
    Column('jit_optimization_count', BigInteger),
    Column('jit_optimization_time', Double(53)),
    Column('jit_emission_count', BigInteger),
    Column('jit_emission_time', Double(53)),
    Column('jit_deform_count', BigInteger),
    Column('jit_deform_time', Double(53)),
    Column('stats_since', DateTime(True)),
    Column('minmax_stats_since', DateTime(True))
)


t_pg_stat_statements_info = Table(
    'pg_stat_statements_info', Base.metadata,
    Column('dealloc', BigInteger),
    Column('stats_reset', DateTime(True))
)


class TareasProgramadas(Base):
    __tablename__ = 'tareas_programadas'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='tareas_programadas_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre_tarea: Mapped[str] = mapped_column(String(100), nullable=False)
    frecuencia_dias: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('1'))
    descripcion: Mapped[Optional[str]] = mapped_column(Text)
    ultima_ejecucion: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    proxima_ejecucion: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    activa: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))
    script_sql: Mapped[Optional[str]] = mapped_column(Text)
    creado_en: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))
    creado_por: Mapped[Optional[str]] = mapped_column(String(100), server_default=text("'SISTEMA'::character varying"))
    actualizado_en: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    actualizado_por: Mapped[Optional[str]] = mapped_column(String(100))


class Usuarios(Base):
    __tablename__ = 'usuarios'
    __table_args__ = (
        ForeignKeyConstraint(['actualizado_por'], ['usuarios.id'], ondelete='SET NULL', name='usuarios_actualizado_por_fkey'),
        ForeignKeyConstraint(['creado_por'], ['usuarios.id'], ondelete='SET NULL', name='usuarios_creado_por_fkey'),
        PrimaryKeyConstraint('id', name='usuarios_pkey'),
        UniqueConstraint('email', name='usuarios_email_key'),
        UniqueConstraint('username', name='usuarios_username_key'),
        {'comment': 'Usuarios del sistema con acceso a la aplicación'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('public.gen_random_uuid()'))
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    creado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    nombre_completo: Mapped[Optional[str]] = mapped_column(String(200))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    password_hash: Mapped[Optional[str]] = mapped_column(Text)
    ultimo_login: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    creado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    actualizado_en: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    actualizado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    usuarios: Mapped[Optional['Usuarios']] = relationship('Usuarios', remote_side=[id], foreign_keys=[actualizado_por], back_populates='usuarios_reverse')
    usuarios_reverse: Mapped[list['Usuarios']] = relationship('Usuarios', remote_side=[actualizado_por], foreign_keys=[actualizado_por], back_populates='usuarios')
    usuarios_: Mapped[Optional['Usuarios']] = relationship('Usuarios', remote_side=[id], foreign_keys=[creado_por], back_populates='usuarios__reverse')
    usuarios__reverse: Mapped[list['Usuarios']] = relationship('Usuarios', remote_side=[creado_por], foreign_keys=[creado_por], back_populates='usuarios_')
    almacenes: Mapped[list['Almacenes']] = relationship('Almacenes', foreign_keys='[Almacenes.actualizado_por]', back_populates='usuarios')
    almacenes_: Mapped[list['Almacenes']] = relationship('Almacenes', foreign_keys='[Almacenes.creado_por]', back_populates='usuarios_')
    auditoria_log: Mapped[list['AuditoriaLog']] = relationship('AuditoriaLog', back_populates='usuario_aplicacion')
    fabricantes_neumatico: Mapped[list['FabricantesNeumatico']] = relationship('FabricantesNeumatico', foreign_keys='[FabricantesNeumatico.actualizado_por]', back_populates='usuarios')
    fabricantes_neumatico_: Mapped[list['FabricantesNeumatico']] = relationship('FabricantesNeumatico', foreign_keys='[FabricantesNeumatico.creado_por]', back_populates='usuarios_')
    motivos_desecho: Mapped[list['MotivosDesecho']] = relationship('MotivosDesecho', foreign_keys='[MotivosDesecho.actualizado_por]', back_populates='usuarios')
    motivos_desecho_: Mapped[list['MotivosDesecho']] = relationship('MotivosDesecho', foreign_keys='[MotivosDesecho.creado_por]', back_populates='usuarios_')
    proveedores: Mapped[list['Proveedores']] = relationship('Proveedores', foreign_keys='[Proveedores.actualizado_por]', back_populates='usuarios')
    proveedores_: Mapped[list['Proveedores']] = relationship('Proveedores', foreign_keys='[Proveedores.creado_por]', back_populates='usuarios_')
    roles: Mapped[list['Roles']] = relationship('Roles', foreign_keys='[Roles.actualizado_por]', back_populates='usuarios')
    roles_: Mapped[list['Roles']] = relationship('Roles', foreign_keys='[Roles.creado_por]', back_populates='usuarios_')
    rutas: Mapped[list['Rutas']] = relationship('Rutas', foreign_keys='[Rutas.actualizado_por]', back_populates='usuarios')
    rutas_: Mapped[list['Rutas']] = relationship('Rutas', foreign_keys='[Rutas.creado_por]', back_populates='usuarios_')
    tipos_ruta: Mapped[list['TiposRuta']] = relationship('TiposRuta', foreign_keys='[TiposRuta.actualizado_por]', back_populates='usuarios')
    tipos_ruta_: Mapped[list['TiposRuta']] = relationship('TiposRuta', foreign_keys='[TiposRuta.creado_por]', back_populates='usuarios_')
    tipos_vehiculo: Mapped[list['TiposVehiculo']] = relationship('TiposVehiculo', foreign_keys='[TiposVehiculo.actualizado_por]', back_populates='usuarios')
    tipos_vehiculo_: Mapped[list['TiposVehiculo']] = relationship('TiposVehiculo', foreign_keys='[TiposVehiculo.creado_por]', back_populates='usuarios_')
    configuraciones_eje: Mapped[list['ConfiguracionesEje']] = relationship('ConfiguracionesEje', foreign_keys='[ConfiguracionesEje.actualizado_por]', back_populates='usuarios')
    configuraciones_eje_: Mapped[list['ConfiguracionesEje']] = relationship('ConfiguracionesEje', foreign_keys='[ConfiguracionesEje.creado_por]', back_populates='usuarios_')
    modelos_neumatico: Mapped[list['ModelosNeumatico']] = relationship('ModelosNeumatico', foreign_keys='[ModelosNeumatico.actualizado_por]', back_populates='usuarios')
    modelos_neumatico_: Mapped[list['ModelosNeumatico']] = relationship('ModelosNeumatico', foreign_keys='[ModelosNeumatico.creado_por]', back_populates='usuarios_')
    roles_permisos: Mapped[list['RolesPermisos']] = relationship('RolesPermisos', back_populates='usuarios')
    usuarios_roles: Mapped[list['UsuariosRoles']] = relationship('UsuariosRoles', foreign_keys='[UsuariosRoles.asignado_por]', back_populates='usuarios')
    usuarios_roles_: Mapped[list['UsuariosRoles']] = relationship('UsuariosRoles', foreign_keys='[UsuariosRoles.usuario_id]', back_populates='usuario')
    vehiculos: Mapped[list['Vehiculos']] = relationship('Vehiculos', foreign_keys='[Vehiculos.actualizado_por]', back_populates='usuarios')
    vehiculos_: Mapped[list['Vehiculos']] = relationship('Vehiculos', foreign_keys='[Vehiculos.creado_por]', back_populates='usuarios_')
    bitacora_operaciones: Mapped[list['BitacoraOperaciones']] = relationship('BitacoraOperaciones', foreign_keys='[BitacoraOperaciones.actualizado_por]', back_populates='usuarios')
    bitacora_operaciones_: Mapped[list['BitacoraOperaciones']] = relationship('BitacoraOperaciones', foreign_keys='[BitacoraOperaciones.creado_por]', back_populates='usuarios_')
    bitacora_operaciones1: Mapped[list['BitacoraOperaciones']] = relationship('BitacoraOperaciones', foreign_keys='[BitacoraOperaciones.usuario_id]', back_populates='usuario')
    especificaciones_desgaste: Mapped[list['EspecificacionesDesgaste']] = relationship('EspecificacionesDesgaste', foreign_keys='[EspecificacionesDesgaste.actualizado_por]', back_populates='usuarios')
    especificaciones_desgaste_: Mapped[list['EspecificacionesDesgaste']] = relationship('EspecificacionesDesgaste', foreign_keys='[EspecificacionesDesgaste.creado_por]', back_populates='usuarios_')
    neumaticos: Mapped[list['Neumaticos']] = relationship('Neumaticos', foreign_keys='[Neumaticos.actualizado_por]', back_populates='usuarios')
    neumaticos_: Mapped[list['Neumaticos']] = relationship('Neumaticos', foreign_keys='[Neumaticos.creado_por]', back_populates='usuarios_')
    parametros_inventario: Mapped[list['ParametrosInventario']] = relationship('ParametrosInventario', foreign_keys='[ParametrosInventario.actualizado_por]', back_populates='usuarios')
    parametros_inventario_: Mapped[list['ParametrosInventario']] = relationship('ParametrosInventario', foreign_keys='[ParametrosInventario.creado_por]', back_populates='usuarios_')
    parametros_rendimiento_esperado_modelo: Mapped[list['ParametrosRendimientoEsperadoModelo']] = relationship('ParametrosRendimientoEsperadoModelo', foreign_keys='[ParametrosRendimientoEsperadoModelo.actualizado_por]', back_populates='usuarios')
    parametros_rendimiento_esperado_modelo_: Mapped[list['ParametrosRendimientoEsperadoModelo']] = relationship('ParametrosRendimientoEsperadoModelo', foreign_keys='[ParametrosRendimientoEsperadoModelo.creado_por]', back_populates='usuarios_')
    posiciones_neumatico: Mapped[list['PosicionesNeumatico']] = relationship('PosicionesNeumatico', foreign_keys='[PosicionesNeumatico.actualizado_por]', back_populates='usuarios')
    posiciones_neumatico_: Mapped[list['PosicionesNeumatico']] = relationship('PosicionesNeumatico', foreign_keys='[PosicionesNeumatico.creado_por]', back_populates='usuarios_')
    registros_odometro: Mapped[list['RegistrosOdometro']] = relationship('RegistrosOdometro', back_populates='usuarios')
    alertas: Mapped[list['Alertas']] = relationship('Alertas', back_populates='usuario_gestion')
    bitacora_operaciones_neumaticos: Mapped[list['BitacoraOperacionesNeumaticos']] = relationship('BitacoraOperacionesNeumaticos', foreign_keys='[BitacoraOperacionesNeumaticos.actualizado_por]', back_populates='usuarios')
    bitacora_operaciones_neumaticos_: Mapped[list['BitacoraOperacionesNeumaticos']] = relationship('BitacoraOperacionesNeumaticos', foreign_keys='[BitacoraOperacionesNeumaticos.creado_por]', back_populates='usuarios_')
    eventos_neumaticos: Mapped[list['EventosNeumaticos']] = relationship('EventosNeumaticos', back_populates='usuario')
    garantias_neumaticos: Mapped[list['GarantiasNeumaticos']] = relationship('GarantiasNeumaticos', foreign_keys='[GarantiasNeumaticos.actualizado_por]', back_populates='usuarios')
    garantias_neumaticos_: Mapped[list['GarantiasNeumaticos']] = relationship('GarantiasNeumaticos', foreign_keys='[GarantiasNeumaticos.creado_por]', back_populates='usuarios_')
    historial_estados_neumaticos: Mapped[list['HistorialEstadosNeumaticos']] = relationship('HistorialEstadosNeumaticos', back_populates='usuario')
    mediciones_profundidad: Mapped[list['MedicionesProfundidad']] = relationship('MedicionesProfundidad', foreign_keys='[MedicionesProfundidad.actualizado_por]', back_populates='usuarios')
    mediciones_profundidad_: Mapped[list['MedicionesProfundidad']] = relationship('MedicionesProfundidad', foreign_keys='[MedicionesProfundidad.creado_por]', back_populates='usuarios_')
    mediciones_profundidad1: Mapped[list['MedicionesProfundidad']] = relationship('MedicionesProfundidad', foreign_keys='[MedicionesProfundidad.usuario_id]', back_populates='usuario')
    modelos_posiciones_permitidas: Mapped[list['ModelosPosicionesPermitidas']] = relationship('ModelosPosicionesPermitidas', back_populates='usuarios')


t_v_auditoria_motivos_desecho = Table(
    'v_auditoria_motivos_desecho', Base.metadata,
    Column('id', BigInteger),
    Column('fecha_hora', DateTime(True)),
    Column('operacion', String(10)),
    Column('usuario', String),
    Column('direccion_ip', String),
    Column('datos_antiguos', JSONB),
    Column('datos_nuevos', JSONB),
    Column('cambios', JSONB),
    Column('motivo_id', Uuid),
    Column('codigo_motivo', Text),
    Column('descripcion', Text),
    Column('requiere_evidencia', Boolean),
    Column('activo', Boolean),
    comment='Vista para consultar los registros de auditoría de la tabla motivos_desecho. \n\nIncluye todos los cambios realizados en la tabla con información detallada de cada operación.'
)


t_vw_auditoria = Table(
    'vw_auditoria', Base.metadata,
    Column('id', BigInteger),
    Column('timestamp_log', DateTime(True)),
    Column('nombre_tabla', String(63)),
    Column('operacion', String(10)),
    Column('usuario_db', String(63)),
    Column('id_entidad', Text),
    Column('datos_antiguos', JSONB),
    Column('datos_nuevos', JSONB),
    Column('cambios', JSONB),
    Column('contexto_aplicacion', JSONB),
    Column('query_ejecutada', Text),
    Column('tipo_operacion', Text)
)


t_vw_auditoria_permisos = Table(
    'vw_auditoria_permisos', Base.metadata,
    Column('usuario_id', Uuid),
    Column('username', String(50)),
    Column('rol', String(100)),
    Column('permiso', Text),
    Column('asignado_en', DateTime(True)),
    Column('asignado_por', String(50))
)


class Almacenes(Base):
    __tablename__ = 'almacenes'
    __table_args__ = (
        ForeignKeyConstraint(['actualizado_por'], ['usuarios.id'], ondelete='SET NULL', name='almacenes_actualizado_por_fkey'),
        ForeignKeyConstraint(['creado_por'], ['usuarios.id'], ondelete='SET NULL', name='almacenes_creado_por_fkey'),
        PrimaryKeyConstraint('id', name='almacenes_pkey'),
        UniqueConstraint('codigo', name='almacenes_codigo_key'),
        {'comment': 'Ubicaciones físicas donde se almacenan los neumáticos'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('public.gen_random_uuid()'))
    codigo: Mapped[str] = mapped_column(String(20), nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    creado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    tipo: Mapped[Optional[str]] = mapped_column(String(50))
    direccion: Mapped[Optional[str]] = mapped_column(Text)
    creado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    actualizado_en: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    actualizado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    usuarios: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[actualizado_por], back_populates='almacenes')
    usuarios_: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[creado_por], back_populates='almacenes_')
    bitacora_operaciones: Mapped[list['BitacoraOperaciones']] = relationship('BitacoraOperaciones', back_populates='almacen')
    neumaticos: Mapped[list['Neumaticos']] = relationship('Neumaticos', back_populates='ubicacion_almacen')
    parametros_inventario: Mapped[list['ParametrosInventario']] = relationship('ParametrosInventario', back_populates='ubicacion_almacen')
    alertas: Mapped[list['Alertas']] = relationship('Alertas', back_populates='almacen')
    eventos_neumaticos: Mapped[list['EventosNeumaticos']] = relationship('EventosNeumaticos', back_populates='almacen_destino')


class AuditoriaLog(Base):
    __tablename__ = 'auditoria_log'
    __table_args__ = (
        CheckConstraint("operacion::text = ANY (ARRAY['INSERT'::character varying::text, 'UPDATE'::character varying::text, 'DELETE'::character varying::text])", name='auditoria_log_operacion_check'),
        ForeignKeyConstraint(['usuario_aplicacion_id'], ['usuarios.id'], ondelete='SET NULL', name='auditoria_log_usuario_aplicacion_id_fkey'),
        PrimaryKeyConstraint('id', name='auditoria_log_pkey'),
        Index('idx_audit_log_cambios_gin', 'cambios'),
        Index('idx_audit_log_datos_antiguos_gin', 'datos_antiguos'),
        Index('idx_audit_log_datos_nuevos_gin', 'datos_nuevos'),
        Index('idx_audit_log_id_entidad', 'id_entidad'),
        Index('idx_audit_log_nombre_tabla_lower'),
        Index('idx_audit_log_operacion_timestamp', 'operacion', 'timestamp_log'),
        Index('idx_audit_log_tabla_timestamp', 'nombre_tabla', 'timestamp_log'),
        Index('idx_audit_log_usuario_timestamp', 'usuario_aplicacion_username', 'timestamp_log'),
        {'comment': 'Registro centralizado de auditoría para todas las operaciones DML '
                'en la base de datos'}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    timestamp_log: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    esquema_tabla: Mapped[str] = mapped_column(String(63), nullable=False)
    nombre_tabla: Mapped[str] = mapped_column(String(63), nullable=False)
    operacion: Mapped[str] = mapped_column(String(10), nullable=False)
    usuario_db: Mapped[str] = mapped_column(String(63), nullable=False, server_default=text('CURRENT_USER'))
    usuario_aplicacion_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    usuario_aplicacion_username: Mapped[Optional[str]] = mapped_column(String(50))
    direccion_ip: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    id_entidad: Mapped[Optional[str]] = mapped_column(Text, comment='Identificador de la entidad afectada (puede ser NULL). Almacena un hash MD5 de las claves primarias para identificar el registro.')
    datos_antiguos: Mapped[Optional[dict]] = mapped_column(JSONB)
    datos_nuevos: Mapped[Optional[dict]] = mapped_column(JSONB)
    cambios: Mapped[Optional[dict]] = mapped_column(JSONB)
    contexto_aplicacion: Mapped[Optional[dict]] = mapped_column(JSONB)
    query_ejecutada: Mapped[Optional[str]] = mapped_column(Text)

    usuario_aplicacion: Mapped[Optional['Usuarios']] = relationship('Usuarios', back_populates='auditoria_log')


class FabricantesNeumatico(Base):
    __tablename__ = 'fabricantes_neumatico'
    __table_args__ = (
        CheckConstraint('length(nombre::text) >= 2', name='fabricantes_neumatico_nombre_length'),
        ForeignKeyConstraint(['actualizado_por'], ['usuarios.id'], ondelete='SET NULL', name='fabricantes_neumatico_actualizado_por_fkey'),
        ForeignKeyConstraint(['creado_por'], ['usuarios.id'], ondelete='SET NULL', name='fabricantes_neumatico_creado_por_fkey'),
        PrimaryKeyConstraint('id', name='fabricantes_neumatico_pkey'),
        UniqueConstraint('codigo_abreviado', name='fabricantes_neumatico_codigo_abreviado_key'),
        Index('idx_fabricantes_nombre_unique', unique=True)
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('public.gen_random_uuid()'))
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    creado_en: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    codigo_abreviado: Mapped[Optional[str]] = mapped_column(String(10))
    pais_origen: Mapped[Optional[str]] = mapped_column(String(50))
    sitio_web: Mapped[Optional[str]] = mapped_column(String(255))
    creado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    actualizado_en: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    actualizado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    usuarios: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[actualizado_por], back_populates='fabricantes_neumatico')
    usuarios_: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[creado_por], back_populates='fabricantes_neumatico_')
    modelos_neumatico: Mapped[list['ModelosNeumatico']] = relationship('ModelosNeumatico', back_populates='fabricante')


class MotivosDesecho(Base):
    __tablename__ = 'motivos_desecho'
    __table_args__ = (
        ForeignKeyConstraint(['actualizado_por'], ['usuarios.id'], ondelete='SET NULL', name='motivos_desecho_actualizado_por_fkey'),
        ForeignKeyConstraint(['creado_por'], ['usuarios.id'], ondelete='SET NULL', name='motivos_desecho_creado_por_fkey'),
        PrimaryKeyConstraint('id', name='motivos_desecho_pkey'),
        UniqueConstraint('codigo', name='motivos_desecho_codigo_key'),
        {'comment': 'Motivos por los que un neumático puede ser dado de baja'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('public.gen_random_uuid()'))
    codigo: Mapped[str] = mapped_column(String(20), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    requiere_evidencia: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    creado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    creado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    actualizado_en: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    actualizado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    usuarios: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[actualizado_por], back_populates='motivos_desecho')
    usuarios_: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[creado_por], back_populates='motivos_desecho_')
    neumaticos: Mapped[list['Neumaticos']] = relationship('Neumaticos', back_populates='motivo_desecho')
    eventos_neumaticos: Mapped[list['EventosNeumaticos']] = relationship('EventosNeumaticos', back_populates='motivos_desecho')


class Proveedores(Base):
    __tablename__ = 'proveedores'
    __table_args__ = (
        CheckConstraint("ruc IS NULL OR ruc::text ~ '^10[0-9]{9}$'::text OR ruc::text ~ '^20[0-9]{9}$'::text OR ruc::text ~ '^1[5-9][0-9]{9}$'::text OR ruc::text ~ '^5[0-9][0-9]{9}$'::text OR ruc::text ~ '^(2[7-9]|[3-9][0-9])[0-9]{10}$'::text", name='proveedores_ruc_check'),
        ForeignKeyConstraint(['actualizado_por'], ['usuarios.id'], ondelete='SET NULL', name='proveedores_actualizado_por_fkey'),
        ForeignKeyConstraint(['creado_por'], ['usuarios.id'], ondelete='SET NULL', name='proveedores_creado_por_fkey'),
        PrimaryKeyConstraint('id', name='proveedores_pkey'),
        UniqueConstraint('ruc', name='proveedores_ruc_key'),
        Index('idx_proveedores_nombre_unique', unique=True),
        {'comment': 'Proveedores de neumáticos y servicios relacionados'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('public.gen_random_uuid()'))
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    creado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    tipo: Mapped[Optional[str]] = mapped_column(Enum('FABRICANTE', 'DISTRIBUIDOR', 'SERVICIO_REPARACION', 'SERVICIO_REENCAUCHE', 'OTRO', name='tipoproveedorenum'))
    ruc: Mapped[Optional[str]] = mapped_column(String(11))
    contacto_principal: Mapped[Optional[str]] = mapped_column(Text)
    telefono: Mapped[Optional[str]] = mapped_column(String(50))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    direccion: Mapped[Optional[str]] = mapped_column(Text)
    creado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    actualizado_en: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    actualizado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    usuarios: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[actualizado_por], back_populates='proveedores')
    usuarios_: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[creado_por], back_populates='proveedores_')
    bitacora_operaciones: Mapped[list['BitacoraOperaciones']] = relationship('BitacoraOperaciones', back_populates='proveedor')
    neumaticos: Mapped[list['Neumaticos']] = relationship('Neumaticos', back_populates='proveedor_compra')
    eventos_neumaticos: Mapped[list['EventosNeumaticos']] = relationship('EventosNeumaticos', back_populates='proveedor_servicio')
    garantias_neumaticos: Mapped[list['GarantiasNeumaticos']] = relationship('GarantiasNeumaticos', back_populates='proveedor')


class Roles(Base):
    __tablename__ = 'roles'
    __table_args__ = (
        ForeignKeyConstraint(['actualizado_por'], ['usuarios.id'], ondelete='SET NULL', name='roles_actualizado_por_fkey'),
        ForeignKeyConstraint(['creado_por'], ['usuarios.id'], ondelete='SET NULL', name='roles_creado_por_fkey'),
        PrimaryKeyConstraint('id', name='roles_pkey'),
        UniqueConstraint('nombre', name='roles_nombre_key'),
        Index('idx_roles_nombre_lower'),
        Index('idx_roles_nombre_lower_unaccent'),
        {'comment': 'Roles de usuario en el sistema'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('public.gen_random_uuid()'))
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    es_rol_sistema: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    creado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    descripcion: Mapped[Optional[str]] = mapped_column(Text)
    creado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    actualizado_en: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    actualizado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    usuarios: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[actualizado_por], back_populates='roles')
    usuarios_: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[creado_por], back_populates='roles_')
    roles_permisos: Mapped[list['RolesPermisos']] = relationship('RolesPermisos', back_populates='rol')
    usuarios_roles: Mapped[list['UsuariosRoles']] = relationship('UsuariosRoles', back_populates='rol')


class Rutas(Base):
    __tablename__ = 'rutas'
    __table_args__ = (
        ForeignKeyConstraint(['actualizado_por'], ['usuarios.id'], ondelete='SET NULL', name='rutas_actualizado_por_fkey'),
        ForeignKeyConstraint(['creado_por'], ['usuarios.id'], ondelete='SET NULL', name='rutas_creado_por_fkey'),
        PrimaryKeyConstraint('id', name='rutas_pkey'),
        UniqueConstraint('codigo', name='rutas_codigo_key')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('public.gen_random_uuid()'))
    codigo: Mapped[str] = mapped_column(String(20), nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    distancia_total_km: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    ida_vuelta: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    activa: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    creado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    descripcion: Mapped[Optional[str]] = mapped_column(Text)
    creado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    actualizado_en: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    actualizado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    usuarios: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[actualizado_por], back_populates='rutas')
    usuarios_: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[creado_por], back_populates='rutas_')


class TiposRuta(Base):
    __tablename__ = 'tipos_ruta'
    __table_args__ = (
        CheckConstraint('porcentaje_promedio_con_carga IS NULL OR porcentaje_promedio_con_carga >= 0::numeric AND porcentaje_promedio_con_carga <= 100::numeric', name='chk_porc_carga_ruta_gesneu'),
        ForeignKeyConstraint(['actualizado_por'], ['usuarios.id'], ondelete='SET NULL', name='tipos_ruta_actualizado_por_fkey'),
        ForeignKeyConstraint(['creado_por'], ['usuarios.id'], ondelete='SET NULL', name='tipos_ruta_creado_por_fkey'),
        PrimaryKeyConstraint('id', name='tipos_ruta_pkey'),
        UniqueConstraint('nombre_ruta', name='tipos_ruta_nombre_ruta_key'),
        {'comment': 'Define perfiles de rutas o ciclos operativos con sus '
                'características de terreno y carga.'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('public.gen_random_uuid()'))
    nombre_ruta: Mapped[str] = mapped_column(String(150), nullable=False)
    creado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    descripcion: Mapped[Optional[str]] = mapped_column(Text)
    distancia_total_km_ciclo: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(8, 2))
    distancia_trocha_km_ciclo: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(8, 2), server_default=text('0'))
    distancia_asfalto_km_ciclo: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(8, 2), server_default=text('0'))
    distancia_otro_terreno_km_ciclo: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(8, 2), server_default=text('0'))
    porcentaje_promedio_con_carga: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    creado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    actualizado_en: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    actualizado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    usuarios: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[actualizado_por], back_populates='tipos_ruta')
    usuarios_: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[creado_por], back_populates='tipos_ruta_')
    eventos_neumaticos: Mapped[list['EventosNeumaticos']] = relationship('EventosNeumaticos', back_populates='tipo_ruta')


class TiposVehiculo(Base):
    __tablename__ = 'tipos_vehiculo'
    __table_args__ = (
        CheckConstraint('ejes_standard >= 1 AND ejes_standard <= 10', name='tipos_vehiculo_ejes_standard_check'),
        ForeignKeyConstraint(['actualizado_por'], ['usuarios.id'], ondelete='SET NULL', name='tipos_vehiculo_actualizado_por_fkey'),
        ForeignKeyConstraint(['creado_por'], ['usuarios.id'], ondelete='SET NULL', name='tipos_vehiculo_creado_por_fkey'),
        PrimaryKeyConstraint('id', name='tipos_vehiculo_pkey'),
        Index('idx_tipos_vehiculo_nombre', unique=True)
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('public.gen_random_uuid()'))
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    ejes_standard: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text('2'))
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    creado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    descripcion: Mapped[Optional[str]] = mapped_column(Text)
    categoria_principal: Mapped[Optional[str]] = mapped_column(String(50))
    subtipo: Mapped[Optional[str]] = mapped_column(String(50))
    creado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    actualizado_en: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    actualizado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    usuarios: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[actualizado_por], back_populates='tipos_vehiculo')
    usuarios_: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[creado_por], back_populates='tipos_vehiculo_')
    configuraciones_eje: Mapped[list['ConfiguracionesEje']] = relationship('ConfiguracionesEje', back_populates='tipo_vehiculo')
    vehiculos: Mapped[list['Vehiculos']] = relationship('Vehiculos', back_populates='tipo_vehiculo')


class ConfiguracionesEje(Base):
    __tablename__ = 'configuraciones_eje'
    __table_args__ = (
        CheckConstraint('neumaticos_por_posicion = ANY (ARRAY[1, 2])', name='configuraciones_eje_neumaticos_por_posicion_check'),
        CheckConstraint('numero_eje > 0', name='configuraciones_eje_numero_eje_check'),
        CheckConstraint('numero_posiciones >= 1 AND numero_posiciones <= 6', name='configuraciones_eje_numero_posiciones_check'),
        ForeignKeyConstraint(['actualizado_por'], ['usuarios.id'], ondelete='SET NULL', name='configuraciones_eje_actualizado_por_fkey'),
        ForeignKeyConstraint(['creado_por'], ['usuarios.id'], ondelete='SET NULL', name='configuraciones_eje_creado_por_fkey'),
        ForeignKeyConstraint(['tipo_vehiculo_id'], ['tipos_vehiculo.id'], ondelete='CASCADE', name='configuraciones_eje_tipo_vehiculo_id_fkey'),
        PrimaryKeyConstraint('id', name='configuraciones_eje_pkey'),
        UniqueConstraint('tipo_vehiculo_id', 'numero_eje', name='uq_configuracion_eje')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('public.gen_random_uuid()'))
    tipo_vehiculo_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    numero_eje: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    nombre_eje: Mapped[str] = mapped_column(String(50), nullable=False)
    tipo_eje: Mapped[str] = mapped_column(Enum('DIRECCION', 'TRACCION', 'ARRASTRE', 'ELEVADOR', 'RETRACTIL', 'OTRO', name='tipo_eje_enum'), nullable=False)
    numero_posiciones: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    posiciones_duales: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    permite_reencauchados: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    neumaticos_por_posicion: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text('1'))
    creado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    creado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    actualizado_en: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    actualizado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    usuarios: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[actualizado_por], back_populates='configuraciones_eje')
    usuarios_: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[creado_por], back_populates='configuraciones_eje_')
    tipo_vehiculo: Mapped['TiposVehiculo'] = relationship('TiposVehiculo', back_populates='configuraciones_eje')
    posiciones_neumatico: Mapped[list['PosicionesNeumatico']] = relationship('PosicionesNeumatico', back_populates='configuracion_eje')


class ModelosNeumatico(Base):
    __tablename__ = 'modelos_neumatico'
    __table_args__ = (
        CheckConstraint('max_vidas_utiles > 0', name='chk_max_vidas_utiles_positivo'),
        CheckConstraint('porcentaje_desgaste_por_vida >= 0::numeric', name='chk_porcentaje_desgaste_positivo'),
        CheckConstraint('presion_recomendada_psi IS NULL OR presion_recomendada_psi > 0::numeric', name='modelos_neumatico_presion_recomendada_psi_check'),
        CheckConstraint('profundidad_minima_retiro_mm > 0::numeric', name='chk_profundidad_minima_positiva'),
        CheckConstraint('profundidad_minima_retiro_mm > 0::numeric AND profundidad_minima_retiro_mm <= profundidad_original_mm', name='modelos_neumatico_profundidad_minima_retiro_mm_check'),
        CheckConstraint('profundidad_original_mm > 0::numeric', name='modelos_neumatico_profundidad_original_mm_check'),
        CheckConstraint('reencauches_maximos >= 0 AND reencauches_maximos <= 10', name='modelos_neumatico_reencauches_maximos_check'),
        CheckConstraint('tasa_desgaste_esperada_mm_km > 0::numeric', name='chk_tasa_desgaste_positiva'),
        CheckConstraint('tasa_desgaste_esperada_mm_km IS NULL OR tasa_desgaste_esperada_mm_km > 0::numeric', name='modelos_neumatico_tasa_desgaste_esperada_check'),
        CheckConstraint('vida_util_teorica_km IS NULL OR vida_util_teorica_km > 0', name='modelos_neumatico_vida_util_teorica_km_check'),
        ForeignKeyConstraint(['actualizado_por'], ['usuarios.id'], ondelete='SET NULL', name='modelos_neumatico_actualizado_por_fkey'),
        ForeignKeyConstraint(['creado_por'], ['usuarios.id'], ondelete='SET NULL', name='modelos_neumatico_creado_por_fkey'),
        ForeignKeyConstraint(['fabricante_id'], ['fabricantes_neumatico.id'], ondelete='RESTRICT', name='modelos_neumatico_fabricante_id_fkey'),
        PrimaryKeyConstraint('id', name='modelos_neumatico_pkey'),
        Index('idx_modelos_fabricante', 'fabricante_id'),
        Index('idx_modelos_unique', 'fabricante_id', 'medida', unique=True),
        {'comment': 'Define los diferentes modelos de neumáticos con sus '
                'especificaciones técnicas y parámetros de rendimiento esperados'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('public.gen_random_uuid()'))
    fabricante_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    nombre_modelo: Mapped[str] = mapped_column(String(100), nullable=False)
    medida: Mapped[str] = mapped_column(String(20), nullable=False)
    profundidad_original_mm: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    permite_reencauche: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    creado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    profundidad_minima_retiro_mm: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False, server_default=text('1.6'), comment='Profundidad mínima del dibujo (en mm) antes de que el neumático deba ser retirado. Debe ser mayor que cero.')
    tasa_desgaste_esperada_mm_km: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 8), nullable=False, comment='Tasa de desgaste esperada en mm por kilómetro. Debe ser mayor que cero.')
    indice_carga: Mapped[Optional[str]] = mapped_column(String(5))
    indice_velocidad: Mapped[Optional[str]] = mapped_column(String(2))
    presion_recomendada_psi: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    reencauches_maximos: Mapped[Optional[int]] = mapped_column(SmallInteger, server_default=text('0'))
    patron_dibujo: Mapped[Optional[str]] = mapped_column(String(50))
    tipo_servicio: Mapped[Optional[str]] = mapped_column(String(50))
    creado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    actualizado_en: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    actualizado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    posicion_uso_recomendada: Mapped[Optional[str]] = mapped_column(Enum('DIRECCION', 'TRACCION', 'ARRASTRE', 'ELEVADOR', 'RETRACTIL', 'OTRO', name='tipo_eje_enum'), comment='Tipo de eje/posición para la cual este modelo es recomendado (ej. DIRECCION, TRACCION).')
    diseno_predominante_para_eje: Mapped[Optional[str]] = mapped_column(Enum('DIRECCION', 'TRACCION', 'ARRASTRE', 'ELEVADOR', 'RETRACTIL', 'OTRO', name='tipo_eje_enum'), comment='[OPCIONAL] Indica si el diseño del neumático es específicamente para dirección, tracción o libre/arrastre.')
    vida_util_teorica_km: Mapped[Optional[int]] = mapped_column(Integer, comment='Vida útil teórica del neumático en kilómetros según el fabricante (Lt)')
    activo: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'), comment='Indica si el modelo está activo (soft delete)')
    frecuencia_inspeccion_km: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('5000'))
    max_vidas_utiles: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('5'))
    porcentaje_desgaste_por_vida: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2), server_default=text('10.0'))

    usuarios: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[actualizado_por], back_populates='modelos_neumatico')
    usuarios_: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[creado_por], back_populates='modelos_neumatico_')
    fabricante: Mapped['FabricantesNeumatico'] = relationship('FabricantesNeumatico', back_populates='modelos_neumatico')
    especificaciones_desgaste: Mapped[list['EspecificacionesDesgaste']] = relationship('EspecificacionesDesgaste', back_populates='modelo_neumatico')
    neumaticos: Mapped[list['Neumaticos']] = relationship('Neumaticos', back_populates='modelo')
    parametros_inventario: Mapped[list['ParametrosInventario']] = relationship('ParametrosInventario', back_populates='modelo')
    parametros_rendimiento_esperado_modelo: Mapped[list['ParametrosRendimientoEsperadoModelo']] = relationship('ParametrosRendimientoEsperadoModelo', back_populates='modelo')
    alertas: Mapped[list['Alertas']] = relationship('Alertas', back_populates='modelo')
    modelos_posiciones_permitidas: Mapped[list['ModelosPosicionesPermitidas']] = relationship('ModelosPosicionesPermitidas', back_populates='modelo_neumatico')


class RolesPermisos(Base):
    __tablename__ = 'roles_permisos'
    __table_args__ = (
        ForeignKeyConstraint(['asignado_por'], ['usuarios.id'], ondelete='SET NULL', name='roles_permisos_asignado_por_fkey'),
        ForeignKeyConstraint(['permiso_id'], ['permisos.id'], ondelete='CASCADE', name='roles_permisos_permiso_id_fkey'),
        ForeignKeyConstraint(['rol_id'], ['roles.id'], ondelete='CASCADE', name='roles_permisos_rol_id_fkey'),
        PrimaryKeyConstraint('rol_id', 'permiso_id', name='roles_permisos_pkey'),
        Index('idx_roles_permisos_permiso_id', 'permiso_id'),
        {'comment': 'Relación muchos a muchos entre roles y permisos'}
    )

    rol_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    permiso_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    asignado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    asignado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    usuarios: Mapped[Optional['Usuarios']] = relationship('Usuarios', back_populates='roles_permisos')
    permiso: Mapped['Permisos'] = relationship('Permisos', back_populates='roles_permisos')
    rol: Mapped['Roles'] = relationship('Roles', back_populates='roles_permisos')


class UsuariosRoles(Base):
    __tablename__ = 'usuarios_roles'
    __table_args__ = (
        ForeignKeyConstraint(['asignado_por'], ['usuarios.id'], ondelete='SET NULL', name='usuarios_roles_asignado_por_fkey'),
        ForeignKeyConstraint(['rol_id'], ['roles.id'], ondelete='CASCADE', name='usuarios_roles_rol_id_fkey'),
        ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE', name='usuarios_roles_usuario_id_fkey'),
        PrimaryKeyConstraint('usuario_id', 'rol_id', name='usuarios_roles_pkey'),
        Index('idx_usuarios_roles_rol_id', 'rol_id'),
        Index('idx_usuarios_roles_usuario_id', 'usuario_id'),
        {'comment': 'Relación muchos a muchos entre usuarios y roles'}
    )

    usuario_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    rol_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    asignado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    asignado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    usuarios: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[asignado_por], back_populates='usuarios_roles')
    rol: Mapped['Roles'] = relationship('Roles', back_populates='usuarios_roles')
    usuario: Mapped['Usuarios'] = relationship('Usuarios', foreign_keys=[usuario_id], back_populates='usuarios_roles_')


class Vehiculos(Base):
    __tablename__ = 'vehiculos'
    __table_args__ = (
        CheckConstraint('anio_fabricacion >= 1900 AND anio_fabricacion::numeric <= (EXTRACT(year FROM CURRENT_DATE) + 1::numeric)', name='vehiculos_anio_fabricacion_check'),
        CheckConstraint('fecha_baja IS NULL OR fecha_baja >= fecha_alta', name='vehiculos_fecha_baja_check'),
        CheckConstraint('odometro_actual IS NULL OR odometro_actual >= 0', name='vehiculos_odometro_actual_check'),
        ForeignKeyConstraint(['actualizado_por'], ['usuarios.id'], ondelete='SET NULL', name='vehiculos_actualizado_por_fkey'),
        ForeignKeyConstraint(['creado_por'], ['usuarios.id'], ondelete='SET NULL', name='vehiculos_creado_por_fkey'),
        ForeignKeyConstraint(['tipo_vehiculo_id'], ['tipos_vehiculo.id'], ondelete='RESTRICT', name='vehiculos_tipo_vehiculo_id_fkey'),
        PrimaryKeyConstraint('id', name='vehiculos_pkey'),
        UniqueConstraint('numero_economico', name='vehiculos_numero_economico_key'),
        UniqueConstraint('placa', name='vehiculos_placa_key'),
        UniqueConstraint('vin', name='vehiculos_vin_key'),
        Index('idx_vehiculos_activos', 'activo'),
        Index('idx_vehiculos_numero_economico'),
        Index('idx_vehiculos_placa', 'placa'),
        Index('idx_vehiculos_tipo', 'tipo_vehiculo_id'),
        {'comment': 'Vehículos de la flota que utilizan neumáticos'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('public.gen_random_uuid()'))
    tipo_vehiculo_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    numero_economico: Mapped[str] = mapped_column(String(50), nullable=False)
    fecha_alta: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    creado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    placa: Mapped[Optional[str]] = mapped_column(DOMAIN('placa_vehiculo', VARCHAR(), constraint_name='placa_vehiculo_check', not_null=False, check=text("VALUE::text ~ '^[A-Z0-9]{1,7}-?[A-Z0-9]{1,7}$'::text")))
    vin: Mapped[Optional[str]] = mapped_column(String(17))
    marca: Mapped[Optional[str]] = mapped_column(String(50))
    modelo_vehiculo: Mapped[Optional[str]] = mapped_column(String(50))
    anio_fabricacion: Mapped[Optional[int]] = mapped_column(SmallInteger)
    fecha_baja: Mapped[Optional[datetime.date]] = mapped_column(Date)
    odometro_actual: Mapped[Optional[int]] = mapped_column(Integer)
    fecha_ultimo_odometro: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    ubicacion_actual: Mapped[Optional[str]] = mapped_column(String(100))
    notas: Mapped[Optional[str]] = mapped_column(Text)
    creado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    actualizado_en: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    actualizado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    peso_carga_maxima_diseno_ton: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2), comment='Capacidad máxima de carga de diseño del vehículo en toneladas.')

    usuarios: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[actualizado_por], back_populates='vehiculos')
    usuarios_: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[creado_por], back_populates='vehiculos_')
    tipo_vehiculo: Mapped['TiposVehiculo'] = relationship('TiposVehiculo', back_populates='vehiculos')
    bitacora_operaciones: Mapped[list['BitacoraOperaciones']] = relationship('BitacoraOperaciones', back_populates='vehiculo')
    neumaticos: Mapped[list['Neumaticos']] = relationship('Neumaticos', back_populates='ubicacion_actual_vehiculo')
    registros_odometro: Mapped[list['RegistrosOdometro']] = relationship('RegistrosOdometro', back_populates='vehiculo')
    alertas: Mapped[list['Alertas']] = relationship('Alertas', back_populates='vehiculo')
    eventos_neumaticos: Mapped[list['EventosNeumaticos']] = relationship('EventosNeumaticos', back_populates='vehiculo')


class BitacoraOperaciones(Base):
    __tablename__ = 'bitacora_operaciones'
    __table_args__ = (
        ForeignKeyConstraint(['actualizado_por'], ['usuarios.id'], ondelete='SET NULL', name='bitacora_operaciones_actualizado_por_fkey'),
        ForeignKeyConstraint(['almacen_id'], ['almacenes.id'], ondelete='SET NULL', name='bitacora_operaciones_almacen_id_fkey'),
        ForeignKeyConstraint(['creado_por'], ['usuarios.id'], ondelete='SET NULL', name='bitacora_operaciones_creado_por_fkey'),
        ForeignKeyConstraint(['proveedor_id'], ['proveedores.id'], name='bitacora_operaciones_proveedor_id_fkey'),
        ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='SET NULL', name='bitacora_operaciones_usuario_id_fkey'),
        ForeignKeyConstraint(['vehiculo_id'], ['vehiculos.id'], ondelete='SET NULL', name='bitacora_operaciones_vehiculo_id_fkey'),
        PrimaryKeyConstraint('id', name='bitacora_operaciones_pkey'),
        Index('idx_bitacora_operaciones_almacen', 'almacen_id'),
        Index('idx_bitacora_operaciones_estado', 'estado_operacion'),
        Index('idx_bitacora_operaciones_fecha', 'fecha_operacion'),
        Index('idx_bitacora_operaciones_vehiculo', 'vehiculo_id'),
        {'comment': 'Registra operaciones de mantenimiento realizadas en el taller o '
                'en vehículos'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    tipo_operacion: Mapped[str] = mapped_column(Enum('ROTACION', 'BALANCEO', 'ALINEACION', 'REPARACION_GENERAL', 'INSPECCION_GENERAL', 'CAMBIO_ACEITE', 'OTRO', 'DESMONTAJE', name='tipo_operacion_enum'), nullable=False, comment='Tipo de operación realizada (balanceo, rotación, etc.)')
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    fecha_operacion: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    estado_operacion: Mapped[str] = mapped_column(Enum('PENDIENTE', 'EN_PROCESO', 'COMPLETADA', 'CANCELADA', 'VENCIDA', name='estado_operacion_enum'), nullable=False, comment='Estado actual de la operación (PENDIENTE, EN_PROCESO, COMPLETADA, etc.)')
    creado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    actualizado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    usuario_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    almacen_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    vehiculo_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    duracion_minutos: Mapped[Optional[int]] = mapped_column(Integer)
    costo_estimado: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2))
    costo_real: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2))
    proveedor_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    observaciones: Mapped[Optional[str]] = mapped_column(Text)
    creado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    actualizado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    usuarios: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[actualizado_por], back_populates='bitacora_operaciones')
    almacen: Mapped[Optional['Almacenes']] = relationship('Almacenes', back_populates='bitacora_operaciones')
    usuarios_: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[creado_por], back_populates='bitacora_operaciones_')
    proveedor: Mapped[Optional['Proveedores']] = relationship('Proveedores', back_populates='bitacora_operaciones')
    usuario: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[usuario_id], back_populates='bitacora_operaciones1')
    vehiculo: Mapped[Optional['Vehiculos']] = relationship('Vehiculos', back_populates='bitacora_operaciones')
    bitacora_operaciones_neumaticos: Mapped[list['BitacoraOperacionesNeumaticos']] = relationship('BitacoraOperacionesNeumaticos', back_populates='operacion')


class EspecificacionesDesgaste(Base):
    __tablename__ = 'especificaciones_desgaste'
    __table_args__ = (
        CheckConstraint('vida_util_km_min < vida_util_km_max', name='especificaciones_desgaste_check_km'),
        ForeignKeyConstraint(['actualizado_por'], ['usuarios.id'], ondelete='SET NULL', name='especificaciones_desgaste_actualizado_por_fkey'),
        ForeignKeyConstraint(['creado_por'], ['usuarios.id'], ondelete='SET NULL', name='especificaciones_desgaste_creado_por_fkey'),
        ForeignKeyConstraint(['modelo_neumatico_id'], ['modelos_neumatico.id'], ondelete='CASCADE', name='especificaciones_desgaste_modelo_neumatico_id_fkey'),
        PrimaryKeyConstraint('id', name='especificaciones_desgaste_pkey'),
        Index('idx_especificaciones_desgaste_modelo', 'modelo_neumatico_id'),
        Index('idx_especificaciones_desgaste_tipo_posicion', 'tipo_posicion')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('public.gen_random_uuid()'))
    modelo_neumatico_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    tipo_posicion: Mapped[str] = mapped_column(String(50), nullable=False)
    vida_util_km_min: Mapped[int] = mapped_column(Integer, nullable=False)
    vida_util_km_max: Mapped[int] = mapped_column(Integer, nullable=False)
    descripcion_estado: Mapped[str] = mapped_column(String(100), nullable=False)
    creado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    creado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    actualizado_en: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    actualizado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    usuarios: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[actualizado_por], back_populates='especificaciones_desgaste')
    usuarios_: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[creado_por], back_populates='especificaciones_desgaste_')
    modelo_neumatico: Mapped['ModelosNeumatico'] = relationship('ModelosNeumatico', back_populates='especificaciones_desgaste')


class Neumaticos(Base):
    __tablename__ = 'neumaticos'
    __table_args__ = (
        CheckConstraint('costo_compra IS NULL OR costo_compra >= 0::numeric', name='neumaticos_costo_compra_check'),
        CheckConstraint('fecha_fabricacion IS NULL OR fecha_fabricacion <= fecha_compra', name='neumaticos_fechas_check'),
        CheckConstraint('kilometraje_acumulado >= 0', name='neumaticos_kilometraje_acumulado_check'),
        CheckConstraint('kilometraje_vida_actual >= 0', name='neumaticos_kilometraje_vida_actual_check'),
        CheckConstraint('profundidad_inicial_mm IS NULL OR profundidad_inicial_mm > 0::numeric', name='neumaticos_profundidad_inicial_mm_check'),
        CheckConstraint('profundidad_remanente_actual_mm IS NULL OR profundidad_remanente_actual_mm >= 0::numeric AND profundidad_remanente_actual_mm <= 50::numeric', name='neumaticos_profundidad_remanente_check'),
        CheckConstraint('reencauches_realizados >= 0', name='neumaticos_reencauches_realizados_check'),
        CheckConstraint('tasa_desgaste_actual_mm_km IS NULL OR tasa_desgaste_actual_mm_km > 0::numeric', name='chk_tasa_desgaste_positiva'),
        CheckConstraint('tasa_desgaste_actual_mm_km IS NULL OR tasa_desgaste_actual_mm_km > 0::numeric', name='neumaticos_tasa_desgaste_actual_check'),
        CheckConstraint("ubicacion_almacen_id IS NOT NULL AND ubicacion_actual_vehiculo_id IS NULL AND ubicacion_actual_posicion_id IS NULL AND estado_actual <> 'INSTALADO'::estado_neumatico_enum OR ubicacion_almacen_id IS NULL AND ubicacion_actual_vehiculo_id IS NOT NULL AND ubicacion_actual_posicion_id IS NOT NULL AND estado_actual = 'INSTALADO'::estado_neumatico_enum OR ubicacion_almacen_id IS NULL AND ubicacion_actual_vehiculo_id IS NULL AND ubicacion_actual_posicion_id IS NULL AND estado_actual <> 'INSTALADO'::estado_neumatico_enum", name='chk_ubicacion_mutuamente_exclusiva'),
        CheckConstraint('vida_actual >= 1 AND vida_actual <= 11', name='neumaticos_vida_actual_check'),
        CheckConstraint('vida_util_restante_km IS NULL OR vida_util_restante_km >= 0', name='neumaticos_vida_util_restante_check'),
        CheckConstraint('vida_util_restante_km IS NULL OR vida_util_restante_km >= 0', name='chk_vida_util_restante_no_negativa'),
        ForeignKeyConstraint(['actualizado_por'], ['usuarios.id'], ondelete='SET NULL', name='neumaticos_actualizado_por_fkey'),
        ForeignKeyConstraint(['creado_por'], ['usuarios.id'], ondelete='SET NULL', name='neumaticos_creado_por_fkey'),
        ForeignKeyConstraint(['modelo_id'], ['modelos_neumatico.id'], ondelete='RESTRICT', name='neumaticos_modelo_id_fkey'),
        ForeignKeyConstraint(['motivo_desecho_id'], ['motivos_desecho.id'], ondelete='RESTRICT', name='neumaticos_motivo_desecho_id_fkey'),
        ForeignKeyConstraint(['proveedor_compra_id'], ['proveedores.id'], ondelete='SET NULL', name='neumaticos_proveedor_compra_id_fkey'),
        ForeignKeyConstraint(['ubicacion_actual_vehiculo_id'], ['vehiculos.id'], ondelete='SET NULL', name='neumaticos_ubicacion_actual_vehiculo_id_fkey'),
        ForeignKeyConstraint(['ubicacion_almacen_id'], ['almacenes.id'], ondelete='SET NULL', name='neumaticos_ubicacion_almacen_id_fkey'),
        PrimaryKeyConstraint('id', name='neumaticos_pkey'),
        Index('idx_neumaticos_activos', 'estado_actual'),
        Index('idx_neumaticos_activos_compuesto', 'estado_actual', 'modelo_id', 'vida_util_restante_km'),
        Index('idx_neumaticos_dot', 'dot'),
        Index('idx_neumaticos_estado', 'estado_actual'),
        Index('idx_neumaticos_estado_actual', 'estado_actual'),
        Index('idx_neumaticos_estado_ubicacion', 'estado_actual', 'ubicacion_actual_vehiculo_id', 'ubicacion_actual_posicion_id'),
        Index('idx_neumaticos_fechas_compra', 'fecha_compra'),
        Index('idx_neumaticos_modelo', 'modelo_id'),
        Index('idx_neumaticos_modelo_id', 'modelo_id'),
        Index('idx_neumaticos_prox_inspeccion', 'proxima_inspeccion_fecha'),
        Index('idx_neumaticos_proximos_desecho', 'estado_actual', 'fecha_fabricacion'),
        Index('idx_neumaticos_sensor_id', 'sensor_id'),
        Index('idx_neumaticos_serie', 'numero_serie'),
        Index('idx_neumaticos_tasa_desgaste', 'tasa_desgaste_actual_mm_km'),
        Index('idx_neumaticos_ubicacion', 'ubicacion_actual_vehiculo_id', 'ubicacion_actual_posicion_id'),
        Index('idx_neumaticos_ubicacion_almacen', 'ubicacion_almacen_id'),
        Index('idx_neumaticos_vida_util_restante', 'vida_util_restante_km'),
        Index('uq_idx_neumatico_dot_vida', 'dot', 'vida_actual', unique=True),
        {'comment': 'Almacena información sobre neumáticos individuales, incluyendo su '
                'estado actual, ubicación y métricas de rendimiento'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('public.gen_random_uuid()'))
    modelo_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    fecha_compra: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    es_reencauchado: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    vida_actual: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text('1'))
    estado_actual: Mapped[str] = mapped_column(Enum('EN_STOCK', 'INSTALADO', 'EN_REPARACION', 'EN_REENCAUCHE', 'DESECHADO', 'EN_TRANSITO', name='estado_neumatico_enum'), nullable=False, server_default=text("'EN_STOCK'::estado_neumatico_enum"))
    kilometraje_acumulado: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    reencauches_realizados: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text('0'))
    creado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    profundidad_remanente_actual_mm: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False, comment='Profundidad actual de la banda de rodadura (en mm)')
    numero_serie: Mapped[Optional[str]] = mapped_column(String(100))
    dot: Mapped[Optional[str]] = mapped_column(DOMAIN('dot_code', TEXT(), constraint_name='dot_code_check', not_null=False, check=text("VALUE ~ '^[A-Z0-9]{2,4}[A-Z0-9]{2}[A-Z0-9]{3,4}$'::text")))
    fecha_fabricacion: Mapped[Optional[datetime.date]] = mapped_column(Date)
    costo_compra: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2))
    moneda_compra: Mapped[Optional[str]] = mapped_column(String(3), server_default=text("'PEN'::character varying"))
    proveedor_compra_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    ubicacion_actual_vehiculo_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    ubicacion_actual_posicion_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    fecha_ultimo_evento: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    profundidad_inicial_mm: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    fecha_desecho: Mapped[Optional[datetime.date]] = mapped_column(Date)
    motivo_desecho_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    creado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    actualizado_en: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    actualizado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    ubicacion_almacen_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    sensor_id: Mapped[Optional[str]] = mapped_column(String(100))
    fecha_ultima_medicion_profundidad: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), comment='Fecha de la última medición de profundidad')
    kilometraje_vida_actual: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'), comment='Kilometraje acumulado en la vida actual del neumático')
    fecha_inicio_vida_actual: Mapped[Optional[datetime.date]] = mapped_column(Date, comment='Fecha de inicio de la vida actual del neumático')
    odometro_instalacion_vida_actual: Mapped[Optional[int]] = mapped_column(Integer, comment='Odómetro del vehículo al momento de la instalación para la vida actual')
    tasa_desgaste_actual_mm_km: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 8), comment='Tasa de desgaste actual en mm/km')
    vida_util_restante_km: Mapped[Optional[int]] = mapped_column(Integer, comment='Vida útil restante estimada en kilómetros (Lr)')
    fecha_ultimo_reencauche: Mapped[Optional[datetime.date]] = mapped_column(Date, comment='Fecha del último reencauche realizado')
    activo: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'), comment='Indica si el neumático está activo (soft delete)')
    proxima_inspeccion_fecha: Mapped[Optional[datetime.date]] = mapped_column(Date, comment='Fecha recomendada para la próxima inspección del neumático')
    proxima_inspeccion_km: Mapped[Optional[int]] = mapped_column(Integer, comment='Kilometraje recomendado para la próxima inspección del neumático')
    profundidad_inicio_vida_actual_mm: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))

    usuarios: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[actualizado_por], back_populates='neumaticos')
    usuarios_: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[creado_por], back_populates='neumaticos_')
    modelo: Mapped['ModelosNeumatico'] = relationship('ModelosNeumatico', back_populates='neumaticos')
    motivo_desecho: Mapped[Optional['MotivosDesecho']] = relationship('MotivosDesecho', back_populates='neumaticos')
    proveedor_compra: Mapped[Optional['Proveedores']] = relationship('Proveedores', back_populates='neumaticos')
    ubicacion_actual_vehiculo: Mapped[Optional['Vehiculos']] = relationship('Vehiculos', back_populates='neumaticos')
    ubicacion_almacen: Mapped[Optional['Almacenes']] = relationship('Almacenes', back_populates='neumaticos')
    alertas: Mapped[list['Alertas']] = relationship('Alertas', back_populates='neumatico')
    bitacora_operaciones_neumaticos: Mapped[list['BitacoraOperacionesNeumaticos']] = relationship('BitacoraOperacionesNeumaticos', back_populates='neumatico')
    eventos_neumaticos: Mapped[list['EventosNeumaticos']] = relationship('EventosNeumaticos', back_populates='neumatico')
    garantias_neumaticos: Mapped[list['GarantiasNeumaticos']] = relationship('GarantiasNeumaticos', back_populates='neumatico')
    historial_estados_neumaticos: Mapped[list['HistorialEstadosNeumaticos']] = relationship('HistorialEstadosNeumaticos', back_populates='neumatico')
    mediciones_profundidad: Mapped[list['MedicionesProfundidad']] = relationship('MedicionesProfundidad', back_populates='neumatico')


class ParametrosInventario(Base):
    __tablename__ = 'parametros_inventario'
    __table_args__ = (
        ForeignKeyConstraint(['actualizado_por'], ['usuarios.id'], ondelete='SET NULL', name='parametros_inventario_actualizado_por_fkey'),
        ForeignKeyConstraint(['creado_por'], ['usuarios.id'], ondelete='SET NULL', name='parametros_inventario_creado_por_fkey'),
        ForeignKeyConstraint(['modelo_id'], ['modelos_neumatico.id'], ondelete='CASCADE', name='parametros_inventario_modelo_id_fkey'),
        ForeignKeyConstraint(['ubicacion_almacen_id'], ['almacenes.id'], ondelete='SET NULL', name='parametros_inventario_ubicacion_almacen_id_fkey'),
        PrimaryKeyConstraint('id', name='parametros_inventario_pkey'),
        UniqueConstraint('parametro_tipo', 'modelo_id', 'ubicacion_almacen_id', name='uq_parametro_inventario_gesneu'),
        UniqueConstraint('parametro_tipo', 'modelo_id', 'ubicacion_almacen_id', name='uq_parametro_inventario'),
        Index('idx_param_inv_tipo_modelo_ubicacion', 'parametro_tipo', 'modelo_id', 'ubicacion_almacen_id'),
        {'comment': 'Parámetros configurables para la gestión de inventario de '
                'neumáticos'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('public.gen_random_uuid()'))
    parametro_tipo: Mapped[str] = mapped_column(Enum('STOCK_MINIMO', 'STOCK_MAXIMO', 'PROFUNDIDAD_MINIMA_RETIRO_MM', 'PROFUNDIDAD_MINIMA_REENCAUCHE_MM', 'TIEMPO_MAXIMO_VIDA_MESES', 'MAX_ROTACIONES_PERIODO', 'MAX_REPARACIONES_PERIODO', 'VIDA_MAXIMA_ESTANTE_MESES_SIN_USO', name='tipo_parametro_inventario_gesneu_enum'), nullable=False)
    modelo_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    creado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    ubicacion_almacen_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    valor_numerico: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2))
    valor_texto: Mapped[Optional[str]] = mapped_column(Text)
    notas: Mapped[Optional[str]] = mapped_column(Text)
    creado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    actualizado_en: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    actualizado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    usuarios: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[actualizado_por], back_populates='parametros_inventario')
    usuarios_: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[creado_por], back_populates='parametros_inventario_')
    modelo: Mapped['ModelosNeumatico'] = relationship('ModelosNeumatico', back_populates='parametros_inventario')
    ubicacion_almacen: Mapped[Optional['Almacenes']] = relationship('Almacenes', back_populates='parametros_inventario')
    alertas: Mapped[list['Alertas']] = relationship('Alertas', back_populates='parametro')


class ParametrosRendimientoEsperadoModelo(Base):
    __tablename__ = 'parametros_rendimiento_esperado_modelo'
    __table_args__ = (
        CheckConstraint('km_esperado_vida_original_max IS NULL OR km_esperado_vida_original_max >= COALESCE(km_esperado_vida_original_min, 0)', name='parametros_rendimiento_esperado_modelo_check'),
        CheckConstraint('km_esperado_vida_original_min IS NULL OR km_esperado_vida_original_min >= 0', name='parametros_rendimiento_esper_km_esperado_vida_original_mi_check'),
        ForeignKeyConstraint(['actualizado_por'], ['usuarios.id'], ondelete='SET NULL', name='parametros_rendimiento_esperado_modelo_actualizado_por_fkey'),
        ForeignKeyConstraint(['creado_por'], ['usuarios.id'], ondelete='SET NULL', name='parametros_rendimiento_esperado_modelo_creado_por_fkey'),
        ForeignKeyConstraint(['modelo_id'], ['modelos_neumatico.id'], ondelete='CASCADE', name='parametros_rendimiento_esperado_modelo_modelo_id_fkey'),
        PrimaryKeyConstraint('id', name='parametros_rendimiento_esperado_modelo_pkey'),
        UniqueConstraint('modelo_id', 'tipo_eje_aplicacion', name='uq_rendimiento_modelo_eje_gesneu'),
        {'comment': 'Almacena los parámetros de rendimiento esperado para cada modelo '
                'de neumático según el tipo de eje de aplicación'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('public.gen_random_uuid()'))
    modelo_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    tipo_eje_aplicacion: Mapped[str] = mapped_column(Enum('DIRECCION', 'TRACCION', 'ARRASTRE', 'ELEVADOR', 'RETRACTIL', 'OTRO', name='tipo_eje_enum'), nullable=False)
    creado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    km_esperado_vida_original_min: Mapped[Optional[int]] = mapped_column(Integer)
    km_esperado_vida_original_max: Mapped[Optional[int]] = mapped_column(Integer)
    notas: Mapped[Optional[str]] = mapped_column(Text)
    creado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    actualizado_en: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    actualizado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    usuarios: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[actualizado_por], back_populates='parametros_rendimiento_esperado_modelo')
    usuarios_: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[creado_por], back_populates='parametros_rendimiento_esperado_modelo_')
    modelo: Mapped['ModelosNeumatico'] = relationship('ModelosNeumatico', back_populates='parametros_rendimiento_esperado_modelo')


class PosicionesNeumatico(Base):
    __tablename__ = 'posiciones_neumatico'
    __table_args__ = (
        CheckConstraint('posicion_relativa > 0', name='posiciones_neumatico_posicion_relativa_check'),
        ForeignKeyConstraint(['actualizado_por'], ['usuarios.id'], ondelete='SET NULL', name='posiciones_neumatico_actualizado_por_fkey'),
        ForeignKeyConstraint(['configuracion_eje_id'], ['configuraciones_eje.id'], ondelete='CASCADE', name='posiciones_neumatico_configuracion_eje_id_fkey'),
        ForeignKeyConstraint(['creado_por'], ['usuarios.id'], ondelete='SET NULL', name='posiciones_neumatico_creado_por_fkey'),
        PrimaryKeyConstraint('id', name='posiciones_neumatico_pkey'),
        UniqueConstraint('configuracion_eje_id', 'codigo_posicion', name='uq_posicion_neumatico')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('public.gen_random_uuid()'))
    configuracion_eje_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    codigo_posicion: Mapped[str] = mapped_column(String(10), nullable=False)
    lado: Mapped[str] = mapped_column(Enum('IZQUIERDO', 'DERECHO', 'CENTRAL', 'INDETERMINADO', name='lado_vehiculo_enum'), nullable=False)
    posicion_relativa: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    es_interna: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    es_direccion: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    es_traccion: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    requiere_neumatico_especifico: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    creado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    etiqueta_posicion: Mapped[Optional[str]] = mapped_column(String(50))
    creado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    actualizado_en: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    actualizado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    usuarios: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[actualizado_por], back_populates='posiciones_neumatico')
    configuracion_eje: Mapped['ConfiguracionesEje'] = relationship('ConfiguracionesEje', back_populates='posiciones_neumatico')
    usuarios_: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[creado_por], back_populates='posiciones_neumatico_')
    bitacora_operaciones_neumaticos: Mapped[list['BitacoraOperacionesNeumaticos']] = relationship('BitacoraOperacionesNeumaticos', back_populates='posicion_neumatico')
    eventos_neumaticos: Mapped[list['EventosNeumaticos']] = relationship('EventosNeumaticos', back_populates='posicion')
    modelos_posiciones_permitidas: Mapped[list['ModelosPosicionesPermitidas']] = relationship('ModelosPosicionesPermitidas', back_populates='posicion_neumatico')


class RegistrosOdometro(Base):
    __tablename__ = 'registros_odometro'
    __table_args__ = (
        CheckConstraint("fuente::text <> ''::text", name='registros_odometro_fuente_check'),
        CheckConstraint('odometro >= 0', name='registros_odometro_odometro_check'),
        ForeignKeyConstraint(['creado_por'], ['usuarios.id'], ondelete='SET NULL', name='registros_odometro_creado_por_fkey'),
        ForeignKeyConstraint(['vehiculo_id'], ['vehiculos.id'], ondelete='CASCADE', name='registros_odometro_vehiculo_id_fkey'),
        PrimaryKeyConstraint('id', name='registros_odometro_pkey'),
        Index('idx_registros_odometro_vehiculo_fecha', 'vehiculo_id', 'fecha_medicion'),
        {'comment': 'Registros históricos de lecturas de odómetro de los vehículos'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('public.gen_random_uuid()'))
    vehiculo_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    odometro: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_medicion: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    fuente: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'manual'::character varying"))
    creado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    notas: Mapped[Optional[str]] = mapped_column(Text)

    usuarios: Mapped[Optional['Usuarios']] = relationship('Usuarios', back_populates='registros_odometro')
    vehiculo: Mapped['Vehiculos'] = relationship('Vehiculos', back_populates='registros_odometro')


class Alertas(Base):
    __tablename__ = 'alertas'
    __table_args__ = (
        CheckConstraint("estado_alerta::text = ANY (ARRAY['NUEVA'::character varying::text, 'VISTA'::character varying::text, 'GESTIONADA'::character varying::text])", name='alertas_estado_alerta_check'),
        CheckConstraint("nivel_severidad::text = ANY (ARRAY['INFO'::character varying::text, 'WARN'::character varying::text, 'CRITICAL'::character varying::text])", name='alertas_nivel_severidad_check'),
        ForeignKeyConstraint(['almacen_id'], ['almacenes.id'], ondelete='CASCADE', name='alertas_almacen_id_fkey'),
        ForeignKeyConstraint(['modelo_id'], ['modelos_neumatico.id'], ondelete='CASCADE', name='alertas_modelo_id_fkey'),
        ForeignKeyConstraint(['neumatico_id'], ['neumaticos.id'], ondelete='CASCADE', name='alertas_neumatico_id_fkey'),
        ForeignKeyConstraint(['parametro_id'], ['parametros_inventario.id'], ondelete='SET NULL', name='alertas_parametro_id_fkey'),
        ForeignKeyConstraint(['usuario_gestion_id'], ['usuarios.id'], ondelete='SET NULL', name='alertas_usuario_gestion_id_fkey'),
        ForeignKeyConstraint(['vehiculo_id'], ['vehiculos.id'], ondelete='CASCADE', name='alertas_vehiculo_id_fkey'),
        PrimaryKeyConstraint('id', name='alertas_pkey'),
        Index('idx_alertas_estado_ts', 'estado_alerta', 'timestamp_generacion'),
        Index('idx_alertas_fecha', 'timestamp_generacion'),
        Index('idx_alertas_neumatico', 'neumatico_id'),
        {'comment': 'Alertas generadas por el sistema'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('public.gen_random_uuid()'))
    tipo_alerta: Mapped[str] = mapped_column(String(50), nullable=False)
    mensaje: Mapped[str] = mapped_column(Text, nullable=False)
    nivel_severidad: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'INFO'::character varying"))
    estado_alerta: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'NUEVA'::character varying"))
    timestamp_generacion: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    timestamp_gestion: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    usuario_gestion_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    neumatico_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    vehiculo_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    modelo_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    almacen_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    parametro_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    datos_contexto: Mapped[Optional[dict]] = mapped_column(JSONB)

    almacen: Mapped[Optional['Almacenes']] = relationship('Almacenes', back_populates='alertas')
    modelo: Mapped[Optional['ModelosNeumatico']] = relationship('ModelosNeumatico', back_populates='alertas')
    neumatico: Mapped[Optional['Neumaticos']] = relationship('Neumaticos', back_populates='alertas')
    parametro: Mapped[Optional['ParametrosInventario']] = relationship('ParametrosInventario', back_populates='alertas')
    usuario_gestion: Mapped[Optional['Usuarios']] = relationship('Usuarios', back_populates='alertas')
    vehiculo: Mapped[Optional['Vehiculos']] = relationship('Vehiculos', back_populates='alertas')


class BitacoraOperacionesNeumaticos(Base):
    __tablename__ = 'bitacora_operaciones_neumaticos'
    __table_args__ = (
        ForeignKeyConstraint(['actualizado_por'], ['usuarios.id'], ondelete='SET NULL', name='bitacora_operaciones_neumaticos_actualizado_por_fkey'),
        ForeignKeyConstraint(['creado_por'], ['usuarios.id'], ondelete='SET NULL', name='bitacora_operaciones_neumaticos_creado_por_fkey'),
        ForeignKeyConstraint(['neumatico_id'], ['neumaticos.id'], ondelete='CASCADE', name='bitacora_operaciones_neumaticos_neumatico_id_fkey'),
        ForeignKeyConstraint(['operacion_id'], ['bitacora_operaciones.id'], ondelete='CASCADE', name='bitacora_operaciones_neumaticos_operacion_id_fkey'),
        ForeignKeyConstraint(['posicion_neumatico_id'], ['posiciones_neumatico.id'], ondelete='SET NULL', name='bitacora_operaciones_neumaticos_posicion_neumatico_id_fkey'),
        PrimaryKeyConstraint('id', name='bitacora_operaciones_neumaticos_pkey'),
        UniqueConstraint('operacion_id', 'neumatico_id', 'tipo_accion', name='bitacora_operaciones_neumatic_operacion_id_neumatico_id_tip_key'),
        Index('idx_bitacora_op_neu_neumatico', 'neumatico_id'),
        Index('idx_bitacora_op_neu_operacion', 'operacion_id'),
        Index('idx_bitacora_op_neu_posicion', 'posicion_neumatico_id'),
        Index('idx_bitacora_op_neu_tipo_accion', 'tipo_accion'),
        {'comment': 'Relación muchos a muchos entre operaciones de mantenimiento y '
                'neumáticos'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    operacion_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    neumatico_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    tipo_accion: Mapped[str] = mapped_column(Enum('INSTALACION', 'DESMONTAJE', 'ROTACION', 'REPARACION_NEU', 'INSPECCION_NEU', 'OTRO_NEU', name='tipo_accion_operacion_enum'), nullable=False, comment='Tipo de acción realizada sobre el neumático durante la operación')
    creado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    actualizado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    posicion_neumatico_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    profundidad_inicial_mm: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    profundidad_final_mm: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    presion_inicial_psi: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    presion_final_psi: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    kilometraje_vehiculo_km: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2))
    observaciones: Mapped[Optional[str]] = mapped_column(Text)
    creado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    actualizado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    usuarios: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[actualizado_por], back_populates='bitacora_operaciones_neumaticos')
    usuarios_: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[creado_por], back_populates='bitacora_operaciones_neumaticos_')
    neumatico: Mapped['Neumaticos'] = relationship('Neumaticos', back_populates='bitacora_operaciones_neumaticos')
    operacion: Mapped['BitacoraOperaciones'] = relationship('BitacoraOperaciones', back_populates='bitacora_operaciones_neumaticos')
    posicion_neumatico: Mapped[Optional['PosicionesNeumatico']] = relationship('PosicionesNeumatico', back_populates='bitacora_operaciones_neumaticos')


class EventosNeumaticos(Base):
    __tablename__ = 'eventos_neumaticos'
    __table_args__ = (
        CheckConstraint('costo_evento IS NULL OR costo_evento >= 0::numeric', name='eventos_neumaticos_costo_evento_check'),
        CheckConstraint('odometro_vehiculo_en_evento IS NULL OR odometro_vehiculo_en_evento >= 0', name='eventos_neumaticos_odometro_vehiculo_en_evento_check'),
        CheckConstraint('presion_psi IS NULL OR presion_psi > 0::numeric', name='eventos_neumaticos_presion_psi_check'),
        CheckConstraint('profundidad_post_reencauche_mm IS NULL OR profundidad_post_reencauche_mm > 0::numeric', name='eventos_neumaticos_profundidad_post_reencauche_mm_check'),
        CheckConstraint('profundidad_remanente_mm IS NULL OR profundidad_remanente_mm >= 0::numeric', name='eventos_neumaticos_profundidad_remanente_mm_check'),
        CheckConstraint("tipo_evento <> 'DESECHO'::tipo_evento_neumatico_enum AND (tipo_evento <> 'DESMONTAJE'::tipo_evento_neumatico_enum OR destino_desmontaje <> 'DESECHADO'::estado_neumatico_enum) OR motivo_desecho_id_evento IS NOT NULL", name='chk_motivo_desecho'),
        CheckConstraint("tipo_evento <> 'DESMONTAJE'::tipo_evento_neumatico_enum OR destino_desmontaje IS NOT NULL", name='chk_destino_desmontaje'),
        CheckConstraint("tipo_evento <> 'REENCAUCHE_SALIDA'::tipo_evento_neumatico_enum OR profundidad_post_reencauche_mm IS NOT NULL", name='chk_profundidad_reencauche'),
        ForeignKeyConstraint(['almacen_destino_id'], ['almacenes.id'], ondelete='SET NULL', name='eventos_neumaticos_almacen_destino_id_fkey'),
        ForeignKeyConstraint(['motivo_desecho_id_evento'], ['motivos_desecho.id'], ondelete='RESTRICT', name='eventos_neumaticos_motivo_desecho_id_evento_fkey'),
        ForeignKeyConstraint(['neumatico_id'], ['neumaticos.id'], ondelete='CASCADE', name='eventos_neumaticos_neumatico_id_fkey'),
        ForeignKeyConstraint(['posicion_id'], ['posiciones_neumatico.id'], ondelete='SET NULL', name='eventos_neumaticos_posicion_id_fkey'),
        ForeignKeyConstraint(['proveedor_servicio_id'], ['proveedores.id'], ondelete='SET NULL', name='eventos_neumaticos_proveedor_servicio_id_fkey'),
        ForeignKeyConstraint(['relacion_evento_anterior'], ['eventos_neumaticos.id'], ondelete='SET NULL', name='eventos_neumaticos_relacion_evento_anterior_fkey'),
        ForeignKeyConstraint(['tipo_ruta_id'], ['tipos_ruta.id'], ondelete='RESTRICT', name='fk_eventos_neumaticos_tipo_ruta'),
        ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='RESTRICT', name='eventos_neumaticos_usuario_id_fkey'),
        ForeignKeyConstraint(['vehiculo_id'], ['vehiculos.id'], ondelete='SET NULL', name='eventos_neumaticos_vehiculo_id_fkey'),
        PrimaryKeyConstraint('id', name='eventos_neumaticos_pkey'),
        Index('idx_eventos_neumatico', 'neumatico_id'),
        Index('idx_eventos_neumatico_fecha', 'neumatico_id', 'timestamp_evento'),
        Index('idx_eventos_neumatico_tipo_fecha', 'neumatico_id', 'tipo_evento', 'timestamp_evento'),
        Index('idx_eventos_neumaticos_tipo_ruta_id', 'tipo_ruta_id'),
        Index('idx_eventos_timestamp', 'timestamp_evento'),
        Index('idx_eventos_tipo', 'tipo_evento'),
        Index('idx_eventos_usuario', 'usuario_id'),
        {'comment': 'Registro de eventos que afectan el ciclo de vida de los '
                'neumáticos'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('public.gen_random_uuid()'))
    neumatico_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    tipo_evento: Mapped[str] = mapped_column(Enum('COMPRA', 'INSTALACION', 'DESMONTAJE', 'INSPECCION', 'ROTACION', 'REPARACION_ENTRADA', 'REPARACION_SALIDA', 'REENCAUCHE_ENTRADA', 'REENCAUCHE_SALIDA', 'DESECHO', 'AJUSTE_INVENTARIO', 'TRANSFERENCIA_UBICACION', name='tipo_evento_neumatico_enum'), nullable=False)
    timestamp_evento: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    usuario_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    creado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    vehiculo_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    posicion_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    odometro_vehiculo_en_evento: Mapped[Optional[int]] = mapped_column(Integer)
    profundidad_remanente_mm: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    presion_psi: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    costo_evento: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2))
    moneda_costo: Mapped[Optional[str]] = mapped_column(String(3), server_default=text("'PEN'::character varying"))
    proveedor_servicio_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    notas: Mapped[Optional[str]] = mapped_column(Text)
    destino_desmontaje: Mapped[Optional[str]] = mapped_column(Enum('EN_STOCK', 'INSTALADO', 'EN_REPARACION', 'EN_REENCAUCHE', 'DESECHADO', 'EN_TRANSITO', name='estado_neumatico_enum'))
    motivo_desecho_id_evento: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    profundidad_post_reencauche_mm: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    datos_evento: Mapped[Optional[dict]] = mapped_column(JSONB)
    relacion_evento_anterior: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    almacen_destino_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    tipo_ruta_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, comment='Tipo de ruta predominante durante el periodo cubierto hasta este evento.')
    peso_carga_promedio_ton_evento: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2), comment='Peso promedio de carga estimado durante el uso hasta este evento.')
    motivo_reparacion_texto: Mapped[Optional[str]] = mapped_column(Text, comment='Descripción del motivo o síntoma que llevó a la reparación.')
    tipo_dano_detectado_texto: Mapped[Optional[str]] = mapped_column(Text, comment='Descripción del tipo de daño encontrado en la reparación.')

    almacen_destino: Mapped[Optional['Almacenes']] = relationship('Almacenes', back_populates='eventos_neumaticos')
    motivos_desecho: Mapped[Optional['MotivosDesecho']] = relationship('MotivosDesecho', back_populates='eventos_neumaticos')
    neumatico: Mapped['Neumaticos'] = relationship('Neumaticos', back_populates='eventos_neumaticos')
    posicion: Mapped[Optional['PosicionesNeumatico']] = relationship('PosicionesNeumatico', back_populates='eventos_neumaticos')
    proveedor_servicio: Mapped[Optional['Proveedores']] = relationship('Proveedores', back_populates='eventos_neumaticos')
    eventos_neumaticos: Mapped[Optional['EventosNeumaticos']] = relationship('EventosNeumaticos', remote_side=[id], back_populates='eventos_neumaticos_reverse')
    eventos_neumaticos_reverse: Mapped[list['EventosNeumaticos']] = relationship('EventosNeumaticos', remote_side=[relacion_evento_anterior], back_populates='eventos_neumaticos')
    tipo_ruta: Mapped[Optional['TiposRuta']] = relationship('TiposRuta', back_populates='eventos_neumaticos')
    usuario: Mapped['Usuarios'] = relationship('Usuarios', back_populates='eventos_neumaticos')
    vehiculo: Mapped[Optional['Vehiculos']] = relationship('Vehiculos', back_populates='eventos_neumaticos')


class GarantiasNeumaticos(Base):
    __tablename__ = 'garantias_neumaticos'
    __table_args__ = (
        CheckConstraint('fecha_fin IS NULL OR fecha_fin >= fecha_inicio', name='chk_fechas_garantia'),
        CheckConstraint("tipo_garantia::text = ANY (ARRAY['KILOMETRAJE'::character varying::text, 'TIEMPO'::character varying::text, 'AMBOS'::character varying::text])", name='chk_tipo_garantia'),
        ForeignKeyConstraint(['actualizado_por'], ['usuarios.id'], ondelete='SET NULL', name='garantias_neumaticos_actualizado_por_fkey'),
        ForeignKeyConstraint(['creado_por'], ['usuarios.id'], ondelete='SET NULL', name='garantias_neumaticos_creado_por_fkey'),
        ForeignKeyConstraint(['neumatico_id'], ['neumaticos.id'], ondelete='CASCADE', name='garantias_neumaticos_neumatico_id_fkey'),
        ForeignKeyConstraint(['proveedor_id'], ['proveedores.id'], ondelete='SET NULL', name='garantias_neumaticos_proveedor_id_fkey'),
        PrimaryKeyConstraint('id', name='garantias_neumaticos_pkey'),
        Index('idx_garantias_neumatico_id', 'neumatico_id'),
        Index('idx_garantias_vencimiento', 'fecha_fin'),
        {'comment': 'Almacena información detallada sobre las garantías de los '
                'neumáticos'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    neumatico_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    tipo_garantia: Mapped[str] = mapped_column(String(50), nullable=False)
    fecha_inicio: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    creado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    proveedor_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    fecha_fin: Mapped[Optional[datetime.date]] = mapped_column(Date)
    kilometraje_cubierto: Mapped[Optional[int]] = mapped_column(Integer)
    meses_cobertura: Mapped[Optional[int]] = mapped_column(Integer)
    condiciones_url: Mapped[Optional[str]] = mapped_column(Text)
    actualizado_en: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    creado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    actualizado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    usuarios: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[actualizado_por], back_populates='garantias_neumaticos')
    usuarios_: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[creado_por], back_populates='garantias_neumaticos_')
    neumatico: Mapped['Neumaticos'] = relationship('Neumaticos', back_populates='garantias_neumaticos')
    proveedor: Mapped[Optional['Proveedores']] = relationship('Proveedores', back_populates='garantias_neumaticos')


class HistorialEstadosNeumaticos(Base):
    __tablename__ = 'historial_estados_neumaticos'
    __table_args__ = (
        ForeignKeyConstraint(['neumatico_id'], ['neumaticos.id'], ondelete='CASCADE', name='historial_estados_neumaticos_neumatico_id_fkey'),
        ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='SET NULL', name='historial_estados_neumaticos_usuario_id_fkey'),
        PrimaryKeyConstraint('id', name='historial_estados_neumaticos_pkey'),
        Index('idx_hist_estados_estado_nuevo', 'estado_nuevo'),
        Index('idx_hist_estados_fecha', 'fecha_cambio'),
        Index('idx_hist_estados_neumatico_id', 'neumatico_id'),
        {'comment': 'Registra el historial de cambios de estado de los neumáticos'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    neumatico_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    estado_nuevo: Mapped[str] = mapped_column(String(50), nullable=False)
    fecha_cambio: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    estado_anterior: Mapped[Optional[str]] = mapped_column(String(50))
    usuario_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    comentario: Mapped[Optional[str]] = mapped_column(Text)
    metadata_: Mapped[Optional[dict]] = mapped_column('metadata', JSONB)

    neumatico: Mapped['Neumaticos'] = relationship('Neumaticos', back_populates='historial_estados_neumaticos')
    usuario: Mapped[Optional['Usuarios']] = relationship('Usuarios', back_populates='historial_estados_neumaticos')


class MedicionesProfundidad(Base):
    __tablename__ = 'mediciones_profundidad'
    __table_args__ = (
        CheckConstraint('profundidad_mm >= 0::numeric AND profundidad_mm <= 100::numeric', name='mediciones_profundidad_profundidad_mm_check'),
        ForeignKeyConstraint(['actualizado_por'], ['usuarios.id'], ondelete='SET NULL', name='mediciones_profundidad_actualizado_por_fkey'),
        ForeignKeyConstraint(['creado_por'], ['usuarios.id'], ondelete='SET NULL', name='mediciones_profundidad_creado_por_fkey'),
        ForeignKeyConstraint(['neumatico_id'], ['neumaticos.id'], ondelete='CASCADE', name='mediciones_profundidad_neumatico_id_fkey'),
        ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='SET NULL', name='mediciones_profundidad_usuario_id_fkey'),
        PrimaryKeyConstraint('id', name='mediciones_profundidad_pkey'),
        Index('idx_mediciones_profundidad_fecha', 'fecha_medicion'),
        Index('idx_mediciones_profundidad_neumatico_id', 'neumatico_id'),
        {'comment': 'Registra las mediciones de profundidad de la banda de rodadura de '
                'los neumáticos'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    neumatico_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    fecha_medicion: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    profundidad_mm: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False, comment='Profundidad medida en milímetros')
    ubicacion_medicion: Mapped[str] = mapped_column(Text, nullable=False, comment='Ubicación donde se realizó la medición (ej: posición en el vehículo, almacén, etc.)')
    creado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    actualizado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    metodo_medicion: Mapped[Optional[str]] = mapped_column(Text, comment='Método utilizado para la medición (ej: calibrador, escáner, etc.)')
    usuario_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    observaciones: Mapped[Optional[str]] = mapped_column(Text)
    creado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    actualizado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    usuarios: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[actualizado_por], back_populates='mediciones_profundidad')
    usuarios_: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[creado_por], back_populates='mediciones_profundidad_')
    neumatico: Mapped['Neumaticos'] = relationship('Neumaticos', back_populates='mediciones_profundidad')
    usuario: Mapped[Optional['Usuarios']] = relationship('Usuarios', foreign_keys=[usuario_id], back_populates='mediciones_profundidad1')


class ModelosPosicionesPermitidas(Base):
    __tablename__ = 'modelos_posiciones_permitidas'
    __table_args__ = (
        ForeignKeyConstraint(['creado_por'], ['usuarios.id'], ondelete='SET NULL', name='modelos_posiciones_permitidas_creado_por_fkey'),
        ForeignKeyConstraint(['modelo_neumatico_id'], ['modelos_neumatico.id'], ondelete='CASCADE', name='modelos_posiciones_permitidas_modelo_neumatico_id_fkey'),
        ForeignKeyConstraint(['posicion_neumatico_id'], ['posiciones_neumatico.id'], ondelete='CASCADE', name='modelos_posiciones_permitidas_posicion_neumatico_id_fkey'),
        PrimaryKeyConstraint('modelo_neumatico_id', 'posicion_neumatico_id', name='modelos_posiciones_permitidas_pkey'),
        {'comment': 'Relación muchos a muchos entre modelos de neumáticos y posiciones '
                'permitidas'}
    )

    modelo_neumatico_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    posicion_neumatico_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    es_recomendado: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    creado_en: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    creado_por: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    usuarios: Mapped[Optional['Usuarios']] = relationship('Usuarios', back_populates='modelos_posiciones_permitidas')
    modelo_neumatico: Mapped['ModelosNeumatico'] = relationship('ModelosNeumatico', back_populates='modelos_posiciones_permitidas')
    posicion_neumatico: Mapped['PosicionesNeumatico'] = relationship('PosicionesNeumatico', back_populates='modelos_posiciones_permitidas')
