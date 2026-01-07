-- ============================================================
-- PRE-MIGRATION SCRIPT: Ejecutar en Supabase SQL Editor ANTES de prisma db push
-- Esto agrega las columnas faltantes y las pobla con valores basados en datos existentes
-- ============================================================

-- 1. ALMACENES: Agregar columna codigo con valor generado
ALTER TABLE "almacenes" ADD COLUMN IF NOT EXISTS "codigo" VARCHAR(20);
UPDATE "almacenes" SET "codigo" = 'ALM-' || SUBSTRING(id::text, 1, 6) WHERE "codigo" IS NULL;
ALTER TABLE "almacenes" ALTER COLUMN "codigo" SET NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS "almacenes_codigo_key" ON "almacenes"("codigo");

ALTER TABLE "almacenes" ADD COLUMN IF NOT EXISTS "direccion" TEXT;
ALTER TABLE "almacenes" ALTER COLUMN "nombre" TYPE VARCHAR(150);
ALTER TABLE "almacenes" ALTER COLUMN "tipo" TYPE VARCHAR(50);
ALTER TABLE "almacenes" ALTER COLUMN "tipo" DROP DEFAULT;

-- 2. CONFIGURACIONES_EJE: Agregar columnas con valores derivados
ALTER TABLE "configuraciones_eje" ADD COLUMN IF NOT EXISTS "nombre_eje" VARCHAR(50);
ALTER TABLE "configuraciones_eje" ADD COLUMN IF NOT EXISTS "numero_posiciones" INTEGER;
ALTER TABLE "configuraciones_eje" ADD COLUMN IF NOT EXISTS "posiciones_duales" BOOLEAN DEFAULT false;
ALTER TABLE "configuraciones_eje" ADD COLUMN IF NOT EXISTS "neumaticos_por_posicion" INTEGER DEFAULT 1;
ALTER TABLE "configuraciones_eje" ADD COLUMN IF NOT EXISTS "creado_en" TIMESTAMPTZ(6) DEFAULT now();
ALTER TABLE "configuraciones_eje" ADD COLUMN IF NOT EXISTS "creado_por" UUID;
ALTER TABLE "configuraciones_eje" ADD COLUMN IF NOT EXISTS "actualizado_en" TIMESTAMPTZ(6);
ALTER TABLE "configuraciones_eje" ADD COLUMN IF NOT EXISTS "actualizado_por" UUID;

UPDATE "configuraciones_eje" SET 
  "nombre_eje" = CASE 
    WHEN tipo_eje = 'DIRECCION' THEN 'Eje Direccional ' || numero_eje
    WHEN tipo_eje = 'TRACCION' THEN 'Eje Tracción ' || numero_eje
    WHEN tipo_eje = 'ARRASTRE' THEN 'Eje Arrastre ' || numero_eje
    ELSE 'Eje ' || numero_eje
  END,
  "numero_posiciones" = COALESCE("posiciones_neumatico", 2)
WHERE "nombre_eje" IS NULL OR "numero_posiciones" IS NULL;

ALTER TABLE "configuraciones_eje" ALTER COLUMN "nombre_eje" SET NOT NULL;
ALTER TABLE "configuraciones_eje" ALTER COLUMN "numero_posiciones" SET NOT NULL;
ALTER TABLE "configuraciones_eje" ALTER COLUMN "neumaticos_por_posicion" SET NOT NULL;
ALTER TABLE "configuraciones_eje" ALTER COLUMN "neumaticos_por_posicion" DROP DEFAULT;
ALTER TABLE "configuraciones_eje" ALTER COLUMN "posiciones_duales" SET NOT NULL;
ALTER TABLE "configuraciones_eje" ALTER COLUMN "posiciones_duales" DROP DEFAULT;

-- Eliminar duplicados antes del unique constraint
DELETE FROM "configuraciones_eje" a USING "configuraciones_eje" b 
WHERE a.ctid < b.ctid AND a.tipo_vehiculo_id = b.tipo_vehiculo_id AND a.numero_eje = b.numero_eje;

