
-- CreateSchema
CREATE SCHEMA IF NOT EXISTS "public";

-- CreateEnum
CREATE TYPE "RolEnum" AS ENUM ('ADMIN', 'GESTOR', 'OPERADOR');

-- CreateEnum
CREATE TYPE "TipoMedicionEnum" AS ENUM ('KILOMETRAJE', 'HOROMETRO');

-- CreateEnum
CREATE TYPE "EstadoNeumaticoEnum" AS ENUM ('EN_STOCK', 'INSTALADO', 'EN_REPARACION', 'EN_REENCAUCHE', 'DESECHADO');

-- CreateEnum
CREATE TYPE "TipoEventoNeumaticoEnum" AS ENUM ('COMPRA', 'INSTALACION', 'DESMONTAJE', 'ROTACION', 'INSPECCION', 'REPARACION_ENTRADA', 'REPARACION_SALIDA', 'REENCAUCHE_ENTRADA', 'REENCAUCHE_SALIDA', 'DESECHO', 'AJUSTE_INVENTARIO');

-- CreateEnum
CREATE TYPE "TipoEjeEnum" AS ENUM ('DIRECCION', 'TRACCION', 'ARRASTRE');

-- CreateEnum
CREATE TYPE "LadoVehiculoEnum" AS ENUM ('IZQUIERDO', 'DERECHO', 'CENTRAL');

-- CreateEnum
CREATE TYPE "TipoProveedorEnum" AS ENUM ('FABRICANTE', 'SERVICIO_REPARACION', 'SERVICIO_REENCAUCHE', 'OTRO');

-- CreateEnum
CREATE TYPE "TipoAlertaEnum" AS ENUM ('PROFUNDIDAD_MINIMA', 'REENCAUCHE_MAXIMO', 'DESGASTE_IRREGULAR', 'VENCIMIENTO_DOT', 'PRESION_BAJA');

-- CreateEnum
CREATE TYPE "SeveridadAlertaEnum" AS ENUM ('INFO', 'WARNING', 'CRITICAL');

-- CreateEnum
CREATE TYPE "FuenteLectura" AS ENUM ('MANUAL', 'SENSOR_TPMS');

-- CreateEnum
CREATE TYPE "WebhookEventType" AS ENUM ('ALERTA_CRITICAL', 'DESECHO', 'REENCAUCHE_SALIDA', 'INSTALACION', 'DESMONTAJE', 'ALL_EVENTS');

-- CreateEnum
CREATE TYPE "JobStatus" AS ENUM ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED');

-- CreateEnum
CREATE TYPE "TipoParametroEnum" AS ENUM ('PROFUNDIDAD_MINIMA_MM', 'PRESION_MINIMA_PSI', 'PRESION_MAXIMA_PSI', 'TOLERANCIA_PRESION_PCT', 'REENC_MAXIMOS', 'VIDA_UTIL_ESTIMADA_KM');

