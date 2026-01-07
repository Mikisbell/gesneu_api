/*
  Warnings:

  - You are about to drop the column `ubicacion` on the `almacenes` table. All the data in the column will be lost.
  - You are about to alter the column `tipo` on the `almacenes` table. The data in that column could be lost. The data in that column will be cast from `Text` to `VarChar(50)`.
  - You are about to drop the column `posiciones_neumatico` on the `configuraciones_eje` table. All the data in the column will be lost.
  - You are about to drop the column `nombre` on the `modelos_neumatico` table. All the data in the column will be lost.
  - You are about to drop the column `profundidad_inicial_mm` on the `modelos_neumatico` table. All the data in the column will be lost.
  - You are about to alter the column `medida` on the `modelos_neumatico` table. The data in that column could be lost. The data in that column will be cast from `VarChar(50)` to `VarChar(20)`.
  - You are about to drop the column `marca_id` on the `neumaticos` table. All the data in the column will be lost.
  - You are about to drop the column `profundidad_actual_mm` on the `neumaticos` table. All the data in the column will be lost.
  - You are about to drop the column `lado_vehiculo` on the `posiciones_neumatico` table. All the data in the column will be lost.
  - You are about to drop the column `numero_posicion` on the `posiciones_neumatico` table. All the data in the column will be lost.
  - You are about to drop the column `anio` on the `vehiculos` table. All the data in the column will be lost.
  - You are about to drop the column `contador_actual` on the `vehiculos` table. All the data in the column will be lost.
  - You are about to drop the column `modelo` on the `vehiculos` table. All the data in the column will be lost.
  - You are about to drop the column `numero_serie` on the `vehiculos` table. All the data in the column will be lost.
  - You are about to alter the column `placa` on the `vehiculos` table. The data in that column could be lost. The data in that column will be cast from `VarChar(20)` to `VarChar(15)`.
  - A unique constraint covering the columns `[codigo]` on the table `almacenes` will be added. If there are existing duplicate values, this will fail.
  - A unique constraint covering the columns `[tipo_vehiculo_id,numero_eje]` on the table `configuraciones_eje` will be added. If there are existing duplicate values, this will fail.
  - A unique constraint covering the columns `[codigo_abreviado]` on the table `fabricantes_neumatico` will be added. If there are existing duplicate values, this will fail.
  - A unique constraint covering the columns `[fabricante_id,nombre_modelo,medida]` on the table `modelos_neumatico` will be added. If there are existing duplicate values, this will fail.
  - A unique constraint covering the columns `[codigo]` on the table `motivos_desecho` will be added. If there are existing duplicate values, this will fail.
  - A unique constraint covering the columns `[configuracion_eje_id,codigo_posicion]` on the table `posiciones_neumatico` will be added. If there are existing duplicate values, this will fail.
  - A unique constraint covering the columns `[vin]` on the table `vehiculos` will be added. If there are existing duplicate values, this will fail.
  - A unique constraint covering the columns `[numero_economico]` on the table `vehiculos` will be added. If there are existing duplicate values, this will fail.
  - Added the required column `codigo` to the `almacenes` table without a default value. This is not possible if the table is not empty.
  - Added the required column `nombre_eje` to the `configuraciones_eje` table without a default value. This is not possible if the table is not empty.
  - Added the required column `numero_posiciones` to the `configuraciones_eje` table without a default value. This is not possible if the table is not empty.
  - Added the required column `nombre_modelo` to the `modelos_neumatico` table without a default value. This is not possible if the table is not empty.
  - Added the required column `profundidad_original_mm` to the `modelos_neumatico` table without a default value. This is not possible if the table is not empty.
  - Added the required column `codigo` to the `motivos_desecho` table without a default value. This is not possible if the table is not empty.
  - Added the required column `profundidad_remanente_actual_mm` to the `neumaticos` table without a default value. This is not possible if the table is not empty.
  - Made the column `fecha_compra` on table `neumaticos` required. This step will fail if there are existing NULL values in that column.
  - Added the required column `codigo_posicion` to the `posiciones_neumatico` table without a default value. This is not possible if the table is not empty.
  - Added the required column `lado` to the `posiciones_neumatico` table without a default value. This is not possible if the table is not empty.
  - Added the required column `posicion_relativa` to the `posiciones_neumatico` table without a default value. This is not possible if the table is not empty.
  - Added the required column `numero_economico` to the `vehiculos` table without a default value. This is not possible if the table is not empty.

*/
-- CreateEnum
CREATE TYPE "TipoOperacionBitacora" AS ENUM ('MANTENIMIENTO_PREVENTIVO', 'MANTENIMIENTO_CORRECTIVO', 'INSPECCION_PROGRAMADA', 'INSPECCION_ALEATORIA', 'LAVADO', 'ALINEACION', 'BALANCEO', 'CAMBIO_ACEITE', 'OTRO');

