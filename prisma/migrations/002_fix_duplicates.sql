DO $$ 
DECLARE 
    r RECORD;
    dup_id UUID;
    pos RECORD;
    target_pos_id UUID;
BEGIN 
    -- Iterar sobre grupos de duplicados (mismo vehículo y número de eje)
    FOR r IN 
        SELECT 
            min(id::text)::uuid as keep_id, 
            array_agg(id) as ids 
        FROM configuraciones_eje 
        GROUP BY tipo_vehiculo_id, numero_eje 
        HAVING count(*) > 1 
    LOOP
        RAISE NOTICE 'Procesando duplicados para vehiculo %', r.keep_id;
        
        -- Para cada ID duplicado (saltando el primero)
        FOR i IN 2..array_length(r.ids, 1) LOOP
            dup_id := r.ids[i];
            
            -- Procesar cada posición del duplicado
            FOR pos IN SELECT * FROM posiciones_neumatico WHERE configuracion_eje_id = dup_id LOOP
                -- Buscar si existe posición equivalente en el destino
                SELECT id INTO target_pos_id FROM posiciones_neumatico 
                WHERE configuracion_eje_id = r.keep_id AND codigo_posicion = pos.codigo_posicion;
                
                IF target_pos_id IS NOT NULL THEN
                    -- Ya existe en destino. Mover neumáticos a la posición destino
                    UPDATE neumaticos 
                    SET ubicacion_posicion_id = target_pos_id
                    WHERE ubicacion_posicion_id = pos.id;
                    
                    -- Mover eventos a la posición destino (si hubiera)
                    UPDATE eventos_neumaticos
                    SET posicion_montaje_id = target_pos_id
                    WHERE posicion_montaje_id = pos.id;

                    -- Borrar la posición redundante del duplicado
                    DELETE FROM posiciones_neumatico WHERE id = pos.id;
                ELSE
                    -- No existe, mover la posición completa al destino
                    UPDATE posiciones_neumatico 
                    SET configuracion_eje_id = r.keep_id 
                    WHERE id = pos.id;
                END IF;
            END LOOP;
            
            -- Ahora sí borrar la configuración duplicada
            DELETE FROM configuraciones_eje WHERE id = dup_id;
            
            RAISE NOTICE 'Eliminado eje duplicado %', dup_id;
        END LOOP;
    END LOOP;
END $$;
