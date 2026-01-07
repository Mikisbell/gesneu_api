-- AlterTable
ALTER TABLE "neumaticos" ADD COLUMN     "version" INTEGER NOT NULL DEFAULT 0;

-- AlterTable
ALTER TABLE "vehiculos" ADD COLUMN     "version" INTEGER NOT NULL DEFAULT 0;

-- CreateIndex
CREATE INDEX "lecturas_presion_neumatico_id_fecha_lectura_idx" ON "lecturas_presion"("neumatico_id", "fecha_lectura" DESC);
