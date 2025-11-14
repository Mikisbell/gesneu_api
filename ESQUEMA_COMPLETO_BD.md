# Esquema Completo de Base de Datos - ges_neu_bd

**Fecha de extracción:** 2025-08-31T20:22:07.754240
**Base de datos:** ges_neu_bd
**PostgreSQL:** PostgreSQL 17.6 on x86_64-windows, compiled by msvc-19.44.35213, 64-bit
**Total de tablas:** 37

## Tipos Enum

### estado_alerta_enum
```sql
CREATE TYPE estado_alerta_enum AS ENUM (
    'NUEVA',
    'VISTA',
    'GESTIONADA'
);
```

### estado_neumatico_enum
```sql
CREATE TYPE estado_neumatico_enum AS ENUM (
    'EN_STOCK',
    'INSTALADO',
    'EN_REPARACION',
    'EN_REENCAUCHE',
    'DESECHADO',
    'EN_TRANSITO'
);
```

### estado_neumatico_enum_destino
```sql
CREATE TYPE estado_neumatico_enum_destino AS ENUM (
    'EN_STOCK',
    'INSTALADO',
    'EN_REPARACION',
    'EN_REENCAUCHE',
    'DESECHADO',
    'PARA_REPARACION',
    'REPARADO',
    'PARA_REENCAUCHE',
    'REENCAUCHADO',
    'EN_TRANSITO'
);
```

### estado_operacion_enum
```sql
CREATE TYPE estado_operacion_enum AS ENUM (
    'PENDIENTE',
    'EN_PROCESO',
    'COMPLETADA',
    'CANCELADA',
    'VENCIDA'
);
```

### estadoalerta
```sql
CREATE TYPE estadoalerta AS ENUM (
    'NUEVA',
    'VISTA',
    'GESTIONADA'
);
```

### estadoneumaticoenum
```sql
CREATE TYPE estadoneumaticoenum AS ENUM (
    'EN_STOCK',
    'INSTALADO',
    'EN_REPARACION',
    'EN_REENCAUCHE',
    'DESECHADO',
    'BAJA'
);
```

### lado_vehiculo_enum
```sql
CREATE TYPE lado_vehiculo_enum AS ENUM (
    'IZQUIERDO',
    'DERECHO',
    'CENTRAL',
    'INDETERMINADO'
);
```

### nivel_severidad_enum
```sql
CREATE TYPE nivel_severidad_enum AS ENUM (
    'INFO',
    'WARN',
    'CRITICAL'
);
```

### nivelseveridad
```sql
CREATE TYPE nivelseveridad AS ENUM (
    'INFO',
    'WARN',
    'CRITICAL'
);
```

### tipo_accion_operacion_enum
```sql
CREATE TYPE tipo_accion_operacion_enum AS ENUM (
    'INSTALACION',
    'DESMONTAJE',
    'ROTACION',
    'REPARACION_NEU',
    'INSPECCION_NEU',
    'OTRO_NEU'
);
```

### tipo_eje_enum
```sql
CREATE TYPE tipo_eje_enum AS ENUM (
    'DIRECCION',
    'TRACCION',
    'ARRASTRE',
    'ELEVADOR',
    'RETRACTIL',
    'OTRO'
);
```

### tipo_evento_neumatico_enum
```sql
CREATE TYPE tipo_evento_neumatico_enum AS ENUM (
    'COMPRA',
    'INSTALACION',
    'DESMONTAJE',
    'INSPECCION',
    'ROTACION',
    'REPARACION_ENTRADA',
    'REPARACION_SALIDA',
    'REENCAUCHE_ENTRADA',
    'REENCAUCHE_SALIDA',
    'DESECHO',
    'AJUSTE_INVENTARIO',
    'TRANSFERENCIA_UBICACION'
);
```

### tipo_operacion_enum
```sql
CREATE TYPE tipo_operacion_enum AS ENUM (
    'ROTACION',
    'BALANCEO',
    'ALINEACION',
    'REPARACION_GENERAL',
    'INSPECCION_GENERAL',
    'CAMBIO_ACEITE',
    'OTRO',
    'DESMONTAJE'
);
```

### tipo_parametro_inventario_enum
```sql
CREATE TYPE tipo_parametro_inventario_enum AS ENUM (
    'PROFUNDIDAD_MINIMA',
    'STOCK_MINIMO',
    'STOCK_MAXIMO',
    'VIDA_UTIL_KM',
    'VIDA_UTIL_ANIOS'
);
```

### tipo_parametro_inventario_gesneu_enum
```sql
CREATE TYPE tipo_parametro_inventario_gesneu_enum AS ENUM (
    'STOCK_MINIMO',
    'STOCK_MAXIMO',
    'PROFUNDIDAD_MINIMA_RETIRO_MM',
    'PROFUNDIDAD_MINIMA_REENCAUCHE_MM',
    'TIEMPO_MAXIMO_VIDA_MESES',
    'MAX_ROTACIONES_PERIODO',
    'MAX_REPARACIONES_PERIODO',
    'VIDA_MAXIMA_ESTANTE_MESES_SIN_USO'
);
```

### tipoalertaenum
```sql
CREATE TYPE tipoalertaenum AS ENUM (
    'PROFUNDIDAD_BAJA',
    'STOCK_MINIMO',
    'LIMITE_REENCAUCHES',
    'PRESION_BAJA',
    'PRESION_ALTA',
    'DESGASTE_IRREGULAR',
    'SOBRECARGA',
    'FIN_VIDA_UTIL_ESTIMADO',
    'MANTENIMIENTO_PREVENTIVO',
    'OTRO'
);
```

### tipoeventoneumaticoenum
```sql
CREATE TYPE tipoeventoneumaticoenum AS ENUM (
    'INSTALACION',
    'DESMONTAJE',
    'ROTACION',
    'INSPECCION',
    'REPARACION',
    'REENCAUCHE_ENTRADA',
    'REENCAUCHE_SALIDA',
    'DESECHO',
    'MOVIMIENTO_ALMACEN',
    'AJUSTE_INVENTARIO',
    'CAMBIO_ESTADO'
);
```

### tipoparametro
```sql
CREATE TYPE tipoparametro AS ENUM (
    'STOCK_MINIMO',
    'STOCK_MAXIMO',
    'PUNTO_REORDEN',
    'VIDA_UTIL',
    'PRESION_OPTIMA',
    'TEMPERATURA_MAXIMA'
);
```

### tipoproveedorenum
```sql
CREATE TYPE tipoproveedorenum AS ENUM (
    'FABRICANTE',
    'DISTRIBUIDOR',
    'SERVICIO_REPARACION',
    'SERVICIO_REENCAUCHE',
    'OTRO'
);
```

## Tablas

### alembic_version

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| version_num | character varying(32) | No |  |  |

#### Restricciones

- **2200_19501_1_not_null** (CHECK) - Condición: version_num IS NOT NULL
- **alembic_version_pkc** (PRIMARY KEY) - Columna: version_num - Referencia: alembic_version.version_num

#### Índices

- **alembic_version_pkc**
  ```sql
  CREATE UNIQUE INDEX alembic_version_pkc ON public.alembic_version USING btree (version_num)
  ```

---

### alertas

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | uuid | No | public.gen_random_uuid() |  |
| tipo_alerta | character varying(50) | No |  |  |
| mensaje | text | No |  |  |
| nivel_severidad | character varying(20) | No | 'INFO'::character varying |  |
| estado_alerta | character varying(20) | No | 'NUEVA'::character varying |  |
| timestamp_generacion | timestamp with time zone | No | now() |  |
| timestamp_gestion | timestamp with time zone | Sí |  |  |
| usuario_gestion_id | uuid | Sí |  |  |
| neumatico_id | uuid | Sí |  |  |
| vehiculo_id | uuid | Sí |  |  |
| modelo_id | uuid | Sí |  |  |
| almacen_id | uuid | Sí |  |  |
| parametro_id | uuid | Sí |  |  |
| datos_contexto | jsonb | Sí |  |  |

#### Restricciones

- **2200_19504_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19504_2_not_null** (CHECK) - Condición: tipo_alerta IS NOT NULL
- **2200_19504_3_not_null** (CHECK) - Condición: mensaje IS NOT NULL
- **2200_19504_4_not_null** (CHECK) - Condición: nivel_severidad IS NOT NULL
- **2200_19504_5_not_null** (CHECK) - Condición: estado_alerta IS NOT NULL
- **2200_19504_6_not_null** (CHECK) - Condición: timestamp_generacion IS NOT NULL
- **alertas_estado_alerta_check** (CHECK) - Referencia: alertas.estado_alerta - Condición: ((estado_alerta)::text = ANY (ARRAY[('NUEVA'::character varying)::text, ('VISTA'::character varying)::text, ('GESTIONADA'::character varying)::text]))
- **alertas_nivel_severidad_check** (CHECK) - Referencia: alertas.nivel_severidad - Condición: ((nivel_severidad)::text = ANY (ARRAY[('INFO'::character varying)::text, ('WARN'::character varying)::text, ('CRITICAL'::character varying)::text]))
- **alertas_almacen_id_fkey** (FOREIGN KEY) - Columna: almacen_id - Referencia: almacenes.id
- **alertas_modelo_id_fkey** (FOREIGN KEY) - Columna: modelo_id - Referencia: modelos_neumatico.id
- **alertas_neumatico_id_fkey** (FOREIGN KEY) - Columna: neumatico_id - Referencia: neumaticos.id
- **alertas_parametro_id_fkey** (FOREIGN KEY) - Columna: parametro_id - Referencia: parametros_inventario.id
- **alertas_usuario_gestion_id_fkey** (FOREIGN KEY) - Columna: usuario_gestion_id - Referencia: usuarios.id
- **alertas_vehiculo_id_fkey** (FOREIGN KEY) - Columna: vehiculo_id - Referencia: vehiculos.id
- **alertas_pkey** (PRIMARY KEY) - Columna: id - Referencia: alertas.id

#### Índices

- **alertas_pkey**
  ```sql
  CREATE UNIQUE INDEX alertas_pkey ON public.alertas USING btree (id)
  ```
- **idx_alertas_estado_ts**
  ```sql
  CREATE INDEX idx_alertas_estado_ts ON public.alertas USING btree (estado_alerta, timestamp_generacion DESC)
  ```
- **idx_alertas_fecha**
  ```sql
  CREATE INDEX idx_alertas_fecha ON public.alertas USING btree (timestamp_generacion DESC) WHERE ((estado_alerta)::text = 'NUEVA'::text)
  ```
- **idx_alertas_neumatico**
  ```sql
  CREATE INDEX idx_alertas_neumatico ON public.alertas USING btree (neumatico_id) WHERE (neumatico_id IS NOT NULL)
  ```

---

### almacenes

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | uuid | No | public.gen_random_uuid() |  |
| codigo | character varying(20) | No |  |  |
| nombre | character varying(150) | No |  |  |
| tipo | character varying(50) | Sí |  |  |
| direccion | text | Sí |  |  |
| activo | boolean | No | true |  |
| creado_en | timestamp with time zone | No | now() |  |
| creado_por | uuid | Sí |  |  |
| actualizado_en | timestamp with time zone | Sí |  |  |
| actualizado_por | uuid | Sí |  |  |

#### Restricciones

- **2200_19515_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19515_2_not_null** (CHECK) - Condición: codigo IS NOT NULL
- **2200_19515_3_not_null** (CHECK) - Condición: nombre IS NOT NULL
- **2200_19515_6_not_null** (CHECK) - Condición: activo IS NOT NULL
- **2200_19515_7_not_null** (CHECK) - Condición: creado_en IS NOT NULL
- **almacenes_actualizado_por_fkey** (FOREIGN KEY) - Columna: actualizado_por - Referencia: usuarios.id
- **almacenes_creado_por_fkey** (FOREIGN KEY) - Columna: creado_por - Referencia: usuarios.id
- **almacenes_pkey** (PRIMARY KEY) - Columna: id - Referencia: almacenes.id
- **almacenes_codigo_key** (UNIQUE) - Columna: codigo - Referencia: almacenes.codigo

#### Índices

- **almacenes_codigo_key**
  ```sql
  CREATE UNIQUE INDEX almacenes_codigo_key ON public.almacenes USING btree (codigo)
  ```
- **almacenes_pkey**
  ```sql
  CREATE UNIQUE INDEX almacenes_pkey ON public.almacenes USING btree (id)
  ```

---

### auditoria_log

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | bigint(64) | No | nextval('auditoria_log_id_seq'::regclass) |  |
| timestamp_log | timestamp with time zone | No | now() |  |
| esquema_tabla | character varying(63) | No |  |  |
| nombre_tabla | character varying(63) | No |  |  |
| operacion | character varying(10) | No |  |  |
| usuario_db | character varying(63) | No | CURRENT_USER |  |
| usuario_aplicacion_id | uuid | Sí |  |  |
| usuario_aplicacion_username | character varying(50) | Sí |  |  |
| direccion_ip | character varying(45) | Sí |  |  |
| user_agent | text | Sí |  |  |
| id_entidad | text | Sí |  |  |
| datos_antiguos | jsonb | Sí |  |  |
| datos_nuevos | jsonb | Sí |  |  |
| cambios | jsonb | Sí |  |  |
| contexto_aplicacion | jsonb | Sí |  |  |
| query_ejecutada | text | Sí |  |  |

#### Restricciones

- **2200_19523_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19523_2_not_null** (CHECK) - Condición: timestamp_log IS NOT NULL
- **2200_19523_3_not_null** (CHECK) - Condición: esquema_tabla IS NOT NULL
- **2200_19523_4_not_null** (CHECK) - Condición: nombre_tabla IS NOT NULL
- **2200_19523_5_not_null** (CHECK) - Condición: operacion IS NOT NULL
- **2200_19523_6_not_null** (CHECK) - Condición: usuario_db IS NOT NULL
- **auditoria_log_operacion_check** (CHECK) - Referencia: auditoria_log.operacion - Condición: ((operacion)::text = ANY (ARRAY[('INSERT'::character varying)::text, ('UPDATE'::character varying)::text, ('DELETE'::character varying)::text]))
- **auditoria_log_usuario_aplicacion_id_fkey** (FOREIGN KEY) - Columna: usuario_aplicacion_id - Referencia: usuarios.id
- **auditoria_log_pkey** (PRIMARY KEY) - Columna: id - Referencia: auditoria_log.id

#### Índices

- **auditoria_log_pkey**
  ```sql
  CREATE UNIQUE INDEX auditoria_log_pkey ON public.auditoria_log USING btree (id)
  ```
- **idx_audit_log_cambios_gin**
  ```sql
  CREATE INDEX idx_audit_log_cambios_gin ON public.auditoria_log USING gin (cambios)
  ```
- **idx_audit_log_datos_antiguos_gin**
  ```sql
  CREATE INDEX idx_audit_log_datos_antiguos_gin ON public.auditoria_log USING gin (datos_antiguos)
  ```
- **idx_audit_log_datos_nuevos_gin**
  ```sql
  CREATE INDEX idx_audit_log_datos_nuevos_gin ON public.auditoria_log USING gin (datos_nuevos)
  ```
- **idx_audit_log_id_entidad**
  ```sql
  CREATE INDEX idx_audit_log_id_entidad ON public.auditoria_log USING btree (id_entidad) WHERE (id_entidad IS NOT NULL)
  ```
- **idx_audit_log_nombre_tabla_lower**
  ```sql
  CREATE INDEX idx_audit_log_nombre_tabla_lower ON public.auditoria_log USING btree (lower((nombre_tabla)::text))
  ```
- **idx_audit_log_operacion_timestamp**
  ```sql
  CREATE INDEX idx_audit_log_operacion_timestamp ON public.auditoria_log USING btree (operacion, timestamp_log)
  ```