CREATE UNIQUE INDEX IF NOT EXISTS "configuraciones_eje_tipo_vehiculo_id_numero_eje_key" 
ON "configuraciones_eje"("tipo_vehiculo_id", "numero_eje");

-- Eliminar columna vieja
ALTER TABLE "configuraciones_eje" DROP COLUMN IF EXISTS "posiciones_neumatico";

-- 3. MOTIVOS_DESECHO: Agregar columna codigo
ALTER TABLE "motivos_desecho" ADD COLUMN IF NOT EXISTS "codigo" VARCHAR(20);
UPDATE "motivos_desecho" SET "codigo" = UPPER(SUBSTRING(REPLACE(nombre, ' ', '_'), 1, 15)) || '-' || SUBSTRING(id::text, 1, 3) WHERE "codigo" IS NULL;
ALTER TABLE "motivos_desecho" ALTER COLUMN "codigo" SET NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS "motivos_desecho_codigo_key" ON "motivos_desecho"("codigo");

-- Eliminar unique de nombre
DROP INDEX IF EXISTS "motivos_desecho_nombre_key";

-- 4. POSICIONES_NEUMATICO: Agregar nuevas columnas
ALTER TABLE "posiciones_neumatico" ADD COLUMN IF NOT EXISTS "codigo_posicion" VARCHAR(10);
ALTER TABLE "posiciones_neumatico" ADD COLUMN IF NOT EXISTS "lado" "LadoVehiculoEnum";
ALTER TABLE "posiciones_neumatico" ADD COLUMN IF NOT EXISTS "posicion_relativa" INTEGER;
ALTER TABLE "posiciones_neumatico" ADD COLUMN IF NOT EXISTS "etiqueta_posicion" VARCHAR(50);
ALTER TABLE "posiciones_neumatico" ADD COLUMN IF NOT EXISTS "es_interna" BOOLEAN DEFAULT false;
ALTER TABLE "posiciones_neumatico" ADD COLUMN IF NOT EXISTS "es_direccion" BOOLEAN DEFAULT false;
ALTER TABLE "posiciones_neumatico" ADD COLUMN IF NOT EXISTS "es_traccion" BOOLEAN DEFAULT false;
ALTER TABLE "posiciones_neumatico" ADD COLUMN IF NOT EXISTS "requiere_neumatico_especifico" BOOLEAN DEFAULT false;
ALTER TABLE "posiciones_neumatico" ADD COLUMN IF NOT EXISTS "creado_en" TIMESTAMPTZ(6) DEFAULT now();
ALTER TABLE "posiciones_neumatico" ADD COLUMN IF NOT EXISTS "creado_por" UUID;
ALTER TABLE "posiciones_neumatico" ADD COLUMN IF NOT EXISTS "actualizado_en" TIMESTAMPTZ(6);
ALTER TABLE "posiciones_neumatico" ADD COLUMN IF NOT EXISTS "actualizado_por" UUID;

UPDATE "posiciones_neumatico" SET 
  "codigo_posicion" = CASE 
    WHEN lado_vehiculo = 'IZQUIERDO' THEN numero_posicion || 'I'
    WHEN lado_vehiculo = 'DERECHO' THEN numero_posicion || 'D'
    WHEN lado_vehiculo = 'CENTRAL' THEN numero_posicion || 'C'
    ELSE numero_posicion || 'X'
  END,
  "lado" = lado_vehiculo,
  "posicion_relativa" = numero_posicion
WHERE "codigo_posicion" IS NULL OR "lado" IS NULL OR "posicion_relativa" IS NULL;

ALTER TABLE "posiciones_neumatico" ALTER COLUMN "codigo_posicion" SET NOT NULL;
ALTER TABLE "posiciones_neumatico" ALTER COLUMN "lado" SET NOT NULL;
ALTER TABLE "posiciones_neumatico" ALTER COLUMN "posicion_relativa" SET NOT NULL;
ALTER TABLE "posiciones_neumatico" ALTER COLUMN "es_interna" SET NOT NULL;
ALTER TABLE "posiciones_neumatico" ALTER COLUMN "es_direccion" SET NOT NULL;
ALTER TABLE "posiciones_neumatico" ALTER COLUMN "es_traccion" SET NOT NULL;
ALTER TABLE "posiciones_neumatico" ALTER COLUMN "requiere_neumatico_especifico" SET NOT NULL;

