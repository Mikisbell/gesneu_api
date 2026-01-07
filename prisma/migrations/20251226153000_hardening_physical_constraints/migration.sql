-- Hardening: Physical Constraints

-- 1. Neumaticos
ALTER TABLE "neumaticos" ADD CONSTRAINT "check_neumatico_presion_positiva" CHECK (presion_actual_psi IS NULL OR presion_actual_psi >= 0);
ALTER TABLE "neumaticos" ADD CONSTRAINT "check_neumatico_profundidad_inicial" CHECK (profundidad_inicial_mm > 0);
ALTER TABLE "neumaticos" ADD CONSTRAINT "check_neumatico_profundidad_actual" CHECK (profundidad_actual_mm IS NULL OR profundidad_actual_mm >= 0);
ALTER TABLE "neumaticos" ADD CONSTRAINT "check_neumatico_desgaste_logico" CHECK (profundidad_actual_mm IS NULL OR profundidad_actual_mm <= profundidad_inicial_mm);

ALTER TABLE "neumaticos" ADD CONSTRAINT "check_neumatico_vida_positiva" CHECK (vida_actual >= 1);
ALTER TABLE "neumaticos" ADD CONSTRAINT "check_neumatico_reencauches_positivos" CHECK (reencauches_realizados >= 0);
ALTER TABLE "neumaticos" ADD CONSTRAINT "check_neumatico_km_positivo" CHECK (kilometraje_acumulado >= 0);

-- 2. Eventos
ALTER TABLE "eventos_neumaticos" ADD CONSTRAINT "check_evento_presion_positiva" CHECK (presion_psi IS NULL OR presion_psi >= 0);
ALTER TABLE "eventos_neumaticos" ADD CONSTRAINT "check_evento_profundidad_remanente" CHECK (profundidad_remanente IS NULL OR profundidad_remanente >= 0);
ALTER TABLE "eventos_neumaticos" ADD CONSTRAINT "check_evento_costo_positivo" CHECK (costo_evento IS NULL OR costo_evento >= 0);

-- 3. Lecturas
ALTER TABLE "lecturas_presion" ADD CONSTRAINT "check_lectura_presion_positiva" CHECK (presion_psi >= 0);

-- 4. Modelos
ALTER TABLE "modelos_neumatico" ADD CONSTRAINT "check_modelo_profundidad_valida" CHECK (profundidad_inicial_mm > 0);
ALTER TABLE "modelos_neumatico" ADD CONSTRAINT "check_modelo_reencauches_validos" CHECK (reencauches_maximos >= 0);
