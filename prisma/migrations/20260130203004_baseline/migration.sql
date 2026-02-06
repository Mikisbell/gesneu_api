/*
  Warnings:

  - A unique constraint covering the columns `[empresa_id,numero_serie]` on the table `neumaticos` will be added. If there are existing duplicate values, this will fail.
  - Added the required column `actualizado_en` to the `webhook_configs` table without a default value. This is not possible if the table is not empty.

*/
-- AlterEnum
-- This migration adds more than one value to an enum.
-- With PostgreSQL versions 11 and earlier, this is not possible
-- in a single migration. This can be worked around by creating
-- multiple migrations, each migration adding only one value to
-- the enum.


ALTER TYPE "EstadoNeumaticoEnum" ADD VALUE 'NUEVO';
ALTER TYPE "EstadoNeumaticoEnum" ADD VALUE 'EN_USO';
ALTER TYPE "EstadoNeumaticoEnum" ADD VALUE 'EN_ALMACEN';
ALTER TYPE "EstadoNeumaticoEnum" ADD VALUE 'PARA_REPARACION';
ALTER TYPE "EstadoNeumaticoEnum" ADD VALUE 'REPARADO';
ALTER TYPE "EstadoNeumaticoEnum" ADD VALUE 'PARA_REENCAUCHE';
ALTER TYPE "EstadoNeumaticoEnum" ADD VALUE 'REENCAUCHADO';
ALTER TYPE "EstadoNeumaticoEnum" ADD VALUE 'PARA_DESECHO';
ALTER TYPE "EstadoNeumaticoEnum" ADD VALUE 'VENDIDO';
ALTER TYPE "EstadoNeumaticoEnum" ADD VALUE 'EN_TRANSITO';

-- AlterEnum
ALTER TYPE "RolEnum" ADD VALUE 'SUPERADMIN';

-- AlterEnum
-- This migration adds more than one value to an enum.
-- With PostgreSQL versions 11 and earlier, this is not possible
-- in a single migration. This can be worked around by creating
-- multiple migrations, each migration adding only one value to
-- the enum.


ALTER TYPE "TipoEventoNeumaticoEnum" ADD VALUE 'ASIGNACION_A_ALMACEN';
ALTER TYPE "TipoEventoNeumaticoEnum" ADD VALUE 'VENTA';
ALTER TYPE "TipoEventoNeumaticoEnum" ADD VALUE 'MOVIMIENTO_ENTRE_ALMACENES';
ALTER TYPE "TipoEventoNeumaticoEnum" ADD VALUE 'BAJA_POR_ROBO_EXTRAVIO';
ALTER TYPE "TipoEventoNeumaticoEnum" ADD VALUE 'TRANSFERENCIA_UBICACION';
ALTER TYPE "TipoEventoNeumaticoEnum" ADD VALUE 'DESMONTE_POR_FIN_VIDA_UTIL';
ALTER TYPE "TipoEventoNeumaticoEnum" ADD VALUE 'DESMONTE_TEMPORAL';

-- AlterEnum
ALTER TYPE "TipoProveedorEnum" ADD VALUE 'DISTRIBUIDOR';

-- DropIndex
DROP INDEX "neumaticos_numero_serie_key";

-- AlterTable
ALTER TABLE "webhook_configs" ADD COLUMN     "actualizado_en" TIMESTAMP(3) NOT NULL,
ADD COLUMN     "empresa_id" UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000';

-- CreateIndex
CREATE UNIQUE INDEX "neumaticos_empresa_id_numero_serie_key" ON "neumaticos"("empresa_id", "numero_serie");

-- AddForeignKey
ALTER TABLE "webhook_configs" ADD CONSTRAINT "webhook_configs_empresa_id_fkey" FOREIGN KEY ("empresa_id") REFERENCES "empresas"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