- **idx_audit_log_tabla_timestamp**
  ```sql
  CREATE INDEX idx_audit_log_tabla_timestamp ON public.auditoria_log USING btree (nombre_tabla, timestamp_log)
  ```
- **idx_audit_log_usuario_timestamp**
  ```sql
  CREATE INDEX idx_audit_log_usuario_timestamp ON public.auditoria_log USING btree (usuario_aplicacion_username, timestamp_log) WHERE (usuario_aplicacion_username IS NOT NULL)
  ```

---

### auditoria_roles_usuarios

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | bigint(64) | No | nextval('auditoria_roles_usuarios_id_seq'::regclass) |  |
| usuario_id | uuid | No |  |  |
| rol_id | uuid | No |  |  |
| accion | character varying(10) | No |  |  |
| ejecutado_por | uuid | Sí |  |  |
| ejecutado_en | timestamp with time zone | No | now() |  |
| metadata | jsonb | Sí |  |  |

#### Restricciones

- **2200_19532_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19532_2_not_null** (CHECK) - Condición: usuario_id IS NOT NULL
- **2200_19532_3_not_null** (CHECK) - Condición: rol_id IS NOT NULL
- **2200_19532_4_not_null** (CHECK) - Condición: accion IS NOT NULL
- **2200_19532_6_not_null** (CHECK) - Condición: ejecutado_en IS NOT NULL
- **auditoria_roles_usuarios_pkey** (PRIMARY KEY) - Columna: id - Referencia: auditoria_roles_usuarios.id

#### Índices

- **auditoria_roles_usuarios_pkey**
  ```sql
  CREATE UNIQUE INDEX auditoria_roles_usuarios_pkey ON public.auditoria_roles_usuarios USING btree (id)
  ```

---

### bitacora_mantenimiento

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | integer(32) | No | nextval('bitacora_mantenimiento_id_seq'::regclass) |  |
| fecha_ejecucion | timestamp with time zone | No | now() |  |
| tipo | character varying(50) | No |  |  |
| descripcion | text | No |  |  |
| ejecutado_por | name | No | CURRENT_USER |  |
| duracion | interval | Sí |  |  |
| exito | boolean | Sí | true |  |
| detalles | text | Sí |  |  |

#### Restricciones

- **2200_19539_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19539_2_not_null** (CHECK) - Condición: fecha_ejecucion IS NOT NULL
- **2200_19539_3_not_null** (CHECK) - Condición: tipo IS NOT NULL
- **2200_19539_4_not_null** (CHECK) - Condición: descripcion IS NOT NULL
- **2200_19539_5_not_null** (CHECK) - Condición: ejecutado_por IS NOT NULL
- **bitacora_mantenimiento_pkey** (PRIMARY KEY) - Columna: id - Referencia: bitacora_mantenimiento.id

#### Índices

- **bitacora_mantenimiento_pkey**
  ```sql
  CREATE UNIQUE INDEX bitacora_mantenimiento_pkey ON public.bitacora_mantenimiento USING btree (id)
  ```
- **idx_bitacora_mantenimiento_exito**
  ```sql
  CREATE INDEX idx_bitacora_mantenimiento_exito ON public.bitacora_mantenimiento USING btree (exito)
  ```
- **idx_bitacora_mantenimiento_fecha**
  ```sql
  CREATE INDEX idx_bitacora_mantenimiento_fecha ON public.bitacora_mantenimiento USING btree (fecha_ejecucion)
  ```
- **idx_bitacora_mantenimiento_tipo**
  ```sql
  CREATE INDEX idx_bitacora_mantenimiento_tipo ON public.bitacora_mantenimiento USING btree (tipo)
  ```

---

### bitacora_operaciones

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | uuid | No | gen_random_uuid() |  |
| tipo_operacion | USER-DEFINED | No |  |  |
| descripcion | text | No |  |  |
| fecha_operacion | timestamp with time zone | No | now() |  |
| usuario_id | uuid | Sí |  |  |
| almacen_id | uuid | Sí |  |  |
| vehiculo_id | uuid | Sí |  |  |
| estado_operacion | USER-DEFINED | No |  |  |
| duracion_minutos | integer(32) | Sí |  |  |
| costo_estimado | numeric(10,2) | Sí |  |  |
| costo_real | numeric(10,2) | Sí |  |  |
| proveedor_id | uuid | Sí |  |  |
| observaciones | text | Sí |  |  |
| creado_en | timestamp with time zone | No | now() |  |
| actualizado_en | timestamp with time zone | No | now() |  |
| creado_por | uuid | Sí |  |  |
| actualizado_por | uuid | Sí |  |  |

#### Restricciones

- **2200_19548_14_not_null** (CHECK) - Condición: creado_en IS NOT NULL
- **2200_19548_15_not_null** (CHECK) - Condición: actualizado_en IS NOT NULL
- **2200_19548_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19548_2_not_null** (CHECK) - Condición: tipo_operacion IS NOT NULL
- **2200_19548_3_not_null** (CHECK) - Condición: descripcion IS NOT NULL
- **2200_19548_4_not_null** (CHECK) - Condición: fecha_operacion IS NOT NULL
- **2200_19548_8_not_null** (CHECK) - Condición: estado_operacion IS NOT NULL
- **bitacora_operaciones_actualizado_por_fkey** (FOREIGN KEY) - Columna: actualizado_por - Referencia: usuarios.id
- **bitacora_operaciones_almacen_id_fkey** (FOREIGN KEY) - Columna: almacen_id - Referencia: almacenes.id
- **bitacora_operaciones_creado_por_fkey** (FOREIGN KEY) - Columna: creado_por - Referencia: usuarios.id
- **bitacora_operaciones_proveedor_id_fkey** (FOREIGN KEY) - Columna: proveedor_id - Referencia: proveedores.id
- **bitacora_operaciones_usuario_id_fkey** (FOREIGN KEY) - Columna: usuario_id - Referencia: usuarios.id
- **bitacora_operaciones_vehiculo_id_fkey** (FOREIGN KEY) - Columna: vehiculo_id - Referencia: vehiculos.id
- **bitacora_operaciones_pkey** (PRIMARY KEY) - Columna: id - Referencia: bitacora_operaciones.id

#### Índices

- **bitacora_operaciones_pkey**
  ```sql
  CREATE UNIQUE INDEX bitacora_operaciones_pkey ON public.bitacora_operaciones USING btree (id)
  ```
- **idx_bitacora_operaciones_almacen**
  ```sql
  CREATE INDEX idx_bitacora_operaciones_almacen ON public.bitacora_operaciones USING btree (almacen_id) WHERE (almacen_id IS NOT NULL)
  ```
- **idx_bitacora_operaciones_estado**
  ```sql
  CREATE INDEX idx_bitacora_operaciones_estado ON public.bitacora_operaciones USING btree (estado_operacion)
  ```
- **idx_bitacora_operaciones_fecha**
  ```sql
  CREATE INDEX idx_bitacora_operaciones_fecha ON public.bitacora_operaciones USING btree (fecha_operacion)
  ```
- **idx_bitacora_operaciones_vehiculo**
  ```sql
  CREATE INDEX idx_bitacora_operaciones_vehiculo ON public.bitacora_operaciones USING btree (vehiculo_id) WHERE (vehiculo_id IS NOT NULL)
  ```

---

### bitacora_operaciones_neumaticos

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | uuid | No | gen_random_uuid() |  |
| operacion_id | uuid | No |  |  |
| neumatico_id | uuid | No |  |  |
| tipo_accion | USER-DEFINED | No |  |  |
| posicion_neumatico_id | uuid | Sí |  |  |
| profundidad_inicial_mm | numeric(5,2) | Sí |  |  |
| profundidad_final_mm | numeric(5,2) | Sí |  |  |
| presion_inicial_psi | numeric(5,2) | Sí |  |  |
| presion_final_psi | numeric(5,2) | Sí |  |  |
| kilometraje_vehiculo_km | numeric(10,2) | Sí |  |  |
| observaciones | text | Sí |  |  |
| creado_en | timestamp with time zone | No | now() |  |
| actualizado_en | timestamp with time zone | No | now() |  |
| creado_por | uuid | Sí |  |  |
| actualizado_por | uuid | Sí |  |  |

#### Restricciones

- **2200_19557_12_not_null** (CHECK) - Condición: creado_en IS NOT NULL
- **2200_19557_13_not_null** (CHECK) - Condición: actualizado_en IS NOT NULL
- **2200_19557_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19557_2_not_null** (CHECK) - Condición: operacion_id IS NOT NULL
- **2200_19557_3_not_null** (CHECK) - Condición: neumatico_id IS NOT NULL
- **2200_19557_4_not_null** (CHECK) - Condición: tipo_accion IS NOT NULL
- **bitacora_operaciones_neumaticos_actualizado_por_fkey** (FOREIGN KEY) - Columna: actualizado_por - Referencia: usuarios.id
- **bitacora_operaciones_neumaticos_creado_por_fkey** (FOREIGN KEY) - Columna: creado_por - Referencia: usuarios.id
- **bitacora_operaciones_neumaticos_neumatico_id_fkey** (FOREIGN KEY) - Columna: neumatico_id - Referencia: neumaticos.id
- **bitacora_operaciones_neumaticos_operacion_id_fkey** (FOREIGN KEY) - Columna: operacion_id - Referencia: bitacora_operaciones.id
- **bitacora_operaciones_neumaticos_posicion_neumatico_id_fkey** (FOREIGN KEY) - Columna: posicion_neumatico_id - Referencia: posiciones_neumatico.id
- **bitacora_operaciones_neumaticos_pkey** (PRIMARY KEY) - Columna: id - Referencia: bitacora_operaciones_neumaticos.id
- **bitacora_operaciones_neumatic_operacion_id_neumatico_id_tip_key** (UNIQUE) - Columna: neumatico_id - Referencia: bitacora_operaciones_neumaticos.operacion_id
- **bitacora_operaciones_neumatic_operacion_id_neumatico_id_tip_key** (UNIQUE) - Columna: neumatico_id - Referencia: bitacora_operaciones_neumaticos.neumatico_id
- **bitacora_operaciones_neumatic_operacion_id_neumatico_id_tip_key** (UNIQUE) - Columna: operacion_id - Referencia: bitacora_operaciones_neumaticos.tipo_accion
- **bitacora_operaciones_neumatic_operacion_id_neumatico_id_tip_key** (UNIQUE) - Columna: tipo_accion - Referencia: bitacora_operaciones_neumaticos.operacion_id
- **bitacora_operaciones_neumatic_operacion_id_neumatico_id_tip_key** (UNIQUE) - Columna: operacion_id - Referencia: bitacora_operaciones_neumaticos.operacion_id
- **bitacora_operaciones_neumatic_operacion_id_neumatico_id_tip_key** (UNIQUE) - Columna: tipo_accion - Referencia: bitacora_operaciones_neumaticos.tipo_accion
- **bitacora_operaciones_neumatic_operacion_id_neumatico_id_tip_key** (UNIQUE) - Columna: operacion_id - Referencia: bitacora_operaciones_neumaticos.neumatico_id
- **bitacora_operaciones_neumatic_operacion_id_neumatico_id_tip_key** (UNIQUE) - Columna: tipo_accion - Referencia: bitacora_operaciones_neumaticos.neumatico_id
- **bitacora_operaciones_neumatic_operacion_id_neumatico_id_tip_key** (UNIQUE) - Columna: neumatico_id - Referencia: bitacora_operaciones_neumaticos.tipo_accion

#### Índices

- **bitacora_operaciones_neumatic_operacion_id_neumatico_id_tip_key**
  ```sql
  CREATE UNIQUE INDEX bitacora_operaciones_neumatic_operacion_id_neumatico_id_tip_key ON public.bitacora_operaciones_neumaticos USING btree (operacion_id, neumatico_id, tipo_accion)
  ```
- **bitacora_operaciones_neumaticos_pkey**
  ```sql
  CREATE UNIQUE INDEX bitacora_operaciones_neumaticos_pkey ON public.bitacora_operaciones_neumaticos USING btree (id)
  ```
- **idx_bitacora_op_neu_neumatico**
  ```sql
  CREATE INDEX idx_bitacora_op_neu_neumatico ON public.bitacora_operaciones_neumaticos USING btree (neumatico_id)
  ```
- **idx_bitacora_op_neu_operacion**
  ```sql
  CREATE INDEX idx_bitacora_op_neu_operacion ON public.bitacora_operaciones_neumaticos USING btree (operacion_id)
  ```
- **idx_bitacora_op_neu_posicion**
  ```sql
  CREATE INDEX idx_bitacora_op_neu_posicion ON public.bitacora_operaciones_neumaticos USING btree (posicion_neumatico_id) WHERE (posicion_neumatico_id IS NOT NULL)
  ```
- **idx_bitacora_op_neu_tipo_accion**
  ```sql
  CREATE INDEX idx_bitacora_op_neu_tipo_accion ON public.bitacora_operaciones_neumaticos USING btree (tipo_accion)
  ```

---

### configuracion_auditoria

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| nombre_tabla | character varying(63) | No |  |  |
| activo | boolean | No | true |  |
| prioridad | character varying(20) | Sí |  |  |
| campos_excluidos | jsonb | Sí | '{}'::jsonb |  |
| creado_en | timestamp with time zone | Sí | now() |  |
| actualizado_en | timestamp with time zone | Sí | now() |  |

#### Restricciones

- **2200_19565_1_not_null** (CHECK) - Condición: nombre_tabla IS NOT NULL
- **2200_19565_2_not_null** (CHECK) - Condición: activo IS NOT NULL
- **configuracion_auditoria_prioridad_check** (CHECK) - Referencia: configuracion_auditoria.prioridad - Condición: ((prioridad)::text = ANY (ARRAY[('low'::character varying)::text, ('medium'::character varying)::text, ('high'::character varying)::text]))
- **configuracion_auditoria_pkey** (PRIMARY KEY) - Columna: nombre_tabla - Referencia: configuracion_auditoria.nombre_tabla

#### Índices

- **configuracion_auditoria_pkey**
  ```sql
  CREATE UNIQUE INDEX configuracion_auditoria_pkey ON public.configuracion_auditoria USING btree (nombre_tabla)
  ```

---

### configuraciones_eje

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | uuid | No | public.gen_random_uuid() |  |
| tipo_vehiculo_id | uuid | No |  |  |
| numero_eje | smallint(16) | No |  |  |
| nombre_eje | character varying(50) | No |  |  |
| tipo_eje | USER-DEFINED | No |  |  |
| numero_posiciones | smallint(16) | No |  |  |
| posiciones_duales | boolean | No | false |  |
| permite_reencauchados | boolean | No | true |  |
| neumaticos_por_posicion | smallint(16) | No | 1 |  |
| creado_en | timestamp with time zone | No | now() |  |
| creado_por | uuid | Sí |  |  |
| actualizado_en | timestamp with time zone | Sí |  |  |
| actualizado_por | uuid | Sí |  |  |

#### Restricciones

