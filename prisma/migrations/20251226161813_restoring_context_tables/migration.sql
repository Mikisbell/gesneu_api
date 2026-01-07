-- AlterTable
ALTER TABLE "vehiculos" ADD COLUMN     "ruta_id" UUID;

-- CreateTable
CREATE TABLE "tipos_ruta" (
    "id" UUID NOT NULL,
    "nombre" VARCHAR(50) NOT NULL,
    "descripcion" TEXT,
    "factor_desgaste" DECIMAL(3,2) NOT NULL DEFAULT 1.00,
    "distancia_trocha_pct" DECIMAL(5,2),
    "distancia_asfalto_pct" DECIMAL(5,2),
    "activo" BOOLEAN NOT NULL DEFAULT true,

    CONSTRAINT "tipos_ruta_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "rutas" (
    "id" UUID NOT NULL,
    "nombre" VARCHAR(100) NOT NULL,
    "origen" VARCHAR(100),
    "destino" VARCHAR(100),
    "distancia_km" DECIMAL(10,2) NOT NULL DEFAULT 0,
    "tipo_ruta_id" UUID NOT NULL,
    "activo" BOOLEAN NOT NULL DEFAULT true,
    "creado_en" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "rutas_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "modelos_posiciones_permitidas" (
    "id" UUID NOT NULL,
    "modelo_id" UUID NOT NULL,
    "tipo_eje" "TipoEjeEnum" NOT NULL,
    "es_preferida" BOOLEAN NOT NULL DEFAULT false,

    CONSTRAINT "modelos_posiciones_permitidas_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "tipos_ruta_nombre_key" ON "tipos_ruta"("nombre");

-- CreateIndex
CREATE UNIQUE INDEX "modelos_posiciones_permitidas_modelo_id_tipo_eje_key" ON "modelos_posiciones_permitidas"("modelo_id", "tipo_eje");

-- AddForeignKey
ALTER TABLE "vehiculos" ADD CONSTRAINT "vehiculos_ruta_id_fkey" FOREIGN KEY ("ruta_id") REFERENCES "rutas"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "rutas" ADD CONSTRAINT "rutas_tipo_ruta_id_fkey" FOREIGN KEY ("tipo_ruta_id") REFERENCES "tipos_ruta"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "modelos_posiciones_permitidas" ADD CONSTRAINT "modelos_posiciones_permitidas_modelo_id_fkey" FOREIGN KEY ("modelo_id") REFERENCES "modelos_neumatico"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
