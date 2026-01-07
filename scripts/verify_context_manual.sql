
-- Verify existence of new tables and columns
SELECT 
    table_name 
FROM 
    information_schema.tables 
WHERE 
    table_name IN ('tipos_ruta', 'rutas', 'modelos_posiciones_permitidas');

-- Verify Vehiculo column
SELECT 
    column_name, data_type 
FROM 
    information_schema.columns 
WHERE 
    table_name = 'vehiculos' AND column_name = 'ruta_id';

-- Verify ModeloPosicionPermitida columns
SELECT 
    column_name, data_type 
FROM 
    information_schema.columns 
WHERE 
    table_name = 'modelos_posiciones_permitidas';
