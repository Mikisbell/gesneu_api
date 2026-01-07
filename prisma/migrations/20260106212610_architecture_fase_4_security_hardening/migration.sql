-- 1. Habilitar RLS en Tablas Críticas
ALTER TABLE vehiculos ENABLE ROW LEVEL SECURITY;
ALTER TABLE neumaticos ENABLE ROW LEVEL SECURITY;
ALTER TABLE almacenes ENABLE ROW LEVEL SECURITY;
ALTER TABLE proveedores ENABLE ROW LEVEL SECURITY;
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;

-- 2. Crear Políticas de Aislamiento (Tenant Isolation)
-- NOTA: Estas políticas asumen que el backend ejecuta "SET app.current_tenant = 'UUID'"
-- Si la variable es NULL, no se retorna nada (Fail Safe).

-- Vehiculos
CREATE POLICY tenant_isolation_vehiculos ON vehiculos
    USING (empresa_id = current_setting('app.current_tenant', true)::uuid);

-- Neumaticos
CREATE POLICY tenant_isolation_neumaticos ON neumaticos
    USING (empresa_id = current_setting('app.current_tenant', true)::uuid);

-- Almacenes
CREATE POLICY tenant_isolation_almacenes ON almacenes
    USING (empresa_id = current_setting('app.current_tenant', true)::uuid);

-- Proveedores
CREATE POLICY tenant_isolation_proveedores ON proveedores
    USING (empresa_id = current_setting('app.current_tenant', true)::uuid);
    
-- Usuarios (Permitir ver su propio usuario o todos si es del tenant)
CREATE POLICY tenant_isolation_usuarios ON usuarios
    USING (empresa_id = current_setting('app.current_tenant', true)::uuid);


-- 3. Trigger de Auditoría Genérica
-- Función para capturar cambios
CREATE OR REPLACE FUNCTION audit_trigger_func()
RETURNS TRIGGER AS $$
DECLARE
    audit_data jsonb;
    old_data jsonb;
    new_data jsonb;
    entity_id uuid;
    app_user_id uuid;
BEGIN
    -- Intentar obtener usuario de la sesión
    BEGIN
        app_user_id := current_setting('app.current_user_id', true)::uuid;
    EXCEPTION WHEN OTHERS THEN
        app_user_id := NULL;
    END;

    IF (TG_OP = 'DELETE') THEN
        old_data := to_jsonb(OLD);
        new_data := NULL;
        -- Asumimos que la PK es 'id'
        IF (old_data ? 'id') THEN
             entity_id := (old_data->>'id')::uuid;
        END IF;
    ELSIF (TG_OP = 'UPDATE') THEN
        old_data := to_jsonb(OLD);
        new_data := to_jsonb(NEW);
        IF (new_data ? 'id') THEN
             entity_id := (new_data->>'id')::uuid;
        END IF;
    ELSIF (TG_OP = 'INSERT') THEN
        old_data := NULL;
        new_data := to_jsonb(NEW);
        IF (new_data ? 'id') THEN
             entity_id := (new_data->>'id')::uuid;
        END IF;
    END IF;

    -- Insertar en log centralizado
    INSERT INTO auditoria_logs (
        esquema_tabla,
        nombre_tabla,
        operacion,
        usuario_db,
        usuario_app_id,
        entidad_id,
        datos_antiguos,
        datos_nuevos
    ) VALUES (
        TG_TABLE_SCHEMA,
        TG_TABLE_NAME,
        TG_OP,
        current_user,
        app_user_id,
        entity_id,
        old_data,
        new_data
    );

    RETURN NULL; -- Trigger AFTER, return value ignored
END;
$$ LANGUAGE plpgsql;

-- Aplicar Trigger a tablas críticas
CREATE TRIGGER audit_vehiculos_trigger
AFTER INSERT OR UPDATE OR DELETE ON vehiculos
FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

CREATE TRIGGER audit_neumaticos_trigger
AFTER INSERT OR UPDATE OR DELETE ON neumaticos
FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

CREATE TRIGGER audit_almacenes_trigger
AFTER INSERT OR UPDATE OR DELETE ON almacenes
FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

-- (Se puede extender a más tablas según necesidad)