-- CreateEnum
CREATE TYPE "SeveridadError" AS ENUM ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL');

-- CreateEnum
CREATE TYPE "EstadoGarantia" AS ENUM ('VIGENTE', 'VENCIDA', 'RECLAMADA', 'APROBADA', 'RECHAZADA');

-- CreateEnum
CREATE TYPE "EstadoTarea" AS ENUM ('PENDIENTE', 'EN_EJECUCION', 'COMPLETADA', 'FALLIDA', 'CANCELADA');

-- CreateEnum
CREATE TYPE "TipoTarea" AS ENUM ('ALERTA_VENCIMIENTO', 'REPORTE_AUTOMATICO', 'BACKUP_DB', 'LIMPIEZA_LOGS', 'SINCRONIZACION', 'NOTIFICACION', 'OTRO');

-- DropIndex
DROP INDEX "fabricantes_neumatico_nombre_key";

-- DropIndex
DROP INDEX "motivos_desecho_nombre_key";

-- DropIndex
DROP INDEX "neumaticos_numero_serie_key";

-- DropIndex
DROP INDEX "vehiculos_codigo_interno_key";

-- AlterTable
ALTER TABLE "almacenes" DROP COLUMN "ubicacion",
ADD COLUMN     "codigo" VARCHAR(20) NOT NULL,
ADD COLUMN     "direccion" TEXT,
ALTER COLUMN "nombre" SET DATA TYPE VARCHAR(150),
ALTER COLUMN "tipo" DROP DEFAULT,
ALTER COLUMN "tipo" SET DATA TYPE VARCHAR(50);

-- AlterTable
ALTER TABLE "configuraciones_eje" DROP COLUMN "posiciones_neumatico",
ADD COLUMN     "actualizado_en" TIMESTAMPTZ(6),
ADD COLUMN     "actualizado_por" UUID,
ADD COLUMN     "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN     "creado_por" UUID,
ADD COLUMN     "neumaticos_por_posicion" INTEGER NOT NULL DEFAULT 1,
ADD COLUMN     "nombre_eje" VARCHAR(50) NOT NULL,
ADD COLUMN     "numero_posiciones" INTEGER NOT NULL,
ADD COLUMN     "posiciones_duales" BOOLEAN NOT NULL DEFAULT false;

-- AlterTable
ALTER TABLE "fabricantes_neumatico" ADD COLUMN     "activo" BOOLEAN NOT NULL DEFAULT true,
ADD COLUMN     "actualizado_en" TIMESTAMPTZ(6),
ADD COLUMN     "actualizado_por" UUID,
ADD COLUMN     "codigo_abreviado" VARCHAR(10),
ADD COLUMN     "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN     "creado_por" UUID,
ADD COLUMN     "pais_origen" VARCHAR(50),
ADD COLUMN     "sitio_web" VARCHAR(255);

-- AlterTable
ALTER TABLE "modelos_neumatico" DROP COLUMN "nombre",
DROP COLUMN "profundidad_inicial_mm",
ADD COLUMN     "activo" BOOLEAN NOT NULL DEFAULT true,
ADD COLUMN     "actualizado_en" TIMESTAMPTZ(6),
ADD COLUMN     "actualizado_por" UUID,
ADD COLUMN     "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN     "creado_por" UUID,
ADD COLUMN     "diseno_predominante_para_eje" "TipoEjeEnum",
ADD COLUMN     "frecuencia_inspeccion_km" INTEGER DEFAULT 5000,
ADD COLUMN     "indice_carga" VARCHAR(5),
ADD COLUMN     "indice_velocidad" VARCHAR(2),
ADD COLUMN     "max_vidas_utiles" INTEGER DEFAULT 5,
ADD COLUMN     "nombre_modelo" VARCHAR(100) NOT NULL,
ADD COLUMN     "patron_dibujo" VARCHAR(50),
ADD COLUMN     "permite_reencauche" BOOLEAN NOT NULL DEFAULT false,
ADD COLUMN     "porcentaje_desgaste_por_vida" DECIMAL(5,2) DEFAULT 10.0,
ADD COLUMN     "posicion_uso_recomendada" "TipoEjeEnum",
ADD COLUMN     "presion_recomendada_psi" DECIMAL(5,2),
ADD COLUMN     "profundidad_minima_retiro_mm" DECIMAL(5,2) NOT NULL DEFAULT 1.6,
ADD COLUMN     "profundidad_original_mm" DECIMAL(5,2) NOT NULL,
ADD COLUMN     "tasa_desgaste_esperada_mm_km" DECIMAL(10,8),
ADD COLUMN     "tipo_servicio" VARCHAR(50),
ADD COLUMN     "vida_util_teorica_km" INTEGER,
ALTER COLUMN "medida" SET DATA TYPE VARCHAR(20);

