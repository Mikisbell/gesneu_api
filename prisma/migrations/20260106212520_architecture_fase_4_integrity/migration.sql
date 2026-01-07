/*
  Warnings:

  - You are about to drop the column `actualizado_en` on the `vehiculos` table. All the data in the column will be lost.
  - You are about to drop the column `actualizado_por` on the `vehiculos` table. All the data in the column will be lost.
  - You are about to drop the column `creado_en` on the `vehiculos` table. All the data in the column will be lost.
  - You are about to drop the column `creado_por` on the `vehiculos` table. All the data in the column will be lost.
  - You are about to drop the column `eliminado_en` on the `vehiculos` table. All the data in the column will be lost.
  - You are about to drop the column `eliminado_por` on the `vehiculos` table. All the data in the column will be lost.
  - Added the required column `empresa_id` to the `almacenes` table without a default value. This is not possible if the table is not empty.
  - Added the required column `empresa_id` to the `neumaticos` table without a default value. This is not possible if the table is not empty.
  - Added the required column `empresa_id` to the `proveedores` table without a default value. This is not possible if the table is not empty.
  - Added the required column `empresa_id` to the `usuarios` table without a default value. This is not possible if the table is not empty.
  - Added the required column `empresa_id` to the `vehiculos` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "almacenes" ADD COLUMN     "empresa_id" UUID NOT NULL;

-- AlterTable
ALTER TABLE "neumaticos" ADD COLUMN     "empresa_id" UUID NOT NULL;

-- AlterTable
ALTER TABLE "proveedores" ADD COLUMN     "empresa_id" UUID NOT NULL;

-- AlterTable
ALTER TABLE "usuarios" ADD COLUMN     "empresa_id" UUID NOT NULL;

-- AlterTable
ALTER TABLE "vehiculos" DROP COLUMN "actualizado_en",
DROP COLUMN "actualizado_por",
DROP COLUMN "creado_en",
DROP COLUMN "creado_por",
DROP COLUMN "eliminado_en",
DROP COLUMN "eliminado_por",
ADD COLUMN     "empresa_id" UUID NOT NULL;

-- CreateTable
CREATE TABLE "empresas" (
    "id" UUID NOT NULL,
    "nombre" VARCHAR(100) NOT NULL,
    "ruc" VARCHAR(20) NOT NULL,
    "direccion" TEXT,
    "activo" BOOLEAN NOT NULL DEFAULT true,
    "creado_en" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "empresas_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "empresas_ruc_key" ON "empresas"("ruc");

-- CreateIndex
CREATE INDEX "neumaticos_empresa_id_idx" ON "neumaticos"("empresa_id");

-- AddForeignKey
ALTER TABLE "usuarios" ADD CONSTRAINT "usuarios_empresa_id_fkey" FOREIGN KEY ("empresa_id") REFERENCES "empresas"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "vehiculos" ADD CONSTRAINT "vehiculos_empresa_id_fkey" FOREIGN KEY ("empresa_id") REFERENCES "empresas"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "neumaticos" ADD CONSTRAINT "neumaticos_empresa_id_fkey" FOREIGN KEY ("empresa_id") REFERENCES "empresas"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "almacenes" ADD CONSTRAINT "almacenes_empresa_id_fkey" FOREIGN KEY ("empresa_id") REFERENCES "empresas"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "proveedores" ADD CONSTRAINT "proveedores_empresa_id_fkey" FOREIGN KEY ("empresa_id") REFERENCES "empresas"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