- **2200_19575_10_not_null** (CHECK) - Condición: creado_en IS NOT NULL
- **2200_19575_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19575_2_not_null** (CHECK) - Condición: tipo_vehiculo_id IS NOT NULL
- **2200_19575_3_not_null** (CHECK) - Condición: numero_eje IS NOT NULL
- **2200_19575_4_not_null** (CHECK) - Condición: nombre_eje IS NOT NULL
- **2200_19575_5_not_null** (CHECK) - Condición: tipo_eje IS NOT NULL
- **2200_19575_6_not_null** (CHECK) - Condición: numero_posiciones IS NOT NULL
- **2200_19575_7_not_null** (CHECK) - Condición: posiciones_duales IS NOT NULL
- **2200_19575_8_not_null** (CHECK) - Condición: permite_reencauchados IS NOT NULL
- **2200_19575_9_not_null** (CHECK) - Condición: neumaticos_por_posicion IS NOT NULL
- **configuraciones_eje_neumaticos_por_posicion_check** (CHECK) - Referencia: configuraciones_eje.neumaticos_por_posicion - Condición: (neumaticos_por_posicion = ANY (ARRAY[1, 2]))
- **configuraciones_eje_numero_eje_check** (CHECK) - Referencia: configuraciones_eje.numero_eje - Condición: (numero_eje > 0)
- **configuraciones_eje_numero_posiciones_check** (CHECK) - Referencia: configuraciones_eje.numero_posiciones - Condición: ((numero_posiciones >= 1) AND (numero_posiciones <= 6))
- **configuraciones_eje_actualizado_por_fkey** (FOREIGN KEY) - Columna: actualizado_por - Referencia: usuarios.id
- **configuraciones_eje_creado_por_fkey** (FOREIGN KEY) - Columna: creado_por - Referencia: usuarios.id
- **configuraciones_eje_tipo_vehiculo_id_fkey** (FOREIGN KEY) - Columna: tipo_vehiculo_id - Referencia: tipos_vehiculo.id
- **configuraciones_eje_pkey** (PRIMARY KEY) - Columna: id - Referencia: configuraciones_eje.id
- **uq_configuracion_eje** (UNIQUE) - Columna: numero_eje - Referencia: configuraciones_eje.numero_eje
- **uq_configuracion_eje** (UNIQUE) - Columna: tipo_vehiculo_id - Referencia: configuraciones_eje.tipo_vehiculo_id
- **uq_configuracion_eje** (UNIQUE) - Columna: tipo_vehiculo_id - Referencia: configuraciones_eje.numero_eje
- **uq_configuracion_eje** (UNIQUE) - Columna: numero_eje - Referencia: configuraciones_eje.tipo_vehiculo_id

#### Índices

- **configuraciones_eje_pkey**
  ```sql
  CREATE UNIQUE INDEX configuraciones_eje_pkey ON public.configuraciones_eje USING btree (id)
  ```
- **uq_configuracion_eje**
  ```sql
  CREATE UNIQUE INDEX uq_configuracion_eje ON public.configuraciones_eje USING btree (tipo_vehiculo_id, numero_eje)
  ```

---

### errores_aplicacion

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | uuid | No | gen_random_uuid() |  |
| nombre_funcion | text | No |  |  |
| mensaje_error | text | No |  |  |
| detalles | jsonb | Sí |  |  |
| creado_por | text | Sí | 'SISTEMA'::text |  |
| creado_en | timestamp with time zone | No | now() |  |
| resuelto | boolean | Sí | false |  |
| resuelto_por | text | Sí |  |  |
| resuelto_en | timestamp with time zone | Sí |  |  |
| comentario_resolucion | text | Sí |  |  |

#### Restricciones

- **2200_19586_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19586_2_not_null** (CHECK) - Condición: nombre_funcion IS NOT NULL
- **2200_19586_3_not_null** (CHECK) - Condición: mensaje_error IS NOT NULL
- **2200_19586_6_not_null** (CHECK) - Condición: creado_en IS NOT NULL
- **errores_aplicacion_pkey** (PRIMARY KEY) - Columna: id - Referencia: errores_aplicacion.id

#### Índices

- **errores_aplicacion_pkey**
  ```sql
  CREATE UNIQUE INDEX errores_aplicacion_pkey ON public.errores_aplicacion USING btree (id)
  ```
- **idx_errores_aplicacion_creado_en**
  ```sql
  CREATE INDEX idx_errores_aplicacion_creado_en ON public.errores_aplicacion USING btree (creado_en)
  ```
- **idx_errores_aplicacion_nombre_funcion**
  ```sql
  CREATE INDEX idx_errores_aplicacion_nombre_funcion ON public.errores_aplicacion USING btree (nombre_funcion)
  ```
- **idx_errores_aplicacion_resuelto**
  ```sql
  CREATE INDEX idx_errores_aplicacion_resuelto ON public.errores_aplicacion USING btree (resuelto)
  ```

---

### especificaciones_desgaste

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | uuid | No | public.gen_random_uuid() |  |
| modelo_neumatico_id | uuid | No |  |  |
| tipo_posicion | character varying(50) | No |  |  |
| vida_util_km_min | integer(32) | No |  |  |
| vida_util_km_max | integer(32) | No |  |  |
| descripcion_estado | character varying(100) | No |  |  |
| creado_en | timestamp with time zone | No | now() |  |
| creado_por | uuid | Sí |  |  |
| actualizado_en | timestamp with time zone | Sí |  |  |
| actualizado_por | uuid | Sí |  |  |

#### Restricciones

- **2200_19595_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19595_2_not_null** (CHECK) - Condición: modelo_neumatico_id IS NOT NULL
- **2200_19595_3_not_null** (CHECK) - Condición: tipo_posicion IS NOT NULL
- **2200_19595_4_not_null** (CHECK) - Condición: vida_util_km_min IS NOT NULL
- **2200_19595_5_not_null** (CHECK) - Condición: vida_util_km_max IS NOT NULL
- **2200_19595_6_not_null** (CHECK) - Condición: descripcion_estado IS NOT NULL
- **2200_19595_7_not_null** (CHECK) - Condición: creado_en IS NOT NULL
- **especificaciones_desgaste_check_km** (CHECK) - Referencia: especificaciones_desgaste.vida_util_km_min - Condición: (vida_util_km_min < vida_util_km_max)
- **especificaciones_desgaste_check_km** (CHECK) - Referencia: especificaciones_desgaste.vida_util_km_max - Condición: (vida_util_km_min < vida_util_km_max)
- **especificaciones_desgaste_actualizado_por_fkey** (FOREIGN KEY) - Columna: actualizado_por - Referencia: usuarios.id
- **especificaciones_desgaste_creado_por_fkey** (FOREIGN KEY) - Columna: creado_por - Referencia: usuarios.id
- **especificaciones_desgaste_modelo_neumatico_id_fkey** (FOREIGN KEY) - Columna: modelo_neumatico_id - Referencia: modelos_neumatico.id
- **especificaciones_desgaste_pkey** (PRIMARY KEY) - Columna: id - Referencia: especificaciones_desgaste.id

#### Índices

- **especificaciones_desgaste_pkey**
  ```sql
  CREATE UNIQUE INDEX especificaciones_desgaste_pkey ON public.especificaciones_desgaste USING btree (id)
  ```
- **idx_especificaciones_desgaste_modelo**
  ```sql
  CREATE INDEX idx_especificaciones_desgaste_modelo ON public.especificaciones_desgaste USING btree (modelo_neumatico_id)
  ```
- **idx_especificaciones_desgaste_tipo_posicion**
  ```sql
  CREATE INDEX idx_especificaciones_desgaste_tipo_posicion ON public.especificaciones_desgaste USING btree (tipo_posicion)
  ```

---

### eventos_neumaticos

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | uuid | No | public.gen_random_uuid() |  |
| neumatico_id | uuid | No |  |  |
| tipo_evento | USER-DEFINED | No |  |  |
| timestamp_evento | timestamp with time zone | No | now() |  |
| usuario_id | uuid | No |  |  |
| vehiculo_id | uuid | Sí |  |  |
| posicion_id | uuid | Sí |  |  |
| odometro_vehiculo_en_evento | integer(32) | Sí |  |  |
| profundidad_remanente_mm | numeric(5,2) | Sí |  |  |
| presion_psi | numeric(5,2) | Sí |  |  |
| costo_evento | numeric(10,2) | Sí |  |  |
| moneda_costo | character varying(3) | Sí | 'PEN'::character varying |  |
| proveedor_servicio_id | uuid | Sí |  |  |
| notas | text | Sí |  |  |
| destino_desmontaje | USER-DEFINED | Sí |  |  |
| motivo_desecho_id_evento | uuid | Sí |  |  |
| profundidad_post_reencauche_mm | numeric(5,2) | Sí |  |  |
| datos_evento | jsonb | Sí |  |  |
| relacion_evento_anterior | uuid | Sí |  |  |
| creado_en | timestamp with time zone | No | now() |  |
| almacen_destino_id | uuid | Sí |  |  |
| tipo_ruta_id | uuid | Sí |  |  |
| peso_carga_promedio_ton_evento | numeric(5,2) | Sí |  |  |
| motivo_reparacion_texto | text | Sí |  |  |
| tipo_dano_detectado_texto | text | Sí |  |  |

#### Restricciones

- **2200_19601_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19601_20_not_null** (CHECK) - Condición: creado_en IS NOT NULL
- **2200_19601_2_not_null** (CHECK) - Condición: neumatico_id IS NOT NULL
- **2200_19601_3_not_null** (CHECK) - Condición: tipo_evento IS NOT NULL
- **2200_19601_4_not_null** (CHECK) - Condición: timestamp_evento IS NOT NULL
- **2200_19601_5_not_null** (CHECK) - Condición: usuario_id IS NOT NULL
- **chk_destino_desmontaje** (CHECK) - Referencia: eventos_neumaticos.destino_desmontaje - Condición: ((tipo_evento <> 'DESMONTAJE'::tipo_evento_neumatico_enum) OR (destino_desmontaje IS NOT NULL))
- **chk_destino_desmontaje** (CHECK) - Referencia: eventos_neumaticos.tipo_evento - Condición: ((tipo_evento <> 'DESMONTAJE'::tipo_evento_neumatico_enum) OR (destino_desmontaje IS NOT NULL))
- **chk_motivo_desecho** (CHECK) - Referencia: eventos_neumaticos.destino_desmontaje - Condición: (((tipo_evento <> 'DESECHO'::tipo_evento_neumatico_enum) AND ((tipo_evento <> 'DESMONTAJE'::tipo_evento_neumatico_enum) OR (destino_desmontaje <> 'DESECHADO'::estado_neumatico_enum))) OR (motivo_desecho_id_evento IS NOT NULL))
- **chk_motivo_desecho** (CHECK) - Referencia: eventos_neumaticos.motivo_desecho_id_evento - Condición: (((tipo_evento <> 'DESECHO'::tipo_evento_neumatico_enum) AND ((tipo_evento <> 'DESMONTAJE'::tipo_evento_neumatico_enum) OR (destino_desmontaje <> 'DESECHADO'::estado_neumatico_enum))) OR (motivo_desecho_id_evento IS NOT NULL))
- **chk_motivo_desecho** (CHECK) - Referencia: eventos_neumaticos.tipo_evento - Condición: (((tipo_evento <> 'DESECHO'::tipo_evento_neumatico_enum) AND ((tipo_evento <> 'DESMONTAJE'::tipo_evento_neumatico_enum) OR (destino_desmontaje <> 'DESECHADO'::estado_neumatico_enum))) OR (motivo_desecho_id_evento IS NOT NULL))
- **chk_profundidad_reencauche** (CHECK) - Referencia: eventos_neumaticos.profundidad_post_reencauche_mm - Condición: ((tipo_evento <> 'REENCAUCHE_SALIDA'::tipo_evento_neumatico_enum) OR (profundidad_post_reencauche_mm IS NOT NULL))
- **chk_profundidad_reencauche** (CHECK) - Referencia: eventos_neumaticos.tipo_evento - Condición: ((tipo_evento <> 'REENCAUCHE_SALIDA'::tipo_evento_neumatico_enum) OR (profundidad_post_reencauche_mm IS NOT NULL))
- **eventos_neumaticos_costo_evento_check** (CHECK) - Referencia: eventos_neumaticos.costo_evento - Condición: ((costo_evento IS NULL) OR (costo_evento >= (0)::numeric))
- **eventos_neumaticos_odometro_vehiculo_en_evento_check** (CHECK) - Referencia: eventos_neumaticos.odometro_vehiculo_en_evento - Condición: ((odometro_vehiculo_en_evento IS NULL) OR (odometro_vehiculo_en_evento >= 0))
- **eventos_neumaticos_presion_psi_check** (CHECK) - Referencia: eventos_neumaticos.presion_psi - Condición: ((presion_psi IS NULL) OR (presion_psi > (0)::numeric))
- **eventos_neumaticos_profundidad_post_reencauche_mm_check** (CHECK) - Referencia: eventos_neumaticos.profundidad_post_reencauche_mm - Condición: ((profundidad_post_reencauche_mm IS NULL) OR (profundidad_post_reencauche_mm > (0)::numeric))
- **eventos_neumaticos_profundidad_remanente_mm_check** (CHECK) - Referencia: eventos_neumaticos.profundidad_remanente_mm - Condición: ((profundidad_remanente_mm IS NULL) OR (profundidad_remanente_mm >= (0)::numeric))
- **eventos_neumaticos_almacen_destino_id_fkey** (FOREIGN KEY) - Columna: almacen_destino_id - Referencia: almacenes.id
- **eventos_neumaticos_motivo_desecho_id_evento_fkey** (FOREIGN KEY) - Columna: motivo_desecho_id_evento - Referencia: motivos_desecho.id
- **eventos_neumaticos_neumatico_id_fkey** (FOREIGN KEY) - Columna: neumatico_id - Referencia: neumaticos.id
- **eventos_neumaticos_posicion_id_fkey** (FOREIGN KEY) - Columna: posicion_id - Referencia: posiciones_neumatico.id
- **eventos_neumaticos_proveedor_servicio_id_fkey** (FOREIGN KEY) - Columna: proveedor_servicio_id - Referencia: proveedores.id
- **eventos_neumaticos_relacion_evento_anterior_fkey** (FOREIGN KEY) - Columna: relacion_evento_anterior - Referencia: eventos_neumaticos.id
- **eventos_neumaticos_usuario_id_fkey** (FOREIGN KEY) - Columna: usuario_id - Referencia: usuarios.id
- **eventos_neumaticos_vehiculo_id_fkey** (FOREIGN KEY) - Columna: vehiculo_id - Referencia: vehiculos.id
- **fk_eventos_neumaticos_tipo_ruta** (FOREIGN KEY) - Columna: tipo_ruta_id - Referencia: tipos_ruta.id
- **eventos_neumaticos_pkey** (PRIMARY KEY) - Columna: id - Referencia: eventos_neumaticos.id

#### Índices

- **eventos_neumaticos_pkey**
  ```sql
  CREATE UNIQUE INDEX eventos_neumaticos_pkey ON public.eventos_neumaticos USING btree (id)
  ```
- **idx_eventos_neumatico**
  ```sql
  CREATE INDEX idx_eventos_neumatico ON public.eventos_neumaticos USING btree (neumatico_id)
  ```
- **idx_eventos_neumatico_fecha**
  ```sql
  CREATE INDEX idx_eventos_neumatico_fecha ON public.eventos_neumaticos USING btree (neumatico_id, timestamp_evento DESC)
  ```
- **idx_eventos_neumatico_tipo_fecha**
  ```sql
  CREATE INDEX idx_eventos_neumatico_tipo_fecha ON public.eventos_neumaticos USING btree (neumatico_id, tipo_evento, timestamp_evento DESC)
  ```
- **idx_eventos_neumaticos_tipo_ruta_id**
  ```sql
  CREATE INDEX idx_eventos_neumaticos_tipo_ruta_id ON public.eventos_neumaticos USING btree (tipo_ruta_id)
  ```
- **idx_eventos_timestamp**
  ```sql
  CREATE INDEX idx_eventos_timestamp ON public.eventos_neumaticos USING btree (timestamp_evento DESC)
  ```