-- AlterTable
ALTER TABLE "motivos_desecho" ADD COLUMN     "codigo" VARCHAR(20) NOT NULL;

-- AlterTable
ALTER TABLE "neumaticos" DROP COLUMN "marca_id",
DROP COLUMN "profundidad_actual_mm",
ADD COLUMN     "fecha_desecho" DATE,
ADD COLUMN     "fecha_fabricacion" DATE,
ADD COLUMN     "fecha_inicio_vida_actual" DATE,
ADD COLUMN     "fecha_ultima_medicion_profundidad" TIMESTAMPTZ(6),
ADD COLUMN     "fecha_ultimo_evento" TIMESTAMPTZ(6),
ADD COLUMN     "fecha_ultimo_reencauche" DATE,
ADD COLUMN     "kilometraje_vida_actual" DECIMAL(12,2) DEFAULT 0,
ADD COLUMN     "moneda_compra" VARCHAR(3) DEFAULT 'PEN',
ADD COLUMN     "motivo_desecho_id" UUID,
ADD COLUMN     "odometro_instalacion_vida_actual" DECIMAL(12,2),
ADD COLUMN     "profundidad_inicio_vida_actual_mm" DECIMAL(5,2),
ADD COLUMN     "profundidad_remanente_actual_mm" DECIMAL(5,2) NOT NULL,
ADD COLUMN     "proveedor_compra_id" UUID,
ADD COLUMN     "proxima_inspeccion_fecha" DATE,
ADD COLUMN     "proxima_inspeccion_km" DECIMAL(12,2),
ADD COLUMN     "sensor_id" VARCHAR(100),
ADD COLUMN     "tasa_desgaste_actual_mm_km" DECIMAL(10,8),
ADD COLUMN     "vida_util_restante_km" DECIMAL(12,2),
ALTER COLUMN "numero_serie" DROP NOT NULL,
ALTER COLUMN "numero_serie" SET DATA TYPE VARCHAR(100),
ALTER COLUMN "dot" SET DATA TYPE TEXT,
ALTER COLUMN "profundidad_inicial_mm" DROP NOT NULL,
ALTER COLUMN "horas_acumuladas" SET DATA TYPE DECIMAL(12,2),
ALTER COLUMN "fecha_compra" SET NOT NULL;

-- AlterTable
ALTER TABLE "posiciones_neumatico" DROP COLUMN "lado_vehiculo",
DROP COLUMN "numero_posicion",
ADD COLUMN     "actualizado_en" TIMESTAMPTZ(6),
ADD COLUMN     "actualizado_por" UUID,
ADD COLUMN     "codigo_posicion" VARCHAR(10) NOT NULL,
ADD COLUMN     "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN     "creado_por" UUID,
ADD COLUMN     "es_direccion" BOOLEAN NOT NULL DEFAULT false,
ADD COLUMN     "es_interna" BOOLEAN NOT NULL DEFAULT false,
ADD COLUMN     "es_traccion" BOOLEAN NOT NULL DEFAULT false,
ADD COLUMN     "etiqueta_posicion" VARCHAR(50),
ADD COLUMN     "lado" "LadoVehiculoEnum" NOT NULL,
ADD COLUMN     "posicion_relativa" INTEGER NOT NULL,
ADD COLUMN     "requiere_neumatico_especifico" BOOLEAN NOT NULL DEFAULT false;

-- AlterTable
ALTER TABLE "proveedores" ADD COLUMN     "contacto_principal" TEXT,
ADD COLUMN     "direccion" TEXT,
ADD COLUMN     "email" VARCHAR(100),
ADD COLUMN     "telefono" VARCHAR(50);

-- AlterTable
ALTER TABLE "vehiculos" DROP COLUMN "anio",
DROP COLUMN "contador_actual",
DROP COLUMN "modelo",
DROP COLUMN "numero_serie",
ADD COLUMN     "anio_fabricacion" INTEGER,
ADD COLUMN     "fecha_alta" DATE NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN     "fecha_baja" DATE,
ADD COLUMN     "fecha_ultimo_odometro" TIMESTAMPTZ(6),
ADD COLUMN     "modelo_vehiculo" VARCHAR(50),
ADD COLUMN     "notas" TEXT,
ADD COLUMN     "numero_economico" VARCHAR(50) NOT NULL,
ADD COLUMN     "odometro_actual" INTEGER DEFAULT 0,
ADD COLUMN     "peso_carga_maxima_diseno_ton" DECIMAL(5,2),
ADD COLUMN     "ubicacion_actual" VARCHAR(100),
ADD COLUMN     "vin" VARCHAR(17),
ALTER COLUMN "placa" SET DATA TYPE VARCHAR(15);