-- CreateTable
CREATE TABLE "centros_costo" (
    "id" UUID NOT NULL,
    "codigo" VARCHAR(20) NOT NULL,
    "nombre" VARCHAR(100) NOT NULL,
    "area_negocio" VARCHAR(100),
    "activo" BOOLEAN NOT NULL DEFAULT true,
    "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "centros_costo_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "usuarios" (
    "id" UUID NOT NULL,
    "username" VARCHAR(50) NOT NULL,
    "nombre_completo" VARCHAR(200) NOT NULL,
    "email" VARCHAR(100) NOT NULL,
    "password_hash" TEXT NOT NULL,
    "rol" "RolEnum" NOT NULL DEFAULT 'OPERADOR',
    "activo" BOOLEAN NOT NULL DEFAULT true,
    "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "usuarios_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "vehiculos" (
    "id" UUID NOT NULL,
    "codigo_interno" VARCHAR(20),
    "placa" VARCHAR(20),
    "tipo_vehiculo_id" UUID NOT NULL,
    "centro_costo_id" UUID,
    "marca" VARCHAR(50),
    "modelo" VARCHAR(50),
    "anio" INTEGER,
    "numero_serie" TEXT,
    "tipo_medicion" "TipoMedicionEnum" NOT NULL DEFAULT 'KILOMETRAJE',
    "contador_actual" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "activo" BOOLEAN NOT NULL DEFAULT true,
    "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "actualizado_en" TIMESTAMPTZ(6),
    "creado_por" UUID,
    "actualizado_por" UUID,
    "eliminado_por" UUID,
    "eliminado_en" TIMESTAMPTZ(6),

    CONSTRAINT "vehiculos_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "neumaticos" (
    "id" UUID NOT NULL,
    "numero_serie" VARCHAR(50) NOT NULL,
    "modelo_id" UUID NOT NULL,
    "dot" VARCHAR(4),
    "marca_id" UUID,
    "estado_actual" "EstadoNeumaticoEnum" NOT NULL DEFAULT 'EN_STOCK',
    "profundidad_inicial_mm" DOUBLE PRECISION NOT NULL,
    "profundidad_actual_mm" DOUBLE PRECISION,
    "profundidad_int" DOUBLE PRECISION,
    "profundidad_cen" DOUBLE PRECISION,
    "profundidad_ext" DOUBLE PRECISION,
    "presion_actual_psi" DOUBLE PRECISION,
    "kilometraje_acumulado" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "horas_acumuladas" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "vida_actual" INTEGER NOT NULL DEFAULT 1,
    "reencauches_realizados" INTEGER NOT NULL DEFAULT 0,
    "es_reencauchado" BOOLEAN NOT NULL DEFAULT false,
    "costo_compra" DECIMAL(10,2),
    "fecha_compra" DATE,
    "ubicacion_almacen_id" UUID,
    "ubicacion_vehiculo_id" UUID,
    "ubicacion_posicion_id" UUID,
    "activo" BOOLEAN NOT NULL DEFAULT true,
    "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "actualizado_en" TIMESTAMPTZ(6),
    "creado_por" UUID,
    "actualizado_por" UUID,
    "eliminado_por" UUID,
    "eliminado_en" TIMESTAMPTZ(6),

    CONSTRAINT "neumaticos_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "historial_estado_neumatico" (
    "id" UUID NOT NULL,
    "neumatico_id" UUID NOT NULL,
    "estado_anterior" "EstadoNeumaticoEnum" NOT NULL,
    "estado_nuevo" "EstadoNeumaticoEnum" NOT NULL,
    "fecha_cambio" TIMESTAMPTZ(6) NOT NULL,
    "motivo" TEXT,
    "creado_por" UUID,
    "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "historial_estado_neumatico_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "eventos_neumaticos" (
    "id" UUID NOT NULL,
    "tipo_evento" "TipoEventoNeumaticoEnum" NOT NULL,
    "neumatico_id" UUID NOT NULL,
    "fecha_evento" TIMESTAMPTZ(6) NOT NULL,
    "contador_vehiculo" DOUBLE PRECISION,
    "profundidad_int" DECIMAL(5,2),
    "profundidad_cen" DECIMAL(5,2),
    "profundidad_ext" DECIMAL(5,2),
    "profundidad_remanente" DECIMAL(5,2),
    "presion_psi" DOUBLE PRECISION,
    "vehiculo_id" UUID,
    "posicion_montaje_id" UUID,
    "almacen_destino_id" UUID,
    "proveedor_id" UUID,
    "motivo_desecho_id" UUID,
    "costo_evento" DECIMAL(10,2),
    "notas" TEXT,
    "creado_por" UUID,
    "creado_en" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "eventos_neumaticos_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "tipos_vehiculo" (
    "id" UUID NOT NULL,
    "nombre" VARCHAR(50) NOT NULL,
    "descripcion" TEXT,
    "activo" BOOLEAN NOT NULL DEFAULT true,

    CONSTRAINT "tipos_vehiculo_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "configuraciones_eje" (
    "id" UUID NOT NULL,
    "tipo_vehiculo_id" UUID NOT NULL,
    "numero_eje" INTEGER NOT NULL,
    "tipo_eje" "TipoEjeEnum" NOT NULL,
    "posiciones_neumatico" INTEGER NOT NULL,
    "permite_reencauchados" BOOLEAN NOT NULL DEFAULT true,

    CONSTRAINT "configuraciones_eje_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "posiciones_neumatico" (
    "id" UUID NOT NULL,
    "configuracion_eje_id" UUID NOT NULL,
    "numero_posicion" INTEGER NOT NULL,
    "lado_vehiculo" "LadoVehiculoEnum" NOT NULL,
    "permite_reencauchado" BOOLEAN NOT NULL DEFAULT true,

    CONSTRAINT "posiciones_neumatico_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "fabricantes_neumatico" (
    "id" UUID NOT NULL,
    "nombre" VARCHAR(100) NOT NULL,

    CONSTRAINT "fabricantes_neumatico_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "modelos_neumatico" (
    "id" UUID NOT NULL,
    "nombre" VARCHAR(100) NOT NULL,
    "medida" VARCHAR(50) NOT NULL,
    "profundidad_inicial_mm" DOUBLE PRECISION NOT NULL,
    "reencauches_maximos" INTEGER NOT NULL DEFAULT 0,
    "fabricante_id" UUID NOT NULL,

    CONSTRAINT "modelos_neumatico_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "almacenes" (
    "id" UUID NOT NULL,
    "nombre" VARCHAR(100) NOT NULL,
    "tipo" TEXT DEFAULT 'PRINCIPAL',
    "ubicacion" TEXT,
    "activo" BOOLEAN NOT NULL DEFAULT true,
    "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "actualizado_en" TIMESTAMPTZ(6),
    "creado_por" UUID,
    "actualizado_por" UUID,
    "eliminado_por" UUID,
    "eliminado_en" TIMESTAMPTZ(6),

    CONSTRAINT "almacenes_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "proveedores" (
    "id" UUID NOT NULL,
    "nombre" VARCHAR(200) NOT NULL,
    "ruc" VARCHAR(20),
    "tipo" "TipoProveedorEnum" NOT NULL,
    "activo" BOOLEAN NOT NULL DEFAULT true,
    "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "actualizado_en" TIMESTAMPTZ(6),
    "creado_por" UUID,
    "actualizado_por" UUID,
    "eliminado_por" UUID,
    "eliminado_en" TIMESTAMPTZ(6),

    CONSTRAINT "proveedores_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "registros_contador" (
    "id" UUID NOT NULL,
    "vehiculo_id" UUID NOT NULL,
    "valor" DOUBLE PRECISION NOT NULL,
    "fecha_registro" TIMESTAMPTZ(6) NOT NULL,
    "notas" TEXT,
    "creado_en" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "registros_contador_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "motivos_desecho" (
    "id" UUID NOT NULL,
    "nombre" VARCHAR(100) NOT NULL,
    "descripcion" TEXT,
    "requiere_evidencia" BOOLEAN NOT NULL DEFAULT false,
    "activo" BOOLEAN NOT NULL DEFAULT true,
    "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "creado_por" UUID,
    "actualizado_en" TIMESTAMPTZ(6),
    "actualizado_por" UUID,

    CONSTRAINT "motivos_desecho_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "alertas" (
    "id" UUID NOT NULL,
    "tipo" "TipoAlertaEnum" NOT NULL,
    "severidad" "SeveridadAlertaEnum" NOT NULL,
    "neumatico_id" UUID,
    "vehiculo_id" UUID,
    "mensaje" TEXT NOT NULL,
    "leida" BOOLEAN NOT NULL DEFAULT false,
    "resuelta" BOOLEAN NOT NULL DEFAULT false,
    "creada_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "alertas_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "lecturas_presion" (
    "id" UUID NOT NULL,
    "neumatico_id" UUID NOT NULL,
    "presion_psi" DOUBLE PRECISION NOT NULL,
    "temperatura_c" DOUBLE PRECISION,
    "bateria_nivel" INTEGER,
    "fuente" "FuenteLectura" NOT NULL DEFAULT 'MANUAL',
    "creado_por" UUID,
    "fecha_lectura" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "lecturas_presion_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "webhook_configs" (
    "id" UUID NOT NULL,
    "nombre" TEXT NOT NULL,
    "url" TEXT NOT NULL,
    "secret" TEXT NOT NULL,
    "eventos" "WebhookEventType"[],
    "activo" BOOLEAN NOT NULL DEFAULT true,
    "creado_en" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "creado_por" UUID,

    CONSTRAINT "webhook_configs_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "webhook_logs" (
    "id" UUID NOT NULL,
    "webhook_id" UUID NOT NULL,
    "evento" TEXT NOT NULL,
    "payload" JSONB NOT NULL,
    "status_code" INTEGER,
    "response" TEXT,
    "intentos" INTEGER NOT NULL DEFAULT 1,
    "exitoso" BOOLEAN NOT NULL DEFAULT false,
    "creado_en" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "webhook_logs_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "webhook_jobs" (
    "id" UUID NOT NULL,
    "webhook_id" UUID NOT NULL,
    "evento" TEXT NOT NULL,
    "payload" JSONB NOT NULL,
    "status" "JobStatus" NOT NULL DEFAULT 'PENDING',
    "attempts" INTEGER NOT NULL DEFAULT 0,
    "max_retries" INTEGER NOT NULL DEFAULT 5,
    "run_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "webhook_jobs_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "auditoria_logs" (
    "id" BIGSERIAL NOT NULL,
    "timestamp_log" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "esquema_tabla" VARCHAR(63) NOT NULL,
    "nombre_tabla" VARCHAR(63) NOT NULL,
    "operacion" VARCHAR(10) NOT NULL,
    "usuario_db" VARCHAR(63) NOT NULL DEFAULT current_user,
    "usuario_app_id" UUID,
    "usuario_app" VARCHAR(50),
    "ip_direccion" VARCHAR(45),
    "user_agent" TEXT,
    "entidad_id" UUID,
    "datos_antiguos" JSONB,
    "datos_nuevos" JSONB,
    "cambios" JSONB,

    CONSTRAINT "auditoria_logs_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "parametros_config" (
    "id" UUID NOT NULL,
    "tipo" "TipoParametroEnum" NOT NULL,
    "valor" TEXT NOT NULL,
    "descripcion" TEXT,
    "modelo_id" UUID,
    "almacen_id" UUID,
    "activo" BOOLEAN NOT NULL DEFAULT true,
    "creado_en" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "actualizado_en" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "parametros_config_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "centros_costo_codigo_key" ON "centros_costo"("codigo");

-- CreateIndex
CREATE UNIQUE INDEX "usuarios_username_key" ON "usuarios"("username");

-- CreateIndex
CREATE UNIQUE INDEX "usuarios_email_key" ON "usuarios"("email");

-- CreateIndex
CREATE UNIQUE INDEX "vehiculos_codigo_interno_key" ON "vehiculos"("codigo_interno");

-- CreateIndex
CREATE UNIQUE INDEX "vehiculos_placa_key" ON "vehiculos"("placa");

-- CreateIndex
CREATE UNIQUE INDEX "neumaticos_numero_serie_key" ON "neumaticos"("numero_serie");

-- CreateIndex
CREATE UNIQUE INDEX "tipos_vehiculo_nombre_key" ON "tipos_vehiculo"("nombre");

-- CreateIndex
CREATE UNIQUE INDEX "fabricantes_neumatico_nombre_key" ON "fabricantes_neumatico"("nombre");

-- CreateIndex
CREATE UNIQUE INDEX "proveedores_ruc_key" ON "proveedores"("ruc");

-- CreateIndex
CREATE UNIQUE INDEX "motivos_desecho_nombre_key" ON "motivos_desecho"("nombre");

-- CreateIndex
CREATE INDEX "lecturas_presion_neumatico_id_idx" ON "lecturas_presion"("neumatico_id");

-- CreateIndex
CREATE INDEX "lecturas_presion_fecha_lectura_idx" ON "lecturas_presion"("fecha_lectura");

-- CreateIndex
CREATE INDEX "webhook_logs_webhook_id_idx" ON "webhook_logs"("webhook_id");

-- CreateIndex
CREATE INDEX "webhook_logs_creado_en_idx" ON "webhook_logs"("creado_en");

-- CreateIndex
CREATE INDEX "webhook_jobs_status_run_at_idx" ON "webhook_jobs"("status", "run_at");

-- CreateIndex
CREATE INDEX "auditoria_logs_esquema_tabla_nombre_tabla_idx" ON "auditoria_logs"("esquema_tabla", "nombre_tabla");

-- CreateIndex
CREATE INDEX "auditoria_logs_timestamp_log_idx" ON "auditoria_logs"("timestamp_log" DESC);

-- CreateIndex
CREATE INDEX "auditoria_logs_entidad_id_idx" ON "auditoria_logs"("entidad_id");

-- CreateIndex
CREATE INDEX "auditoria_logs_usuario_app_id_idx" ON "auditoria_logs"("usuario_app_id");

-- CreateIndex
CREATE UNIQUE INDEX "parametros_config_tipo_modelo_id_almacen_id_key" ON "parametros_config"("tipo", "modelo_id", "almacen_id");

-- AddForeignKey
ALTER TABLE "vehiculos" ADD CONSTRAINT "vehiculos_tipo_vehiculo_id_fkey" FOREIGN KEY ("tipo_vehiculo_id") REFERENCES "tipos_vehiculo"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "vehiculos" ADD CONSTRAINT "vehiculos_centro_costo_id_fkey" FOREIGN KEY ("centro_costo_id") REFERENCES "centros_costo"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "neumaticos" ADD CONSTRAINT "neumaticos_modelo_id_fkey" FOREIGN KEY ("modelo_id") REFERENCES "modelos_neumatico"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "neumaticos" ADD CONSTRAINT "neumaticos_ubicacion_almacen_id_fkey" FOREIGN KEY ("ubicacion_almacen_id") REFERENCES "almacenes"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "neumaticos" ADD CONSTRAINT "neumaticos_ubicacion_vehiculo_id_fkey" FOREIGN KEY ("ubicacion_vehiculo_id") REFERENCES "vehiculos"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "neumaticos" ADD CONSTRAINT "neumaticos_ubicacion_posicion_id_fkey" FOREIGN KEY ("ubicacion_posicion_id") REFERENCES "posiciones_neumatico"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "historial_estado_neumatico" ADD CONSTRAINT "historial_estado_neumatico_neumatico_id_fkey" FOREIGN KEY ("neumatico_id") REFERENCES "neumaticos"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "eventos_neumaticos" ADD CONSTRAINT "eventos_neumaticos_neumatico_id_fkey" FOREIGN KEY ("neumatico_id") REFERENCES "neumaticos"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "eventos_neumaticos" ADD CONSTRAINT "eventos_neumaticos_vehiculo_id_fkey" FOREIGN KEY ("vehiculo_id") REFERENCES "vehiculos"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "eventos_neumaticos" ADD CONSTRAINT "eventos_neumaticos_posicion_montaje_id_fkey" FOREIGN KEY ("posicion_montaje_id") REFERENCES "posiciones_neumatico"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "eventos_neumaticos" ADD CONSTRAINT "eventos_neumaticos_almacen_destino_id_fkey" FOREIGN KEY ("almacen_destino_id") REFERENCES "almacenes"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "eventos_neumaticos" ADD CONSTRAINT "eventos_neumaticos_proveedor_id_fkey" FOREIGN KEY ("proveedor_id") REFERENCES "proveedores"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "eventos_neumaticos" ADD CONSTRAINT "eventos_neumaticos_motivo_desecho_id_fkey" FOREIGN KEY ("motivo_desecho_id") REFERENCES "motivos_desecho"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "eventos_neumaticos" ADD CONSTRAINT "eventos_neumaticos_creado_por_fkey" FOREIGN KEY ("creado_por") REFERENCES "usuarios"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "configuraciones_eje" ADD CONSTRAINT "configuraciones_eje_tipo_vehiculo_id_fkey" FOREIGN KEY ("tipo_vehiculo_id") REFERENCES "tipos_vehiculo"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "posiciones_neumatico" ADD CONSTRAINT "posiciones_neumatico_configuracion_eje_id_fkey" FOREIGN KEY ("configuracion_eje_id") REFERENCES "configuraciones_eje"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "modelos_neumatico" ADD CONSTRAINT "modelos_neumatico_fabricante_id_fkey" FOREIGN KEY ("fabricante_id") REFERENCES "fabricantes_neumatico"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "registros_contador" ADD CONSTRAINT "registros_contador_vehiculo_id_fkey" FOREIGN KEY ("vehiculo_id") REFERENCES "vehiculos"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "alertas" ADD CONSTRAINT "alertas_neumatico_id_fkey" FOREIGN KEY ("neumatico_id") REFERENCES "neumaticos"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "alertas" ADD CONSTRAINT "alertas_vehiculo_id_fkey" FOREIGN KEY ("vehiculo_id") REFERENCES "vehiculos"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "lecturas_presion" ADD CONSTRAINT "lecturas_presion_neumatico_id_fkey" FOREIGN KEY ("neumatico_id") REFERENCES "neumaticos"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "lecturas_presion" ADD CONSTRAINT "lecturas_presion_creado_por_fkey" FOREIGN KEY ("creado_por") REFERENCES "usuarios"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "webhook_configs" ADD CONSTRAINT "webhook_configs_creado_por_fkey" FOREIGN KEY ("creado_por") REFERENCES "usuarios"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "webhook_logs" ADD CONSTRAINT "webhook_logs_webhook_id_fkey" FOREIGN KEY ("webhook_id") REFERENCES "webhook_configs"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "webhook_jobs" ADD CONSTRAINT "webhook_jobs_webhook_id_fkey" FOREIGN KEY ("webhook_id") REFERENCES "webhook_configs"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "auditoria_logs" ADD CONSTRAINT "auditoria_logs_usuario_app_id_fkey" FOREIGN KEY ("usuario_app_id") REFERENCES "usuarios"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "parametros_config" ADD CONSTRAINT "parametros_config_modelo_id_fkey" FOREIGN KEY ("modelo_id") REFERENCES "modelos_neumatico"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "parametros_config" ADD CONSTRAINT "parametros_config_almacen_id_fkey" FOREIGN KEY ("almacen_id") REFERENCES "almacenes"("id") ON DELETE SET NULL ON UPDATE CASCADE;