-- Eliminar duplicados y crear unique constraint
DELETE FROM "posiciones_neumatico" a USING "posiciones_neumatico" b
WHERE a.ctid < b.ctid AND a.configuracion_eje_id = b.configuracion_eje_id AND a.codigo_posicion = b.codigo_posicion;

CREATE UNIQUE INDEX IF NOT EXISTS "posiciones_neumatico_configuracion_eje_id_codigo_posicion_key" 
ON "posiciones_neumatico"("configuracion_eje_id", "codigo_posicion");

-- Eliminar columnas viejas
ALTER TABLE "posiciones_neumatico" DROP COLUMN IF EXISTS "lado_vehiculo";
ALTER TABLE "posiciones_neumatico" DROP COLUMN IF EXISTS "numero_posicion";

-- 5. VEHICULOS: Agregar nuevas columnas
ALTER TABLE "vehiculos" ADD COLUMN IF NOT EXISTS "numero_economico" VARCHAR(50);
ALTER TABLE "vehiculos" ADD COLUMN IF NOT EXISTS "vin" VARCHAR(17);
ALTER TABLE "vehiculos" ADD COLUMN IF NOT EXISTS "modelo_vehiculo" VARCHAR(50);
ALTER TABLE "vehiculos" ADD COLUMN IF NOT EXISTS "anio_fabricacion" INTEGER;
ALTER TABLE "vehiculos" ADD COLUMN IF NOT EXISTS "fecha_alta" DATE DEFAULT CURRENT_DATE;
ALTER TABLE "vehiculos" ADD COLUMN IF NOT EXISTS "fecha_baja" DATE;
ALTER TABLE "vehiculos" ADD COLUMN IF NOT EXISTS "odometro_actual" INTEGER DEFAULT 0;
ALTER TABLE "vehiculos" ADD COLUMN IF NOT EXISTS "fecha_ultimo_odometro" TIMESTAMPTZ(6);
ALTER TABLE "vehiculos" ADD COLUMN IF NOT EXISTS "peso_carga_maxima_diseno_ton" DECIMAL(5,2);
ALTER TABLE "vehiculos" ADD COLUMN IF NOT EXISTS "ubicacion_actual" VARCHAR(100);
ALTER TABLE "vehiculos" ADD COLUMN IF NOT EXISTS "notas" TEXT;

-- Poblar numero_economico desde codigo_interno o placa
UPDATE "vehiculos" SET 
  "numero_economico" = COALESCE(codigo_interno, placa, 'VEH-' || SUBSTRING(id::text, 1, 8)),
  "modelo_vehiculo" = "modelo",
  "anio_fabricacion" = "anio",
  "odometro_actual" = COALESCE(CAST("contador_actual" AS INTEGER), 0)
WHERE "numero_economico" IS NULL;

ALTER TABLE "vehiculos" ALTER COLUMN "numero_economico" SET NOT NULL;
ALTER TABLE "vehiculos" ALTER COLUMN "fecha_alta" SET NOT NULL;

-- Crear unique constraints
CREATE UNIQUE INDEX IF NOT EXISTS "vehiculos_vin_key" ON "vehiculos"("vin");
CREATE UNIQUE INDEX IF NOT EXISTS "vehiculos_numero_economico_key" ON "vehiculos"("numero_economico");

-- Eliminar columnas viejas (DESPUÉS de copiar datos)
ALTER TABLE "vehiculos" DROP COLUMN IF EXISTS "codigo_interno";
ALTER TABLE "vehiculos" DROP COLUMN IF EXISTS "modelo";
ALTER TABLE "vehiculos" DROP COLUMN IF EXISTS "anio";
ALTER TABLE "vehiculos" DROP COLUMN IF EXISTS "numero_serie";
ALTER TABLE "vehiculos" DROP COLUMN IF EXISTS "contador_actual";