- **idx_eventos_tipo**
  ```sql
  CREATE INDEX idx_eventos_tipo ON public.eventos_neumaticos USING btree (tipo_evento)
  ```
- **idx_eventos_usuario**
  ```sql
  CREATE INDEX idx_eventos_usuario ON public.eventos_neumaticos USING btree (usuario_id)
  ```

---

### fabricantes_neumatico

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | uuid | No | public.gen_random_uuid() |  |
| nombre | character varying(100) | No |  |  |
| codigo_abreviado | character varying(10) | Sí |  |  |
| pais_origen | character varying(50) | Sí |  |  |
| sitio_web | character varying(255) | Sí |  |  |
| activo | boolean | No | true |  |
| creado_en | timestamp without time zone | No | now() |  |
| creado_por | uuid | Sí |  |  |
| actualizado_en | timestamp without time zone | Sí |  |  |
| actualizado_por | uuid | Sí |  |  |

#### Restricciones

- **2200_19618_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19618_2_not_null** (CHECK) - Condición: nombre IS NOT NULL
- **2200_19618_6_not_null** (CHECK) - Condición: activo IS NOT NULL
- **2200_19618_7_not_null** (CHECK) - Condición: creado_en IS NOT NULL
- **fabricantes_neumatico_nombre_length** (CHECK) - Referencia: fabricantes_neumatico.nombre - Condición: (length((nombre)::text) >= 2)
- **fabricantes_neumatico_actualizado_por_fkey** (FOREIGN KEY) - Columna: actualizado_por - Referencia: usuarios.id
- **fabricantes_neumatico_creado_por_fkey** (FOREIGN KEY) - Columna: creado_por - Referencia: usuarios.id
- **fabricantes_neumatico_pkey** (PRIMARY KEY) - Columna: id - Referencia: fabricantes_neumatico.id
- **fabricantes_neumatico_codigo_abreviado_key** (UNIQUE) - Columna: codigo_abreviado - Referencia: fabricantes_neumatico.codigo_abreviado

#### Índices

- **fabricantes_neumatico_codigo_abreviado_key**
  ```sql
  CREATE UNIQUE INDEX fabricantes_neumatico_codigo_abreviado_key ON public.fabricantes_neumatico USING btree (codigo_abreviado)
  ```
- **fabricantes_neumatico_pkey**
  ```sql
  CREATE UNIQUE INDEX fabricantes_neumatico_pkey ON public.fabricantes_neumatico USING btree (id)
  ```
- **idx_fabricantes_nombre_unique**
  ```sql
  CREATE UNIQUE INDEX idx_fabricantes_nombre_unique ON public.fabricantes_neumatico USING btree (f_immutable_lower_unaccent((nombre)::text)) WHERE (activo = true)
  ```

---

### garantias_neumaticos

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | uuid | No | gen_random_uuid() |  |
| neumatico_id | uuid | No |  |  |
| proveedor_id | uuid | Sí |  |  |
| tipo_garantia | character varying(50) | No |  |  |
| fecha_inicio | date | No |  |  |
| fecha_fin | date | Sí |  |  |
| kilometraje_cubierto | integer(32) | Sí |  |  |
| meses_cobertura | integer(32) | Sí |  |  |
| condiciones_url | text | Sí |  |  |
| creado_en | timestamp with time zone | No | now() |  |
| actualizado_en | timestamp with time zone | Sí |  |  |
| creado_por | uuid | Sí |  |  |
| actualizado_por | uuid | Sí |  |  |

#### Restricciones

- **2200_19625_10_not_null** (CHECK) - Condición: creado_en IS NOT NULL
- **2200_19625_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19625_2_not_null** (CHECK) - Condición: neumatico_id IS NOT NULL
- **2200_19625_4_not_null** (CHECK) - Condición: tipo_garantia IS NOT NULL
- **2200_19625_5_not_null** (CHECK) - Condición: fecha_inicio IS NOT NULL
- **chk_fechas_garantia** (CHECK) - Referencia: garantias_neumaticos.fecha_fin - Condición: ((fecha_fin IS NULL) OR (fecha_fin >= fecha_inicio))
- **chk_fechas_garantia** (CHECK) - Referencia: garantias_neumaticos.fecha_inicio - Condición: ((fecha_fin IS NULL) OR (fecha_fin >= fecha_inicio))
- **chk_tipo_garantia** (CHECK) - Referencia: garantias_neumaticos.tipo_garantia - Condición: ((tipo_garantia)::text = ANY (ARRAY[('KILOMETRAJE'::character varying)::text, ('TIEMPO'::character varying)::text, ('AMBOS'::character varying)::text]))
- **garantias_neumaticos_actualizado_por_fkey** (FOREIGN KEY) - Columna: actualizado_por - Referencia: usuarios.id
- **garantias_neumaticos_creado_por_fkey** (FOREIGN KEY) - Columna: creado_por - Referencia: usuarios.id
- **garantias_neumaticos_neumatico_id_fkey** (FOREIGN KEY) - Columna: neumatico_id - Referencia: neumaticos.id
- **garantias_neumaticos_proveedor_id_fkey** (FOREIGN KEY) - Columna: proveedor_id - Referencia: proveedores.id
- **garantias_neumaticos_pkey** (PRIMARY KEY) - Columna: id - Referencia: garantias_neumaticos.id

#### Índices

- **garantias_neumaticos_pkey**
  ```sql
  CREATE UNIQUE INDEX garantias_neumaticos_pkey ON public.garantias_neumaticos USING btree (id)
  ```
- **idx_garantias_neumatico_id**
  ```sql
  CREATE INDEX idx_garantias_neumatico_id ON public.garantias_neumaticos USING btree (neumatico_id)
  ```
- **idx_garantias_vencimiento**
  ```sql
  CREATE INDEX idx_garantias_vencimiento ON public.garantias_neumaticos USING btree (fecha_fin) WHERE (fecha_fin IS NOT NULL)
  ```

---

### historial_estados_neumaticos

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | uuid | No | gen_random_uuid() |  |
| neumatico_id | uuid | No |  |  |
| estado_anterior | character varying(50) | Sí |  |  |
| estado_nuevo | character varying(50) | No |  |  |
| fecha_cambio | timestamp with time zone | No | now() |  |
| usuario_id | uuid | Sí |  |  |
| comentario | text | Sí |  |  |
| metadata | jsonb | Sí |  |  |

#### Restricciones

- **2200_19634_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19634_2_not_null** (CHECK) - Condición: neumatico_id IS NOT NULL
- **2200_19634_4_not_null** (CHECK) - Condición: estado_nuevo IS NOT NULL
- **2200_19634_5_not_null** (CHECK) - Condición: fecha_cambio IS NOT NULL
- **historial_estados_neumaticos_neumatico_id_fkey** (FOREIGN KEY) - Columna: neumatico_id - Referencia: neumaticos.id
- **historial_estados_neumaticos_usuario_id_fkey** (FOREIGN KEY) - Columna: usuario_id - Referencia: usuarios.id
- **historial_estados_neumaticos_pkey** (PRIMARY KEY) - Columna: id - Referencia: historial_estados_neumaticos.id

#### Índices

- **historial_estados_neumaticos_pkey**
  ```sql
  CREATE UNIQUE INDEX historial_estados_neumaticos_pkey ON public.historial_estados_neumaticos USING btree (id)
  ```
- **idx_hist_estados_estado_nuevo**
  ```sql
  CREATE INDEX idx_hist_estados_estado_nuevo ON public.historial_estados_neumaticos USING btree (estado_nuevo)
  ```
- **idx_hist_estados_fecha**
  ```sql
  CREATE INDEX idx_hist_estados_fecha ON public.historial_estados_neumaticos USING btree (fecha_cambio)
  ```
- **idx_hist_estados_neumatico_id**
  ```sql
  CREATE INDEX idx_hist_estados_neumatico_id ON public.historial_estados_neumaticos USING btree (neumatico_id)
  ```

---

### mediciones_profundidad

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | uuid | No | gen_random_uuid() |  |
| neumatico_id | uuid | No |  |  |
| fecha_medicion | timestamp with time zone | No | now() |  |
| profundidad_mm | numeric(5,2) | No |  |  |
| ubicacion_medicion | text | No |  |  |
| metodo_medicion | text | Sí |  |  |
| usuario_id | uuid | Sí |  |  |
| observaciones | text | Sí |  |  |
| creado_en | timestamp with time zone | No | now() |  |
| actualizado_en | timestamp with time zone | No | now() |  |
| creado_por | uuid | Sí |  |  |
| actualizado_por | uuid | Sí |  |  |

#### Restricciones

- **2200_19641_10_not_null** (CHECK) - Condición: actualizado_en IS NOT NULL
- **2200_19641_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19641_2_not_null** (CHECK) - Condición: neumatico_id IS NOT NULL
- **2200_19641_3_not_null** (CHECK) - Condición: fecha_medicion IS NOT NULL
- **2200_19641_4_not_null** (CHECK) - Condición: profundidad_mm IS NOT NULL
- **2200_19641_5_not_null** (CHECK) - Condición: ubicacion_medicion IS NOT NULL
- **2200_19641_9_not_null** (CHECK) - Condición: creado_en IS NOT NULL
- **mediciones_profundidad_profundidad_mm_check** (CHECK) - Referencia: mediciones_profundidad.profundidad_mm - Condición: ((profundidad_mm >= (0)::numeric) AND (profundidad_mm <= (100)::numeric))
- **mediciones_profundidad_actualizado_por_fkey** (FOREIGN KEY) - Columna: actualizado_por - Referencia: usuarios.id
- **mediciones_profundidad_creado_por_fkey** (FOREIGN KEY) - Columna: creado_por - Referencia: usuarios.id
- **mediciones_profundidad_neumatico_id_fkey** (FOREIGN KEY) - Columna: neumatico_id - Referencia: neumaticos.id
- **mediciones_profundidad_usuario_id_fkey** (FOREIGN KEY) - Columna: usuario_id - Referencia: usuarios.id
- **mediciones_profundidad_pkey** (PRIMARY KEY) - Columna: id - Referencia: mediciones_profundidad.id

#### Índices

- **idx_mediciones_profundidad_fecha**
  ```sql
  CREATE INDEX idx_mediciones_profundidad_fecha ON public.mediciones_profundidad USING btree (fecha_medicion)
  ```
- **idx_mediciones_profundidad_neumatico_id**
  ```sql
  CREATE INDEX idx_mediciones_profundidad_neumatico_id ON public.mediciones_profundidad USING btree (neumatico_id)
  ```
- **mediciones_profundidad_pkey**
  ```sql
  CREATE UNIQUE INDEX mediciones_profundidad_pkey ON public.mediciones_profundidad USING btree (id)
  ```

---

### modelos_neumatico

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | uuid | No | public.gen_random_uuid() |  |
| fabricante_id | uuid | No |  |  |
| nombre_modelo | character varying(100) | No |  |  |
| medida | character varying(20) | No |  |  |
| indice_carga | character varying(5) | Sí |  |  |
| indice_velocidad | character varying(2) | Sí |  |  |
| profundidad_original_mm | numeric(5,2) | No |  |  |
| presion_recomendada_psi | numeric(5,2) | Sí |  |  |
| permite_reencauche | boolean | No | false |  |
| reencauches_maximos | smallint(16) | Sí | 0 |  |
| patron_dibujo | character varying(50) | Sí |  |  |
| tipo_servicio | character varying(50) | Sí |  |  |
| creado_en | timestamp with time zone | No | now() |  |
| creado_por | uuid | Sí |  |  |
| actualizado_en | timestamp with time zone | Sí |  |  |
| actualizado_por | uuid | Sí |  |  |
| posicion_uso_recomendada | USER-DEFINED | Sí |  |  |
| diseno_predominante_para_eje | USER-DEFINED | Sí |  |  |
| vida_util_teorica_km | integer(32) | Sí |  |  |
| profundidad_minima_retiro_mm | numeric(5,2) | No | 1.6 |  |
| tasa_desgaste_esperada_mm_km | numeric(10,8) | No |  |  |
| activo | boolean | Sí | true |  |
| frecuencia_inspeccion_km | integer(32) | Sí | 5000 |  |
| max_vidas_utiles | integer(32) | Sí | 5 |  |
| porcentaje_desgaste_por_vida | numeric(5,2) | Sí | 10.0 |  |

#### Restricciones

- **2200_19651_13_not_null** (CHECK) - Condición: creado_en IS NOT NULL
- **2200_19651_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19651_20_not_null** (CHECK) - Condición: profundidad_minima_retiro_mm IS NOT NULL
- **2200_19651_21_not_null** (CHECK) - Condición: tasa_desgaste_esperada_mm_km IS NOT NULL
- **2200_19651_2_not_null** (CHECK) - Condición: fabricante_id IS NOT NULL
- **2200_19651_3_not_null** (CHECK) - Condición: nombre_modelo IS NOT NULL
- **2200_19651_4_not_null** (CHECK) - Condición: medida IS NOT NULL
- **2200_19651_7_not_null** (CHECK) - Condición: profundidad_original_mm IS NOT NULL
- **2200_19651_9_not_null** (CHECK) - Condición: permite_reencauche IS NOT NULL
- **chk_max_vidas_utiles_positivo** (CHECK) - Referencia: modelos_neumatico.max_vidas_utiles - Condición: (max_vidas_utiles > 0)
- **chk_porcentaje_desgaste_positivo** (CHECK) - Referencia: modelos_neumatico.porcentaje_desgaste_por_vida - Condición: (porcentaje_desgaste_por_vida >= (0)::numeric)
- **chk_profundidad_minima_positiva** (CHECK) - Referencia: modelos_neumatico.profundidad_minima_retiro_mm - Condición: (profundidad_minima_retiro_mm > (0)::numeric)
- **chk_tasa_desgaste_positiva** (CHECK) - Referencia: modelos_neumatico.tasa_desgaste_esperada_mm_km - Condición: (tasa_desgaste_esperada_mm_km > (0)::numeric)
- **chk_tasa_desgaste_positiva** (CHECK) - Referencia: neumaticos.tasa_desgaste_actual_mm_km - Condición: ((tasa_desgaste_actual_mm_km IS NULL) OR (tasa_desgaste_actual_mm_km > (0)::numeric))
- **chk_tasa_desgaste_positiva** (CHECK) - Referencia: modelos_neumatico.tasa_desgaste_esperada_mm_km - Condición: ((tasa_desgaste_actual_mm_km IS NULL) OR (tasa_desgaste_actual_mm_km > (0)::numeric))
- **chk_tasa_desgaste_positiva** (CHECK) - Referencia: neumaticos.tasa_desgaste_actual_mm_km - Condición: (tasa_desgaste_esperada_mm_km > (0)::numeric)
- **modelos_neumatico_presion_recomendada_psi_check** (CHECK) - Referencia: modelos_neumatico.presion_recomendada_psi - Condición: ((presion_recomendada_psi IS NULL) OR (presion_recomendada_psi > (0)::numeric))
- **modelos_neumatico_profundidad_minima_retiro_mm_check** (CHECK) - Referencia: modelos_neumatico.profundidad_original_mm - Condición: ((profundidad_minima_retiro_mm > (0)::numeric) AND (profundidad_minima_retiro_mm <= profundidad_original_mm))
- **modelos_neumatico_profundidad_minima_retiro_mm_check** (CHECK) - Referencia: modelos_neumatico.profundidad_minima_retiro_mm - Condición: ((profundidad_minima_retiro_mm > (0)::numeric) AND (profundidad_minima_retiro_mm <= profundidad_original_mm))
- **modelos_neumatico_profundidad_original_mm_check** (CHECK) - Referencia: modelos_neumatico.profundidad_original_mm - Condición: (profundidad_original_mm > (0)::numeric)
- **modelos_neumatico_reencauches_maximos_check** (CHECK) - Referencia: modelos_neumatico.reencauches_maximos - Condición: ((reencauches_maximos >= 0) AND (reencauches_maximos <= 10))
- **modelos_neumatico_tasa_desgaste_esperada_check** (CHECK) - Referencia: modelos_neumatico.tasa_desgaste_esperada_mm_km - Condición: ((tasa_desgaste_esperada_mm_km IS NULL) OR (tasa_desgaste_esperada_mm_km > (0)::numeric))
- **modelos_neumatico_vida_util_teorica_km_check** (CHECK) - Referencia: modelos_neumatico.vida_util_teorica_km - Condición: ((vida_util_teorica_km IS NULL) OR (vida_util_teorica_km > 0))
- **modelos_neumatico_actualizado_por_fkey** (FOREIGN KEY) - Columna: actualizado_por - Referencia: usuarios.id
- **modelos_neumatico_creado_por_fkey** (FOREIGN KEY) - Columna: creado_por - Referencia: usuarios.id
- **modelos_neumatico_fabricante_id_fkey** (FOREIGN KEY) - Columna: fabricante_id - Referencia: fabricantes_neumatico.id
- **modelos_neumatico_pkey** (PRIMARY KEY) - Columna: id - Referencia: modelos_neumatico.id

