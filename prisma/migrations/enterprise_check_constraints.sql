-- ============================================================
-- CHECK CONSTRAINTS ALINEADOS CON ESQUEMA LEGACY ges_neu_bd
-- Ejecutar en Supabase SQL Editor
-- ============================================================

-- === NEUMÁTICOS ===

-- Ubicación mutuamente exclusiva (del legacy)
ALTER TABLE neumaticos DROP CONSTRAINT IF EXISTS chk_ubicacion_mutuamente_exclusiva;
ALTER TABLE neumaticos ADD CONSTRAINT chk_ubicacion_mutuamente_exclusiva CHECK (
  (ubicacion_almacen_id IS NOT NULL AND ubicacion_vehiculo_id IS NULL AND ubicacion_posicion_id IS NULL AND estado_actual != 'INSTALADO')
  OR
  (ubicacion_almacen_id IS NULL AND ubicacion_vehiculo_id IS NOT NULL AND ubicacion_posicion_id IS NOT NULL AND estado_actual = 'INSTALADO')
  OR
  (ubicacion_almacen_id IS NULL AND ubicacion_vehiculo_id IS NULL AND ubicacion_posicion_id IS NULL AND estado_actual NOT IN ('INSTALADO', 'EN_STOCK'))
);

-- Vida útil restante no negativa
ALTER TABLE neumaticos DROP CONSTRAINT IF EXISTS chk_vida_util_restante_no_negativa;
ALTER TABLE neumaticos ADD CONSTRAINT chk_vida_util_restante_no_negativa CHECK (
  vida_util_restante_km IS NULL OR vida_util_restante_km >= 0
);

-- Tasa desgaste positiva
ALTER TABLE neumaticos DROP CONSTRAINT IF EXISTS chk_tasa_desgaste_positiva;
ALTER TABLE neumaticos ADD CONSTRAINT chk_tasa_desgaste_positiva CHECK (
  tasa_desgaste_actual_mm_km IS NULL OR tasa_desgaste_actual_mm_km > 0
);

-- Profundidad remanente válida
ALTER TABLE neumaticos DROP CONSTRAINT IF EXISTS chk_profundidad_remanente;
ALTER TABLE neumaticos ADD CONSTRAINT chk_profundidad_remanente CHECK (
  profundidad_remanente_actual_mm >= 0 AND profundidad_remanente_actual_mm <= 50
);

-- Kilometraje no negativo
ALTER TABLE neumaticos DROP CONSTRAINT IF EXISTS chk_kilometraje_no_negativo;
ALTER TABLE neumaticos ADD CONSTRAINT chk_kilometraje_no_negativo CHECK (
  kilometraje_acumulado >= 0
);

-- Vida actual válida (1-11)
ALTER TABLE neumaticos DROP CONSTRAINT IF EXISTS chk_vida_actual_valida;
ALTER TABLE neumaticos ADD CONSTRAINT chk_vida_actual_valida CHECK (
  vida_actual >= 1 AND vida_actual <= 11
);

-- Reencauches no negativos
ALTER TABLE neumaticos DROP CONSTRAINT IF EXISTS chk_reencauches_no_negativos;
ALTER TABLE neumaticos ADD CONSTRAINT chk_reencauches_no_negativos CHECK (
  reencauches_realizados >= 0
);

-- Costo compra no negativo
ALTER TABLE neumaticos DROP CONSTRAINT IF EXISTS chk_costo_compra_no_negativo;
ALTER TABLE neumaticos ADD CONSTRAINT chk_costo_compra_no_negativo CHECK (
  costo_compra IS NULL OR costo_compra >= 0
);

-- Fecha fabricación antes de compra
ALTER TABLE neumaticos DROP CONSTRAINT IF EXISTS chk_fechas_neumatico;
ALTER TABLE neumaticos ADD CONSTRAINT chk_fechas_neumatico CHECK (
  fecha_fabricacion IS NULL OR fecha_fabricacion <= fecha_compra
);

-- === VEHÍCULOS ===

-- Año fabricación válido
ALTER TABLE vehiculos DROP CONSTRAINT IF EXISTS chk_anio_fabricacion;
ALTER TABLE vehiculos ADD CONSTRAINT chk_anio_fabricacion CHECK (
  anio_fabricacion >= 1900 AND anio_fabricacion <= EXTRACT(YEAR FROM CURRENT_DATE) + 1
);

-- Fecha baja después de fecha alta
ALTER TABLE vehiculos DROP CONSTRAINT IF EXISTS chk_fechas_vehiculo;
ALTER TABLE vehiculos ADD CONSTRAINT chk_fechas_vehiculo CHECK (
  fecha_baja IS NULL OR fecha_baja >= fecha_alta
);

-- Odómetro no negativo
ALTER TABLE vehiculos DROP CONSTRAINT IF EXISTS chk_odometro_no_negativo;
ALTER TABLE vehiculos ADD CONSTRAINT chk_odometro_no_negativo CHECK (
  odometro_actual IS NULL OR odometro_actual >= 0
);

-- === EVENTOS NEUMÁTICOS ===

-- Presión positiva
ALTER TABLE eventos_neumaticos DROP CONSTRAINT IF EXISTS chk_presion_positiva;
ALTER TABLE eventos_neumaticos ADD CONSTRAINT chk_presion_positiva CHECK (
  presion_psi IS NULL OR presion_psi > 0
);

-- Costo evento no negativo
ALTER TABLE eventos_neumaticos DROP CONSTRAINT IF EXISTS chk_costo_evento_no_negativo;
ALTER TABLE eventos_neumaticos ADD CONSTRAINT chk_costo_evento_no_negativo CHECK (
  costo_evento IS NULL OR costo_evento >= 0
);