-- Ajustar placa a VARCHAR(15)
-- (Solo si las placas existentes son <= 15 caracteres)
UPDATE "vehiculos" SET placa = SUBSTRING(placa, 1, 15) WHERE LENGTH(placa) > 15;
ALTER TABLE "vehiculos" ALTER COLUMN "placa" TYPE VARCHAR(15);

-- Drop old unique
DROP INDEX IF EXISTS "vehiculos_codigo_interno_key";

-- 6. MODELOS_NEUMATICO: Renombrar columnas y agregar nuevas
ALTER TABLE "modelos_neumatico" ADD COLUMN IF NOT EXISTS "nombre_modelo" VARCHAR(100);
ALTER TABLE "modelos_neumatico" ADD COLUMN IF NOT EXISTS "profundidad_original_mm" DECIMAL(5,2);
ALTER TABLE "modelos_neumatico" ADD COLUMN IF NOT EXISTS "indice_carga" VARCHAR(5);
ALTER TABLE "modelos_neumatico" ADD COLUMN IF NOT EXISTS "indice_velocidad" VARCHAR(2);
ALTER TABLE "modelos_neumatico" ADD COLUMN IF NOT EXISTS "presion_recomendada_psi" DECIMAL(5,2);
ALTER TABLE "modelos_neumatico" ADD COLUMN IF NOT EXISTS "permite_reencauche" BOOLEAN DEFAULT false;
ALTER TABLE "modelos_neumatico" ADD COLUMN IF NOT EXISTS "patron_dibujo" VARCHAR(50);
ALTER TABLE "modelos_neumatico" ADD COLUMN IF NOT EXISTS "tipo_servicio" VARCHAR(50);
ALTER TABLE "modelos_neumatico" ADD COLUMN IF NOT EXISTS "posicion_uso_recomendada" "TipoEjeEnum";
ALTER TABLE "modelos_neumatico" ADD COLUMN IF NOT EXISTS "diseno_predominante_para_eje" "TipoEjeEnum";
ALTER TABLE "modelos_neumatico" ADD COLUMN IF NOT EXISTS "vida_util_teorica_km" INTEGER;
ALTER TABLE "modelos_neumatico" ADD COLUMN IF NOT EXISTS "profundidad_minima_retiro_mm" DECIMAL(5,2) DEFAULT 1.6;
ALTER TABLE "modelos_neumatico" ADD COLUMN IF NOT EXISTS "tasa_desgaste_esperada_mm_km" DECIMAL(10,8);
ALTER TABLE "modelos_neumatico" ADD COLUMN IF NOT EXISTS "frecuencia_inspeccion_km" INTEGER DEFAULT 5000;
ALTER TABLE "modelos_neumatico" ADD COLUMN IF NOT EXISTS "max_vidas_utiles" INTEGER DEFAULT 5;
ALTER TABLE "modelos_neumatico" ADD COLUMN IF NOT EXISTS "porcentaje_desgaste_por_vida" DECIMAL(5,2) DEFAULT 10.0;
ALTER TABLE "modelos_neumatico" ADD COLUMN IF NOT EXISTS "activo" BOOLEAN DEFAULT true;
ALTER TABLE "modelos_neumatico" ADD COLUMN IF NOT EXISTS "creado_en" TIMESTAMPTZ(6) DEFAULT now();
ALTER TABLE "modelos_neumatico" ADD COLUMN IF NOT EXISTS "creado_por" UUID;
ALTER TABLE "modelos_neumatico" ADD COLUMN IF NOT EXISTS "actualizado_en" TIMESTAMPTZ(6);
ALTER TABLE "modelos_neumatico" ADD COLUMN IF NOT EXISTS "actualizado_por" UUID;

UPDATE "modelos_neumatico" SET 
  "nombre_modelo" = "nombre",
  "profundidad_original_mm" = "profundidad_inicial_mm"
WHERE "nombre_modelo" IS NULL OR "profundidad_original_mm" IS NULL;

