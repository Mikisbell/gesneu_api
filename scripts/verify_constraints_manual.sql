
-- Setup
DO $$
DECLARE
    fab_id uuid;
    mod_id uuid;
BEGIN
    -- Create dummy data
    INSERT INTO fabricantes_neumatico (id, nombre) VALUES (gen_random_uuid(), 'TEST_FAB_SQL_' || extract(epoch from now())) RETURNING id INTO fab_id;
    INSERT INTO modelos_neumatico (id, nombre, medida, profundidad_inicial_mm, fabricante_id) 
    VALUES (gen_random_uuid(), 'TEST_MODEL_SQL', '11R22.5', 20, fab_id) RETURNING id INTO mod_id;
    
    RAISE NOTICE 'Created Dummy Model: %', mod_id;

    -- TEST 1: Negative Pressure CHECK (check_neumatico_presion_positiva)
    BEGIN
        INSERT INTO neumaticos (id, numero_serie, modelo_id, profundidad_inicial_mm, presion_actual_psi)
        VALUES (gen_random_uuid(), 'TEST-FAIL-PSI-' || extract(epoch from now()), mod_id, 20, -5);
        RAISE EXCEPTION 'FAIL: Negative pressure was allowed!';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE '✅ SUCCESS: Blocked negative pressure (Constraint: %)', SQLERRM;
    END;

    -- TEST 2: Depth > Initial CHECK (check_neumatico_desgaste_logico)
    BEGIN
        INSERT INTO neumaticos (id, numero_serie, modelo_id, profundidad_inicial_mm, profundidad_actual_mm)
        VALUES (gen_random_uuid(), 'TEST-FAIL-DEPTH-' || extract(epoch from now()), mod_id, 20, 25);
        RAISE EXCEPTION 'FAIL: Magical growth allowed!';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE '✅ SUCCESS: Blocked growth (Constraint: %)', SQLERRM;
    END;

    -- Cleanup
    DELETE FROM modelos_neumatico WHERE id = mod_id;
    DELETE FROM fabricantes_neumatico WHERE id = fab_id;
END;
$$;
