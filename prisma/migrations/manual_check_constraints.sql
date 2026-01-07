-- ========================================
-- GesNeu API - CHECK Constraints Migration
-- Validación de integridad a nivel de DB
-- ========================================

-- 1. Presión positiva en lecturas
ALTER TABLE lecturas_presion
ADD CONSTRAINT chk_presion_positiva 
CHECK (presion_psi > 0);

-- 2. Presión válida en neumáticos (puede ser NULL)
ALTER TABLE neumaticos
ADD CONSTRAINT chk_neumatico_presion_positiva 
CHECK (presion_actual_psi IS NULL OR presion_actual_psi > 0);

-- 3. Profundidad válida (0-100mm)
ALTER TABLE neumaticos
ADD CONSTRAINT chk_profundidad_valida 
CHECK (profundidad_actual_mm IS NULL OR (profundidad_actual_mm >= 0 AND profundidad_actual_mm <= 100));

-- 4. Profundidad inicial válida
ALTER TABLE neumaticos
ADD CONSTRAINT chk_profundidad_inicial_valida 
CHECK (profundidad_inicial_mm > 0 AND profundidad_inicial_mm <= 50);

-- 5. Contador de vehículo no negativo
ALTER TABLE vehiculos
ADD CONSTRAINT chk_contador_no_negativo 
CHECK (contador_actual >= 0);

-- 6. Reencauches no exceden máximo (requiere JOIN, implementar como trigger o en app)
-- Nota: CHECK no puede referenciar otras tablas, esto se valida en la app

-- 7. Kilometraje acumulado no negativo
ALTER TABLE neumaticos
ADD CONSTRAINT chk_km_no_negativo 
CHECK (kilometraje_acumulado >= 0);

-- 8. Horas acumuladas no negativas
ALTER TABLE neumaticos
ADD CONSTRAINT chk_horas_no_negativo 
CHECK (horas_acumuladas >= 0);

-- 9. Vida actual positiva
ALTER TABLE neumaticos
ADD CONSTRAINT chk_vida_actual_positiva 
CHECK (vida_actual >= 1);

-- 10. Distancia de ruta no negativa
ALTER TABLE rutas
ADD CONSTRAINT chk_distancia_no_negativa 
CHECK (distancia_km >= 0);