#### Índices

- **idx_modelos_fabricante**
  ```sql
  CREATE INDEX idx_modelos_fabricante ON public.modelos_neumatico USING btree (fabricante_id)
  ```
- **idx_modelos_unique**
  ```sql
  CREATE UNIQUE INDEX idx_modelos_unique ON public.modelos_neumatico USING btree (fabricante_id, f_immutable_lower_unaccent((nombre_modelo)::text), medida) WHERE (fabricante_id IS NOT NULL)
  ```
- **modelos_neumatico_pkey**
  ```sql
  CREATE UNIQUE INDEX modelos_neumatico_pkey ON public.modelos_neumatico USING btree (id)
  ```

---

### modelos_posiciones_permitidas

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| modelo_neumatico_id | uuid | No |  |  |
| posicion_neumatico_id | uuid | No |  |  |
| es_recomendado | boolean | No | false |  |
| creado_en | timestamp with time zone | No | now() |  |
| creado_por | uuid | Sí |  |  |

#### Restricciones

- **2200_19673_1_not_null** (CHECK) - Condición: modelo_neumatico_id IS NOT NULL
- **2200_19673_2_not_null** (CHECK) - Condición: posicion_neumatico_id IS NOT NULL
- **2200_19673_3_not_null** (CHECK) - Condición: es_recomendado IS NOT NULL
- **2200_19673_4_not_null** (CHECK) - Condición: creado_en IS NOT NULL
- **modelos_posiciones_permitidas_creado_por_fkey** (FOREIGN KEY) - Columna: creado_por - Referencia: usuarios.id
- **modelos_posiciones_permitidas_modelo_neumatico_id_fkey** (FOREIGN KEY) - Columna: modelo_neumatico_id - Referencia: modelos_neumatico.id
- **modelos_posiciones_permitidas_posicion_neumatico_id_fkey** (FOREIGN KEY) - Columna: posicion_neumatico_id - Referencia: posiciones_neumatico.id
- **modelos_posiciones_permitidas_pkey** (PRIMARY KEY) - Columna: modelo_neumatico_id - Referencia: modelos_posiciones_permitidas.modelo_neumatico_id
- **modelos_posiciones_permitidas_pkey** (PRIMARY KEY) - Columna: posicion_neumatico_id - Referencia: modelos_posiciones_permitidas.posicion_neumatico_id
- **modelos_posiciones_permitidas_pkey** (PRIMARY KEY) - Columna: posicion_neumatico_id - Referencia: modelos_posiciones_permitidas.modelo_neumatico_id
- **modelos_posiciones_permitidas_pkey** (PRIMARY KEY) - Columna: modelo_neumatico_id - Referencia: modelos_posiciones_permitidas.posicion_neumatico_id

#### Índices

- **modelos_posiciones_permitidas_pkey**
  ```sql
  CREATE UNIQUE INDEX modelos_posiciones_permitidas_pkey ON public.modelos_posiciones_permitidas USING btree (modelo_neumatico_id, posicion_neumatico_id)
  ```

---

### motivos_desecho

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | uuid | No | public.gen_random_uuid() |  |
| codigo | character varying(20) | No |  |  |
| descripcion | text | No |  |  |
| requiere_evidencia | boolean | No | false |  |
| activo | boolean | No | true |  |
| creado_en | timestamp with time zone | No | now() |  |
| creado_por | uuid | Sí |  |  |
| actualizado_en | timestamp with time zone | Sí |  |  |
| actualizado_por | uuid | Sí |  |  |

#### Restricciones

- **2200_19678_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19678_2_not_null** (CHECK) - Condición: codigo IS NOT NULL
- **2200_19678_3_not_null** (CHECK) - Condición: descripcion IS NOT NULL
- **2200_19678_4_not_null** (CHECK) - Condición: requiere_evidencia IS NOT NULL
- **2200_19678_5_not_null** (CHECK) - Condición: activo IS NOT NULL
- **2200_19678_6_not_null** (CHECK) - Condición: creado_en IS NOT NULL
- **motivos_desecho_actualizado_por_fkey** (FOREIGN KEY) - Columna: actualizado_por - Referencia: usuarios.id
- **motivos_desecho_creado_por_fkey** (FOREIGN KEY) - Columna: creado_por - Referencia: usuarios.id
- **motivos_desecho_pkey** (PRIMARY KEY) - Columna: id - Referencia: motivos_desecho.id
- **motivos_desecho_codigo_key** (UNIQUE) - Columna: codigo - Referencia: motivos_desecho.codigo

#### Índices

- **motivos_desecho_codigo_key**
  ```sql
  CREATE UNIQUE INDEX motivos_desecho_codigo_key ON public.motivos_desecho USING btree (codigo)
  ```
- **motivos_desecho_pkey**
  ```sql
  CREATE UNIQUE INDEX motivos_desecho_pkey ON public.motivos_desecho USING btree (id)
  ```

---

### neumaticos

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | uuid | No | public.gen_random_uuid() |  |
| numero_serie | character varying(100) | Sí |  |  |
| dot | text | Sí |  |  |
| modelo_id | uuid | No |  |  |
| fecha_compra | date | No |  |  |
| fecha_fabricacion | date | Sí |  |  |
| costo_compra | numeric(10,2) | Sí |  |  |
| moneda_compra | character varying(3) | Sí | 'PEN'::character varying |  |
| proveedor_compra_id | uuid | Sí |  |  |
| es_reencauchado | boolean | No | false |  |
| vida_actual | smallint(16) | No | 1 |  |
| estado_actual | USER-DEFINED | No | 'EN_STOCK'::estado_neumatico_enum |  |
| ubicacion_actual_vehiculo_id | uuid | Sí |  |  |
| ubicacion_actual_posicion_id | uuid | Sí |  |  |
| fecha_ultimo_evento | timestamp with time zone | Sí |  |  |
| profundidad_inicial_mm | numeric(5,2) | Sí |  |  |
| kilometraje_acumulado | integer(32) | No | 0 |  |
| reencauches_realizados | smallint(16) | No | 0 |  |
| fecha_desecho | date | Sí |  |  |
| motivo_desecho_id | uuid | Sí |  |  |
| creado_en | timestamp with time zone | No | now() |  |
| creado_por | uuid | Sí |  |  |
| actualizado_en | timestamp with time zone | Sí |  |  |
| actualizado_por | uuid | Sí |  |  |
| ubicacion_almacen_id | uuid | Sí |  |  |
| sensor_id | character varying(100) | Sí |  |  |
| profundidad_remanente_actual_mm | numeric(5,2) | No |  |  |
| fecha_ultima_medicion_profundidad | timestamp with time zone | Sí |  |  |
| kilometraje_vida_actual | integer(32) | Sí | 0 |  |
| fecha_inicio_vida_actual | date | Sí |  |  |
| odometro_instalacion_vida_actual | integer(32) | Sí |  |  |
| tasa_desgaste_actual_mm_km | numeric(10,8) | Sí |  |  |
| vida_util_restante_km | integer(32) | Sí |  |  |
| fecha_ultimo_reencauche | date | Sí |  |  |
| activo | boolean | Sí | true |  |
| proxima_inspeccion_fecha | date | Sí |  |  |
| proxima_inspeccion_km | integer(32) | Sí |  |  |
| profundidad_inicio_vida_actual_mm | numeric(5,2) | Sí |  |  |

#### Restricciones

- **2200_19687_10_not_null** (CHECK) - Condición: es_reencauchado IS NOT NULL
- **2200_19687_11_not_null** (CHECK) - Condición: vida_actual IS NOT NULL
- **2200_19687_12_not_null** (CHECK) - Condición: estado_actual IS NOT NULL
- **2200_19687_17_not_null** (CHECK) - Condición: kilometraje_acumulado IS NOT NULL
- **2200_19687_18_not_null** (CHECK) - Condición: reencauches_realizados IS NOT NULL
- **2200_19687_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19687_21_not_null** (CHECK) - Condición: creado_en IS NOT NULL
- **2200_19687_27_not_null** (CHECK) - Condición: profundidad_remanente_actual_mm IS NOT NULL
- **2200_19687_4_not_null** (CHECK) - Condición: modelo_id IS NOT NULL
- **2200_19687_5_not_null** (CHECK) - Condición: fecha_compra IS NOT NULL
- **chk_tasa_desgaste_positiva** (CHECK) - Referencia: modelos_neumatico.tasa_desgaste_esperada_mm_km - Condición: (tasa_desgaste_esperada_mm_km > (0)::numeric)
- **chk_tasa_desgaste_positiva** (CHECK) - Referencia: modelos_neumatico.tasa_desgaste_esperada_mm_km - Condición: ((tasa_desgaste_actual_mm_km IS NULL) OR (tasa_desgaste_actual_mm_km > (0)::numeric))
- **chk_tasa_desgaste_positiva** (CHECK) - Referencia: neumaticos.tasa_desgaste_actual_mm_km - Condición: (tasa_desgaste_esperada_mm_km > (0)::numeric)
- **chk_tasa_desgaste_positiva** (CHECK) - Referencia: neumaticos.tasa_desgaste_actual_mm_km - Condición: ((tasa_desgaste_actual_mm_km IS NULL) OR (tasa_desgaste_actual_mm_km > (0)::numeric))
- **chk_ubicacion_mutuamente_exclusiva** (CHECK) - Referencia: neumaticos.estado_actual - Condición: (((ubicacion_almacen_id IS NOT NULL) AND (ubicacion_actual_vehiculo_id IS NULL) AND (ubicacion_actual_posicion_id IS NULL) AND (estado_actual <> 'INSTALADO'::estado_neumatico_enum)) OR ((ubicacion_almacen_id IS NULL) AND (ubicacion_actual_vehiculo_id IS NOT NULL) AND (ubicacion_actual_posicion_id IS NOT NULL) AND (estado_actual = 'INSTALADO'::estado_neumatico_enum)) OR ((ubicacion_almacen_id IS NULL) AND (ubicacion_actual_vehiculo_id IS NULL) AND (ubicacion_actual_posicion_id IS NULL) AND (estado_actual <> 'INSTALADO'::estado_neumatico_enum)))
- **chk_ubicacion_mutuamente_exclusiva** (CHECK) - Referencia: neumaticos.ubicacion_actual_posicion_id - Condición: (((ubicacion_almacen_id IS NOT NULL) AND (ubicacion_actual_vehiculo_id IS NULL) AND (ubicacion_actual_posicion_id IS NULL) AND (estado_actual <> 'INSTALADO'::estado_neumatico_enum)) OR ((ubicacion_almacen_id IS NULL) AND (ubicacion_actual_vehiculo_id IS NOT NULL) AND (ubicacion_actual_posicion_id IS NOT NULL) AND (estado_actual = 'INSTALADO'::estado_neumatico_enum)) OR ((ubicacion_almacen_id IS NULL) AND (ubicacion_actual_vehiculo_id IS NULL) AND (ubicacion_actual_posicion_id IS NULL) AND (estado_actual <> 'INSTALADO'::estado_neumatico_enum)))
- **chk_ubicacion_mutuamente_exclusiva** (CHECK) - Referencia: neumaticos.ubicacion_actual_vehiculo_id - Condición: (((ubicacion_almacen_id IS NOT NULL) AND (ubicacion_actual_vehiculo_id IS NULL) AND (ubicacion_actual_posicion_id IS NULL) AND (estado_actual <> 'INSTALADO'::estado_neumatico_enum)) OR ((ubicacion_almacen_id IS NULL) AND (ubicacion_actual_vehiculo_id IS NOT NULL) AND (ubicacion_actual_posicion_id IS NOT NULL) AND (estado_actual = 'INSTALADO'::estado_neumatico_enum)) OR ((ubicacion_almacen_id IS NULL) AND (ubicacion_actual_vehiculo_id IS NULL) AND (ubicacion_actual_posicion_id IS NULL) AND (estado_actual <> 'INSTALADO'::estado_neumatico_enum)))
- **chk_ubicacion_mutuamente_exclusiva** (CHECK) - Referencia: neumaticos.ubicacion_almacen_id - Condición: (((ubicacion_almacen_id IS NOT NULL) AND (ubicacion_actual_vehiculo_id IS NULL) AND (ubicacion_actual_posicion_id IS NULL) AND (estado_actual <> 'INSTALADO'::estado_neumatico_enum)) OR ((ubicacion_almacen_id IS NULL) AND (ubicacion_actual_vehiculo_id IS NOT NULL) AND (ubicacion_actual_posicion_id IS NOT NULL) AND (estado_actual = 'INSTALADO'::estado_neumatico_enum)) OR ((ubicacion_almacen_id IS NULL) AND (ubicacion_actual_vehiculo_id IS NULL) AND (ubicacion_actual_posicion_id IS NULL) AND (estado_actual <> 'INSTALADO'::estado_neumatico_enum)))
- **chk_vida_util_restante_no_negativa** (CHECK) - Referencia: neumaticos.vida_util_restante_km - Condición: ((vida_util_restante_km IS NULL) OR (vida_util_restante_km >= 0))
- **neumaticos_costo_compra_check** (CHECK) - Referencia: neumaticos.costo_compra - Condición: ((costo_compra IS NULL) OR (costo_compra >= (0)::numeric))
- **neumaticos_fechas_check** (CHECK) - Referencia: neumaticos.fecha_compra - Condición: ((fecha_fabricacion IS NULL) OR (fecha_fabricacion <= fecha_compra))
- **neumaticos_fechas_check** (CHECK) - Referencia: neumaticos.fecha_fabricacion - Condición: ((fecha_fabricacion IS NULL) OR (fecha_fabricacion <= fecha_compra))
- **neumaticos_kilometraje_acumulado_check** (CHECK) - Referencia: neumaticos.kilometraje_acumulado - Condición: (kilometraje_acumulado >= 0)
- **neumaticos_kilometraje_vida_actual_check** (CHECK) - Referencia: neumaticos.kilometraje_vida_actual - Condición: (kilometraje_vida_actual >= 0)
- **neumaticos_profundidad_inicial_mm_check** (CHECK) - Referencia: neumaticos.profundidad_inicial_mm - Condición: ((profundidad_inicial_mm IS NULL) OR (profundidad_inicial_mm > (0)::numeric))
- **neumaticos_profundidad_remanente_check** (CHECK) - Referencia: neumaticos.profundidad_remanente_actual_mm - Condición: ((profundidad_remanente_actual_mm IS NULL) OR ((profundidad_remanente_actual_mm >= (0)::numeric) AND (profundidad_remanente_actual_mm <= (50)::numeric)))
- **neumaticos_reencauches_realizados_check** (CHECK) - Referencia: neumaticos.reencauches_realizados - Condición: (reencauches_realizados >= 0)
- **neumaticos_tasa_desgaste_actual_check** (CHECK) - Referencia: neumaticos.tasa_desgaste_actual_mm_km - Condición: ((tasa_desgaste_actual_mm_km IS NULL) OR (tasa_desgaste_actual_mm_km > (0)::numeric))
- **neumaticos_vida_actual_check** (CHECK) - Referencia: neumaticos.vida_actual - Condición: ((vida_actual >= 1) AND (vida_actual <= 11))
- **neumaticos_vida_util_restante_check** (CHECK) - Referencia: neumaticos.vida_util_restante_km - Condición: ((vida_util_restante_km IS NULL) OR (vida_util_restante_km >= 0))
- **neumaticos_actualizado_por_fkey** (FOREIGN KEY) - Columna: actualizado_por - Referencia: usuarios.id
- **neumaticos_creado_por_fkey** (FOREIGN KEY) - Columna: creado_por - Referencia: usuarios.id
- **neumaticos_modelo_id_fkey** (FOREIGN KEY) - Columna: modelo_id - Referencia: modelos_neumatico.id
- **neumaticos_motivo_desecho_id_fkey** (FOREIGN KEY) - Columna: motivo_desecho_id - Referencia: motivos_desecho.id
- **neumaticos_proveedor_compra_id_fkey** (FOREIGN KEY) - Columna: proveedor_compra_id - Referencia: proveedores.id
- **neumaticos_ubicacion_actual_vehiculo_id_fkey** (FOREIGN KEY) - Columna: ubicacion_actual_vehiculo_id - Referencia: vehiculos.id
- **neumaticos_ubicacion_almacen_id_fkey** (FOREIGN KEY) - Columna: ubicacion_almacen_id - Referencia: almacenes.id
- **neumaticos_pkey** (PRIMARY KEY) - Columna: id - Referencia: neumaticos.id