-- Profundidad remanente no negativa
ALTER TABLE eventos_neumaticos DROP CONSTRAINT IF EXISTS chk_profundidad_remanente_evento;
ALTER TABLE eventos_neumaticos ADD CONSTRAINT chk_profundidad_remanente_evento CHECK (
  profundidad_remanente IS NULL OR profundidad_remanente >= 0
);

-- === MODELOS NEUMÁTICO ===

-- Profundidad original positiva
ALTER TABLE modelos_neumatico DROP CONSTRAINT IF EXISTS chk_profundidad_original_positiva;
ALTER TABLE modelos_neumatico ADD CONSTRAINT chk_profundidad_original_positiva CHECK (
  profundidad_original_mm > 0
);

-- Presión recomendada positiva
ALTER TABLE modelos_neumatico DROP CONSTRAINT IF EXISTS chk_presion_recomendada_positiva;
ALTER TABLE modelos_neumatico ADD CONSTRAINT chk_presion_recomendada_positiva CHECK (
  presion_recomendada_psi IS NULL OR presion_recomendada_psi > 0
);

-- Reencauches máximos válidos
ALTER TABLE modelos_neumatico DROP CONSTRAINT IF EXISTS chk_reencauches_maximos;
ALTER TABLE modelos_neumatico ADD CONSTRAINT chk_reencauches_maximos CHECK (
  reencauches_maximos >= 0 AND reencauches_maximos <= 10
);

-- Profundidad mínima retiro válida
ALTER TABLE modelos_neumatico DROP CONSTRAINT IF EXISTS chk_profundidad_minima_retiro;
ALTER TABLE modelos_neumatico ADD CONSTRAINT chk_profundidad_minima_retiro CHECK (
  profundidad_minima_retiro_mm > 0 AND profundidad_minima_retiro_mm <= profundidad_original_mm
);

-- Tasa desgaste esperada positiva
ALTER TABLE modelos_neumatico DROP CONSTRAINT IF EXISTS chk_tasa_desgaste_esperada;
ALTER TABLE modelos_neumatico ADD CONSTRAINT chk_tasa_desgaste_esperada CHECK (
  tasa_desgaste_esperada_mm_km IS NULL OR tasa_desgaste_esperada_mm_km > 0
);

-- Vida útil teórica positiva
ALTER TABLE modelos_neumatico DROP CONSTRAINT IF EXISTS chk_vida_util_teorica;
ALTER TABLE modelos_neumatico ADD CONSTRAINT chk_vida_util_teorica CHECK (
  vida_util_teorica_km IS NULL OR vida_util_teorica_km > 0
);

-- === CONFIGURACIONES EJE ===

-- Número eje positivo
ALTER TABLE configuraciones_eje DROP CONSTRAINT IF EXISTS chk_numero_eje_positivo;
ALTER TABLE configuraciones_eje ADD CONSTRAINT chk_numero_eje_positivo CHECK (
  numero_eje > 0
);

-- Número posiciones válido
ALTER TABLE configuraciones_eje DROP CONSTRAINT IF EXISTS chk_numero_posiciones_valido;
ALTER TABLE configuraciones_eje ADD CONSTRAINT chk_numero_posiciones_valido CHECK (
  numero_posiciones >= 1 AND numero_posiciones <= 6
);

-- Neumáticos por posición válido
ALTER TABLE configuraciones_eje DROP CONSTRAINT IF EXISTS chk_neumaticos_por_posicion;
ALTER TABLE configuraciones_eje ADD CONSTRAINT chk_neumaticos_por_posicion CHECK (
  neumaticos_por_posicion IN (1, 2)
);

-- === POSICIONES NEUMÁTICO ===

-- Posición relativa positiva
ALTER TABLE posiciones_neumatico DROP CONSTRAINT IF EXISTS chk_posicion_relativa_positiva;
ALTER TABLE posiciones_neumatico ADD CONSTRAINT chk_posicion_relativa_positiva CHECK (
  posicion_relativa > 0
);

-- === TIPOS VEHÍCULO ===

-- Ejes estándar válidos
ALTER TABLE tipos_vehiculo DROP CONSTRAINT IF EXISTS chk_ejes_standard;
ALTER TABLE tipos_vehiculo ADD CONSTRAINT chk_ejes_standard CHECK (
  ejes_standard >= 1 AND ejes_standard <= 10
);

-- === GARANTÍAS ===

-- Fecha fin después de inicio
ALTER TABLE garantias_neumaticos DROP CONSTRAINT IF EXISTS chk_fechas_garantia;
ALTER TABLE garantias_neumaticos ADD CONSTRAINT chk_fechas_garantia CHECK (
  fecha_fin IS NULL OR fecha_fin >= fecha_inicio
);

-- === MEDICIONES PROFUNDIDAD ===

-- Profundidad válida
ALTER TABLE mediciones_profundidad DROP CONSTRAINT IF EXISTS chk_profundidad_valida;
ALTER TABLE mediciones_profundidad ADD CONSTRAINT chk_profundidad_valida CHECK (
  profundidad_int >= 0 AND profundidad_int <= 50
  AND profundidad_cen >= 0 AND profundidad_cen <= 50
  AND profundidad_ext >= 0 AND profundidad_ext <= 50
);

-- === TIPOS RUTA ===

-- Porcentaje carga válido
ALTER TABLE tipos_ruta DROP CONSTRAINT IF EXISTS chk_porcentaje_carga_valido;
ALTER TABLE tipos_ruta ADD CONSTRAINT chk_porcentaje_carga_valido CHECK (
  factor_desgaste IS NULL OR (factor_desgaste >= 0 AND factor_desgaste <= 5)
);

-- ============================================================
-- FIN DE CONSTRAINTS
-- ============================================================