ALTER TABLE "modelos_neumatico" ALTER COLUMN "nombre_modelo" SET NOT NULL;
ALTER TABLE "modelos_neumatico" ALTER COLUMN "profundidad_original_mm" SET NOT NULL;
ALTER TABLE "modelos_neumatico" ALTER COLUMN "permite_reencauche" SET NOT NULL;
ALTER TABLE "modelos_neumatico" ALTER COLUMN "profundidad_minima_retiro_mm" SET NOT NULL;
ALTER TABLE "modelos_neumatico" ALTER COLUMN "activo" SET NOT NULL;

-- Eliminar duplicados antes de unique constraint
DELETE FROM "modelos_neumatico" a USING "modelos_neumatico" b
WHERE a.ctid < b.ctid AND a.fabricante_id = b.fabricante_id AND a.nombre_modelo = b.nombre_modelo AND a.medida = b.medida;

CREATE UNIQUE INDEX IF NOT EXISTS "modelos_neumatico_fabricante_id_nombre_modelo_medida_key" 
ON "modelos_neumatico"("fabricante_id", "nombre_modelo", "medida");

-- Drop old columns
ALTER TABLE "modelos_neumatico" DROP COLUMN IF EXISTS "nombre";
ALTER TABLE "modelos_neumatico" DROP COLUMN IF EXISTS "profundidad_inicial_mm";

-- Ajustar medida a VARCHAR(20)
UPDATE "modelos_neumatico" SET medida = SUBSTRING(medida, 1, 20) WHERE LENGTH(medida) > 20;
ALTER TABLE "modelos_neumatico" ALTER COLUMN "medida" TYPE VARCHAR(20);

-- 7. NEUMATICOS: Agregar nuevas columnas
ALTER TABLE "neumaticos" ADD COLUMN IF NOT EXISTS "profundidad_remanente_actual_mm" DECIMAL(5,2);
ALTER TABLE "neumaticos" ADD COLUMN IF NOT EXISTS "fecha_fabricacion" DATE;
ALTER TABLE "neumaticos" ADD COLUMN IF NOT EXISTS "moneda_compra" VARCHAR(3) DEFAULT 'PEN';
ALTER TABLE "neumaticos" ADD COLUMN IF NOT EXISTS "proveedor_compra_id" UUID;
ALTER TABLE "neumaticos" ADD COLUMN IF NOT EXISTS "fecha_ultimo_evento" TIMESTAMPTZ(6);
ALTER TABLE "neumaticos" ADD COLUMN IF NOT EXISTS "fecha_ultima_medicion_profundidad" TIMESTAMPTZ(6);
ALTER TABLE "neumaticos" ADD COLUMN IF NOT EXISTS "fecha_ultimo_reencauche" DATE;
ALTER TABLE "neumaticos" ADD COLUMN IF NOT EXISTS "kilometraje_vida_actual" INTEGER DEFAULT 0;
ALTER TABLE "neumaticos" ADD COLUMN IF NOT EXISTS "fecha_inicio_vida_actual" DATE;
ALTER TABLE "neumaticos" ADD COLUMN IF NOT EXISTS "odometro_instalacion_vida_actual" INTEGER;
ALTER TABLE "neumaticos" ADD COLUMN IF NOT EXISTS "profundidad_inicio_vida_actual_mm" DECIMAL(5,2);
ALTER TABLE "neumaticos" ADD COLUMN IF NOT EXISTS "tasa_desgaste_actual_mm_km" DECIMAL(10,8);
ALTER TABLE "neumaticos" ADD COLUMN IF NOT EXISTS "vida_util_restante_km" INTEGER;
ALTER TABLE "neumaticos" ADD COLUMN IF NOT EXISTS "proxima_inspeccion_fecha" DATE;
ALTER TABLE "neumaticos" ADD COLUMN IF NOT EXISTS "proxima_inspeccion_km" INTEGER;
ALTER TABLE "neumaticos" ADD COLUMN IF NOT EXISTS "fecha_desecho" DATE;
ALTER TABLE "neumaticos" ADD COLUMN IF NOT EXISTS "motivo_desecho_id" UUID;
ALTER TABLE "neumaticos" ADD COLUMN IF NOT EXISTS "sensor_id" VARCHAR(100);