#### Índices

- **idx_neumaticos_activos**
  ```sql
  CREATE INDEX idx_neumaticos_activos ON public.neumaticos USING btree (estado_actual) WHERE (estado_actual <> 'DESECHADO'::estado_neumatico_enum)
  ```
- **idx_neumaticos_activos_compuesto**
  ```sql
  CREATE INDEX idx_neumaticos_activos_compuesto ON public.neumaticos USING btree (estado_actual, modelo_id, vida_util_restante_km) WHERE (estado_actual <> 'DESECHADO'::estado_neumatico_enum)
  ```
- **idx_neumaticos_dot**
  ```sql
  CREATE INDEX idx_neumaticos_dot ON public.neumaticos USING btree (dot) WHERE (dot IS NOT NULL)
  ```
- **idx_neumaticos_estado**
  ```sql
  CREATE INDEX idx_neumaticos_estado ON public.neumaticos USING btree (estado_actual)
  ```
- **idx_neumaticos_estado_actual**
  ```sql
  CREATE INDEX idx_neumaticos_estado_actual ON public.neumaticos USING btree (estado_actual) WHERE (estado_actual <> 'DESECHADO'::estado_neumatico_enum)
  ```
- **idx_neumaticos_estado_ubicacion**
  ```sql
  CREATE INDEX idx_neumaticos_estado_ubicacion ON public.neumaticos USING btree (estado_actual, ubicacion_actual_vehiculo_id, ubicacion_actual_posicion_id) WHERE (estado_actual = 'INSTALADO'::estado_neumatico_enum)
  ```
- **idx_neumaticos_fechas_compra**
  ```sql
  CREATE INDEX idx_neumaticos_fechas_compra ON public.neumaticos USING btree (fecha_compra)
  ```
- **idx_neumaticos_modelo**
  ```sql
  CREATE INDEX idx_neumaticos_modelo ON public.neumaticos USING btree (modelo_id)
  ```
- **idx_neumaticos_modelo_id**
  ```sql
  CREATE INDEX idx_neumaticos_modelo_id ON public.neumaticos USING btree (modelo_id)
  ```
- **idx_neumaticos_prox_inspeccion**
  ```sql
  CREATE INDEX idx_neumaticos_prox_inspeccion ON public.neumaticos USING btree (proxima_inspeccion_fecha) WHERE (proxima_inspeccion_fecha IS NOT NULL)
  ```
- **idx_neumaticos_proximos_desecho**
  ```sql
  CREATE INDEX idx_neumaticos_proximos_desecho ON public.neumaticos USING btree (estado_actual, fecha_fabricacion) WHERE (estado_actual <> 'DESECHADO'::estado_neumatico_enum)
  ```
- **idx_neumaticos_sensor_id**
  ```sql
  CREATE INDEX idx_neumaticos_sensor_id ON public.neumaticos USING btree (sensor_id) WHERE (sensor_id IS NOT NULL)
  ```
- **idx_neumaticos_serie**
  ```sql
  CREATE INDEX idx_neumaticos_serie ON public.neumaticos USING btree (numero_serie) WHERE (numero_serie IS NOT NULL)
  ```
- **idx_neumaticos_tasa_desgaste**
  ```sql
  CREATE INDEX idx_neumaticos_tasa_desgaste ON public.neumaticos USING btree (tasa_desgaste_actual_mm_km) WHERE (tasa_desgaste_actual_mm_km IS NOT NULL)
  ```
- **idx_neumaticos_ubicacion**
  ```sql
  CREATE INDEX idx_neumaticos_ubicacion ON public.neumaticos USING btree (ubicacion_actual_vehiculo_id, ubicacion_actual_posicion_id) WHERE (ubicacion_actual_vehiculo_id IS NOT NULL)
  ```
- **idx_neumaticos_ubicacion_almacen**
  ```sql
  CREATE INDEX idx_neumaticos_ubicacion_almacen ON public.neumaticos USING btree (ubicacion_almacen_id) WHERE (ubicacion_almacen_id IS NOT NULL)
  ```
- **idx_neumaticos_vida_util_restante**
  ```sql
  CREATE INDEX idx_neumaticos_vida_util_restante ON public.neumaticos USING btree (vida_util_restante_km) WHERE (vida_util_restante_km IS NOT NULL)
  ```
- **neumaticos_pkey**
  ```sql
  CREATE UNIQUE INDEX neumaticos_pkey ON public.neumaticos USING btree (id)
  ```
- **uq_idx_neumatico_dot_vida**
  ```sql
  CREATE UNIQUE INDEX uq_idx_neumatico_dot_vida ON public.neumaticos USING btree (dot, vida_actual) WHERE (dot IS NOT NULL)
  ```

---

### parametros_inventario

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | uuid | No | public.gen_random_uuid() |  |
| parametro_tipo | USER-DEFINED | No |  |  |
| modelo_id | uuid | No |  |  |
| ubicacion_almacen_id | uuid | Sí |  |  |
| valor_numerico | numeric(10,2) | Sí |  |  |
| valor_texto | text | Sí |  |  |
| activo | boolean | No | true |  |
| notas | text | Sí |  |  |
| creado_en | timestamp with time zone | No | now() |  |
| creado_por | uuid | Sí |  |  |
| actualizado_en | timestamp with time zone | Sí |  |  |
| actualizado_por | uuid | Sí |  |  |

#### Restricciones

- **2200_19777_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19777_2_not_null** (CHECK) - Condición: parametro_tipo IS NOT NULL
- **2200_19777_3_not_null** (CHECK) - Condición: modelo_id IS NOT NULL
- **2200_19777_7_not_null** (CHECK) - Condición: activo IS NOT NULL
- **2200_19777_9_not_null** (CHECK) - Condición: creado_en IS NOT NULL
- **parametros_inventario_actualizado_por_fkey** (FOREIGN KEY) - Columna: actualizado_por - Referencia: usuarios.id
- **parametros_inventario_creado_por_fkey** (FOREIGN KEY) - Columna: creado_por - Referencia: usuarios.id
- **parametros_inventario_modelo_id_fkey** (FOREIGN KEY) - Columna: modelo_id - Referencia: modelos_neumatico.id
- **parametros_inventario_ubicacion_almacen_id_fkey** (FOREIGN KEY) - Columna: ubicacion_almacen_id - Referencia: almacenes.id
- **parametros_inventario_pkey** (PRIMARY KEY) - Columna: id - Referencia: parametros_inventario.id
- **uq_parametro_inventario** (UNIQUE) - Columna: modelo_id - Referencia: parametros_inventario.ubicacion_almacen_id
- **uq_parametro_inventario** (UNIQUE) - Columna: parametro_tipo - Referencia: parametros_inventario.modelo_id
- **uq_parametro_inventario** (UNIQUE) - Columna: parametro_tipo - Referencia: parametros_inventario.parametro_tipo
- **uq_parametro_inventario** (UNIQUE) - Columna: parametro_tipo - Referencia: parametros_inventario.ubicacion_almacen_id
- **uq_parametro_inventario** (UNIQUE) - Columna: modelo_id - Referencia: parametros_inventario.modelo_id
- **uq_parametro_inventario** (UNIQUE) - Columna: modelo_id - Referencia: parametros_inventario.parametro_tipo
- **uq_parametro_inventario** (UNIQUE) - Columna: ubicacion_almacen_id - Referencia: parametros_inventario.modelo_id
- **uq_parametro_inventario** (UNIQUE) - Columna: ubicacion_almacen_id - Referencia: parametros_inventario.parametro_tipo
- **uq_parametro_inventario** (UNIQUE) - Columna: ubicacion_almacen_id - Referencia: parametros_inventario.ubicacion_almacen_id
- **uq_parametro_inventario_gesneu** (UNIQUE) - Columna: parametro_tipo - Referencia: parametros_inventario.modelo_id
- **uq_parametro_inventario_gesneu** (UNIQUE) - Columna: ubicacion_almacen_id - Referencia: parametros_inventario.ubicacion_almacen_id
- **uq_parametro_inventario_gesneu** (UNIQUE) - Columna: ubicacion_almacen_id - Referencia: parametros_inventario.parametro_tipo
- **uq_parametro_inventario_gesneu** (UNIQUE) - Columna: ubicacion_almacen_id - Referencia: parametros_inventario.modelo_id
- **uq_parametro_inventario_gesneu** (UNIQUE) - Columna: modelo_id - Referencia: parametros_inventario.ubicacion_almacen_id
- **uq_parametro_inventario_gesneu** (UNIQUE) - Columna: modelo_id - Referencia: parametros_inventario.parametro_tipo
- **uq_parametro_inventario_gesneu** (UNIQUE) - Columna: modelo_id - Referencia: parametros_inventario.modelo_id
- **uq_parametro_inventario_gesneu** (UNIQUE) - Columna: parametro_tipo - Referencia: parametros_inventario.ubicacion_almacen_id
- **uq_parametro_inventario_gesneu** (UNIQUE) - Columna: parametro_tipo - Referencia: parametros_inventario.parametro_tipo

#### Índices

- **idx_param_inv_tipo_modelo_ubicacion**
  ```sql
  CREATE INDEX idx_param_inv_tipo_modelo_ubicacion ON public.parametros_inventario USING btree (parametro_tipo, modelo_id, ubicacion_almacen_id) WHERE (activo = true)
  ```
- **parametros_inventario_pkey**
  ```sql
  CREATE UNIQUE INDEX parametros_inventario_pkey ON public.parametros_inventario USING btree (id)
  ```
- **uq_parametro_inventario**
  ```sql
  CREATE UNIQUE INDEX uq_parametro_inventario ON public.parametros_inventario USING btree (parametro_tipo, modelo_id, ubicacion_almacen_id)
  ```
- **uq_parametro_inventario_gesneu**
  ```sql
  CREATE UNIQUE INDEX uq_parametro_inventario_gesneu ON public.parametros_inventario USING btree (parametro_tipo, modelo_id, ubicacion_almacen_id) NULLS NOT DISTINCT
  ```

---

### parametros_rendimiento_esperado_modelo

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | uuid | No | public.gen_random_uuid() |  |
| modelo_id | uuid | No |  |  |
| tipo_eje_aplicacion | USER-DEFINED | No |  |  |
| km_esperado_vida_original_min | integer(32) | Sí |  |  |
| km_esperado_vida_original_max | integer(32) | Sí |  |  |
| notas | text | Sí |  |  |
| creado_en | timestamp with time zone | No | now() |  |
| creado_por | uuid | Sí |  |  |
| actualizado_en | timestamp with time zone | Sí |  |  |
| actualizado_por | uuid | Sí |  |  |

#### Restricciones

- **2200_19785_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19785_2_not_null** (CHECK) - Condición: modelo_id IS NOT NULL
- **2200_19785_3_not_null** (CHECK) - Condición: tipo_eje_aplicacion IS NOT NULL
- **2200_19785_7_not_null** (CHECK) - Condición: creado_en IS NOT NULL
- **parametros_rendimiento_esper_km_esperado_vida_original_mi_check** (CHECK) - Referencia: parametros_rendimiento_esperado_modelo.km_esperado_vida_original_min - Condición: ((km_esperado_vida_original_min IS NULL) OR (km_esperado_vida_original_min >= 0))
- **parametros_rendimiento_esperado_modelo_check** (CHECK) - Referencia: parametros_rendimiento_esperado_modelo.km_esperado_vida_original_max - Condición: ((km_esperado_vida_original_max IS NULL) OR (km_esperado_vida_original_max >= COALESCE(km_esperado_vida_original_min, 0)))
- **parametros_rendimiento_esperado_modelo_check** (CHECK) - Referencia: parametros_rendimiento_esperado_modelo.km_esperado_vida_original_min - Condición: ((km_esperado_vida_original_max IS NULL) OR (km_esperado_vida_original_max >= COALESCE(km_esperado_vida_original_min, 0)))
- **parametros_rendimiento_esperado_modelo_actualizado_por_fkey** (FOREIGN KEY) - Columna: actualizado_por - Referencia: usuarios.id
- **parametros_rendimiento_esperado_modelo_creado_por_fkey** (FOREIGN KEY) - Columna: creado_por - Referencia: usuarios.id
- **parametros_rendimiento_esperado_modelo_modelo_id_fkey** (FOREIGN KEY) - Columna: modelo_id - Referencia: modelos_neumatico.id
- **parametros_rendimiento_esperado_modelo_pkey** (PRIMARY KEY) - Columna: id - Referencia: parametros_rendimiento_esperado_modelo.id
- **uq_rendimiento_modelo_eje_gesneu** (UNIQUE) - Columna: modelo_id - Referencia: parametros_rendimiento_esperado_modelo.tipo_eje_aplicacion
- **uq_rendimiento_modelo_eje_gesneu** (UNIQUE) - Columna: modelo_id - Referencia: parametros_rendimiento_esperado_modelo.modelo_id
- **uq_rendimiento_modelo_eje_gesneu** (UNIQUE) - Columna: tipo_eje_aplicacion - Referencia: parametros_rendimiento_esperado_modelo.tipo_eje_aplicacion
- **uq_rendimiento_modelo_eje_gesneu** (UNIQUE) - Columna: tipo_eje_aplicacion - Referencia: parametros_rendimiento_esperado_modelo.modelo_id

#### Índices

- **parametros_rendimiento_esperado_modelo_pkey**
  ```sql
  CREATE UNIQUE INDEX parametros_rendimiento_esperado_modelo_pkey ON public.parametros_rendimiento_esperado_modelo USING btree (id)
  ```