-- CreateTable
CREATE TABLE "roles" (
    "id" UUID NOT NULL,
    "nombre" VARCHAR(50) NOT NULL,
    "descripcion" TEXT,
    "es_sistema" BOOLEAN NOT NULL DEFAULT false,
    "activo" BOOLEAN NOT NULL DEFAULT true,
    "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "actualizado_en" TIMESTAMPTZ(6),

    CONSTRAINT "roles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "permisos" (
    "id" UUID NOT NULL,
    "codigo" VARCHAR(100) NOT NULL,
    "nombre" VARCHAR(100) NOT NULL,
    "modulo" VARCHAR(50) NOT NULL,
    "descripcion" TEXT,
    "activo" BOOLEAN NOT NULL DEFAULT true,
    "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "permisos_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "roles_permisos" (
    "id" UUID NOT NULL,
    "rol_id" UUID NOT NULL,
    "permiso_id" UUID NOT NULL,
    "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "creado_por" UUID,

    CONSTRAINT "roles_permisos_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "usuarios_roles" (
    "id" UUID NOT NULL,
    "usuario_id" UUID NOT NULL,
    "rol_id" UUID NOT NULL,
    "es_principal" BOOLEAN NOT NULL DEFAULT false,
    "valido_desde" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "valido_hasta" TIMESTAMPTZ(6),
    "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "creado_por" UUID,

    CONSTRAINT "usuarios_roles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "auditoria_roles_usuarios" (
    "id" BIGSERIAL NOT NULL,
    "usuario_id" UUID NOT NULL,
    "rol_id" UUID NOT NULL,
    "accion" VARCHAR(20) NOT NULL,
    "motivo" TEXT,
    "realizado_por" UUID NOT NULL,
    "ip_direccion" VARCHAR(45),
    "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "auditoria_roles_usuarios_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "configuracion_auditoria" (
    "id" UUID NOT NULL,
    "tabla_nombre" VARCHAR(100) NOT NULL,
    "auditar_insert" BOOLEAN NOT NULL DEFAULT true,
    "auditar_update" BOOLEAN NOT NULL DEFAULT true,
    "auditar_delete" BOOLEAN NOT NULL DEFAULT true,
    "campos_excluidos" TEXT[],
    "activo" BOOLEAN NOT NULL DEFAULT true,
    "actualizado_en" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "configuracion_auditoria_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "bitacora_mantenimiento" (
    "id" UUID NOT NULL,
    "vehiculo_id" UUID NOT NULL,
    "tipo_operacion" "TipoOperacionBitacora" NOT NULL,
    "fecha_programada" DATE,
    "fecha_realizada" TIMESTAMPTZ(6) NOT NULL,
    "kilometraje" DECIMAL(12,2),
    "horometro" DECIMAL(12,2),
    "costo" DECIMAL(12,2),
    "proveedor_id" UUID,
    "responsable" VARCHAR(200),
    "observaciones" TEXT,
    "evidencia_url" TEXT,
    "creado_por" UUID,
    "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "bitacora_mantenimiento_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "bitacora_operaciones" (
    "id" BIGSERIAL NOT NULL,
    "modulo" VARCHAR(50) NOT NULL,
    "accion" VARCHAR(100) NOT NULL,
    "entidad_id" UUID,
    "entidad_tipo" VARCHAR(50),
    "descripcion" TEXT NOT NULL,
    "datos_antes" JSONB,
    "datos_despues" JSONB,
    "usuario_id" UUID,
    "ip_direccion" VARCHAR(45),
    "user_agent" TEXT,
    "duracion_ms" INTEGER,
    "exitoso" BOOLEAN NOT NULL DEFAULT true,
    "error_mensaje" TEXT,
    "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "bitacora_operaciones_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "bitacora_operaciones_neumaticos" (
    "id" BIGSERIAL NOT NULL,
    "neumatico_id" UUID NOT NULL,
    "evento_id" UUID,
    "operacion" VARCHAR(50) NOT NULL,
    "vehiculo_id" UUID,
    "posicion_id" UUID,
    "kilometraje" DECIMAL(12,2),
    "profundidad_mm" DECIMAL(5,2),
    "presion_psi" DECIMAL(5,2),
    "observaciones" TEXT,
    "usuario_id" UUID,
    "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "bitacora_operaciones_neumaticos_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "errores_aplicacion" (
    "id" BIGSERIAL NOT NULL,
    "codigo" VARCHAR(50),
    "severidad" "SeveridadError" NOT NULL DEFAULT 'ERROR',
    "mensaje" TEXT NOT NULL,
    "stack_trace" TEXT,
    "modulo" VARCHAR(50),
    "endpoint" VARCHAR(255),
    "metodo_http" VARCHAR(10),
    "usuario_id" UUID,
    "ip_direccion" VARCHAR(45),
    "user_agent" TEXT,
    "request_body" JSONB,
    "response_body" JSONB,
    "contexto" JSONB,
    "resuelto" BOOLEAN NOT NULL DEFAULT false,
    "resuelto_por" UUID,
    "resuelto_en" TIMESTAMPTZ(6),
    "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "errores_aplicacion_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "garantias_neumaticos" (
    "id" UUID NOT NULL,
    "neumatico_id" UUID NOT NULL,
    "proveedor_id" UUID,
    "numero_garantia" VARCHAR(50),
    "fecha_inicio" DATE NOT NULL,
    "fecha_fin" DATE NOT NULL,
    "kilometraje_max" DECIMAL(12,2),
    "profundidad_min" DECIMAL(5,2),
    "condiciones" TEXT,
    "estado" "EstadoGarantia" NOT NULL DEFAULT 'VIGENTE',
    "fecha_reclamo" TIMESTAMPTZ(6),
    "motivo_reclamo" TEXT,
    "resolucion" TEXT,
    "monto_reembolso" DECIMAL(12,2),
    "creado_por" UUID,
    "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "actualizado_en" TIMESTAMPTZ(6),

    CONSTRAINT "garantias_neumaticos_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "especificaciones_desgaste" (
    "id" UUID NOT NULL,
    "modelo_id" UUID NOT NULL,
    "profundidad_nueva_mm" DECIMAL(5,2) NOT NULL,
    "profundidad_critica_mm" DECIMAL(5,2) NOT NULL,
    "profundidad_alerta_mm" DECIMAL(5,2) NOT NULL,
    "profundidad_minima_mm" DECIMAL(5,2) NOT NULL,
    "km_esperado_vida" DECIMAL(12,2),
    "horas_esperado_vida" DECIMAL(10,2),
    "tasa_desgaste_normal" DECIMAL(6,4),
    "activo" BOOLEAN NOT NULL DEFAULT true,
    "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "actualizado_en" TIMESTAMPTZ(6),

    CONSTRAINT "especificaciones_desgaste_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "mediciones_profundidad" (
    "id" UUID NOT NULL,
    "neumatico_id" UUID NOT NULL,
    "evento_id" UUID,
    "fecha_medicion" TIMESTAMPTZ(6) NOT NULL,
    "profundidad_int" DECIMAL(5,2) NOT NULL,
    "profundidad_cen" DECIMAL(5,2) NOT NULL,
    "profundidad_ext" DECIMAL(5,2) NOT NULL,
    "profundidad_prom" DECIMAL(5,2) NOT NULL,
    "desgaste_irregular" BOOLEAN NOT NULL DEFAULT false,
    "tipo_desgaste" VARCHAR(50),
    "observaciones" TEXT,
    "kilometraje" DECIMAL(12,2),
    "creado_por" UUID,
    "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "mediciones_profundidad_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "parametros_sistema" (
    "id" UUID NOT NULL,
    "clave" VARCHAR(100) NOT NULL,
    "valor" TEXT NOT NULL,
    "tipo_dato" VARCHAR(20) NOT NULL DEFAULT 'STRING',
    "categoria" VARCHAR(50),
    "descripcion" TEXT,
    "valor_default" TEXT,
    "es_sistema" BOOLEAN NOT NULL DEFAULT false,
    "editable" BOOLEAN NOT NULL DEFAULT true,
    "requiere_reinicio" BOOLEAN NOT NULL DEFAULT false,
    "actualizado_en" TIMESTAMP(3) NOT NULL,
    "actualizado_por" UUID,

    CONSTRAINT "parametros_sistema_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "parametros_inventario" (
    "id" UUID NOT NULL,
    "almacen_id" UUID,
    "modelo_id" UUID,
    "stock_minimo" INTEGER NOT NULL DEFAULT 0,
    "stock_maximo" INTEGER,
    "punto_reorden" INTEGER,
    "cantidad_reorden" INTEGER,
    "lead_time_dias" INTEGER,
    "activo" BOOLEAN NOT NULL DEFAULT true,
    "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "actualizado_en" TIMESTAMPTZ(6),

    CONSTRAINT "parametros_inventario_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "parametros_rendimiento_esperado_modelo" (
    "id" UUID NOT NULL,
    "modelo_id" UUID NOT NULL,
    "cpk_esperado" DECIMAL(8,4),
    "cpk_minimo_aceptable" DECIMAL(8,4),
    "km_esperado_vida1" DECIMAL(12,2),
    "km_esperado_vida2" DECIMAL(12,2),
    "km_esperado_vida3" DECIMAL(12,2),
    "desgaste_esperado_mm" DECIMAL(6,4),
    "condiciones_prueba" TEXT,
    "fuente_datos" VARCHAR(100),
    "fecha_calculo" DATE,
    "activo" BOOLEAN NOT NULL DEFAULT true,
    "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "actualizado_en" TIMESTAMPTZ(6),

    CONSTRAINT "parametros_rendimiento_esperado_modelo_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "tareas_programadas" (
    "id" UUID NOT NULL,
    "nombre" VARCHAR(100) NOT NULL,
    "tipo" "TipoTarea" NOT NULL,
    "cron_expresion" VARCHAR(50),
    "intervalo_minutos" INTEGER,
    "proxima_ejecucion" TIMESTAMPTZ(6),
    "ultima_ejecucion" TIMESTAMPTZ(6),
    "estado" "EstadoTarea" NOT NULL DEFAULT 'PENDIENTE',
    "parametros" JSONB,
    "resultado_ultimo" JSONB,
    "intentos" INTEGER NOT NULL DEFAULT 0,
    "max_reintentos" INTEGER NOT NULL DEFAULT 3,
    "activo" BOOLEAN NOT NULL DEFAULT true,
    "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "actualizado_en" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "tareas_programadas_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ejecuciones_tareas" (
    "id" BIGSERIAL NOT NULL,
    "tarea_id" UUID NOT NULL,
    "inicio" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "fin" TIMESTAMPTZ(6),
    "duracion_ms" INTEGER,
    "estado" "EstadoTarea" NOT NULL,
    "resultado" JSONB,
    "error_mensaje" TEXT,

    CONSTRAINT "ejecuciones_tareas_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "roles_nombre_key" ON "roles"("nombre");

-- CreateIndex
CREATE UNIQUE INDEX "permisos_codigo_key" ON "permisos"("codigo");

-- CreateIndex
CREATE INDEX "permisos_modulo_idx" ON "permisos"("modulo");

-- CreateIndex
CREATE UNIQUE INDEX "roles_permisos_rol_id_permiso_id_key" ON "roles_permisos"("rol_id", "permiso_id");

-- CreateIndex
CREATE INDEX "usuarios_roles_usuario_id_idx" ON "usuarios_roles"("usuario_id");

-- CreateIndex
CREATE UNIQUE INDEX "usuarios_roles_usuario_id_rol_id_key" ON "usuarios_roles"("usuario_id", "rol_id");

-- CreateIndex
CREATE INDEX "auditoria_roles_usuarios_usuario_id_idx" ON "auditoria_roles_usuarios"("usuario_id");

-- CreateIndex
CREATE INDEX "auditoria_roles_usuarios_creado_en_idx" ON "auditoria_roles_usuarios"("creado_en" DESC);

-- CreateIndex
CREATE UNIQUE INDEX "configuracion_auditoria_tabla_nombre_key" ON "configuracion_auditoria"("tabla_nombre");

-- CreateIndex
CREATE INDEX "bitacora_mantenimiento_vehiculo_id_fecha_realizada_idx" ON "bitacora_mantenimiento"("vehiculo_id", "fecha_realizada" DESC);

-- CreateIndex
CREATE INDEX "bitacora_mantenimiento_tipo_operacion_idx" ON "bitacora_mantenimiento"("tipo_operacion");

-- CreateIndex
CREATE INDEX "bitacora_operaciones_modulo_accion_idx" ON "bitacora_operaciones"("modulo", "accion");

-- CreateIndex
CREATE INDEX "bitacora_operaciones_entidad_id_idx" ON "bitacora_operaciones"("entidad_id");

-- CreateIndex
CREATE INDEX "bitacora_operaciones_usuario_id_idx" ON "bitacora_operaciones"("usuario_id");

-- CreateIndex
CREATE INDEX "bitacora_operaciones_creado_en_idx" ON "bitacora_operaciones"("creado_en" DESC);

-- CreateIndex
CREATE INDEX "bitacora_operaciones_neumaticos_neumatico_id_creado_en_idx" ON "bitacora_operaciones_neumaticos"("neumatico_id", "creado_en" DESC);

-- CreateIndex
CREATE INDEX "bitacora_operaciones_neumaticos_vehiculo_id_idx" ON "bitacora_operaciones_neumaticos"("vehiculo_id");

-- CreateIndex
CREATE INDEX "errores_aplicacion_severidad_creado_en_idx" ON "errores_aplicacion"("severidad", "creado_en" DESC);

-- CreateIndex
CREATE INDEX "errores_aplicacion_modulo_idx" ON "errores_aplicacion"("modulo");

-- CreateIndex
CREATE INDEX "errores_aplicacion_resuelto_idx" ON "errores_aplicacion"("resuelto");

-- CreateIndex
CREATE UNIQUE INDEX "garantias_neumaticos_numero_garantia_key" ON "garantias_neumaticos"("numero_garantia");

-- CreateIndex
CREATE INDEX "garantias_neumaticos_neumatico_id_idx" ON "garantias_neumaticos"("neumatico_id");

-- CreateIndex
CREATE INDEX "garantias_neumaticos_estado_idx" ON "garantias_neumaticos"("estado");

-- CreateIndex
CREATE INDEX "garantias_neumaticos_fecha_fin_idx" ON "garantias_neumaticos"("fecha_fin");

-- CreateIndex
CREATE UNIQUE INDEX "especificaciones_desgaste_modelo_id_key" ON "especificaciones_desgaste"("modelo_id");

-- CreateIndex
CREATE INDEX "mediciones_profundidad_neumatico_id_fecha_medicion_idx" ON "mediciones_profundidad"("neumatico_id", "fecha_medicion" DESC);

-- CreateIndex
CREATE UNIQUE INDEX "parametros_sistema_clave_key" ON "parametros_sistema"("clave");

-- CreateIndex
CREATE INDEX "parametros_sistema_categoria_idx" ON "parametros_sistema"("categoria");

-- CreateIndex
CREATE UNIQUE INDEX "parametros_inventario_almacen_id_modelo_id_key" ON "parametros_inventario"("almacen_id", "modelo_id");

-- CreateIndex
CREATE UNIQUE INDEX "parametros_rendimiento_esperado_modelo_modelo_id_key" ON "parametros_rendimiento_esperado_modelo"("modelo_id");

-- CreateIndex
CREATE INDEX "tareas_programadas_estado_proxima_ejecucion_idx" ON "tareas_programadas"("estado", "proxima_ejecucion");

-- CreateIndex
CREATE INDEX "ejecuciones_tareas_tarea_id_inicio_idx" ON "ejecuciones_tareas"("tarea_id", "inicio" DESC);

-- CreateIndex
CREATE INDEX "alertas_leida_severidad_creada_en_idx" ON "alertas"("leida", "severidad", "creada_en" DESC);

-- CreateIndex
CREATE INDEX "alertas_neumatico_id_idx" ON "alertas"("neumatico_id");

-- CreateIndex
CREATE UNIQUE INDEX "almacenes_codigo_key" ON "almacenes"("codigo");

-- CreateIndex
CREATE UNIQUE INDEX "configuraciones_eje_tipo_vehiculo_id_numero_eje_key" ON "configuraciones_eje"("tipo_vehiculo_id", "numero_eje");

-- CreateIndex
CREATE UNIQUE INDEX "fabricantes_neumatico_codigo_abreviado_key" ON "fabricantes_neumatico"("codigo_abreviado");

-- CreateIndex
CREATE INDEX "historial_estado_neumatico_neumatico_id_fecha_cambio_idx" ON "historial_estado_neumatico"("neumatico_id", "fecha_cambio" DESC);

-- CreateIndex
CREATE INDEX "modelos_neumatico_fabricante_id_idx" ON "modelos_neumatico"("fabricante_id");

-- CreateIndex
CREATE UNIQUE INDEX "modelos_neumatico_fabricante_id_nombre_modelo_medida_key" ON "modelos_neumatico"("fabricante_id", "nombre_modelo", "medida");

-- CreateIndex
CREATE UNIQUE INDEX "motivos_desecho_codigo_key" ON "motivos_desecho"("codigo");

-- CreateIndex
CREATE INDEX "neumaticos_estado_actual_ubicacion_vehiculo_id_idx" ON "neumaticos"("estado_actual", "ubicacion_vehiculo_id");

-- CreateIndex
CREATE INDEX "neumaticos_modelo_id_idx" ON "neumaticos"("modelo_id");

-- CreateIndex
CREATE INDEX "neumaticos_estado_actual_idx" ON "neumaticos"("estado_actual");

-- CreateIndex
CREATE INDEX "neumaticos_dot_idx" ON "neumaticos"("dot");

-- CreateIndex
CREATE INDEX "neumaticos_sensor_id_idx" ON "neumaticos"("sensor_id");

-- CreateIndex
CREATE INDEX "neumaticos_ubicacion_almacen_id_idx" ON "neumaticos"("ubicacion_almacen_id");

-- CreateIndex
CREATE INDEX "neumaticos_tasa_desgaste_actual_mm_km_idx" ON "neumaticos"("tasa_desgaste_actual_mm_km");

-- CreateIndex
CREATE INDEX "neumaticos_vida_util_restante_km_idx" ON "neumaticos"("vida_util_restante_km");

-- CreateIndex
CREATE INDEX "neumaticos_proxima_inspeccion_fecha_idx" ON "neumaticos"("proxima_inspeccion_fecha");

-- CreateIndex
CREATE UNIQUE INDEX "posiciones_neumatico_configuracion_eje_id_codigo_posicion_key" ON "posiciones_neumatico"("configuracion_eje_id", "codigo_posicion");

-- CreateIndex
CREATE UNIQUE INDEX "vehiculos_vin_key" ON "vehiculos"("vin");

-- CreateIndex
CREATE UNIQUE INDEX "vehiculos_numero_economico_key" ON "vehiculos"("numero_economico");

-- CreateIndex
CREATE INDEX "vehiculos_tipo_vehiculo_id_idx" ON "vehiculos"("tipo_vehiculo_id");

-- CreateIndex
CREATE INDEX "vehiculos_placa_idx" ON "vehiculos"("placa");

-- CreateIndex
CREATE INDEX "vehiculos_numero_economico_idx" ON "vehiculos"("numero_economico");

-- AddForeignKey
ALTER TABLE "neumaticos" ADD CONSTRAINT "neumaticos_proveedor_compra_id_fkey" FOREIGN KEY ("proveedor_compra_id") REFERENCES "proveedores"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "neumaticos" ADD CONSTRAINT "neumaticos_motivo_desecho_id_fkey" FOREIGN KEY ("motivo_desecho_id") REFERENCES "motivos_desecho"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "roles_permisos" ADD CONSTRAINT "roles_permisos_rol_id_fkey" FOREIGN KEY ("rol_id") REFERENCES "roles"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "roles_permisos" ADD CONSTRAINT "roles_permisos_permiso_id_fkey" FOREIGN KEY ("permiso_id") REFERENCES "permisos"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "usuarios_roles" ADD CONSTRAINT "usuarios_roles_rol_id_fkey" FOREIGN KEY ("rol_id") REFERENCES "roles"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "bitacora_mantenimiento" ADD CONSTRAINT "bitacora_mantenimiento_proveedor_id_fkey" FOREIGN KEY ("proveedor_id") REFERENCES "proveedores"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "garantias_neumaticos" ADD CONSTRAINT "garantias_neumaticos_neumatico_id_fkey" FOREIGN KEY ("neumatico_id") REFERENCES "neumaticos"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "garantias_neumaticos" ADD CONSTRAINT "garantias_neumaticos_proveedor_id_fkey" FOREIGN KEY ("proveedor_id") REFERENCES "proveedores"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "especificaciones_desgaste" ADD CONSTRAINT "especificaciones_desgaste_modelo_id_fkey" FOREIGN KEY ("modelo_id") REFERENCES "modelos_neumatico"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "mediciones_profundidad" ADD CONSTRAINT "mediciones_profundidad_neumatico_id_fkey" FOREIGN KEY ("neumatico_id") REFERENCES "neumaticos"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "parametros_inventario" ADD CONSTRAINT "parametros_inventario_almacen_id_fkey" FOREIGN KEY ("almacen_id") REFERENCES "almacenes"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "parametros_inventario" ADD CONSTRAINT "parametros_inventario_modelo_id_fkey" FOREIGN KEY ("modelo_id") REFERENCES "modelos_neumatico"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "parametros_rendimiento_esperado_modelo" ADD CONSTRAINT "parametros_rendimiento_esperado_modelo_modelo_id_fkey" FOREIGN KEY ("modelo_id") REFERENCES "modelos_neumatico"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ejecuciones_tareas" ADD CONSTRAINT "ejecuciones_tareas_tarea_id_fkey" FOREIGN KEY ("tarea_id") REFERENCES "tareas_programadas"("id") ON DELETE CASCADE ON UPDATE CASCADE;