-- Poblar profundidad_remanente desde profundidad_actual o inicial
UPDATE "neumaticos" SET 
  "profundidad_remanente_actual_mm" = COALESCE("profundidad_actual_mm", "profundidad_inicial_mm", 12.0)
WHERE "profundidad_remanente_actual_mm" IS NULL;

-- Poblar fecha_compra con default si es NULL
UPDATE "neumaticos" SET "fecha_compra" = CURRENT_DATE WHERE "fecha_compra" IS NULL;

ALTER TABLE "neumaticos" ALTER COLUMN "profundidad_remanente_actual_mm" SET NOT NULL;
ALTER TABLE "neumaticos" ALTER COLUMN "fecha_compra" SET NOT NULL;
ALTER TABLE "neumaticos" ALTER COLUMN "numero_serie" TYPE VARCHAR(100);
ALTER TABLE "neumaticos" ALTER COLUMN "numero_serie" DROP NOT NULL;
ALTER TABLE "neumaticos" ALTER COLUMN "dot" TYPE TEXT;
ALTER TABLE "neumaticos" ALTER COLUMN "profundidad_inicial_mm" DROP NOT NULL;
ALTER TABLE "neumaticos" ALTER COLUMN "kilometraje_acumulado" TYPE INTEGER USING kilometraje_acumulado::INTEGER;

-- Drop old columns
ALTER TABLE "neumaticos" DROP COLUMN IF EXISTS "marca_id";
ALTER TABLE "neumaticos" DROP COLUMN IF EXISTS "profundidad_actual_mm";

-- Drop old unique
DROP INDEX IF EXISTS "neumaticos_numero_serie_key";

-- 8. FABRICANTES_NEUMATICO: Agregar nuevas columnas
ALTER TABLE "fabricantes_neumatico" ADD COLUMN IF NOT EXISTS "codigo_abreviado" VARCHAR(10);
ALTER TABLE "fabricantes_neumatico" ADD COLUMN IF NOT EXISTS "pais_origen" VARCHAR(50);
ALTER TABLE "fabricantes_neumatico" ADD COLUMN IF NOT EXISTS "sitio_web" VARCHAR(255);
ALTER TABLE "fabricantes_neumatico" ADD COLUMN IF NOT EXISTS "activo" BOOLEAN DEFAULT true;
ALTER TABLE "fabricantes_neumatico" ADD COLUMN IF NOT EXISTS "creado_en" TIMESTAMPTZ(6) DEFAULT now();
ALTER TABLE "fabricantes_neumatico" ADD COLUMN IF NOT EXISTS "creado_por" UUID;
ALTER TABLE "fabricantes_neumatico" ADD COLUMN IF NOT EXISTS "actualizado_en" TIMESTAMPTZ(6);
ALTER TABLE "fabricantes_neumatico" ADD COLUMN IF NOT EXISTS "actualizado_por" UUID;

ALTER TABLE "fabricantes_neumatico" ALTER COLUMN "activo" SET NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS "fabricantes_neumatico_codigo_abreviado_key" ON "fabricantes_neumatico"("codigo_abreviado");
DROP INDEX IF EXISTS "fabricantes_neumatico_nombre_key";

-- 9. PROVEEDORES: Agregar nuevas columnas
ALTER TABLE "proveedores" ADD COLUMN IF NOT EXISTS "contacto_principal" TEXT;
ALTER TABLE "proveedores" ADD COLUMN IF NOT EXISTS "telefono" VARCHAR(50);
ALTER TABLE "proveedores" ADD COLUMN IF NOT EXISTS "email" VARCHAR(100);
ALTER TABLE "proveedores" ADD COLUMN IF NOT EXISTS "direccion" TEXT;

-- ============================================================
-- FIN DE PRE-MIGRATION
-- Ahora puedes ejecutar: npx prisma db push
-- ============================================================