- **uq_rendimiento_modelo_eje_gesneu**
  ```sql
  CREATE UNIQUE INDEX uq_rendimiento_modelo_eje_gesneu ON public.parametros_rendimiento_esperado_modelo USING btree (modelo_id, tipo_eje_aplicacion)
  ```

---

### parametros_sistema

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | integer(32) | No | nextval('parametros_sistema_id_seq'::regclass) |  |
| clave | character varying(100) | No |  |  |
| valor | text | No |  |  |
| descripcion | text | Sí |  |  |
| creado_en | timestamp with time zone | Sí | now() |  |
| actualizado_en | timestamp with time zone | Sí | now() |  |
| creado_por | character varying(100) | Sí | 'SISTEMA'::character varying |  |
| actualizado_por | character varying(100) | Sí | 'SISTEMA'::character varying |  |

#### Restricciones

- **2200_19794_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19794_2_not_null** (CHECK) - Condición: clave IS NOT NULL
- **2200_19794_3_not_null** (CHECK) - Condición: valor IS NOT NULL
- **parametros_sistema_pkey** (PRIMARY KEY) - Columna: id - Referencia: parametros_sistema.id
- **parametros_sistema_clave_key** (UNIQUE) - Columna: clave - Referencia: parametros_sistema.clave

#### Índices

- **parametros_sistema_clave_key**
  ```sql
  CREATE UNIQUE INDEX parametros_sistema_clave_key ON public.parametros_sistema USING btree (clave)
  ```
- **parametros_sistema_pkey**
  ```sql
  CREATE UNIQUE INDEX parametros_sistema_pkey ON public.parametros_sistema USING btree (id)
  ```

---

### permisos

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | uuid | No | public.gen_random_uuid() |  |
| nombre_recurso | character varying(100) | No |  |  |
| accion | character varying(100) | No |  |  |
| descripcion | text | Sí |  |  |
| creado_en | timestamp with time zone | No | now() |  |

#### Restricciones

- **2200_19729_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19729_2_not_null** (CHECK) - Condición: nombre_recurso IS NOT NULL
- **2200_19729_3_not_null** (CHECK) - Condición: accion IS NOT NULL
- **2200_19729_5_not_null** (CHECK) - Condición: creado_en IS NOT NULL
- **permisos_pkey** (PRIMARY KEY) - Columna: id - Referencia: permisos.id
- **uq_permiso_recurso_accion** (UNIQUE) - Columna: nombre_recurso - Referencia: permisos.accion
- **uq_permiso_recurso_accion** (UNIQUE) - Columna: accion - Referencia: permisos.nombre_recurso
- **uq_permiso_recurso_accion** (UNIQUE) - Columna: accion - Referencia: permisos.accion
- **uq_permiso_recurso_accion** (UNIQUE) - Columna: nombre_recurso - Referencia: permisos.nombre_recurso

#### Índices

- **idx_permisos_recurso_accion**
  ```sql
  CREATE INDEX idx_permisos_recurso_accion ON public.permisos USING btree (nombre_recurso, accion)
  ```
- **permisos_pkey**
  ```sql
  CREATE UNIQUE INDEX permisos_pkey ON public.permisos USING btree (id)
  ```
- **uq_permiso_recurso_accion**
  ```sql
  CREATE UNIQUE INDEX uq_permiso_recurso_accion ON public.permisos USING btree (nombre_recurso, accion)
  ```

---

### posiciones_neumatico

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | uuid | No | public.gen_random_uuid() |  |
| configuracion_eje_id | uuid | No |  |  |
| codigo_posicion | character varying(10) | No |  |  |
| etiqueta_posicion | character varying(50) | Sí |  |  |
| lado | USER-DEFINED | No |  |  |
| posicion_relativa | smallint(16) | No |  |  |
| es_interna | boolean | No | false |  |
| es_direccion | boolean | No | false |  |
| es_traccion | boolean | No | false |  |
| requiere_neumatico_especifico | boolean | No | false |  |
| creado_en | timestamp with time zone | No | now() |  |
| creado_por | uuid | Sí |  |  |
| actualizado_en | timestamp with time zone | Sí |  |  |
| actualizado_por | uuid | Sí |  |  |

#### Restricciones

- **2200_19804_10_not_null** (CHECK) - Condición: requiere_neumatico_especifico IS NOT NULL
- **2200_19804_11_not_null** (CHECK) - Condición: creado_en IS NOT NULL
- **2200_19804_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19804_2_not_null** (CHECK) - Condición: configuracion_eje_id IS NOT NULL
- **2200_19804_3_not_null** (CHECK) - Condición: codigo_posicion IS NOT NULL
- **2200_19804_5_not_null** (CHECK) - Condición: lado IS NOT NULL
- **2200_19804_6_not_null** (CHECK) - Condición: posicion_relativa IS NOT NULL
- **2200_19804_7_not_null** (CHECK) - Condición: es_interna IS NOT NULL
- **2200_19804_8_not_null** (CHECK) - Condición: es_direccion IS NOT NULL
- **2200_19804_9_not_null** (CHECK) - Condición: es_traccion IS NOT NULL
- **posiciones_neumatico_posicion_relativa_check** (CHECK) - Referencia: posiciones_neumatico.posicion_relativa - Condición: (posicion_relativa > 0)
- **posiciones_neumatico_actualizado_por_fkey** (FOREIGN KEY) - Columna: actualizado_por - Referencia: usuarios.id
- **posiciones_neumatico_configuracion_eje_id_fkey** (FOREIGN KEY) - Columna: configuracion_eje_id - Referencia: configuraciones_eje.id
- **posiciones_neumatico_creado_por_fkey** (FOREIGN KEY) - Columna: creado_por - Referencia: usuarios.id
- **posiciones_neumatico_pkey** (PRIMARY KEY) - Columna: id - Referencia: posiciones_neumatico.id
- **uq_posicion_neumatico** (UNIQUE) - Columna: codigo_posicion - Referencia: posiciones_neumatico.configuracion_eje_id
- **uq_posicion_neumatico** (UNIQUE) - Columna: codigo_posicion - Referencia: posiciones_neumatico.codigo_posicion
- **uq_posicion_neumatico** (UNIQUE) - Columna: configuracion_eje_id - Referencia: posiciones_neumatico.codigo_posicion
- **uq_posicion_neumatico** (UNIQUE) - Columna: configuracion_eje_id - Referencia: posiciones_neumatico.configuracion_eje_id

#### Índices

- **posiciones_neumatico_pkey**
  ```sql
  CREATE UNIQUE INDEX posiciones_neumatico_pkey ON public.posiciones_neumatico USING btree (id)
  ```
- **uq_posicion_neumatico**
  ```sql
  CREATE UNIQUE INDEX uq_posicion_neumatico ON public.posiciones_neumatico USING btree (configuracion_eje_id, codigo_posicion)
  ```

---

### proveedores

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | uuid | No | public.gen_random_uuid() |  |
| nombre | character varying(150) | No |  |  |
| tipo | USER-DEFINED | Sí |  |  |
| ruc | character varying(11) | Sí |  |  |
| contacto_principal | text | Sí |  |  |
| telefono | character varying(50) | Sí |  |  |
| email | character varying(100) | Sí |  |  |
| direccion | text | Sí |  |  |
| activo | boolean | No | true |  |
| creado_en | timestamp with time zone | No | now() |  |
| creado_por | uuid | Sí |  |  |
| actualizado_en | timestamp with time zone | Sí |  |  |
| actualizado_por | uuid | Sí |  |  |

#### Restricciones

- **2200_19814_10_not_null** (CHECK) - Condición: creado_en IS NOT NULL
- **2200_19814_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19814_2_not_null** (CHECK) - Condición: nombre IS NOT NULL
- **2200_19814_9_not_null** (CHECK) - Condición: activo IS NOT NULL
- **proveedores_ruc_check** (CHECK) - Referencia: proveedores.ruc - Condición: ((ruc IS NULL) OR (((ruc)::text ~ '^10[0-9]{9}$'::text) OR ((ruc)::text ~ '^20[0-9]{9}$'::text) OR ((ruc)::text ~ '^1[5-9][0-9]{9}$'::text) OR ((ruc)::text ~ '^5[0-9][0-9]{9}$'::text) OR ((ruc)::text ~ '^(2[7-9]|[3-9][0-9])[0-9]{10}$'::text)))
- **proveedores_actualizado_por_fkey** (FOREIGN KEY) - Columna: actualizado_por - Referencia: usuarios.id
- **proveedores_creado_por_fkey** (FOREIGN KEY) - Columna: creado_por - Referencia: usuarios.id
- **proveedores_pkey** (PRIMARY KEY) - Columna: id - Referencia: proveedores.id
- **proveedores_ruc_key** (UNIQUE) - Columna: ruc - Referencia: proveedores.ruc

#### Índices

- **idx_proveedores_nombre_unique**
  ```sql
  CREATE UNIQUE INDEX idx_proveedores_nombre_unique ON public.proveedores USING btree (f_immutable_lower_unaccent((nombre)::text)) WHERE (activo = true)
  ```
- **proveedores_pkey**
  ```sql
  CREATE UNIQUE INDEX proveedores_pkey ON public.proveedores USING btree (id)
  ```
- **proveedores_ruc_key**
  ```sql
  CREATE UNIQUE INDEX proveedores_ruc_key ON public.proveedores USING btree (ruc)
  ```

---

### registros_odometro

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | uuid | No | public.gen_random_uuid() |  |
| vehiculo_id | uuid | No |  |  |
| odometro | integer(32) | No |  |  |
| fecha_medicion | timestamp with time zone | No | now() |  |
| fuente | character varying(50) | Sí | 'manual'::character varying |  |
| creado_por | uuid | Sí |  |  |
| notas | text | Sí |  |  |

#### Restricciones

- **2200_19823_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19823_2_not_null** (CHECK) - Condición: vehiculo_id IS NOT NULL
- **2200_19823_3_not_null** (CHECK) - Condición: odometro IS NOT NULL
- **2200_19823_4_not_null** (CHECK) - Condición: fecha_medicion IS NOT NULL
- **registros_odometro_fuente_check** (CHECK) - Referencia: registros_odometro.fuente - Condición: ((fuente)::text <> ''::text)
- **registros_odometro_odometro_check** (CHECK) - Referencia: registros_odometro.odometro - Condición: (odometro >= 0)
- **registros_odometro_creado_por_fkey** (FOREIGN KEY) - Columna: creado_por - Referencia: usuarios.id
- **registros_odometro_vehiculo_id_fkey** (FOREIGN KEY) - Columna: vehiculo_id - Referencia: vehiculos.id
- **registros_odometro_pkey** (PRIMARY KEY) - Columna: id - Referencia: registros_odometro.id

#### Índices

- **idx_registros_odometro_vehiculo_fecha**
  ```sql
  CREATE INDEX idx_registros_odometro_vehiculo_fecha ON public.registros_odometro USING btree (vehiculo_id, fecha_medicion DESC)
  ```
- **registros_odometro_pkey**
  ```sql
  CREATE UNIQUE INDEX registros_odometro_pkey ON public.registros_odometro USING btree (id)
  ```

---

### roles

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | uuid | No | public.gen_random_uuid() |  |
| nombre | character varying(100) | No |  |  |
| descripcion | text | Sí |  |  |
| es_rol_sistema | boolean | No | false |  |
| creado_en | timestamp with time zone | No | now() |  |
| creado_por | uuid | Sí |  |  |
| actualizado_en | timestamp with time zone | Sí |  |  |
| actualizado_por | uuid | Sí |  |  |

#### Restricciones

- **2200_19736_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19736_2_not_null** (CHECK) - Condición: nombre IS NOT NULL
- **2200_19736_4_not_null** (CHECK) - Condición: es_rol_sistema IS NOT NULL
- **2200_19736_5_not_null** (CHECK) - Condición: creado_en IS NOT NULL
- **roles_actualizado_por_fkey** (FOREIGN KEY) - Columna: actualizado_por - Referencia: usuarios.id
- **roles_creado_por_fkey** (FOREIGN KEY) - Columna: creado_por - Referencia: usuarios.id
- **roles_pkey** (PRIMARY KEY) - Columna: id - Referencia: roles.id
- **roles_nombre_key** (UNIQUE) - Columna: nombre - Referencia: roles.nombre

#### Índices

- **idx_roles_nombre_lower**
  ```sql
  CREATE INDEX idx_roles_nombre_lower ON public.roles USING btree (lower((nombre)::text))
  ```
- **idx_roles_nombre_lower_unaccent**
  ```sql
  CREATE INDEX idx_roles_nombre_lower_unaccent ON public.roles USING btree (f_immutable_lower_unaccent((nombre)::text))
  ```
- **roles_nombre_key**
  ```sql
  CREATE UNIQUE INDEX roles_nombre_key ON public.roles USING btree (nombre)
  ```
- **roles_pkey**
  ```sql
  CREATE UNIQUE INDEX roles_pkey ON public.roles USING btree (id)
  ```

---

### roles_permisos

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| rol_id | uuid | No |  |  |
| permiso_id | uuid | No |  |  |
| asignado_en | timestamp with time zone | No | now() |  |
| asignado_por | uuid | Sí |  |  |

#### Restricciones

- **2200_19744_1_not_null** (CHECK) - Condición: rol_id IS NOT NULL
- **2200_19744_2_not_null** (CHECK) - Condición: permiso_id IS NOT NULL
- **2200_19744_3_not_null** (CHECK) - Condición: asignado_en IS NOT NULL
- **roles_permisos_asignado_por_fkey** (FOREIGN KEY) - Columna: asignado_por - Referencia: usuarios.id
- **roles_permisos_permiso_id_fkey** (FOREIGN KEY) - Columna: permiso_id - Referencia: permisos.id
- **roles_permisos_rol_id_fkey** (FOREIGN KEY) - Columna: rol_id - Referencia: roles.id
- **roles_permisos_pkey** (PRIMARY KEY) - Columna: rol_id - Referencia: roles_permisos.permiso_id
- **roles_permisos_pkey** (PRIMARY KEY) - Columna: permiso_id - Referencia: roles_permisos.rol_id
- **roles_permisos_pkey** (PRIMARY KEY) - Columna: permiso_id - Referencia: roles_permisos.permiso_id
- **roles_permisos_pkey** (PRIMARY KEY) - Columna: rol_id - Referencia: roles_permisos.rol_id

#### Índices

- **idx_roles_permisos_permiso_id**
  ```sql
  CREATE INDEX idx_roles_permisos_permiso_id ON public.roles_permisos USING btree (permiso_id)
  ```
- **roles_permisos_pkey**
  ```sql
  CREATE UNIQUE INDEX roles_permisos_pkey ON public.roles_permisos USING btree (rol_id, permiso_id)
  ```

---

### rutas

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | uuid | No | public.gen_random_uuid() |  |
| codigo | character varying(20) | No |  |  |
| nombre | character varying(100) | No |  |  |
| descripcion | text | Sí |  |  |
| distancia_total_km | numeric(10,2) | No |  |  |
| ida_vuelta | boolean | No | true |  |
| activa | boolean | No | true |  |
| creado_en | timestamp with time zone | No | now() |  |
| creado_por | uuid | Sí |  |  |
| actualizado_en | timestamp with time zone | Sí |  |  |
| actualizado_por | uuid | Sí |  |  |

#### Restricciones

