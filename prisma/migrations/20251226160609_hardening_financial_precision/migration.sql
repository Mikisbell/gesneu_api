/*
  Warnings:

  - You are about to alter the column `contador_vehiculo` on the `eventos_neumaticos` table. The data in that column could be lost. The data in that column will be cast from `DoublePrecision` to `Decimal(12,2)`.
  - You are about to alter the column `presion_psi` on the `eventos_neumaticos` table. The data in that column could be lost. The data in that column will be cast from `DoublePrecision` to `Decimal(5,2)`.
  - You are about to alter the column `presion_psi` on the `lecturas_presion` table. The data in that column could be lost. The data in that column will be cast from `DoublePrecision` to `Decimal(5,2)`.
  - You are about to alter the column `temperatura_c` on the `lecturas_presion` table. The data in that column could be lost. The data in that column will be cast from `DoublePrecision` to `Decimal(5,2)`.
  - You are about to alter the column `profundidad_inicial_mm` on the `modelos_neumatico` table. The data in that column could be lost. The data in that column will be cast from `DoublePrecision` to `Decimal(5,2)`.
  - You are about to alter the column `profundidad_inicial_mm` on the `neumaticos` table. The data in that column could be lost. The data in that column will be cast from `DoublePrecision` to `Decimal(5,2)`.
  - You are about to alter the column `profundidad_actual_mm` on the `neumaticos` table. The data in that column could be lost. The data in that column will be cast from `DoublePrecision` to `Decimal(5,2)`.
  - You are about to alter the column `profundidad_int` on the `neumaticos` table. The data in that column could be lost. The data in that column will be cast from `DoublePrecision` to `Decimal(5,2)`.
  - You are about to alter the column `profundidad_cen` on the `neumaticos` table. The data in that column could be lost. The data in that column will be cast from `DoublePrecision` to `Decimal(5,2)`.
  - You are about to alter the column `profundidad_ext` on the `neumaticos` table. The data in that column could be lost. The data in that column will be cast from `DoublePrecision` to `Decimal(5,2)`.
  - You are about to alter the column `presion_actual_psi` on the `neumaticos` table. The data in that column could be lost. The data in that column will be cast from `DoublePrecision` to `Decimal(5,2)`.
  - You are about to alter the column `kilometraje_acumulado` on the `neumaticos` table. The data in that column could be lost. The data in that column will be cast from `DoublePrecision` to `Decimal(12,2)`.
  - You are about to alter the column `horas_acumuladas` on the `neumaticos` table. The data in that column could be lost. The data in that column will be cast from `DoublePrecision` to `Decimal(10,2)`.
  - You are about to alter the column `valor` on the `registros_contador` table. The data in that column could be lost. The data in that column will be cast from `DoublePrecision` to `Decimal(12,2)`.
  - You are about to alter the column `contador_actual` on the `vehiculos` table. The data in that column could be lost. The data in that column will be cast from `DoublePrecision` to `Decimal(12,2)`.

*/
-- AlterTable
ALTER TABLE "eventos_neumaticos" ALTER COLUMN "contador_vehiculo" SET DATA TYPE DECIMAL(12,2),
ALTER COLUMN "presion_psi" SET DATA TYPE DECIMAL(5,2);

-- AlterTable
ALTER TABLE "lecturas_presion" ALTER COLUMN "presion_psi" SET DATA TYPE DECIMAL(5,2),
ALTER COLUMN "temperatura_c" SET DATA TYPE DECIMAL(5,2);

-- AlterTable
ALTER TABLE "modelos_neumatico" ALTER COLUMN "profundidad_inicial_mm" SET DATA TYPE DECIMAL(5,2);

-- AlterTable
ALTER TABLE "neumaticos" ALTER COLUMN "profundidad_inicial_mm" SET DATA TYPE DECIMAL(5,2),
ALTER COLUMN "profundidad_actual_mm" SET DATA TYPE DECIMAL(5,2),
ALTER COLUMN "profundidad_int" SET DATA TYPE DECIMAL(5,2),
ALTER COLUMN "profundidad_cen" SET DATA TYPE DECIMAL(5,2),
ALTER COLUMN "profundidad_ext" SET DATA TYPE DECIMAL(5,2),
ALTER COLUMN "presion_actual_psi" SET DATA TYPE DECIMAL(5,2),
ALTER COLUMN "kilometraje_acumulado" SET DATA TYPE DECIMAL(12,2),
ALTER COLUMN "horas_acumuladas" SET DATA TYPE DECIMAL(10,2);

-- AlterTable
ALTER TABLE "registros_contador" ALTER COLUMN "valor" SET DATA TYPE DECIMAL(12,2);

-- AlterTable
ALTER TABLE "vehiculos" ALTER COLUMN "contador_actual" SET DATA TYPE DECIMAL(12,2);
