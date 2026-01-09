/*
  Warnings:

  - A unique constraint covering the columns `[numero_serie]` on the table `neumaticos` will be added. If there are existing duplicate values, this will fail.

*/
-- CreateIndex
CREATE UNIQUE INDEX "neumaticos_numero_serie_key" ON "neumaticos"("numero_serie");