- **2200_19833_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19833_2_not_null** (CHECK) - Condición: codigo IS NOT NULL
- **2200_19833_3_not_null** (CHECK) - Condición: nombre IS NOT NULL
- **2200_19833_5_not_null** (CHECK) - Condición: distancia_total_km IS NOT NULL
- **2200_19833_6_not_null** (CHECK) - Condición: ida_vuelta IS NOT NULL
- **2200_19833_7_not_null** (CHECK) - Condición: activa IS NOT NULL
- **2200_19833_8_not_null** (CHECK) - Condición: creado_en IS NOT NULL
- **rutas_actualizado_por_fkey** (FOREIGN KEY) - Columna: actualizado_por - Referencia: usuarios.id
- **rutas_creado_por_fkey** (FOREIGN KEY) - Columna: creado_por - Referencia: usuarios.id
- **rutas_pkey** (PRIMARY KEY) - Columna: id - Referencia: rutas.id
- **rutas_codigo_key** (UNIQUE) - Columna: codigo - Referencia: rutas.codigo

#### Índices

- **rutas_codigo_key**
  ```sql
  CREATE UNIQUE INDEX rutas_codigo_key ON public.rutas USING btree (codigo)
  ```
- **rutas_pkey**
  ```sql
  CREATE UNIQUE INDEX rutas_pkey ON public.rutas USING btree (id)
  ```

---

### tareas_programadas

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | integer(32) | No | nextval('tareas_programadas_id_seq'::regclass) |  |
| nombre_tarea | character varying(100) | No |  |  |
| descripcion | text | Sí |  |  |
| frecuencia_dias | integer(32) | No | 1 |  |
| ultima_ejecucion | timestamp with time zone | Sí |  |  |
| proxima_ejecucion | timestamp with time zone | Sí |  |  |
| activa | boolean | Sí | true |  |
| script_sql | text | Sí |  |  |
| creado_en | timestamp with time zone | Sí | now() |  |
| creado_por | character varying(100) | Sí | 'SISTEMA'::character varying |  |
| actualizado_en | timestamp with time zone | Sí |  |  |
| actualizado_por | character varying(100) | Sí |  |  |

#### Restricciones

- **2200_19842_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19842_2_not_null** (CHECK) - Condición: nombre_tarea IS NOT NULL
- **2200_19842_4_not_null** (CHECK) - Condición: frecuencia_dias IS NOT NULL
- **tareas_programadas_pkey** (PRIMARY KEY) - Columna: id - Referencia: tareas_programadas.id

#### Índices

- **tareas_programadas_pkey**
  ```sql
  CREATE UNIQUE INDEX tareas_programadas_pkey ON public.tareas_programadas USING btree (id)
  ```

---

### tipos_ruta

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | uuid | No | public.gen_random_uuid() |  |
| nombre_ruta | character varying(150) | No |  |  |
| descripcion | text | Sí |  |  |
| distancia_total_km_ciclo | numeric(8,2) | Sí |  |  |
| distancia_trocha_km_ciclo | numeric(8,2) | Sí | 0 |  |
| distancia_asfalto_km_ciclo | numeric(8,2) | Sí | 0 |  |
| distancia_otro_terreno_km_ciclo | numeric(8,2) | Sí | 0 |  |
| porcentaje_promedio_con_carga | numeric(5,2) | Sí |  |  |
| creado_en | timestamp with time zone | No | now() |  |
| creado_por | uuid | Sí |  |  |
| actualizado_en | timestamp with time zone | Sí |  |  |
| actualizado_por | uuid | Sí |  |  |

#### Restricciones

- **2200_19852_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19852_2_not_null** (CHECK) - Condición: nombre_ruta IS NOT NULL
- **2200_19852_9_not_null** (CHECK) - Condición: creado_en IS NOT NULL
- **chk_porc_carga_ruta_gesneu** (CHECK) - Referencia: tipos_ruta.porcentaje_promedio_con_carga - Condición: ((porcentaje_promedio_con_carga IS NULL) OR ((porcentaje_promedio_con_carga >= (0)::numeric) AND (porcentaje_promedio_con_carga <= (100)::numeric)))
- **tipos_ruta_actualizado_por_fkey** (FOREIGN KEY) - Columna: actualizado_por - Referencia: usuarios.id
- **tipos_ruta_creado_por_fkey** (FOREIGN KEY) - Columna: creado_por - Referencia: usuarios.id
- **tipos_ruta_pkey** (PRIMARY KEY) - Columna: id - Referencia: tipos_ruta.id
- **tipos_ruta_nombre_ruta_key** (UNIQUE) - Columna: nombre_ruta - Referencia: tipos_ruta.nombre_ruta

#### Índices

- **tipos_ruta_nombre_ruta_key**
  ```sql
  CREATE UNIQUE INDEX tipos_ruta_nombre_ruta_key ON public.tipos_ruta USING btree (nombre_ruta)
  ```
- **tipos_ruta_pkey**
  ```sql
  CREATE UNIQUE INDEX tipos_ruta_pkey ON public.tipos_ruta USING btree (id)
  ```

---

### tipos_vehiculo

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | uuid | No | public.gen_random_uuid() |  |
| nombre | character varying(100) | No |  |  |
| descripcion | text | Sí |  |  |
| categoria_principal | character varying(50) | Sí |  |  |
| subtipo | character varying(50) | Sí |  |  |
| ejes_standard | smallint(16) | No | 2 |  |
| activo | boolean | No | true |  |
| creado_en | timestamp with time zone | No | now() |  |
| creado_por | uuid | Sí |  |  |
| actualizado_en | timestamp with time zone | Sí |  |  |
| actualizado_por | uuid | Sí |  |  |

#### Restricciones

- **2200_19863_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19863_2_not_null** (CHECK) - Condición: nombre IS NOT NULL
- **2200_19863_6_not_null** (CHECK) - Condición: ejes_standard IS NOT NULL
- **2200_19863_7_not_null** (CHECK) - Condición: activo IS NOT NULL
- **2200_19863_8_not_null** (CHECK) - Condición: creado_en IS NOT NULL
- **tipos_vehiculo_ejes_standard_check** (CHECK) - Referencia: tipos_vehiculo.ejes_standard - Condición: ((ejes_standard >= 1) AND (ejes_standard <= 10))
- **tipos_vehiculo_actualizado_por_fkey** (FOREIGN KEY) - Columna: actualizado_por - Referencia: usuarios.id
- **tipos_vehiculo_creado_por_fkey** (FOREIGN KEY) - Columna: creado_por - Referencia: usuarios.id
- **tipos_vehiculo_pkey** (PRIMARY KEY) - Columna: id - Referencia: tipos_vehiculo.id

#### Índices

- **idx_tipos_vehiculo_nombre**
  ```sql
  CREATE UNIQUE INDEX idx_tipos_vehiculo_nombre ON public.tipos_vehiculo USING btree (f_immutable_lower_unaccent((nombre)::text)) WHERE (activo = true)
  ```
- **tipos_vehiculo_pkey**
  ```sql
  CREATE UNIQUE INDEX tipos_vehiculo_pkey ON public.tipos_vehiculo USING btree (id)
  ```

---

### usuarios

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | uuid | No | public.gen_random_uuid() |  |
| username | character varying(50) | No |  |  |
| nombre_completo | character varying(200) | Sí |  |  |
| email | character varying(100) | Sí |  |  |
| password_hash | text | Sí |  |  |
| activo | boolean | No | true |  |
| ultimo_login | timestamp with time zone | Sí |  |  |
| creado_en | timestamp with time zone | No | now() |  |
| creado_por | uuid | Sí |  |  |
| actualizado_en | timestamp with time zone | Sí |  |  |
| actualizado_por | uuid | Sí |  |  |

#### Restricciones

- **2200_19748_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19748_2_not_null** (CHECK) - Condición: username IS NOT NULL
- **2200_19748_6_not_null** (CHECK) - Condición: activo IS NOT NULL
- **2200_19748_8_not_null** (CHECK) - Condición: creado_en IS NOT NULL
- **usuarios_actualizado_por_fkey** (FOREIGN KEY) - Columna: actualizado_por - Referencia: usuarios.id
- **usuarios_creado_por_fkey** (FOREIGN KEY) - Columna: creado_por - Referencia: usuarios.id
- **usuarios_pkey** (PRIMARY KEY) - Columna: id - Referencia: usuarios.id
- **usuarios_email_key** (UNIQUE) - Columna: email - Referencia: usuarios.email
- **usuarios_username_key** (UNIQUE) - Columna: username - Referencia: usuarios.username

#### Índices

- **usuarios_email_key**
  ```sql
  CREATE UNIQUE INDEX usuarios_email_key ON public.usuarios USING btree (email)
  ```
- **usuarios_pkey**
  ```sql
  CREATE UNIQUE INDEX usuarios_pkey ON public.usuarios USING btree (id)
  ```
- **usuarios_username_key**
  ```sql
  CREATE UNIQUE INDEX usuarios_username_key ON public.usuarios USING btree (username)
  ```

---

### usuarios_roles

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| usuario_id | uuid | No |  |  |
| rol_id | uuid | No |  |  |
| asignado_en | timestamp with time zone | No | now() |  |
| asignado_por | uuid | Sí |  |  |

#### Restricciones

- **2200_19756_1_not_null** (CHECK) - Condición: usuario_id IS NOT NULL
- **2200_19756_2_not_null** (CHECK) - Condición: rol_id IS NOT NULL
- **2200_19756_3_not_null** (CHECK) - Condición: asignado_en IS NOT NULL
- **usuarios_roles_asignado_por_fkey** (FOREIGN KEY) - Columna: asignado_por - Referencia: usuarios.id
- **usuarios_roles_rol_id_fkey** (FOREIGN KEY) - Columna: rol_id - Referencia: roles.id
- **usuarios_roles_usuario_id_fkey** (FOREIGN KEY) - Columna: usuario_id - Referencia: usuarios.id
- **usuarios_roles_pkey** (PRIMARY KEY) - Columna: usuario_id - Referencia: usuarios_roles.rol_id
- **usuarios_roles_pkey** (PRIMARY KEY) - Columna: rol_id - Referencia: usuarios_roles.usuario_id
- **usuarios_roles_pkey** (PRIMARY KEY) - Columna: rol_id - Referencia: usuarios_roles.rol_id
- **usuarios_roles_pkey** (PRIMARY KEY) - Columna: usuario_id - Referencia: usuarios_roles.usuario_id

#### Índices

- **idx_usuarios_roles_rol_id**
  ```sql
  CREATE INDEX idx_usuarios_roles_rol_id ON public.usuarios_roles USING btree (rol_id)
  ```
- **idx_usuarios_roles_usuario_id**
  ```sql
  CREATE INDEX idx_usuarios_roles_usuario_id ON public.usuarios_roles USING btree (usuario_id)
  ```
- **usuarios_roles_pkey**
  ```sql
  CREATE UNIQUE INDEX usuarios_roles_pkey ON public.usuarios_roles USING btree (usuario_id, rol_id)
  ```

---

### vehiculos

#### Columnas

| Columna | Tipo | Nulable | Por Defecto | Descripción |
|---------|------|---------|-------------|-------------|
| id | uuid | No | public.gen_random_uuid() |  |
| tipo_vehiculo_id | uuid | No |  |  |
| placa | character varying(15) | Sí |  |  |
| vin | character varying(17) | Sí |  |  |
| numero_economico | character varying(50) | No |  |  |
| marca | character varying(50) | Sí |  |  |
| modelo_vehiculo | character varying(50) | Sí |  |  |
| anio_fabricacion | smallint(16) | Sí |  |  |
| fecha_alta | date | No | CURRENT_DATE |  |
| fecha_baja | date | Sí |  |  |
| activo | boolean | No | true |  |
| odometro_actual | integer(32) | Sí |  |  |
| fecha_ultimo_odometro | timestamp with time zone | Sí |  |  |
| ubicacion_actual | character varying(100) | Sí |  |  |
| notas | text | Sí |  |  |
| creado_en | timestamp with time zone | No | now() |  |
| creado_por | uuid | Sí |  |  |
| actualizado_en | timestamp with time zone | Sí |  |  |
| actualizado_por | uuid | Sí |  |  |
| peso_carga_maxima_diseno_ton | numeric(5,2) | Sí |  |  |

#### Restricciones

- **2200_19878_11_not_null** (CHECK) - Condición: activo IS NOT NULL
- **2200_19878_16_not_null** (CHECK) - Condición: creado_en IS NOT NULL
- **2200_19878_1_not_null** (CHECK) - Condición: id IS NOT NULL
- **2200_19878_2_not_null** (CHECK) - Condición: tipo_vehiculo_id IS NOT NULL
- **2200_19878_5_not_null** (CHECK) - Condición: numero_economico IS NOT NULL
- **2200_19878_9_not_null** (CHECK) - Condición: fecha_alta IS NOT NULL
- **vehiculos_anio_fabricacion_check** (CHECK) - Referencia: vehiculos.anio_fabricacion - Condición: ((anio_fabricacion >= 1900) AND ((anio_fabricacion)::numeric <= (EXTRACT(year FROM CURRENT_DATE) + (1)::numeric)))
- **vehiculos_fecha_baja_check** (CHECK) - Referencia: vehiculos.fecha_alta - Condición: ((fecha_baja IS NULL) OR (fecha_baja >= fecha_alta))
- **vehiculos_fecha_baja_check** (CHECK) - Referencia: vehiculos.fecha_baja - Condición: ((fecha_baja IS NULL) OR (fecha_baja >= fecha_alta))
- **vehiculos_odometro_actual_check** (CHECK) - Referencia: vehiculos.odometro_actual - Condición: ((odometro_actual IS NULL) OR (odometro_actual >= 0))
- **vehiculos_actualizado_por_fkey** (FOREIGN KEY) - Columna: actualizado_por - Referencia: usuarios.id
- **vehiculos_creado_por_fkey** (FOREIGN KEY) - Columna: creado_por - Referencia: usuarios.id
- **vehiculos_tipo_vehiculo_id_fkey** (FOREIGN KEY) - Columna: tipo_vehiculo_id - Referencia: tipos_vehiculo.id
- **vehiculos_pkey** (PRIMARY KEY) - Columna: id - Referencia: vehiculos.id
- **vehiculos_numero_economico_key** (UNIQUE) - Columna: numero_economico - Referencia: vehiculos.numero_economico
- **vehiculos_placa_key** (UNIQUE) - Columna: placa - Referencia: vehiculos.placa
- **vehiculos_vin_key** (UNIQUE) - Columna: vin - Referencia: vehiculos.vin

#### Índices

- **idx_vehiculos_activos**
  ```sql
  CREATE INDEX idx_vehiculos_activos ON public.vehiculos USING btree (activo) WHERE (activo = true)
  ```
- **idx_vehiculos_numero_economico**
  ```sql
  CREATE INDEX idx_vehiculos_numero_economico ON public.vehiculos USING btree (lower((numero_economico)::text)) WHERE (activo = true)
  ```
- **idx_vehiculos_placa**
  ```sql
  CREATE INDEX idx_vehiculos_placa ON public.vehiculos USING btree (placa) WHERE ((placa IS NOT NULL) AND (activo = true))
  ```
- **idx_vehiculos_tipo**
  ```sql
  CREATE INDEX idx_vehiculos_tipo ON public.vehiculos USING btree (tipo_vehiculo_id) WHERE (activo = true)
  ```
- **vehiculos_numero_economico_key**
  ```sql
  CREATE UNIQUE INDEX vehiculos_numero_economico_key ON public.vehiculos USING btree (numero_economico)
  ```
- **vehiculos_pkey**
  ```sql
  CREATE UNIQUE INDEX vehiculos_pkey ON public.vehiculos USING btree (id)
  ```
- **vehiculos_placa_key**
  ```sql
  CREATE UNIQUE INDEX vehiculos_placa_key ON public.vehiculos USING btree (placa)
  ```
- **vehiculos_vin_key**
  ```sql
  CREATE UNIQUE INDEX vehiculos_vin_key ON public.vehiculos USING btree (vin)
  ```

---

