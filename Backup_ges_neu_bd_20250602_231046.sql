--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5 (Ubuntu 17.5-1.pgdg24.04+1)
-- Dumped by pg_dump version 17.5 (Ubuntu 17.5-1.pgdg24.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: dblink; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS dblink WITH SCHEMA public;


--
-- Name: EXTENSION dblink; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION dblink IS 'connect to other PostgreSQL databases from within a database';


--
-- Name: pg_stat_statements; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_stat_statements WITH SCHEMA public;


--
-- Name: EXTENSION pg_stat_statements; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_stat_statements IS 'Estadísticas de ejecución de sentencias SQL';


--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'Funciones criptográficas (para hashing de contraseñas, etc.)';


--
-- Name: unaccent; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS unaccent WITH SCHEMA public;


--
-- Name: EXTENSION unaccent; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION unaccent IS 'Funciones para remover acentos';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'Generador de UUIDs v4 (gen_random_uuid)';


--
-- Name: dot_code; Type: DOMAIN; Schema: public; Owner: postgres
--

CREATE DOMAIN public.dot_code AS text
	CONSTRAINT dot_code_check CHECK ((VALUE ~ '^[A-Z0-9]{2,4}[A-Z0-9]{2}[A-Z0-9]{3,4}$'::text));


ALTER DOMAIN public.dot_code OWNER TO postgres;

--
-- Name: DOMAIN dot_code; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON DOMAIN public.dot_code IS 'Código DOT del neumático (formato flexible)';


--
-- Name: estado_neumatico_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.estado_neumatico_enum AS ENUM (
    'EN_STOCK',
    'INSTALADO',
    'EN_REPARACION',
    'EN_REENCAUCHE',
    'DESECHADO',
    'EN_TRANSITO'
);


ALTER TYPE public.estado_neumatico_enum OWNER TO postgres;

--
-- Name: TYPE estado_neumatico_enum; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TYPE public.estado_neumatico_enum IS 'Estados posibles en el ciclo de vida de un neumático';


--
-- Name: estado_neumatico_enum_destino; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.estado_neumatico_enum_destino AS ENUM (
    'EN_STOCK',
    'INSTALADO',
    'EN_REPARACION',
    'EN_REENCAUCHE',
    'DESECHADO',
    'PARA_REPARACION',
    'REPARADO',
    'PARA_REENCAUCHE',
    'REENCAUCHADO',
    'EN_TRANSITO'
);


ALTER TYPE public.estado_neumatico_enum_destino OWNER TO postgres;

--
-- Name: estado_operacion_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.estado_operacion_enum AS ENUM (
    'PENDIENTE',
    'EN_PROCESO',
    'COMPLETADA',
    'CANCELADA',
    'VENCIDA'
);


ALTER TYPE public.estado_operacion_enum OWNER TO postgres;

--
-- Name: estadoalerta; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.estadoalerta AS ENUM (
    'NUEVA',
    'VISTA',
    'GESTIONADA'
);


ALTER TYPE public.estadoalerta OWNER TO postgres;

--
-- Name: lado_vehiculo_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.lado_vehiculo_enum AS ENUM (
    'IZQUIERDO',
    'DERECHO',
    'CENTRAL',
    'INDETERMINADO'
);


ALTER TYPE public.lado_vehiculo_enum OWNER TO postgres;

--
-- Name: TYPE lado_vehiculo_enum; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TYPE public.lado_vehiculo_enum IS 'Posición lateral del neumático en el vehículo';


--
-- Name: medida_neumatico; Type: DOMAIN; Schema: public; Owner: postgres
--

CREATE DOMAIN public.medida_neumatico AS character varying(20)
	CONSTRAINT medida_neumatico_check CHECK ((((VALUE)::text ~ '^([0-9]{2,3}(\.[0-9]{1,2})?/[0-9]{2,3}(\.[0-9]{1,2})?R[0-9]{2}(\.[0-9])?)$'::text) OR ((VALUE)::text ~ '^([0-9]{1,2}(\.[0-9]{1,2})?-[0-9]{2}(\.[0-9])?R[0-9]{2}(\.[0-9])?)$'::text) OR ((VALUE)::text ~ '^([0-9]{1,3}(\.[0-9]{1,2})?X[0-9]{1,3}(\.[0-9]{1,2})?R[0-9]{2}(\.[0-9])?)$'::text) OR ((VALUE)::text ~ '^([0-9]{1,2}(\.[0-9]{1,2})?R[0-9]{2}(\.[0-9])?)$'::text)));


ALTER DOMAIN public.medida_neumatico OWNER TO postgres;

--
-- Name: DOMAIN medida_neumatico; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON DOMAIN public.medida_neumatico IS 'Medida del neumático (ej. 295/80R22.5, 11R22.5, 315/80R22.5)';


--
-- Name: nivelseveridad; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.nivelseveridad AS ENUM (
    'INFO',
    'WARN',
    'CRITICAL'
);


ALTER TYPE public.nivelseveridad OWNER TO postgres;

--
-- Name: placa_vehiculo; Type: DOMAIN; Schema: public; Owner: postgres
--

CREATE DOMAIN public.placa_vehiculo AS character varying(15)
	CONSTRAINT placa_vehiculo_check CHECK (((VALUE)::text ~ '^[A-Z0-9]{1,7}-?[A-Z0-9]{1,7}$'::text));


ALTER DOMAIN public.placa_vehiculo OWNER TO postgres;

--
-- Name: DOMAIN placa_vehiculo; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON DOMAIN public.placa_vehiculo IS 'Placa de identificación del vehículo (formato flexible)';


--
-- Name: tipo_accion_operacion_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.tipo_accion_operacion_enum AS ENUM (
    'INSTALACION',
    'DESMONTAJE',
    'ROTACION',
    'REPARACION_NEU',
    'INSPECCION_NEU',
    'OTRO_NEU'
);


ALTER TYPE public.tipo_accion_operacion_enum OWNER TO postgres;

--
-- Name: tipo_eje_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.tipo_eje_enum AS ENUM (
    'DIRECCION',
    'TRACCION',
    'ARRASTRE',
    'ELEVADOR',
    'RETRACTIL',
    'OTRO'
);


ALTER TYPE public.tipo_eje_enum OWNER TO postgres;

--
-- Name: tipo_evento_neumatico_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.tipo_evento_neumatico_enum AS ENUM (
    'COMPRA',
    'INSTALACION',
    'DESMONTAJE',
    'INSPECCION',
    'ROTACION',
    'REPARACION_ENTRADA',
    'REPARACION_SALIDA',
    'REENCAUCHE_ENTRADA',
    'REENCAUCHE_SALIDA',
    'DESECHO',
    'AJUSTE_INVENTARIO',
    'TRANSFERENCIA_UBICACION'
);


ALTER TYPE public.tipo_evento_neumatico_enum OWNER TO postgres;

--
-- Name: TYPE tipo_evento_neumatico_enum; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TYPE public.tipo_evento_neumatico_enum IS 'Tipos de eventos registrables para neumáticos';


--
-- Name: tipo_operacion_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.tipo_operacion_enum AS ENUM (
    'ROTACION',
    'BALANCEO',
    'ALINEACION',
    'REPARACION_GENERAL',
    'INSPECCION_GENERAL',
    'CAMBIO_ACEITE',
    'OTRO',
    'DESMONTAJE'
);


ALTER TYPE public.tipo_operacion_enum OWNER TO postgres;

--
-- Name: tipo_parametro_inventario_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.tipo_parametro_inventario_enum AS ENUM (
    'PROFUNDIDAD_MINIMA',
    'STOCK_MINIMO',
    'STOCK_MAXIMO',
    'VIDA_UTIL_KM',
    'VIDA_UTIL_ANIOS'
);


ALTER TYPE public.tipo_parametro_inventario_enum OWNER TO postgres;

--
-- Name: tipo_parametro_inventario_gesneu_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.tipo_parametro_inventario_gesneu_enum AS ENUM (
    'STOCK_MINIMO',
    'STOCK_MAXIMO',
    'PROFUNDIDAD_MINIMA_RETIRO_MM',
    'PROFUNDIDAD_MINIMA_REENCAUCHE_MM',
    'TIEMPO_MAXIMO_VIDA_MESES',
    'MAX_ROTACIONES_PERIODO',
    'MAX_REPARACIONES_PERIODO',
    'VIDA_MAXIMA_ESTANTE_MESES_SIN_USO'
);


ALTER TYPE public.tipo_parametro_inventario_gesneu_enum OWNER TO postgres;

--
-- Name: tipoalertaenum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.tipoalertaenum AS ENUM (
    'PROFUNDIDAD_BAJA',
    'STOCK_MINIMO',
    'LIMITE_REENCAUCHES',
    'PRESION_BAJA',
    'PRESION_ALTA',
    'DESGASTE_IRREGULAR',
    'SOBRECARGA',
    'FIN_VIDA_UTIL_ESTIMADO',
    'MANTENIMIENTO_PREVENTIVO',
    'OTRO'
);


ALTER TYPE public.tipoalertaenum OWNER TO postgres;

--
-- Name: tipoproveedorenum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.tipoproveedorenum AS ENUM (
    'FABRICANTE',
    'DISTRIBUIDOR',
    'SERVICIO_REPARACION',
    'SERVICIO_REENCAUCHE',
    'OTRO'
);


ALTER TYPE public.tipoproveedorenum OWNER TO postgres;

--
-- Name: TYPE tipoproveedorenum; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TYPE public.tipoproveedorenum IS 'Tipos de proveedores en el sistema';


--
-- Name: actualizar_fecha_actualizacion(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.actualizar_fecha_actualizacion() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.actualizado_en = NOW();
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.actualizar_fecha_actualizacion() OWNER TO postgres;

--
-- Name: actualizar_fecha_ultimo_evento(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.actualizar_fecha_ultimo_evento() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE neumaticos
    SET fecha_ultimo_evento = NOW(),
        actualizado_en = NOW(),
        actualizado_por = NEW.usuario_id
    WHERE id = NEW.neumatico_id;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.actualizar_fecha_ultimo_evento() OWNER TO postgres;

--
-- Name: actualizar_max_vidas_utiles(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.actualizar_max_vidas_utiles() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Asegurar que max_vidas_utiles = reencauches_maximos + 1
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        NEW.max_vidas_utiles := COALESCE(NEW.reencauches_maximos, 0) + 1;
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.actualizar_max_vidas_utiles() OWNER TO postgres;

--
-- Name: actualizar_metricas_rendimiento(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.actualizar_metricas_rendimiento() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_vida_util_restante_km NUMERIC(10,2);
    v_profundidad_actual_new NUMERIC(5,2);
    v_profundidad_minima_retiro NUMERIC(5,2);
    v_debe_actualizar_inspeccion BOOLEAN := FALSE;
    v_es_actualizacion_vida BOOLEAN := FALSE;
BEGIN
    -- Determinar si estamos actualizando la vida_actual
    IF TG_OP = 'UPDATE' AND OLD.vida_actual IS DISTINCT FROM NEW.vida_actual THEN
        v_es_actualizacion_vida := TRUE;
    END IF;

    -- Calcular vida útil restante solo si cambian campos relevantes o es un INSERT
    -- No calcular si solo se está actualizando vida_actual para evitar bucles
    IF (TG_OP = 'INSERT' OR 
        (TG_OP = 'UPDATE' AND 
         (OLD.profundidad_remanente_actual_mm IS DISTINCT FROM NEW.profundidad_remanente_actual_mm OR
          OLD.kilometraje_vida_actual IS DISTINCT FROM NEW.kilometraje_vida_actual OR
          OLD.tasa_desgaste_actual_mm_km IS DISTINCT FROM NEW.tasa_desgaste_actual_mm_km)))
        AND NOT v_es_actualizacion_vida
    THEN
        RAISE NOTICE 'Calculando vida útil restante para neumático %', NEW.id;
        v_vida_util_restante_km := public.calcular_vida_util_restante(NEW.id);
        NEW.vida_util_restante_km := v_vida_util_restante_km;
        
        -- Registrar el cálculo para depuración
        RAISE NOTICE 'Vida útil restante calculada: % km para neumático %', 
                     v_vida_util_restante_km, NEW.id;
    END IF;

    -- Condiciones para actualizar la próxima inspección
    -- Solo si no es una actualización de vida para evitar bucles
    IF NOT v_es_actualizacion_vida THEN
        -- 1. Si el neumático acaba de ser instalado en un vehículo
        IF OLD.ubicacion_actual_vehiculo_id IS DISTINCT FROM NEW.ubicacion_actual_vehiculo_id 
           AND NEW.ubicacion_actual_vehiculo_id IS NOT NULL THEN
            v_debe_actualizar_inspeccion := TRUE;
            RAISE NOTICE 'Neumático % instalado en vehículo, actualizando inspección', NEW.id;
        END IF;

        -- 2. Si la vida útil restante cambió significativamente
        IF OLD.vida_util_restante_km IS DISTINCT FROM NEW.vida_util_restante_km THEN
            IF (OLD.vida_util_restante_km IS NULL AND NEW.vida_util_restante_km IS NOT NULL) OR
               (NEW.vida_util_restante_km IS NULL AND OLD.vida_util_restante_km IS NOT NULL) OR
               (ABS(COALESCE(OLD.vida_util_restante_km,0) - COALESCE(NEW.vida_util_restante_km,0)) > 100 OR
                (COALESCE(OLD.vida_util_restante_km, 0) > 0 AND 
                 ABS(COALESCE(OLD.vida_util_restante_km,0) - COALESCE(NEW.vida_util_restante_km,0)) / 
                 COALESCE(OLD.vida_util_restante_km,1) > 0.05)) THEN
                v_debe_actualizar_inspeccion := TRUE;
                RAISE NOTICE 'Cambio significativo en vida útil restante para neumático %: % km -> % km', 
                             NEW.id, OLD.vida_util_restante_km, NEW.vida_util_restante_km;
            END IF;
        END IF;

        -- 3. Si la profundidad está cerca del mínimo de retiro
        SELECT m.profundidad_minima_retiro_mm, n.profundidad_remanente_actual_mm 
        INTO v_profundidad_minima_retiro, v_profundidad_actual_new
        FROM modelos_neumatico m 
        JOIN neumaticos n ON m.id = n.modelo_id
        WHERE n.id = NEW.id;

        IF v_profundidad_actual_new IS NOT NULL AND v_profundidad_minima_retiro IS NOT NULL AND
           (v_profundidad_actual_new - v_profundidad_minima_retiro) < 2.0 THEN
            v_debe_actualizar_inspeccion := TRUE;
            RAISE NOTICE 'Neumático % cerca del mínimo de retiro (%.2f mm < %.2f mm + 2.0 mm)', 
                         NEW.id, v_profundidad_actual_new, v_profundidad_minima_retiro;
        END IF;
    END IF;

    -- Actualizar próxima inspección si es necesario
    IF v_debe_actualizar_inspeccion THEN
        RAISE NOTICE 'Actualizando próxima inspección para neumático %', NEW.id;
        PERFORM public.actualizar_proxima_inspeccion(NEW.id);
    END IF;

    -- Siempre actualizar la marca de tiempo de actualización
    NEW.actualizado_en = NOW();
    RETURN NEW;
    
EXCEPTION WHEN OTHERS THEN
    -- Registrar el error pero no fallar la operación principal
    INSERT INTO public.errores_aplicacion (
        nombre_funcion, 
        mensaje_error, 
        detalles, 
        creado_por
    ) VALUES (
        'actualizar_metricas_rendimiento', 
        SQLERRM, 
        jsonb_build_object(
            'neumatico_id', COALESCE(NEW.id::text, 'NULL'),
            'operacion', TG_OP,
            'sqlstate', SQLSTATE,
            'vida_actual_old', CASE WHEN TG_OP = 'UPDATE' THEN OLD.vida_actual ELSE NULL END,
            'vida_actual_new', NEW.vida_actual,
            'profundidad_old', CASE WHEN TG_OP = 'UPDATE' THEN OLD.profundidad_remanente_actual_mm ELSE NULL END,
            'profundidad_new', NEW.profundidad_remanente_actual_mm
        ), 
        'SISTEMA'
    );
    RAISE WARNING 'Error en actualizar_metricas_rendimiento (neumático %): %', 
                  COALESCE(NEW.id::text, 'NULL'), SQLERRM;
    
    -- Asegurarse de que siempre hay un valor de retorno
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.actualizar_metricas_rendimiento() OWNER TO postgres;

--
-- Name: FUNCTION actualizar_metricas_rendimiento(); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.actualizar_metricas_rendimiento() IS 'Función de trigger que actualiza las métricas de rendimiento de un neumático cuando cambian sus valores críticos.

Actualiza la vida útil restante y programa la próxima inspección cuando sea necesario.

Se evitan bucles al no recalcular la vida útil cuando solo se actualiza el campo vida_actual.';


--
-- Name: actualizar_metricas_rendimiento_manual(uuid, numeric, integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.actualizar_metricas_rendimiento_manual(p_neumatico_id uuid, p_profundidad_remanente numeric, p_kilometraje_vida_actual integer, p_vida_actual integer DEFAULT NULL::integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_profundidad_inicial NUMERIC(5,2);
    v_profundidad_desgastada NUMERIC(5,2);
    v_tasa_desgaste_actual NUMERIC(10,8);
    v_vida_util_restante_km INTEGER;
    v_profundidad_minima_desecho NUMERIC(5,2) := 2.0; -- Valor por defecto, ajustar según sea necesario
    v_kilometraje_restante_estimado NUMERIC(10,2);
BEGIN
    -- Obtener la profundidad inicial de la vida actual
    SELECT profundidad_inicial_mm INTO v_profundidad_inicial
    FROM neumaticos
    WHERE id = p_neumatico_id;
    
    -- Calcular la profundidad desgastada
    IF v_profundidad_inicial IS NOT NULL AND p_profundidad_remanente IS NOT NULL THEN
        v_profundidad_desgastada := v_profundidad_inicial - p_profundidad_remanente;
        
        -- Calcular la tasa de desgaste actual (mm/km)
        IF p_kilometraje_vida_actual > 0 THEN
            v_tasa_desgaste_actual := v_profundidad_desgastada / p_kilometraje_vida_actual;
            
            -- Asegurarse de que la tasa de desgaste no sea negativa
            IF v_tasa_desgaste_actual < 0 THEN
                v_tasa_desgaste_actual := 0;
            END IF;
        ELSE
            v_tasa_desgaste_actual := NULL;
        END IF;
        
        -- Calcular la vida útil restante estimada (km)
        IF v_tasa_desgaste_actual > 0 AND p_profundidad_remanente > v_profundidad_minima_desecho THEN
            v_kilometraje_restante_estimado := (p_profundidad_remanente - v_profundidad_minima_desecho) / v_tasa_desgaste_actual;
            v_vida_util_restante_km := GREATEST(0, FLOOR(v_kilometraje_restante_estimado));
        ELSE
            v_vida_util_restante_km := 0;
        END IF;
        
        -- Actualizar solo los campos necesarios para evitar problemas con las restricciones
        -- Primero, verificar si el neumático existe
        IF EXISTS (SELECT 1 FROM neumaticos WHERE id = p_neumatico_id) THEN
            -- Usar una consulta preparada para actualizar solo los campos específicos
            EXECUTE format('UPDATE neumaticos SET 
                tasa_desgaste_actual_mm_km = %L, 
                vida_util_restante_km = %L, 
                actualizado_en = NOW() 
                WHERE id = %L', 
                v_tasa_desgaste_actual, 
                v_vida_util_restante_km,
                p_neumatico_id);
        END IF;
    END IF;
    
EXCEPTION WHEN OTHERS THEN
    -- En caso de error, registrar el error pero no fallar la operación principal
    RAISE WARNING 'Error al actualizar métricas de rendimiento para el neumático %: %', p_neumatico_id, SQLERRM;
END;
$$;


ALTER FUNCTION public.actualizar_metricas_rendimiento_manual(p_neumatico_id uuid, p_profundidad_remanente numeric, p_kilometraje_vida_actual integer, p_vida_actual integer) OWNER TO postgres;

--
-- Name: actualizar_proxima_inspeccion(uuid); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.actualizar_proxima_inspeccion(p_neumatico_id uuid) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_odometro_actual INTEGER;
    v_ultimo_evento_inspeccion TIMESTAMP WITH TIME ZONE;
    v_proxima_inspeccion_km INTEGER;
    v_proxima_inspeccion_fecha TIMESTAMP WITH TIME ZONE;
    v_fecha_actual TIMESTAMP WITH TIME ZONE := NOW();
    v_intervalo_inspeccion_km INTEGER;
    v_intervalo_inspeccion_dias INTEGER;
    v_kilometros_por_dia NUMERIC(10,2);
    v_dias_restantes INTEGER;
    v_dias_desde_ultima_inspeccion INTEGER;
    v_modelo_id UUID;
    v_vehiculo_id UUID;
    v_ubicacion_almacen_id UUID;
BEGIN
    -- Obtener información actual del neumático
    SELECT 
        COALESCE(n.odometro_instalacion_vida_actual, 0) + COALESCE(n.kilometraje_vida_actual, 0) as odometro_actual,
        n.modelo_id,
        n.ubicacion_actual_vehiculo_id,
        n.ubicacion_almacen_id
    INTO 
        v_odometro_actual,
        v_modelo_id,
        v_vehiculo_id,
        v_ubicacion_almacen_id
    FROM neumaticos n
    WHERE n.id = p_neumatico_id;

    -- Si no se encuentra el neumático, salir
    IF v_odometro_actual IS NULL THEN
        RAISE NOTICE 'No se encontró el neumático con ID %', p_neumatico_id;
        RETURN;
    END IF;

    -- Inicializar con valores por defecto
    v_intervalo_inspeccion_km := 5000;  -- 5,000 km por defecto
    v_intervalo_inspeccion_dias := 30;  -- 30 días por defecto
    
    -- Intentar obtener los valores de la base de datos
    DECLARE
        v_intervalo_km_text TEXT;
        v_intervalo_dias_text TEXT;
    BEGIN
        -- Obtener el valor de intervalo de kilómetros
        SELECT valor INTO v_intervalo_km_text 
        FROM parametros_sistema 
        WHERE clave = 'INTERVALO_INSPECCION_KM' 
        LIMIT 1;
        
        -- Si se encontró un valor, intentar convertirlo a entero
        IF v_intervalo_km_text IS NOT NULL AND v_intervalo_km_text <> '' THEN
            BEGIN
                v_intervalo_inspeccion_km := v_intervalo_km_text::INTEGER;
            EXCEPTION WHEN OTHERS THEN
                -- En caso de error, mantener el valor por defecto
                NULL;
            END;
        END IF;
        
        -- Obtener el valor de intervalo de días
        SELECT valor INTO v_intervalo_dias_text 
        FROM parametros_sistema 
        WHERE clave = 'INTERVALO_INSPECCION_DIAS' 
        LIMIT 1;
        
        -- Si se encontró un valor, intentar convertirlo a entero
        IF v_intervalo_dias_text IS NOT NULL AND v_intervalo_dias_text <> '' THEN
            BEGIN
                v_intervalo_inspeccion_dias := v_intervalo_dias_text::INTEGER;
            EXCEPTION WHEN OTHERS THEN
                -- En caso de error, mantener el valor por defecto
                NULL;
            END;
        END IF;
        
        -- Insertar o actualizar los valores en la base de datos
        INSERT INTO parametros_sistema (
            clave,
            valor,
            descripcion,
            creado_por
        ) VALUES 
        (
            'INTERVALO_INSPECCION_KM',
            v_intervalo_inspeccion_km::TEXT,
            'Intervalo en kilómetros entre inspecciones de neumáticos',
            'SISTEMA'
        ),
        (
            'INTERVALO_INSPECCION_DIAS',
            v_intervalo_inspeccion_dias::TEXT,
            'Intervalo en días entre inspecciones de neumáticos',
            'SISTEMA'
        )
        ON CONFLICT (clave) 
        DO UPDATE SET 
            valor = EXCLUDED.valor,
            descripcion = EXCLUDED.descripcion,
            actualizado_en = NOW(),
            actualizado_por = 'SISTEMA';
    END;
    
    -- Calcular el próximo kilometraje de inspección
    v_proxima_inspeccion_km := v_odometro_actual + v_intervalo_inspeccion_km;
    
    -- Calcular la fecha de próxima inspección basada en el kilometraje
    -- Obtener el promedio de kilómetros por día (últimos 90 días)
    WITH eventos_recientes AS (
        SELECT 
            odometro_vehiculo_en_evento,
            timestamp_evento,
            LAG(odometro_vehiculo_en_evento) OVER (ORDER BY timestamp_evento) as odometro_anterior,
            LAG(timestamp_evento) OVER (ORDER BY timestamp_evento) as fecha_anterior
        FROM eventos_neumaticos
        WHERE neumatico_id = p_neumatico_id
        AND odometro_vehiculo_en_evento IS NOT NULL
        AND timestamp_evento >= (NOW() - INTERVAL '90 days')
        ORDER BY timestamp_evento
    )
    SELECT COALESCE(
        (SELECT 
            (MAX(odometro_vehiculo_en_evento) - MIN(odometro_vehiculo_en_evento)) / 
            NULLIF(EXTRACT(DAY FROM (MAX(timestamp_evento) - MIN(timestamp_evento))), 0)
         FROM eventos_recientes
         WHERE odometro_anterior IS NOT NULL
         AND fecha_anterior IS NOT NULL
         AND odometro_vehiculo_en_evento > odometro_anterior
         AND timestamp_evento > fecha_anterior),
        100  -- Valor por defecto: 100 km/día
    ) INTO v_kilometros_por_dia;
    
    -- Calcular días hasta la próxima inspección basado en el kilometraje
    IF v_kilometros_por_dia > 0 AND v_proxima_inspeccion_km > v_odometro_actual THEN
        v_dias_restantes := CEIL((v_proxima_inspeccion_km - v_odometro_actual) / v_kilometros_por_dia);
    END IF;
    
    -- Asegurar un mínimo de días hasta la próxima inspección
    IF v_dias_restantes IS NULL OR v_dias_restantes < 1 THEN
        v_dias_restantes := 1;  -- Mínimo 1 día
    END IF;
    
    -- Calcular la fecha de próxima inspección
    v_proxima_inspeccion_fecha := v_fecha_actual + (v_dias_restantes || ' days')::INTERVAL;
    
    -- Verificar también por fecha (independientemente del kilometraje)
    -- Obtener la fecha de la última inspección
    SELECT MAX(timestamp_evento)
    INTO v_ultimo_evento_inspeccion
    FROM eventos_neumaticos
    WHERE neumatico_id = p_neumatico_id
      AND tipo_evento = 'INSPECCION';
    
    -- Si no hay inspección previa, usar la fecha actual
    IF v_ultimo_evento_inspeccion IS NULL THEN
        v_ultimo_evento_inspeccion := v_fecha_actual;
    END IF;
    
    -- Calcular días desde la última inspección
    v_dias_desde_ultima_inspeccion := v_fecha_actual::date - v_ultimo_evento_inspeccion::date;
    
    -- Si ya pasó el intervalo de días desde la última inspección, programar para mañana
    IF v_dias_desde_ultima_inspeccion >= v_intervalo_inspeccion_dias THEN
        v_proxima_inspeccion_fecha := LEAST(v_proxima_inspeccion_fecha, v_fecha_actual + INTERVAL '1 day');
    END IF;
    
    -- Actualizar el neumático con la próxima fecha y kilómetro de inspección
    UPDATE neumaticos
    SET 
        proxima_inspeccion_km = v_proxima_inspeccion_km,
        proxima_inspeccion_fecha = v_proxima_inspeccion_fecha,
        actualizado_en = NOW()
    WHERE id = p_neumatico_id;
    
EXCEPTION WHEN OTHERS THEN
    -- En caso de error, registrar y continuar
    RAISE WARNING 'Error al actualizar próxima inspección para neumático %: %', p_neumatico_id, SQLERRM;
END;
$$;


ALTER FUNCTION public.actualizar_proxima_inspeccion(p_neumatico_id uuid) OWNER TO postgres;

--
-- Name: FUNCTION actualizar_proxima_inspeccion(p_neumatico_id uuid); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.actualizar_proxima_inspeccion(p_neumatico_id uuid) IS 'Actualiza la próxima fecha y kilómetro de inspección recomendados para un neumático, basado en su uso reciente';


--
-- Name: actualizar_tasa_desgaste_inspeccion(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.actualizar_tasa_desgaste_inspeccion() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_neumatico_id UUID;
    v_es_primera_inspeccion BOOLEAN;
    v_profundidad_inicial NUMERIC(5,2);
    v_profundidad_actual NUMERIC(5,2);
    v_kilometraje_vida_actual INTEGER;
    v_tasa_desgaste_calculada NUMERIC(10,8);
BEGIN
    -- Solo procesar para eventos de inspección
    IF NEW.tipo_evento = 'INSPECCION' AND NEW.profundidad_remanente_mm IS NOT NULL THEN
        v_neumatico_id := NEW.neumatico_id;
        v_profundidad_actual := NEW.profundidad_remanente_mm;
        
        -- Obtener datos actuales del neumático
        SELECT 
            profundidad_inicio_vida_actual_mm,
            kilometraje_vida_actual
        INTO 
            v_profundidad_inicial,
            v_kilometraje_vida_actual
        FROM neumaticos
        WHERE id = v_neumatico_id
        FOR UPDATE;
        
        -- Verificar si es la primera inspección después de instalación
        SELECT COUNT(*) = 0 INTO v_es_primera_inspeccion
        FROM eventos_neumaticos
        WHERE neumatico_id = v_neumatico_id
        AND tipo_evento = 'INSPECCION'
        AND id != COALESCE(NEW.id, '00000000-0000-0000-0000-000000000000');
        
        -- Calcular tasa de desgaste solo si hay datos suficientes
        IF v_profundidad_inicial IS NOT NULL AND v_kilometraje_vida_actual > 0 AND 
           v_profundidad_actual < v_profundidad_inicial THEN
           
            v_tasa_desgaste_calculada := (v_profundidad_inicial - v_profundidad_actual) / 
                                        v_kilometraje_vida_actual;
            
            -- Actualizar tasa de desgaste y profundidad actual
            UPDATE neumaticos
            SET 
                tasa_desgaste_actual_mm_km = v_tasa_desgaste_calculada,
                profundidad_remanente_actual_mm = v_profundidad_actual,
                fecha_ultima_medicion_profundidad = NOW(),
                actualizado_en = NOW()
            WHERE id = v_neumatico_id;
            
            -- Registrar en datos del evento
            NEW.datos_evento = COALESCE(NEW.datos_evento, '{}'::jsonb) || 
                             jsonb_build_object(
                                 'tasa_desgaste_calculada', v_tasa_desgaste_calculada,
                                 'es_primera_inspeccion', v_es_primera_inspeccion
                             );
        END IF;
    END IF;
    
    RETURN NEW;
EXCEPTION WHEN OTHERS THEN
    RAISE WARNING 'Error en actualizar_tasa_desgaste_inspeccion: %', SQLERRM;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.actualizar_tasa_desgaste_inspeccion() OWNER TO postgres;

--
-- Name: FUNCTION actualizar_tasa_desgaste_inspeccion(); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.actualizar_tasa_desgaste_inspeccion() IS 'Actualizada el 2025-05-24: Mejorado el cálculo de la tasa de desgaste en inspecciones';


--
-- Name: actualizar_tasa_desgaste_real(uuid, numeric, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.actualizar_tasa_desgaste_real(p_neumatico_id uuid, p_profundidad_actual_mm numeric, p_kilometraje_vida_actual integer) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_profundidad_inicial NUMERIC(5,2);
    v_tasa_desgaste NUMERIC(10,6);
BEGIN
    -- Get the initial depth for the current life
    SELECT profundidad_inicio_vida_actual_mm
    INTO v_profundidad_inicial
    FROM neumaticos
    WHERE id = p_neumatico_id;
    
    -- Calculate wear rate in mm/km if we have valid data
    IF v_profundidad_inicial IS NOT NULL AND 
       p_profundidad_actual_mm IS NOT NULL AND 
       p_kilometraje_vida_actual > 0 AND
       v_profundidad_inicial > p_profundidad_actual_mm THEN
        
        v_tasa_desgaste := (v_profundidad_inicial - p_profundidad_actual_mm) / p_kilometraje_vida_actual;
        
        -- Update the tire's wear rate
        UPDATE neumaticos
        SET tasa_desgaste_actual_mm_km = v_tasa_desgaste
        WHERE id = p_neumatico_id;
        
        RETURN v_tasa_desgaste;
    END IF;
    
    -- Return NULL if we can't calculate the rate
    RETURN NULL;
EXCEPTION WHEN OTHERS THEN
    RAISE WARNING 'Error al actualizar tasa de desgaste para neumático %: %', p_neumatico_id, SQLERRM;
    RETURN NULL;
END;
$$;


ALTER FUNCTION public.actualizar_tasa_desgaste_real(p_neumatico_id uuid, p_profundidad_actual_mm numeric, p_kilometraje_vida_actual integer) OWNER TO postgres;

--
-- Name: actualizar_tasa_desgaste_real(uuid, numeric, numeric, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.actualizar_tasa_desgaste_real(p_neumatico_id uuid, p_profundidad_inicio_mm numeric, p_profundidad_fin_mm numeric, p_kilometraje_vida_actual integer) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_tasa_desgaste numeric;
    v_profundidad_desgastada_mm numeric;
BEGIN
    -- Calcular la profundidad desgastada
    v_profundidad_desgastada_mm := p_profundidad_inicio_mm - p_profundidad_fin_mm;
    
    -- Calcular la tasa de desgaste (mm/km)
    IF p_kilometraje_vida_actual > 0 AND v_profundidad_desgastada_mm > 0 THEN
        v_tasa_desgaste := v_profundidad_desgastada_mm / p_kilometraje_vida_actual;
    ELSE
        v_tasa_desgaste := NULL;
    END IF;
    
    -- Actualizar el neumático con la nueva tasa de desgaste
    UPDATE neumaticos
    SET 
        tasa_desgaste_actual_mm_km = v_tasa_desgaste,
        actualizado_en = NOW()
    WHERE id = p_neumatico_id;
    
    RETURN v_tasa_desgaste;
EXCEPTION WHEN OTHERS THEN
    RAISE EXCEPTION 'Error en actualizar_tasa_desgaste_real: %', SQLERRM;
END;
$$;


ALTER FUNCTION public.actualizar_tasa_desgaste_real(p_neumatico_id uuid, p_profundidad_inicio_mm numeric, p_profundidad_fin_mm numeric, p_kilometraje_vida_actual integer) OWNER TO postgres;

--
-- Name: FUNCTION actualizar_tasa_desgaste_real(p_neumatico_id uuid, p_profundidad_inicio_mm numeric, p_profundidad_fin_mm numeric, p_kilometraje_vida_actual integer); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.actualizar_tasa_desgaste_real(p_neumatico_id uuid, p_profundidad_inicio_mm numeric, p_profundidad_fin_mm numeric, p_kilometraje_vida_actual integer) IS 'Calcula y actualiza la tasa de desgaste real de un neumático basado en la profundidad inicial, final y el kilometraje.

Parámetros:
- p_neumatico_id: ID del neumático a actualizar
- p_profundidad_inicio_mm: Profundidad del dibujo al inicio del período (mm)
- p_profundidad_fin_mm: Profundidad del dibujo al final del período (mm)
- p_kilometraje_vida_actual: Kilometraje recorrido en la vida actual (km)

Retorna:
- La tasa de desgaste calculada en mm/km o NULL si no se pudo calcular';


--
-- Name: actualizar_tasa_desgaste_real_safe(uuid, numeric, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.actualizar_tasa_desgaste_real_safe(p_neumatico_id uuid, p_profundidad_actual_mm numeric, p_kilometros_recorridos integer) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_profundidad_inicial_mm NUMERIC;
    v_tasa_desgaste NUMERIC;
    v_error_message TEXT;
    v_error_context TEXT;
    v_error_detail TEXT;
BEGIN
    -- Obtener la profundidad inicial de la última instalación
    SELECT profundidad_instalacion_mm
    INTO v_profundidad_inicial_mm
    FROM neumaticos
    WHERE id = p_neumatico_id;
    
    -- Verificar que tengamos todos los datos necesarios
    IF v_profundidad_inicial_mm IS NULL OR p_profundidad_actual_mm IS NULL OR p_kilometros_recorridos IS NULL OR p_kilometros_recorridos <= 0 THEN
        RETURN NULL;
    END IF;
    
    -- Calcular la tasa de desgaste (mm por 1,000 km)
    v_tasa_desgaste := ((v_profundidad_inicial_mm - p_profundidad_actual_mm) / p_kilometros_recorridos) * 1000;
    
    -- Actualizar el neumático con la nueva tasa de desgaste
    UPDATE neumaticos
    SET 
        tasa_desgaste_real = v_tasa_desgaste,
        actualizado_en = NOW()
    WHERE id = p_neumatico_id;
    
    RETURN v_tasa_desgaste;
    
EXCEPTION WHEN OTHERS THEN
    -- Capturar información del error
    GET STACKED DIAGNOSTICS
        v_error_message = MESSAGE_TEXT,
        v_error_context = PG_EXCEPTION_CONTEXT,
        v_error_detail = PG_EXCEPTION_DETAIL;
    
    -- Intentar registrar el error en auditoria_log si es posible
    BEGIN
        INSERT INTO auditoria_log (
            esquema_tabla,
            nombre_tabla,
            operacion,
            usuario_db,
            id_entidad,
            datos_nuevos,
            contexto_aplicacion
        ) VALUES (
            'public',
            'neumaticos',
            'UPDATE',
            CURRENT_USER,
            p_neumatico_id::text,
            jsonb_build_object(
                'error', 'Error en actualizar_tasa_desgaste_real_safe',
                'mensaje', v_error_message,
                'contexto', v_error_context,
                'detalle', v_error_detail
            ),
            jsonb_build_object(
                'funcion', 'actualizar_tasa_desgaste_real_safe',
                'neumatico_id', p_neumatico_id,
                'profundidad_actual_mm', p_profundidad_actual_mm,
                'kilometros_recorridos', p_kilometros_recorridos
            )
        );
    EXCEPTION WHEN OTHERS THEN
        -- Si falla el registro de auditoría, simplemente continuamos
        NULL;
    END;
    
    RETURN NULL; -- Devolver NULL en caso de error
END;
$$;


ALTER FUNCTION public.actualizar_tasa_desgaste_real_safe(p_neumatico_id uuid, p_profundidad_actual_mm numeric, p_kilometros_recorridos integer) OWNER TO postgres;

--
-- Name: actualizar_timestamp(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.actualizar_timestamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.actualizado_en = NOW();
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.actualizar_timestamp() OWNER TO postgres;

--
-- Name: actualizar_vida_util_neumaticos(); Type: PROCEDURE; Schema: public; Owner: postgres
--

CREATE PROCEDURE public.actualizar_vida_util_neumaticos()
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_actualizados INT;
BEGIN
    UPDATE neumaticos
    SET 
        vida_util_restante_km = calcular_vida_util_restante(id),
        actualizado_en = NOW()
    WHERE 
        estado_actual NOT IN ('DESECHADO')  -- Solo excluimos DESECHADO
        AND calcular_vida_util_restante(id) IS DISTINCT FROM COALESCE(vida_util_restante_km, -1);
    
    GET DIAGNOSTICS v_actualizados = ROW_COUNT;
    
    RAISE NOTICE 'Se actualizó la vida útil de % neumáticos', v_actualizados;
END;
$$;


ALTER PROCEDURE public.actualizar_vida_util_neumaticos() OWNER TO postgres;

--
-- Name: actualizar_vistas_materializadas(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.actualizar_vistas_materializadas() RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    RAISE NOTICE 'Actualizando vistas materializadas...';
    
    -- Actualizar vistas con índices únicos usando CONCURRENTLY
    BEGIN
        REFRESH MATERIALIZED VIEW CONCURRENTLY mv_resumen_neumaticos_estado;
        RAISE NOTICE '  - mv_resumen_neumaticos_estado actualizada';
    EXCEPTION WHEN OTHERS THEN
        RAISE WARNING 'Error al actualizar mv_resumen_neumaticos_estado: %', SQLERRM;
    END;
    
    BEGIN
        REFRESH MATERIALIZED VIEW CONCURRENTLY mv_eventos_recientes;
        RAISE NOTICE '  - mv_eventos_recientes actualizada';
    EXCEPTION WHEN OTHERS THEN
        RAISE WARNING 'Error al actualizar mv_eventos_recientes: %', SQLERRM;
    END;
    
    BEGIN
        REFRESH MATERIALIZED VIEW CONCURRENTLY mv_desempeno_modelos;
        RAISE NOTICE '  - mv_desempeno_modelos actualizada';
    EXCEPTION WHEN OTHERS THEN
        RAISE WARNING 'Error al actualizar mv_desempeno_modelos: %', SQLERRM;
    END;
    
    RAISE NOTICE 'Vistas materializadas actualizadas correctamente.';
END;
$$;


ALTER FUNCTION public.actualizar_vistas_materializadas() OWNER TO postgres;

--
-- Name: agregar_auditoria_tabla(text, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.agregar_auditoria_tabla(p_esquema text, p_tabla text) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Eliminar trigger existente si existe
    EXECUTE format('DROP TRIGGER IF EXISTS tr_audit_%s ON %I.%I CASCADE', 
                  p_tabla, p_esquema, p_tabla);
    
    -- Crear nuevo trigger
    EXECUTE format('CREATE TRIGGER tr_audit_%s
                  AFTER INSERT OR UPDATE OR DELETE ON %I.%I
                  FOR EACH ROW EXECUTE FUNCTION audit_high_priority_trigger()',
                  p_tabla, p_esquema, p_tabla);
    
    RAISE NOTICE 'Creado trigger de auditoría para %.%', p_esquema, p_tabla;
END;
$$;


ALTER FUNCTION public.agregar_auditoria_tabla(p_esquema text, p_tabla text) OWNER TO postgres;

--
-- Name: audit_high_priority_trigger(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.audit_high_priority_trigger() RETURNS trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    v_old_jsonb JSONB;
    v_new_jsonb JSONB;
    v_changes JSONB;
    v_changed_keys TEXT[] := '{}';
    v_key TEXT;
    v_old_value TEXT;
    v_new_value TEXT;
BEGIN
    IF (TG_OP = 'DELETE') THEN
        -- Para DELETE, registrar todos los datos antiguos
        INSERT INTO auditoria_log (
            esquema_tabla, 
            nombre_tabla, 
            operacion,
            id_entidad, 
            datos_antiguos,
            usuario_aplicacion_id,
            usuario_aplicacion_username,
            direccion_ip,
            user_agent
        ) VALUES (
            TG_TABLE_SCHEMA, 
            TG_TABLE_NAME, 
            'DELETE',
            OLD.id, 
            row_to_json(OLD)::jsonb,
            current_setting('app.current_user_id', TRUE)::uuid,
            current_setting('app.current_username', TRUE),
            current_setting('app.client_ip', TRUE),
            current_setting('app.user_agent', TRUE)
        );
        RETURN OLD;
        
    ELSIF (TG_OP = 'UPDATE') THEN
        -- Para UPDATE, calcular solo los campos que cambiaron
        v_old_jsonb := row_to_json(OLD)::jsonb;
        v_new_jsonb := row_to_json(NEW)::jsonb;
        v_changes := '{}'::jsonb;
        
        -- Comparar cada campo
        FOR v_key IN (SELECT jsonb_object_keys(v_new_jsonb)) LOOP
            -- Ignorar campos de auditoría que siempre cambian
            CONTINUE WHEN v_key IN ('actualizado_en', 'actualizado_por');
            
            v_old_value := v_old_jsonb->>v_key;
            v_new_value := v_new_jsonb->>v_key;
            
            -- Si el valor cambió, agregar al objeto de cambios
            IF (v_old_value IS DISTINCT FROM v_new_value) THEN
                v_changes := jsonb_insert(v_changes, ARRAY[v_key], to_jsonb(v_new_value));
                v_changed_keys := v_changed_keys || v_key;
            END IF;
        END LOOP;
        
        -- Solo registrar si hay cambios reales (además de los campos de auditoría)
        IF array_length(v_changed_keys, 1) > 0 THEN
            INSERT INTO auditoria_log (
                esquema_tabla, 
                nombre_tabla, 
                operacion,
                id_entidad, 
                datos_antiguos, 
                datos_nuevos, 
                cambios,
                usuario_aplicacion_id,
                usuario_aplicacion_username,
                direccion_ip,
                user_agent
            ) VALUES (
                TG_TABLE_SCHEMA, 
                TG_TABLE_NAME, 
                'UPDATE',
                NEW.id, 
                v_old_jsonb,
                v_new_jsonb,
                v_changes,
                current_setting('app.current_user_id', TRUE)::uuid,
                current_setting('app.current_username', TRUE),
                current_setting('app.client_ip', TRUE),
                current_setting('app.user_agent', TRUE)
            );
        END IF;
        RETURN NEW;
        
    ELSIF (TG_OP = 'INSERT') THEN
        -- Para INSERT, registrar todos los datos nuevos
        INSERT INTO auditoria_log (
            esquema_tabla, 
            nombre_tabla, 
            operacion,
            id_entidad, 
            datos_nuevos,
            usuario_aplicacion_id,
            usuario_aplicacion_username,
            direccion_ip,
            user_agent
        ) VALUES (
            TG_TABLE_SCHEMA, 
            TG_TABLE_NAME, 
            'INSERT',
            NEW.id, 
            row_to_json(NEW)::jsonb,
            current_setting('app.current_user_id', TRUE)::uuid,
            current_setting('app.current_username', TRUE),
            current_setting('app.client_ip', TRUE),
            current_setting('app.user_agent', TRUE)
        );
        RETURN NEW;
    END IF;
    
    -- Para operaciones no manejadas, devolver NULL
    RETURN NULL;
EXCEPTION
    WHEN OTHERS THEN
        -- En caso de error, registrar el error y continuar
        RAISE WARNING 'Error en la función de auditoría: %', SQLERRM;
        
        -- Devolver el registro apropiado según la operación
        IF (TG_OP = 'DELETE') THEN
            RETURN OLD;
        ELSIF (TG_OP = 'INSERT' OR TG_OP = 'UPDATE') THEN
            RETURN NEW;
        END IF;
        
        RETURN NULL;
END;
$$;


ALTER FUNCTION public.audit_high_priority_trigger() OWNER TO postgres;

--
-- Name: FUNCTION audit_high_priority_trigger(); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.audit_high_priority_trigger() IS 'Función de trigger para auditoría de alta prioridad. Registra operaciones INSERT, UPDATE y DELETE en las tablas de auditoría.';


--
-- Name: audit_medium_priority_trigger(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.audit_medium_priority_trigger() RETURNS trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    v_username TEXT;
    v_ip TEXT;
    v_user_agent TEXT;
    v_user_id TEXT;
    v_datos_antiguos JSONB;
    v_datos_nuevos JSONB;
    v_cambios JSONB;
    v_query TEXT;
BEGIN
    -- Obtener valores de las variables de sesión con manejo de NULL
    BEGIN
        v_username := current_setting('app.current_username', TRUE);
    EXCEPTION WHEN OTHERS THEN
        v_username := NULL;
    END;
    
    BEGIN
        v_ip := current_setting('app.client_ip', TRUE);
    EXCEPTION WHEN OTHERS THEN
        v_ip := NULL;
    END;
    
    BEGIN
        v_user_agent := current_setting('app.user_agent', TRUE);
    EXCEPTION WHEN OTHERS THEN
        v_user_agent := NULL;
    END;
    
    BEGIN
        v_user_id := current_setting('app.current_user_id', TRUE);
    EXCEPTION WHEN OTHERS THEN
        v_user_id := NULL;
    END;
    
    -- Obtener la consulta SQL que activó el trigger
    v_query := current_query();
    
    IF (TG_OP = 'DELETE') THEN
        -- Para DELETE, registrar el registro completo como datos_antiguos
        v_datos_antiguos := row_to_json(OLD)::jsonb;
        v_datos_antiguos := jsonb_set(v_datos_antiguos, '{deleted_at}', to_jsonb(NOW()));
        
        INSERT INTO auditoria_log (
            esquema_tabla, 
            nombre_tabla, 
            operacion,
            id_entidad, 
            datos_antiguos,
            usuario_aplicacion_username,
            usuario_aplicacion_id,
            direccion_ip,
            user_agent,
            query_ejecutada
        ) VALUES (
            TG_TABLE_SCHEMA, 
            TG_TABLE_NAME, 
            'DELETE',
            OLD.id, 
            v_datos_antiguos,
            v_username,
            v_user_id::uuid,
            v_ip,
            v_user_agent,
            v_query
        );
        RETURN OLD;
        
    ELSIF (TG_OP = 'UPDATE') THEN
        -- Para UPDATE, registrar tanto los datos antiguos como los nuevos
        v_datos_antiguos := row_to_json(OLD)::jsonb;
        v_datos_nuevos := row_to_json(NEW)::jsonb;
        
        -- Calcular solo los campos que cambiaron, excluyendo los campos de auditoría
        SELECT jsonb_object_agg(
            key, 
            jsonb_build_object('old', v_datos_antiguos->>key, 'new', v_datos_nuevos->>key)
        ) INTO v_cambios
        FROM jsonb_object_keys(v_datos_nuevos) as key
        WHERE 
            (v_datos_antiguos->>key IS DISTINCT FROM v_datos_nuevos->>key)
            AND key NOT IN ('actualizado_en', 'actualizado_por', 'creado_en', 'creado_por');
        
        -- Si no hay cambios relevantes, no registrar nada
        IF v_cambios IS NULL OR jsonb_typeof(v_cambios) = 'null' OR v_cambios = '{}'::jsonb THEN
            RETURN NEW;
        END IF;
        
        INSERT INTO auditoria_log (
            esquema_tabla, 
            nombre_tabla, 
            operacion,
            id_entidad, 
            datos_antiguos,
            datos_nuevos,
            cambios,
            usuario_aplicacion_username,
            usuario_aplicacion_id,
            direccion_ip,
            user_agent,
            query_ejecutada
        ) VALUES (
            TG_TABLE_SCHEMA, 
            TG_TABLE_NAME, 
            'UPDATE',
            NEW.id, 
            v_datos_antiguos,
            v_datos_nuevos,
            v_cambios,
            v_username,
            v_user_id::uuid,
            v_ip,
            v_user_agent,
            v_query
        );
        RETURN NEW;
        
    ELSIF (TG_OP = 'INSERT') THEN
        -- Para INSERT, registrar el registro completo como datos_nuevos
        v_datos_nuevos := row_to_json(NEW)::jsonb;
        
        INSERT INTO auditoria_log (
            esquema_tabla, 
            nombre_tabla, 
            operacion,
            id_entidad, 
            datos_nuevos,
            usuario_aplicacion_username,
            usuario_aplicacion_id,
            direccion_ip,
            user_agent,
            query_ejecutada
        ) VALUES (
            TG_TABLE_SCHEMA, 
            TG_TABLE_NAME, 
            'INSERT',
            NEW.id, 
            v_datos_nuevos,
            v_username,
            v_user_id::uuid,
            v_ip,
            v_user_agent,
            v_query
        );
        RETURN NEW;
    END IF;
    
    RETURN NULL;
END;
$$;


ALTER FUNCTION public.audit_medium_priority_trigger() OWNER TO postgres;

--
-- Name: FUNCTION audit_medium_priority_trigger(); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.audit_medium_priority_trigger() IS 'Función de trigger para auditar operaciones en tablas.

Registra operaciones INSERT, UPDATE y DELETE en la tabla auditoria_log.

Para operaciones UPDATE, registra tanto los datos antiguos como los nuevos, 
y calcula los campos que cambiaron en el campo "cambios".

Configuración requerida en la sesión:
- app.current_username: Nombre de usuario de la aplicación
- app.current_user_id: ID del usuario de la aplicación (opcional)
- app.client_ip: Dirección IP del cliente (opcional)
- app.user_agent: User-Agent del cliente (opcional)';


--
-- Name: audit_neumaticos_trigger(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.audit_neumaticos_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_username TEXT;
    v_user_id TEXT;
    v_ip TEXT;
    v_user_agent TEXT;
    v_query TEXT;
    v_datos_antiguos JSONB;
    v_datos_nuevos JSONB;
    v_cambios JSONB;
    v_current_setting TEXT;
BEGIN
    -- Verificar si la auditoría está activada para esta tabla
    IF NOT EXISTS (
        SELECT 1
        FROM configuracion_auditoria
        WHERE nombre_tabla = 'neumaticos'
        AND activo = true
    ) THEN
        RETURN NULL;
    END IF;

    -- Obtener información del contexto de la aplicación
    BEGIN
        -- Intentar obtener el nombre de usuario de la sesión actual
        v_username := current_setting('app.current_username', true);
    EXCEPTION WHEN OTHERS THEN
        v_username := 'sistema';
    END;
    
    BEGIN
        v_user_id := current_setting('app.current_user_id', true);
    EXCEPTION WHEN OTHERS THEN
        v_user_id := NULL;
    END;
    
    BEGIN
        v_ip := current_setting('app.client_ip', true);
    EXCEPTION WHEN OTHERS THEN
        v_ip := NULL;
    END;
    
    BEGIN
        v_user_agent := current_setting('app.user_agent', true);
    EXCEPTION WHEN OTHERS THEN
        v_user_agent := NULL;
    END;
    
    BEGIN
        v_query := current_setting('app.query', true);
    EXCEPTION WHEN OTHERS THEN
        v_query := NULL;
    END;

    -- Manejar diferentes tipos de operaciones
    IF (TG_OP = 'DELETE') THEN
        -- Para DELETE, registrar el registro completo como datos_antiguos
        v_datos_antiguos := row_to_json(OLD)::jsonb;
        
        INSERT INTO auditoria_log (
            esquema_tabla,
            nombre_tabla,
            operacion,
            id_entidad,
            datos_antiguos,
            usuario_aplicacion_username,
            usuario_aplicacion_id,
            direccion_ip,
            user_agent,
            query_ejecutada
        ) VALUES (
            TG_TABLE_SCHEMA,
            TG_TABLE_NAME,
            'DELETE',
            OLD.id::text,
            v_datos_antiguos,
            v_username,
            v_user_id::uuid,
            v_ip,
            v_user_agent,
            v_query
        );
        RETURN OLD;
        
    ELSIF (TG_OP = 'UPDATE') THEN
        -- Para UPDATE, registrar tanto los datos antiguos como los nuevos
        v_datos_antiguos := row_to_json(OLD)::jsonb;
        v_datos_nuevos := row_to_json(NEW)::jsonb;
        
        -- Calcular solo los campos que cambiaron, excluyendo los campos de auditoría
        SELECT jsonb_object_agg(
            key,
            jsonb_build_object('old', v_datos_antiguos->>key, 'new', v_datos_nuevos->>key)
        ) INTO v_cambios
        FROM jsonb_object_keys(v_datos_nuevos) as key
        WHERE 
            (v_datos_antiguos->>key IS DISTINCT FROM v_datos_nuevos->>key)
            AND key NOT IN ('actualizado_en', 'actualizado_por', 'creado_en', 'creado_por');
        
        -- Si no hay cambios relevantes, no registrar nada
        IF v_cambios IS NULL OR jsonb_typeof(v_cambios) = 'null' OR v_cambios = '{}'::jsonb THEN
            RETURN NEW;
        END IF;
        
        INSERT INTO auditoria_log (
            esquema_tabla,
            nombre_tabla,
            operacion,
            id_entidad,
            datos_antiguos,
            datos_nuevos,
            cambios,
            usuario_aplicacion_username,
            usuario_aplicacion_id,
            direccion_ip,
            user_agent,
            query_ejecutada
        ) VALUES (
            TG_TABLE_SCHEMA,
            TG_TABLE_NAME,
            'UPDATE',
            NEW.id::text,
            v_datos_antiguos,
            v_datos_nuevos,
            v_cambios,
            v_username,
            v_user_id::uuid,
            v_ip,
            v_user_agent,
            v_query
        );
        RETURN NEW;
        
    ELSIF (TG_OP = 'INSERT') THEN
        -- Para INSERT, registrar el registro completo como datos_nuevos
        v_datos_nuevos := row_to_json(NEW)::jsonb;
        
        INSERT INTO auditoria_log (
            esquema_tabla,
            nombre_tabla,
            operacion,
            id_entidad,
            datos_nuevos,
            usuario_aplicacion_username,
            usuario_aplicacion_id,
            direccion_ip,
            user_agent,
            query_ejecutada
        ) VALUES (
            TG_TABLE_SCHEMA,
            TG_TABLE_NAME,
            'INSERT',
            NEW.id::text,
            v_datos_nuevos,
            v_username,
            v_user_id::uuid,
            v_ip,
            v_user_agent,
            v_query
        );
        RETURN NEW;
    END IF;
    
    RETURN NULL;
END;
$$;


ALTER FUNCTION public.audit_neumaticos_trigger() OWNER TO postgres;

--
-- Name: audit_registros_odometro(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.audit_registros_odometro() RETURNS trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    v_username TEXT;
    v_changes JSONB;
    v_user_id UUID;
    v_schema_name TEXT := 'public'; -- Esquema por defecto
BEGIN
    -- Determinar el ID de usuario a registrar
    IF TG_OP = 'INSERT' THEN
        v_user_id := NEW.creado_por;
    ELSIF TG_OP = 'UPDATE' THEN
        v_user_id := NEW.creado_por;  -- Usar creado_por ya que no hay actualizado_por
    ELSE
        v_user_id := OLD.creado_por;
    END IF;
    
    -- Obtener el username del usuario si existe
    SELECT username INTO v_username 
    FROM usuarios 
    WHERE id = v_user_id
    LIMIT 1;

    IF TG_OP = 'INSERT' THEN
        INSERT INTO auditoria_log (
            esquema_tabla,
            nombre_tabla,
            operacion,
            id_entidad,
            usuario_aplicacion_id,
            usuario_aplicacion_username,
            datos_nuevos,
            cambios
        ) VALUES (
            v_schema_name,
            TG_TABLE_NAME,
            'INSERT',
            NEW.id,
            v_user_id,
            v_username,
            to_jsonb(NEW) - 'id',
            to_jsonb(NEW) - 'id'
        );
        RETURN NEW;
        
    ELSIF TG_OP = 'UPDATE' THEN
        -- Calcular solo los campos que cambiaron
        SELECT jsonb_object_agg(key, value) INTO v_changes
        FROM jsonb_each(to_jsonb(NEW))
        WHERE key != 'id'
        AND (to_jsonb(OLD)->>key) IS DISTINCT FROM (to_jsonb(NEW)->>key);
        
        INSERT INTO auditoria_log (
            esquema_tabla,
            nombre_tabla,
            operacion,
            id_entidad,
            usuario_aplicacion_id,
            usuario_aplicacion_username,
            datos_antiguos,
            datos_nuevos,
            cambios
        ) VALUES (
            v_schema_name,
            TG_TABLE_NAME,
            'UPDATE',
            NEW.id,
            v_user_id,
            v_username,
            to_jsonb(OLD) - 'id',
            to_jsonb(NEW) - 'id',
            COALESCE(v_changes, '{}'::jsonb)
        );
        RETURN NEW;
        
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO auditoria_log (
            esquema_tabla,
            nombre_tabla,
            operacion,
            id_entidad,
            usuario_aplicacion_id,
            usuario_aplicacion_username,
            datos_antiguos
        ) VALUES (
            v_schema_name,
            TG_TABLE_NAME,
            'DELETE',
            OLD.id,
            v_user_id,
            v_username,
            to_jsonb(OLD) - 'id'
        );
        RETURN OLD;
    END IF;
    
    RETURN NULL;
END;
$$;


ALTER FUNCTION public.audit_registros_odometro() OWNER TO postgres;

--
-- Name: audit_relation_table_trigger(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.audit_relation_table_trigger() RETURNS trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        -- Para DELETE, registrar solo las claves foráneas
        INSERT INTO auditoria_log (
            esquema_tabla, 
            nombre_tabla, 
            operacion,
            datos_antiguos,
            usuario_aplicacion_username,
            direccion_ip
        ) VALUES (
            TG_TABLE_SCHEMA, 
            TG_TABLE_NAME, 
            'DELETE',
            row_to_json(OLD)::jsonb || jsonb_build_object('deleted_at', NOW()),
            current_setting('app.current_username', TRUE),
            current_setting('app.client_ip', TRUE)
        );
        RETURN OLD;
        
    ELSIF (TG_OP = 'UPDATE') THEN
        -- Para UPDATE, registrar solo los cambios
        INSERT INTO auditoria_log (
            esquema_tabla, 
            nombre_tabla, 
            operacion,
            cambios,
            usuario_aplicacion_username,
            direccion_ip
        ) 
        SELECT 
            TG_TABLE_SCHEMA, 
            TG_TABLE_NAME, 
            'UPDATE',
            jsonb_object_agg(
                key, 
                jsonb_build_object('old', row_to_json(OLD)::jsonb->>key, 'new', row_to_json(NEW)::jsonb->>key)
            ) FILTER (
                WHERE row_to_json(OLD)::jsonb->>key IS DISTINCT FROM row_to_json(NEW)::jsonb->>key
                AND key NOT IN ('actualizado_en', 'actualizado_por')
            ),
            current_setting('app.current_username', TRUE),
            current_setting('app.client_ip', TRUE)
        FROM jsonb_object_keys(row_to_json(NEW)::jsonb) as key;
        
        RETURN NEW;
        
    ELSIF (TG_OP = 'INSERT') THEN
        -- Para INSERT, registrar los datos de la relación
        INSERT INTO auditoria_log (
            esquema_tabla, 
            nombre_tabla, 
            operacion,
            datos_nuevos,
            usuario_aplicacion_username,
            direccion_ip
        ) VALUES (
            TG_TABLE_SCHEMA, 
            TG_TABLE_NAME, 
            'INSERT',
            row_to_json(NEW)::jsonb || jsonb_build_object('created_at', NOW()),
            current_setting('app.current_username', TRUE),
            current_setting('app.client_ip', TRUE)
        );
        RETURN NEW;
    END IF;
    
    RETURN NULL;
END;
$$;


ALTER FUNCTION public.audit_relation_table_trigger() OWNER TO postgres;

--
-- Name: FUNCTION audit_relation_table_trigger(); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.audit_relation_table_trigger() IS 'Función de auditoría para tablas de relación que no tienen un campo id único';


--
-- Name: audit_trigger(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.audit_trigger() RETURNS trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    v_old_data JSONB;
    v_new_data JSONB;
    v_changes JSONB;
    v_user_id TEXT;
    v_username TEXT;
    v_id_entidad TEXT;
BEGIN
    -- Obtener el ID de usuario de la aplicación
    BEGIN
        v_user_id := current_setting('app.current_user_id', TRUE);
    EXCEPTION WHEN OTHERS THEN
        v_user_id := NULL;
    END;
    
    -- Obtener el nombre de usuario
    BEGIN
        v_username := current_setting('app.current_username', TRUE);
    EXCEPTION WHEN OTHERS THEN
        v_username := session_user;
    END;
    
    -- Manejar diferentes tipos de operaciones
    IF (TG_OP = 'DELETE') THEN
        v_old_data := to_jsonb(OLD);
        v_new_data := NULL;
        v_changes := NULL;
        v_id_entidad := (v_old_data->>'id')::text;
    ELSIF (TG_OP = 'UPDATE') THEN
        v_old_data := to_jsonb(OLD);
        v_new_data := to_jsonb(NEW);
        v_id_entidad := (v_new_data->>'id')::text;
        
        -- Calcular solo los campos que cambiaron
        SELECT jsonb_object_agg(key, value) INTO v_changes
        FROM jsonb_each(to_jsonb(NEW))
        WHERE (to_jsonb(OLD) ->> key) IS DISTINCT FROM (to_jsonb(NEW) ->> key)
           OR (to_jsonb(OLD) ->> key IS NULL) != (to_jsonb(NEW) ->> key IS NULL);
    ELSIF (TG_OP = 'INSERT') THEN
        v_old_data := NULL;
        v_new_data := to_jsonb(NEW);
        v_changes := NULL;
        v_id_entidad := (v_new_data->>'id')::text;
    END IF;
    
    -- Insertar el registro de auditoría
    INSERT INTO auditoria_log (
        esquema_tabla,
        nombre_tabla,
        operacion,
        usuario_db,
        usuario_aplicacion_id,
        usuario_aplicacion_username,
        id_entidad,
        datos_antiguos,
        datos_nuevos,
        cambios,
        direccion_ip,
        user_agent
    ) VALUES (
        TG_TABLE_SCHEMA,
        TG_TABLE_NAME,
        TG_OP,
        session_user,
        v_user_id::uuid,
        v_username,
        v_id_entidad::uuid,
        v_old_data,
        v_new_data,
        v_changes,
        COALESCE(
            NULLIF(current_setting('app.client_ip', TRUE), ''), 
            inet_client_addr()::text, 
            '0.0.0.0'
        ),
        NULLIF(current_setting('app.user_agent', TRUE), '')
    );
    
    -- Para triggers AFTER, siempre retornar el registro apropiado
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$;


ALTER FUNCTION public.audit_trigger() OWNER TO postgres;

--
-- Name: auditoria_simple(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.auditoria_simple() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_old_data JSONB;
    v_new_data JSONB;
    v_changes JSONB;
    v_pk_columns TEXT[];
    v_pk_values TEXT[];
    v_pk_json JSONB := '{}';
    v_pk_text TEXT;
    v_id_entidad TEXT;
    v_operation TEXT;
    v_table_name TEXT;
    v_schema_name TEXT;
    v_user_name TEXT;
    v_username TEXT;
    v_context JSONB;
    v_query TEXT;
    v_stack_trace TEXT;
BEGIN
    -- Obtener información de la operación
    v_operation := TG_OP;
    v_table_name := TG_TABLE_NAME;
    v_schema_name := TG_TABLE_SCHEMA;
    v_user_name := current_user;
    
    -- Obtener el nombre de usuario de la aplicación si está disponible
    BEGIN
        v_username := current_setting('app.current_user', true);
    EXCEPTION WHEN OTHERS THEN
        v_username := NULL;
    END;
    
    -- Obtener el contexto de la aplicación si está disponible
    BEGIN
        v_context := current_setting('app.context', true)::jsonb;
    EXCEPTION WHEN OTHERS THEN
        v_context := NULL;
    END;
    
    -- Obtener la consulta SQL que activó el trigger si está disponible
    BEGIN
        v_query := current_setting('app.current_query', true);
    EXCEPTION WHEN OTHERS THEN
        v_query := NULL;
    END;
    
    -- Obtener los nombres de las columnas de la clave primaria
    SELECT array_agg(a.attname::TEXT)
    INTO v_pk_columns
    FROM pg_index i
    JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
    WHERE i.indrelid = TG_TABLE_SCHEMA || '.' || TG_TABLE_NAME::regclass
    AND i.indisprimary;
    
    -- Manejar diferentes operaciones
    IF TG_OP = 'UPDATE' THEN
        v_old_data := to_jsonb(OLD);
        v_new_data := to_jsonb(NEW);
        
        -- Calcular solo los campos que cambiaron
        v_changes := (
            SELECT jsonb_object_agg(key, value)
            FROM jsonb_each(v_new_data)
            WHERE (v_old_data->>key) IS DISTINCT FROM (v_new_data->>key)
               OR (v_old_data->>key IS NULL) <> (v_new_data->>key IS NULL)
        );
        
        -- Si no hay cambios reales, salir
        IF v_changes IS NULL OR jsonb_typeof(v_changes) = 'null' THEN
            RETURN NULL;
        END IF;
        
        -- Obtener valores de la clave primaria
        IF v_pk_columns IS NOT NULL THEN
            FOREACH v_pk_text IN ARRAY v_pk_columns LOOP
                v_pk_values := v_pk_values || (v_old_data->>v_pk_text);
                v_pk_json := v_pk_json || jsonb_build_object(v_pk_text, v_old_data->>v_pk_text);
            END LOOP;
            
            -- Usar el primer campo de la clave primaria como id_entidad
            IF array_length(v_pk_columns, 1) > 0 THEN
                v_id_entidad := v_old_data->>v_pk_columns[1];
            END IF;
        END IF;
        
    ELSIF TG_OP = 'DELETE' THEN
        v_old_data := to_jsonb(OLD);
        v_new_data := NULL;
        v_changes := NULL;
        
        -- Obtener valores de la clave primaria
        IF v_pk_columns IS NOT NULL THEN
            FOREACH v_pk_text IN ARRAY v_pk_columns LOOP
                v_pk_values := v_pk_values || (v_old_data->>v_pk_text);
                v_pk_json := v_pk_json || jsonb_build_object(v_pk_text, v_old_data->>v_pk_text);
            END LOOP;
            
            -- Usar el primer campo de la clave primaria como id_entidad
            IF array_length(v_pk_columns, 1) > 0 THEN
                v_id_entidad := v_old_data->>v_pk_columns[1];
            END IF;
        END IF;
        
    ELSIF TG_OP = 'INSERT' THEN
        v_old_data := NULL;
        v_new_data := to_jsonb(NEW);
        v_changes := v_new_data;
        
        -- Obtener valores de la clave primaria
        IF v_pk_columns IS NOT NULL THEN
            FOREACH v_pk_text IN ARRAY v_pk_columns LOOP
                v_pk_values := v_pk_values || (v_new_data->>v_pk_text);
                v_pk_json := v_pk_json || jsonb_build_object(v_pk_text, v_new_data->>v_pk_text);
            END LOOP;
            
            -- Usar el primer campo de la clave primaria como id_entidad
            IF array_length(v_pk_columns, 1) > 0 THEN
                v_id_entidad := v_new_data->>v_pk_columns[1];
            END IF;
        END IF;
    END IF;
    
    -- Insertar el registro de auditoría
    INSERT INTO public.auditoria_log (
        esquema_tabla,
        nombre_tabla,
        operacion,
        usuario_db,
        usuario_aplicacion_username,
        id_entidad,
        datos_antiguos,
        datos_nuevos,
        cambios,
        contexto_aplicacion,
        query_ejecutada
    ) VALUES (
        v_schema_name,
        v_table_name,
        v_operation,
        v_user_name,
        v_username,
        v_id_entidad,  -- Ahora es TEXT, no se intenta convertir a UUID
        v_old_data,
        v_new_data,
        v_changes,
        v_context,
        v_query
    );
    
    -- Para triggers AFTER, siempre retornar el registro apropiado
    IF TG_WHEN = 'AFTER' THEN
        IF TG_OP = 'DELETE' THEN
            RETURN OLD;
        ELSE
            RETURN NEW;
        END IF;
    END IF;
    
    -- Para triggers BEFORE, retornar el registro apropiado
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
    
EXCEPTION WHEN OTHERS THEN
    -- Obtener el stack trace si está disponible
    BEGIN
        v_stack_trace := 'Error: ' || SQLERRM || ' | ' ||
                         'SQLSTATE: ' || SQLSTATE || ' | ' ||
                         'Contexto: ' || v_context::TEXT;
    EXCEPTION WHEN OTHERS THEN
        v_stack_trace := 'Error al obtener detalles del error: ' || SQLERRM;
    END;
    
    -- Registrar el error en la tabla de auditoría
    INSERT INTO public.auditoria_log (
        esquema_tabla,
        nombre_tabla,
        operacion,
        usuario_db,
        usuario_aplicacion_username,
        query_ejecutada,
        datos_nuevos,
        contexto_aplicacion
    ) VALUES (
        v_schema_name,
        v_table_name,
        'ERROR',
        v_user_name,
        v_username,
        v_query,
        jsonb_build_object(
            'error', SQLERRM,
            'sqlstate', SQLSTATE,
            'operation', v_operation,
            'table', v_schema_name || '.' || v_table_name,
            'pk_columns', v_pk_columns,
            'pk_values', v_pk_values
        ),
        jsonb_build_object(
            'context', 'Error en auditoría simplificada',
            'error_detail', SQLERRM,
            'operation', v_operation,
            'table', v_schema_name || '.' || v_table_name,
            'stack', v_stack_trace
        )
    );
    
    -- Relanzar el error original
    RAISE EXCEPTION 'Error en auditoría simplificada: %', SQLERRM
          USING HINT = 'Verifica los datos de la operación ' || v_operation || ' en ' || v_schema_name || '.' || v_table_name,
               DETAIL = 'SQLSTATE: ' || SQLSTATE;
END;
$$;


ALTER FUNCTION public.auditoria_simple() OWNER TO postgres;

--
-- Name: FUNCTION auditoria_simple(); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.auditoria_simple() IS 'Función de trigger para auditoría genérica que registra cambios en cualquier tabla. Maneja correctamente id_entidad como TEXT para evitar problemas de conversión a UUID.';


--
-- Name: buscar_cambios_neumatico(text, text, text, timestamp with time zone, timestamp with time zone, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.buscar_cambios_neumatico(p_campo text, p_valor_anterior text DEFAULT NULL::text, p_valor_nuevo text DEFAULT NULL::text, p_fecha_desde timestamp with time zone DEFAULT NULL::timestamp with time zone, p_fecha_hasta timestamp with time zone DEFAULT NULL::timestamp with time zone, p_limit integer DEFAULT 100) RETURNS TABLE(id_neumatico uuid, operacion text, fecha_hora timestamp with time zone, usuario text, ip text, detalle text)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        al.id_entidad as id_neumatico,
        al.operacion::text,
        al.timestamp_log as fecha_hora,
        COALESCE(al.usuario_aplicacion_username, al.usuario_db) as usuario,
        al.direccion_ip as ip,
        CASE 
            WHEN al.operacion = 'INSERT' THEN 'Nuevo registro'
            WHEN al.operacion = 'UPDATE' THEN (
                SELECT string_agg(
                    key || ': ' || 
                    COALESCE((value->>'old')::text, 'NULL') || ' → ' || 
                    COALESCE((value->>'new')::text, 'NULL'), 
                    ', '
                )
                FROM jsonb_each(al.cambios)
                WHERE key = p_campo
                AND (p_valor_anterior IS NULL OR (value->>'old')::text = p_valor_anterior)
                AND (p_valor_nuevo IS NULL OR (value->>'new')::text = p_valor_nuevo)
            )
            WHEN al.operacion = 'DELETE' THEN 'Registro eliminado'
        END as detalle
    FROM auditoria_log al
    WHERE al.nombre_tabla = 'neumaticos'
    AND (
        -- Para INSERTS: buscar en datos_nuevos
        (al.operacion = 'INSERT' AND al.datos_nuevos->>p_campo IS NOT NULL)
        OR
        -- Para UPDATES: buscar en cambios
        (al.operacion = 'UPDATE' AND al.cambios ? p_campo)
        OR
        -- Para DELETES: buscar en datos_antiguos
        (al.operacion = 'DELETE' AND al.datos_antiguos->>p_campo IS NOT NULL)
    )
    AND (p_fecha_desde IS NULL OR al.timestamp_log >= p_fecha_desde)
    AND (p_fecha_hasta IS NULL OR al.timestamp_log <= p_fecha_hasta)
    ORDER BY al.timestamp_log DESC
    LIMIT p_limit;
END;
$$;


ALTER FUNCTION public.buscar_cambios_neumatico(p_campo text, p_valor_anterior text, p_valor_nuevo text, p_fecha_desde timestamp with time zone, p_fecha_hasta timestamp with time zone, p_limit integer) OWNER TO postgres;

--
-- Name: FUNCTION buscar_cambios_neumatico(p_campo text, p_valor_anterior text, p_valor_nuevo text, p_fecha_desde timestamp with time zone, p_fecha_hasta timestamp with time zone, p_limit integer); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.buscar_cambios_neumatico(p_campo text, p_valor_anterior text, p_valor_nuevo text, p_fecha_desde timestamp with time zone, p_fecha_hasta timestamp with time zone, p_limit integer) IS 'Busca cambios específicos en la tabla neumáticos.
Parámetros:
- p_campo: nombre del campo a buscar
- p_valor_anterior: valor anterior a buscar (opcional)
- p_valor_nuevo: nuevo valor a buscar (opcional)
- p_fecha_desde: fecha mínima de búsqueda (opcional)
- p_fecha_hasta: fecha máxima de búsqueda (opcional)
- p_limit: número máximo de resultados (por defecto 100)

Retorna:
- id_neumatico: ID del neumático modificado
- operacion: tipo de operación
- fecha_hora: cuándo se realizó
- usuario: quién lo realizó
- ip: dirección IP
- detalle: descripción del cambio';


--
-- Name: calcular_vida_util_restante(uuid); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.calcular_vida_util_restante(p_neumatico_id uuid) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
DECLARE
    -- Constantes
    V_PROF_MIN_RETIRO CONSTANT numeric := 2.0; -- Profundidad mínima de retiro en mm
    V_VIDA_UTIL_MAX_KM CONSTANT numeric := 200000; -- Límite superior razonable para la vida útil en km
    
    -- Variables para almacenar datos del neumático
    v_prof_actual numeric;           -- Profundidad actual del dibujo en mm
    v_tasa_desgaste_actual numeric;   -- Tasa de desgaste actual en mm/km
    v_vida_actual integer;            -- Vida actual del neumático (1 = primera vida, 2 = primer reencauche, etc.)
    v_es_reencauchado boolean;        -- Indica si el neumático es reencauchado
    v_prof_min_ret numeric;           -- Profundidad mínima de retiro
    v_tasa_desgaste_esperada numeric; -- Tasa de desgaste esperada del modelo
    v_porc_ajuste_reencauche numeric; -- Porcentaje de aumento de desgaste por reencauche
    v_vida_util_restante numeric;     -- Vida útil restante en km
    v_max_vidas_utiles integer;       -- Número máximo de vidas útiles permitidas
    
    -- Variables para la tasa de desgaste
    v_tasa_desgaste_usar numeric;
    v_tasa_confiable boolean := FALSE;
    v_tasa_historica numeric;
    v_contador_eventos integer := 0;
    v_supero_max_vidas boolean := FALSE;

BEGIN
    -- Obtener datos actuales del neumático y su modelo
    SELECT 
        n.profundidad_remanente_actual_mm,
        n.tasa_desgaste_actual_mm_km,
        n.vida_actual,
        n.es_reencauchado,
        COALESCE(mn.profundidad_minima_retiro_mm, V_PROF_MIN_RETIRO) AS prof_min_retiro,
        mn.tasa_desgaste_esperada_mm_km,
        COALESCE(mn.porcentaje_desgaste_por_vida, 0) AS porc_aumento_tasa_reencauche,
        COALESCE(mn.max_vidas_utiles, 1) AS max_vidas_utiles
    INTO 
        v_prof_actual,
        v_tasa_desgaste_actual,
        v_vida_actual,
        v_es_reencauchado,
        v_prof_min_ret,
        v_tasa_desgaste_esperada,
        v_porc_ajuste_reencauche,
        v_max_vidas_utiles
    FROM 
        neumaticos n
        LEFT JOIN modelos_neumatico mn ON n.modelo_id = mn.id
    WHERE 
        n.id = p_neumatico_id;

    -- Si no se encuentra el neumático, retornar NULL
    IF v_prof_actual IS NULL THEN
        RETURN NULL;
    END IF;

    
    -- Verificar si se superó el máximo de vidas útiles
    IF v_vida_actual >= v_max_vidas_utiles THEN
        RETURN 0; -- No queda vida útil si se superó el máximo de vidas
    END IF;


    -- Si la profundidad actual es menor o igual a la profundidad mínima, retornar 0
    IF v_prof_actual <= v_prof_min_ret THEN
        RETURN 0;
    END IF;

    -- Prioridad 1: Tasa de desgaste actual (si existe y es positiva)
    IF v_tasa_desgaste_actual IS NOT NULL AND v_tasa_desgaste_actual > 0 THEN
        v_tasa_desgaste_usar := v_tasa_desgaste_actual;
        v_tasa_confiable := TRUE;
    -- Prioridad 2: Tasa de desgaste esperada del modelo
    ELSIF v_tasa_desgaste_esperada IS NOT NULL AND v_tasa_desgaste_esperada > 0 THEN
        v_tasa_desgaste_usar := v_tasa_desgaste_esperada;
        v_tasa_confiable := TRUE;
    -- Prioridad 3: Calcular tasa histórica basada en eventos pasados
    ELSE
        -- Intentar calcular la tasa histórica basada en eventos de instalación/desmontaje
        SELECT 
            CASE 
                WHEN SUM(COALESCE(desmontaje.odometro_vehiculo_en_evento, 0) - COALESCE(instalacion.odometro_vehiculo_en_evento, 0)) > 0
                THEN SUM(COALESCE(instalacion.profundidad_inicial_mm, 0) - COALESCE(desmontaje.profundidad_remanente_mm, 0)) /
                     SUM(COALESCE(desmontaje.odometro_vehiculo_en_evento, 0) - COALESCE(instalacion.odometro_vehiculo_en_evento, 0))
                ELSE NULL
            END AS tasa_historica,
            COUNT(*) AS total_eventos
        INTO 
            v_tasa_historica,
            v_contador_eventos
        FROM 
            eventos_neumaticos instalacion
            LEFT JOIN eventos_neumaticos desmontaje ON 
                instalacion.neumatico_id = desmontaje.neumatico_id AND
                desmontaje.tipo_evento = 'DESMONTAJE' AND
                desmontaje.id > instalacion.id AND
                NOT EXISTS (
                    SELECT 1 
                    FROM eventos_neumaticos e 
                    WHERE e.neumatico_id = instalacion.neumatico_id 
                    AND e.tipo_evento = 'INSTALACION' 
                    AND e.id > instalacion.id 
                    AND e.id < desmontaje.id
                )
        WHERE 
            instalacion.neumatico_id = p_neumatico_id AND
            instalacion.tipo_evento = 'INSTALACION' AND
            instalacion.odometro_vehiculo_en_evento IS NOT NULL AND
            instalacion.profundidad_inicial_mm IS NOT NULL;
        
        -- Si se pudo calcular una tasa histórica con datos suficientes, usarla
        IF v_tasa_historica IS NOT NULL AND v_tasa_historica > 0 AND v_contador_eventos > 0 THEN
            v_tasa_desgaste_usar := v_tasa_historica;
            v_tasa_confiable := TRUE;
            
            -- Registrar la tasa calculada para depuración
            RAISE NOTICE 'Tasa histórica calculada: % mm/km basada en % eventos', 
                         ROUND(v_tasa_historica, 6), v_contador_eventos;
        END IF;
    END IF;

    -- Ajustar tasa si es reencauchado y no es la primera vida (aumentar desgaste)
    IF v_es_reencauchado AND v_vida_actual > 1 AND v_tasa_confiable AND v_porc_ajuste_reencauche > 0 THEN
        v_tasa_desgaste_usar := v_tasa_desgaste_usar * (1 + (v_porc_ajuste_reencauche / 100.0));
        
        RAISE NOTICE 'Ajustando tasa de desgaste por reencauche. Tasa antes: %, después: %', 
                     ROUND(v_tasa_desgaste_usar / (1 + (v_porc_ajuste_reencauche / 100.0)), 6),
                     ROUND(v_tasa_desgaste_usar, 6);
    END IF;

    -- Si no hay una tasa confiable, retornar NULL
    IF NOT v_tasa_confiable OR v_tasa_desgaste_usar IS NULL OR v_tasa_desgaste_usar <= 0 THEN
        RAISE NOTICE 'No se pudo determinar una tasa de desgaste confiable para el neumático %', p_neumatico_id;
        RETURN NULL;
    END IF;

    -- Calcular vida útil restante en kilómetros
    v_vida_util_restante := (v_prof_actual - v_prof_min_ret) / v_tasa_desgaste_usar;

    -- Asegurarse de que el valor esté dentro de límites razonables
    v_vida_util_restante := LEAST(v_vida_util_restante, V_VIDA_UTIL_MAX_KM);

    -- Registrar información de depuración
    RAISE NOTICE 'Cálculo vida útil - Profundidad: % mm, Mínimo: % mm, Tasa: % mm/km, Vida restante: % km',
                 v_prof_actual, v_prof_min_ret, ROUND(v_tasa_desgaste_usar, 6), ROUND(v_vida_util_restante, 2);

    -- Retornar el valor redondeado a 2 decimales, asegurando que no sea negativo
    RETURN GREATEST(0, ROUND(v_vida_util_restante, 2));

EXCEPTION WHEN OTHERS THEN
    -- En caso de error, registrar el error y retornar NULL
    RAISE WARNING 'Error en calcular_vida_util_restante (neumático %): %', p_neumatico_id, SQLERRM;
    RETURN NULL;
END;
$$;


ALTER FUNCTION public.calcular_vida_util_restante(p_neumatico_id uuid) OWNER TO postgres;

--
-- Name: FUNCTION calcular_vida_util_restante(p_neumatico_id uuid); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.calcular_vida_util_restante(p_neumatico_id uuid) IS 'Calcula la vida útil restante de un neumático en kilómetros basándose en su tasa de desgaste actual o histórica.

Parámetros:
- p_neumatico_id: ID del neumático para el cual se calculará la vida útil restante

Retorna:
- Número de kilómetros restantes antes de alcanzar la profundidad mínima de retiro
- 0 si el neumático ya alcanzó su vida útil máxima o la profundidad mínima
- NULL si no se pudo calcular la vida útil (datos insuficientes o error)

La función sigue esta jerarquía para determinar la tasa de desgaste a utilizar:
1. Tasa de desgaste actual del neumático (si existe y es válida)
2. Tasa de desgaste esperada del modelo (si está definida)
3. Tasa de desgaste histórica calculada a partir de eventos de instalación/desmontaje

Si el neumático es reencauchado, se aplica un porcentaje de ajuste a la tasa de desgaste.';


--
-- Name: cleanup_audit_triggers(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.cleanup_audit_triggers() RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    trigger_rec RECORD;
BEGIN
    -- Eliminar triggers de auditoría existentes
    FOR trigger_rec IN 
        SELECT 
            n.nspname AS schema_name,
            c.relname AS table_name,
            t.tgname AS trigger_name
        FROM 
            pg_trigger t
            JOIN pg_class c ON t.tgrelid = c.oid
            JOIN pg_namespace n ON c.relnamespace = n.oid
        WHERE 
            t.tgname LIKE 'tr_audit%'
            AND n.nspname NOT LIKE 'pg_%'
            AND n.nspname != 'information_schema'
    LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS %I ON %I.%I CASCADE', 
                      trigger_rec.trigger_name, 
                      trigger_rec.schema_name, 
                      trigger_rec.table_name);
        RAISE NOTICE 'Eliminado trigger % en %.%', 
                    trigger_rec.trigger_name, 
                    trigger_rec.schema_name, 
                    trigger_rec.table_name;
    END LOOP;
    
    -- Eliminar funciones de trigger si existen
    DROP FUNCTION IF EXISTS audit_high_priority_trigger() CASCADE;
    DROP FUNCTION IF EXISTS audit_medium_priority_trigger() CASCADE;
    DROP FUNCTION IF EXISTS create_high_priority_audit_triggers() CASCADE;
    DROP FUNCTION IF EXISTS create_medium_priority_audit_triggers() CASCADE;
    
    RAISE NOTICE 'Limpieza de triggers de auditoría completada';
END;
$$;


ALTER FUNCTION public.cleanup_audit_triggers() OWNER TO postgres;

--
-- Name: crear_triggers_auditoria_compuesta(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.crear_triggers_auditoria_compuesta() RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_table_name TEXT;
    v_trigger_name TEXT;
BEGIN
    -- Eliminar triggers existentes primero
    FOR v_table_name IN 
        SELECT unnest(ARRAY['modelos_posiciones_permitidas', 'roles_permisos', 'usuarios_roles'])
    LOOP
        -- Eliminar triggers existentes usando formato correcto
        EXECUTE format('DROP TRIGGER IF EXISTS tr_audit_comp_%s ON public.%I', 
                      v_table_name, v_table_name);
        EXECUTE format('DROP TRIGGER IF EXISTS tr_audit_%s ON public.%I', 
                      v_table_name, v_table_name);
    END LOOP;
    
    -- Crear nuevos triggers
    FOR v_table_name IN 
        SELECT unnest(ARRAY['modelos_posiciones_permitidas', 'roles_permisos', 'usuarios_roles'])
    LOOP
        v_trigger_name := 'tr_audit_comp_' || v_table_name;
        
        -- Crear el trigger
        EXECUTE format('
            CREATE TRIGGER %I
            AFTER INSERT OR UPDATE OR DELETE ON public.%I
            FOR EACH ROW EXECUTE FUNCTION public.registrar_auditoria_compuesta()',
            v_trigger_name, v_table_name
        );
        
        RAISE NOTICE 'Creado trigger % en la tabla %', v_trigger_name, v_table_name;
    END LOOP;
    
    RAISE NOTICE 'Todos los triggers de auditoría compuesta han sido recreados correctamente.';
END;
$$;


ALTER FUNCTION public.crear_triggers_auditoria_compuesta() OWNER TO postgres;

--
-- Name: crear_triggers_auditoria_compuestas(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.crear_triggers_auditoria_compuestas() RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    r RECORD;
    v_trigger_name TEXT;
    v_table_name TEXT;
    v_tables_to_audit TEXT[] := ARRAY[
        'modelos_posiciones_permitidas', 
        'roles_permisos', 
        'usuarios_roles'
    ];
BEGIN
    RAISE NOTICE 'Iniciando creación de triggers para tablas con claves compuestas...';
    
    FOR v_table_name IN SELECT unnest(v_tables_to_audit)
    LOOP
        v_trigger_name := 'tr_audit_comp_' || v_table_name;
        
        -- Verificar si la tabla existe
        IF EXISTS (
            SELECT 1 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = v_table_name
        ) THEN
            -- Eliminar trigger si ya existe
            EXECUTE format('DROP TRIGGER IF EXISTS %I ON public.%I', 
                          v_trigger_name, v_table_name);
            
            -- Crear trigger para INSERT, UPDATE, DELETE
            EXECUTE format('
                CREATE TRIGGER %I
                AFTER INSERT OR UPDATE OR DELETE ON public.%I
                FOR EACH ROW EXECUTE FUNCTION public.registrar_auditoria_compuesta()',
                v_trigger_name, v_table_name
            );
            
            RAISE NOTICE 'Creado trigger para la tabla %', v_table_name;
        ELSE
            RAISE NOTICE 'La tabla % no existe, se omite', v_table_name;
        END IF;
    END LOOP;
    
    RAISE NOTICE 'Proceso de creación de triggers completado.';
END;
$$;


ALTER FUNCTION public.crear_triggers_auditoria_compuestas() OWNER TO postgres;

--
-- Name: create_high_priority_audit_triggers(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.create_high_priority_audit_triggers() RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    r RECORD;
    table_info RECORD;
BEGIN
    -- Tablas de alta prioridad
    FOR table_info IN 
        SELECT table_schema, table_name 
        FROM information_schema.tables 
        WHERE (table_schema, table_name) IN (
            ('public', 'usuarios'),
            ('public', 'roles'),
            ('public', 'permisos'),
            ('public', 'roles_permisos'),
            ('public', 'neumaticos'),
            ('public', 'eventos_neumaticos'),
            ('public', 'vehiculos')
        )
        AND table_type = 'BASE TABLE'
    LOOP
        -- Eliminar trigger existente si existe
        EXECUTE format('DROP TRIGGER IF EXISTS tr_audit_%s ON %I.%I CASCADE', 
                      table_info.table_name, table_info.table_schema, table_info.table_name);
        
        -- Crear nuevo trigger
        EXECUTE format('CREATE TRIGGER tr_audit_%s
                      AFTER INSERT OR UPDATE OR DELETE ON %I.%I
                      FOR EACH ROW EXECUTE FUNCTION audit_high_priority_trigger()',
                      table_info.table_name, table_info.table_schema, table_info.table_name);
                      
        RAISE NOTICE 'Creado trigger de auditoría para %.%', table_info.table_schema, table_info.table_name;
    END LOOP;
    
    RAISE NOTICE 'Auditoría configurada para tablas de alta prioridad';
END;
$$;


ALTER FUNCTION public.create_high_priority_audit_triggers() OWNER TO postgres;

--
-- Name: create_medium_priority_audit_triggers(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.create_medium_priority_audit_triggers() RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    table_info RECORD;
BEGIN
    -- Tablas de prioridad media
    FOR table_info IN 
        SELECT table_schema, table_name 
        FROM information_schema.tables 
        WHERE (table_schema, table_name) IN (
            ('public', 'proveedores'),
            ('public', 'almacenes'),
            ('public', 'fabricantes_neumatico'),
            ('public', 'modelos_neumatico'),
            ('public', 'modelos_posiciones_permitidas')
        )
        AND table_type = 'BASE TABLE'
    LOOP
        -- Eliminar trigger existente si existe
        EXECUTE format('DROP TRIGGER IF EXISTS tr_audit_%s ON %I.%I CASCADE', 
                      table_info.table_name, table_info.table_schema, table_info.table_name);
        
        -- Crear nuevo trigger
        EXECUTE format('CREATE TRIGGER tr_audit_%s
                      AFTER INSERT OR UPDATE OR DELETE ON %I.%I
                      FOR EACH ROW EXECUTE FUNCTION audit_medium_priority_trigger()',
                      table_info.table_name, table_info.table_schema, table_info.table_name);
                      
        RAISE NOTICE 'Creado trigger de auditoría ligera para %.%', 
                    table_info.table_schema, table_info.table_name;
    END LOOP;
    
    RAISE NOTICE 'Auditoría configurada para tablas de prioridad media';
END;
$$;


ALTER FUNCTION public.create_medium_priority_audit_triggers() OWNER TO postgres;

--
-- Name: ejecutar_como_usuario(text, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.ejecutar_como_usuario(p_username text, p_comando text) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_user_id uuid;
    v_previous_user text;
BEGIN
    -- Obtener el ID del usuario
    SELECT id INTO v_user_id FROM usuarios WHERE username = p_username LIMIT 1;
    
    IF v_user_id IS NULL THEN
        RAISE EXCEPTION 'Usuario % no encontrado', p_username;
    END IF;
    
    -- Guardar el usuario actual
    SELECT current_user INTO v_previous_user;
    
    -- Configurar variables de sesión para el usuario
    EXECUTE format('SET ROLE %I', p_username);
    PERFORM set_config('app.current_user_id', v_user_id::text, true);
    PERFORM set_config('app.current_username', p_username, true);
    PERFORM set_config('app.client_ip', '192.168.1.' || (random() * 255)::int::text, true);
    PERFORM set_config('app.user_agent', 'Mozilla/5.0 (Pruebas)', true);
    
    -- Ejecutar el comando
    EXECUTE p_comando;
    
    -- Restaurar el usuario original
    EXECUTE format('SET ROLE %I', v_previous_user);
    
    RAISE NOTICE 'Comando ejecutado como usuario %', p_username;
EXCEPTION WHEN OTHERS THEN
    -- Asegurarse de restaurar el usuario original en caso de error
    EXECUTE format('SET ROLE %I', v_previous_user);
    RAISE EXCEPTION 'Error ejecutando como %: %', p_username, SQLERRM;
END;
$$;


ALTER FUNCTION public.ejecutar_como_usuario(p_username text, p_comando text) OWNER TO postgres;

--
-- Name: ejecutar_tarea_ahora(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.ejecutar_tarea_ahora(p_nombre_tarea character varying) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_resultado TEXT;
BEGIN
    -- Forzar la próxima ejecución a ahora
    UPDATE tareas_programadas
    SET 
        proxima_ejecucion = NOW(),
        actualizado_en = NOW(),
        actualizado_por = current_user
    WHERE nombre_tarea = p_nombre_tarea
    RETURNING 'Tarea programada para ejecución: ' || nombre_tarea INTO v_resultado;
    
    -- Ejecutar tareas programadas
    PERFORM public.ejecutar_tareas_programadas();
    
    RETURN COALESCE(v_resultado, 'Tarea no encontrada: ' || p_nombre_tarea);
END;
$$;


ALTER FUNCTION public.ejecutar_tarea_ahora(p_nombre_tarea character varying) OWNER TO postgres;

--
-- Name: ejecutar_tareas_programadas(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.ejecutar_tareas_programadas() RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    tarea RECORD;
    tarea_id INTEGER;
    tarea_nombre VARCHAR(100);
    tarea_script TEXT;
    resultado TEXT;
    tareas_ejecutadas INTEGER := 0;
BEGIN
    -- Bloquear la tabla para evitar ejecuciones concurrentes
    LOCK TABLE tareas_programadas IN EXCLUSIVE MODE;
    
    -- Obtener tareas pendientes de ejecutar
    FOR tarea IN 
        SELECT * 
        FROM tareas_programadas 
        WHERE activa = TRUE 
          AND (proxima_ejecucion IS NULL OR proxima_ejecucion <= NOW())
        ORDER BY id
    LOOP
        tarea_id := tarea.id;
        tarea_nombre := tarea.nombre_tarea;
        tarea_script := tarea.script_sql;
        
        BEGIN
            -- Ejecutar el script SQL de la tarea
            IF tarea_script IS NOT NULL AND tarea_script != '' THEN
                EXECUTE tarea_script;
            END IF;
            
            -- Registrar éxito
            resultado := 'Éxito';
            tareas_ejecutadas := tareas_ejecutadas + 1;
            
            -- Registrar en el log
            INSERT INTO public.auditoria_log (
                tabla_afectada, 
                operacion, 
                detalles, 
                creado_por
            ) VALUES (
                'tareas_programadas',
                'EJECUCION',
                jsonb_build_object(
                    'tarea_id', tarea_id,
                    'tarea_nombre', tarea_nombre,
                    'resultado', resultado
                ),
                'SISTEMA_TAREAS'
            );
            
        EXCEPTION WHEN OTHERS THEN
            -- Registrar error
            resultado := 'Error: ' || SQLERRM;
            
            INSERT INTO public.errores_aplicacion (
                nombre_funcion, 
                mensaje_error, 
                detalles, 
                creado_por
            ) VALUES (
                'ejecutar_tareas_programadas', 
                'Error ejecutando tarea: ' || tarea_nombre, 
                jsonb_build_object(
                    'tarea_id', tarea_id,
                    'error', SQLERRM,
                    'sqlstate', SQLSTATE
                ), 
                'SISTEMA_TAREAS'
            );
        END;
        
        -- Actualizar la tarea con la próxima ejecución
        UPDATE tareas_programadas
        SET 
            ultima_ejecucion = NOW(),
            proxima_ejecucion = NOW() + (frecuencia_dias * INTERVAL '1 day'),
            actualizado_en = NOW(),
            actualizado_por = 'SISTEMA'
        WHERE id = tarea_id;
    END LOOP;
    
    RETURN tareas_ejecutadas;
END;
$$;


ALTER FUNCTION public.ejecutar_tareas_programadas() OWNER TO postgres;

--
-- Name: f_immutable_lower_unaccent(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.f_immutable_lower_unaccent(text) RETURNS text
    LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE
    AS $_$
    SELECT lower(public.unaccent($1));
$_$;


ALTER FUNCTION public.f_immutable_lower_unaccent(text) OWNER TO postgres;

--
-- Name: FUNCTION f_immutable_lower_unaccent(text); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.f_immutable_lower_unaccent(text) IS 'Wrapper IMMUTABLE para lower(unaccent(text)) para usar en índices únicos insensibles a mayúsculas/acentos.';


--
-- Name: fn_actualizar_odometro_vehiculo(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fn_actualizar_odometro_vehiculo() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE 
    v_odometro_actual integer; 
    v_fecha_odometro_actual timestamptz;
BEGIN
    -- Evitar recursión infinita
    IF pg_trigger_depth() > 1 THEN 
        RETURN NEW; 
    END IF;
    
    -- Obtener el odómetro actual del vehículo con bloqueo
    SELECT odometro_actual, fecha_ultimo_odometro 
    INTO v_odometro_actual, v_fecha_odometro_actual 
    FROM public.vehiculos 
    WHERE id = NEW.vehiculo_id 
    FOR UPDATE;
    
    -- Actualizar solo si el nuevo registro es más reciente o tiene un odómetro mayor
    IF v_fecha_odometro_actual IS NULL 
       OR NEW.fecha_medicion >= v_fecha_odometro_actual 
       OR (NEW.odometro > v_odometro_actual AND NEW.fecha_medicion >= v_fecha_odometro_actual) 
    THEN
        UPDATE public.vehiculos 
        SET 
            odometro_actual = NEW.odometro, 
            fecha_ultimo_odometro = NEW.fecha_medicion, 
            actualizado_en = now(), 
            actualizado_por = NEW.creado_por 
        WHERE id = NEW.vehiculo_id;
    END IF;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_actualizar_odometro_vehiculo() OWNER TO postgres;

--
-- Name: FUNCTION fn_actualizar_odometro_vehiculo(); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.fn_actualizar_odometro_vehiculo() IS 'Actualiza el odómetro del vehículo cuando se inserta un nuevo registro de odómetro';


--
-- Name: fn_auditoria_registro(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fn_auditoria_registro() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE 
    v_contexto jsonb; 
    v_usuario_id_app uuid; 
    v_usuario_app_username varchar;
    v_entidad_id uuid; 
    v_datos_antiguos jsonb; 
    v_datos_nuevos jsonb; 
    v_responsable_id uuid;
    v_cambios jsonb;
BEGIN
    -- Evitar recursión infinita
    IF pg_trigger_depth() > 1 THEN 
        RETURN CASE WHEN TG_OP = 'DELETE' THEN OLD ELSE NEW END; 
    END IF;
    
    -- Obtener información del usuario desde el contexto de la aplicación
    BEGIN
        v_usuario_id_app := current_setting('app.usuario_id', true)::uuid; 
        v_usuario_app_username := current_setting('app.usuario_username', true);
        v_contexto := jsonb_build_object(
            'endpoint', current_setting('app.endpoint', true), 
            'metodo', current_setting('app.metodo', true), 
            'ip', current_setting('app.ip', true)
        );
    EXCEPTION WHEN OTHERS THEN 
        v_usuario_id_app := NULL; 
        v_usuario_app_username := NULL; 
        v_contexto := NULL; 
    END;

    -- Determinar los datos según el tipo de operación
    IF (TG_OP = 'DELETE') THEN
        v_entidad_id := OLD.id; 
        v_datos_antiguos := to_jsonb(OLD); 
        v_datos_nuevos := NULL;
        
        -- Intentar obtener el ID del responsable
        BEGIN 
            v_responsable_id := OLD.actualizado_por; 
        EXCEPTION WHEN OTHERS THEN 
            v_responsable_id := NULL; 
        END;
        
        -- Si no hay responsable en actualizado_por, intentar con creado_por
        IF v_responsable_id IS NULL THEN 
            BEGIN 
                v_responsable_id := OLD.creado_por; 
            EXCEPTION WHEN OTHERS THEN 
                v_responsable_id := NULL; 
            END; 
        END IF;
        
        -- Calcular los campos que cambiaron (todos en este caso)
        v_cambios := v_datos_antiguos - '{creado_en, actualizado_en, creado_por, actualizado_por}'::text[];
        
    ELSIF (TG_OP = 'UPDATE') THEN
        v_entidad_id := NEW.id; 
        v_datos_antiguos := to_jsonb(OLD); 
        v_datos_nuevos := to_jsonb(NEW);
        
        -- Obtener el ID del responsable de la actualización
        BEGIN 
            v_responsable_id := NEW.actualizado_por; 
        EXCEPTION WHEN OTHERS THEN 
            v_responsable_id := NULL; 
        END;
        
        -- Calcular solo los campos que cambiaron
        SELECT jsonb_object_agg(key, value) 
        INTO v_cambios 
        FROM jsonb_each(v_datos_nuevos)
        WHERE key NOT IN ('actualizado_en', 'actualizado_por') 
        AND (v_datos_antiguos -> key IS DISTINCT FROM v_datos_nuevos -> key);
        
    ELSIF (TG_OP = 'INSERT') THEN
        v_entidad_id := NEW.id; 
        v_datos_antiguos := NULL; 
        v_datos_nuevos := to_jsonb(NEW);
        
        -- Obtener el ID del creador
        BEGIN 
            v_responsable_id := NEW.creado_por; 
        EXCEPTION WHEN OTHERS THEN 
            v_responsable_id := NULL; 
        END;
        
        -- Calcular los campos (todos menos los de auditoría)
        v_cambios := v_datos_nuevos - '{creado_en, actualizado_en, creado_por, actualizado_por}'::text[];
    END IF;

    -- Si no hay usuario de aplicación, usar el responsable si está disponible
    IF v_usuario_id_app IS NULL AND v_responsable_id IS NOT NULL THEN
        v_usuario_id_app := v_responsable_id;
    END IF;
    
    -- Si hay ID de usuario pero no nombre de usuario, intentar obtenerlo
    IF v_usuario_id_app IS NOT NULL AND v_usuario_app_username IS NULL THEN
        SELECT username 
        INTO v_usuario_app_username 
        FROM public.usuarios 
        WHERE id = v_usuario_id_app 
        LIMIT 1;
    END IF;

    -- Insertar el registro de auditoría
    INSERT INTO public.auditoria_log (
        esquema_tabla, 
        nombre_tabla, 
        operacion, 
        usuario_db, 
        usuario_aplicacion_id, 
        usuario_aplicacion_username, 
        direccion_ip, 
        id_entidad, 
        datos_antiguos, 
        datos_nuevos, 
        cambios, 
        contexto_aplicacion, 
        query_ejecutada
    )
    VALUES (
        TG_TABLE_SCHEMA, 
        TG_TABLE_NAME, 
        TG_OP, 
        current_user, 
        v_usuario_id_app, 
        v_usuario_app_username, 
        v_contexto->>'ip', 
        v_entidad_id, 
        v_datos_antiguos, 
        v_datos_nuevos, 
        v_cambios, 
        v_contexto, 
        current_query()
    );

    -- Retornar el registro apropiado
    RETURN CASE WHEN TG_OP = 'DELETE' THEN OLD ELSE NEW END;
END;
$$;


ALTER FUNCTION public.fn_auditoria_registro() OWNER TO postgres;

--
-- Name: FUNCTION fn_auditoria_registro(); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.fn_auditoria_registro() IS 'Función de trigger para auditar cambios en las tablas del sistema';


--
-- Name: fn_validar_modelo_posicion(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fn_validar_modelo_posicion() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE 
    v_modelo_existe boolean; 
    v_posicion_existe boolean;
BEGIN
    -- Verificar si el modelo de neumático existe
    SELECT EXISTS (
        SELECT 1 
        FROM public.modelos_neumatico 
        WHERE id = NEW.modelo_neumatico_id
    ) INTO v_modelo_existe;
    
    IF NOT v_modelo_existe THEN 
        RAISE EXCEPTION 'Validación fallida: Modelo de neumático ID % no existe.', NEW.modelo_neumatico_id; 
    END IF;
    
    -- Verificar si la posición de neumático existe
    SELECT EXISTS (
        SELECT 1 
        FROM public.posiciones_neumatico 
        WHERE id = NEW.posicion_neumatico_id
    ) INTO v_posicion_existe;
    
    IF NOT v_posicion_existe THEN 
        RAISE EXCEPTION 'Validación fallida: Posición de neumático ID % no existe.', NEW.posicion_neumatico_id; 
    END IF;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_validar_modelo_posicion() OWNER TO postgres;

--
-- Name: FUNCTION fn_validar_modelo_posicion(); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.fn_validar_modelo_posicion() IS 'Valida que el modelo y la posición del neumático existan antes de insertar/actualizar registros relacionados';


--
-- Name: fn_validar_superusuario(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fn_validar_superusuario() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Solo el usuario con username 'admin' puede ser superusuario
    IF NEW.username = 'admin' THEN
        NEW.es_superusuario = TRUE;
    ELSE
        NEW.es_superusuario = FALSE;
    END IF;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_validar_superusuario() OWNER TO postgres;

--
-- Name: generar_id_entidad(text[]); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.generar_id_entidad(p_valores text[]) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN md5(array_to_string(p_valores, '|'));
END;
$$;


ALTER FUNCTION public.generar_id_entidad(p_valores text[]) OWNER TO postgres;

--
-- Name: jsonb_diff_val(jsonb, jsonb); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.jsonb_diff_val(val1 jsonb, val2 jsonb) RETURNS jsonb
    LANGUAGE plpgsql
    AS $$
DECLARE
    result jsonb := '{}'::jsonb;
    key text;
    val1_val jsonb;
    val2_val jsonb;
    diff jsonb;
BEGIN
    -- Obtener todas las claves únicas de ambos objetos
    FOR key IN 
        SELECT DISTINCT k FROM (
            SELECT jsonb_object_keys(val1) AS k
            UNION
            SELECT jsonb_object_keys(val2) AS k
        ) AS keys
    LOOP
        val1_val := val1->key;
        val2_val := val2->key;
        
        -- Solo incluir en el resultado si los valores son diferentes
        IF val1_val IS DISTINCT FROM val2_val THEN
            result := result || jsonb_build_object(
                key,
                jsonb_build_object(
                    'old', val1_val,
                    'new', val2_val
                )
            );
        END IF;
    END LOOP;
    
    RETURN result;
END;
$$;


ALTER FUNCTION public.jsonb_diff_val(val1 jsonb, val2 jsonb) OWNER TO postgres;

--
-- Name: limpiar_auditoria_antigua(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.limpiar_auditoria_antigua(p_dias_retencion integer DEFAULT 90) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_registros_eliminados INTEGER;
BEGIN
    -- Eliminar registros más antiguos que p_dias_retencion días
    DELETE FROM public.auditoria_log
    WHERE timestamp_log < (CURRENT_DATE - (p_dias_retencion || ' days')::interval);
    
    -- Devolver el número de registros eliminados
    GET DIAGNOSTICS v_registros_eliminados = ROW_COUNT;
    RETURN v_registros_eliminados;
END;
$$;


ALTER FUNCTION public.limpiar_auditoria_antigua(p_dias_retencion integer) OWNER TO postgres;

--
-- Name: limpiar_auditoria_antigua(integer, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.limpiar_auditoria_antigua(p_dias_retener integer DEFAULT 365, p_tabla text DEFAULT NULL::text) RETURNS integer
    LANGUAGE plpgsql SECURITY DEFINER
    AS $_$
DECLARE
    v_sql text;
    v_where_condition text := 'WHERE timestamp_log < NOW() - $1 * INTERVAL ''1 day''';
    v_count integer;
BEGIN
    IF p_tabla IS NOT NULL THEN
        v_where_condition := v_where_condition || ' AND nombre_tabla = $2';
        EXECUTE 'DELETE FROM auditoria_log ' || v_where_condition 
        USING p_dias_retener, p_tabla;
    ELSE
        EXECUTE 'DELETE FROM auditoria_log ' || v_where_condition 
        USING p_dias_retener;
    END IF;
    
    GET DIAGNOSTICS v_count = ROW_COUNT;
    RETURN v_count;
END;
$_$;


ALTER FUNCTION public.limpiar_auditoria_antigua(p_dias_retener integer, p_tabla text) OWNER TO postgres;

--
-- Name: FUNCTION limpiar_auditoria_antigua(p_dias_retener integer, p_tabla text); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.limpiar_auditoria_antigua(p_dias_retener integer, p_tabla text) IS 'Limpia registros de auditoría más antiguos que el número de días especificado.

Parámetros:
- p_dias_retener: Número de días de retención (por defecto 365)
- p_tabla: (Opcional) Si se especifica, solo limpia registros de esta tabla

Retorna: Número de registros eliminados';


--
-- Name: limpiar_auditoria_antigua(integer, text, boolean); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.limpiar_auditoria_antigua(p_dias_retencion integer DEFAULT 365, p_tabla text DEFAULT NULL::text, p_commit boolean DEFAULT false) RETURNS TABLE(operacion text, registros_afectados bigint, tamano_liberado text, mensaje text)
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_tamano_antes TEXT;
    v_tamano_despues TEXT;
    v_registros_eliminados BIGINT;
    v_query TEXT;
BEGIN
    -- Obtener tamaño actual de la tabla
    SELECT pg_size_pretty(pg_total_relation_size('auditoria_log')) INTO v_tamano_antes;
    
    -- Construir la consulta de eliminación
    v_query := 'DELETE FROM auditoria_log WHERE timestamp_log < NOW() - INTERVAL ''' || 
               p_dias_retencion || ' days''';
    
    -- Filtrar por tabla si se especifica
    IF p_tabla IS NOT NULL THEN
        v_query := v_query || ' AND nombre_tabla = ''' || p_tabla || '''';
    END IF;
    
    -- Ejecutar la consulta o solo mostrarla
    IF p_commit THEN
        EXECUTE 'WITH deleted AS (' || v_query || ' RETURNING *) SELECT COUNT(*) FROM deleted' INTO v_registros_eliminados;
        
        -- Obtener tamaño después de la eliminación
        SELECT pg_size_pretty(pg_total_relation_size('auditoria_log')) INTO v_tamano_despues;
        
        -- Retornar resultados
        RETURN QUERY 
        SELECT 
            'LIMPIEZA' as operacion,
            v_registros_eliminados as registros_afectados,
            pg_size_pretty(
                pg_total_relation_size('auditoria_log') - 
                pg_table_size('auditoria_log')
            ) as tamano_liberado,
            'Se eliminaron ' || v_registros_eliminados || ' registros de auditoría.' as mensaje;
    ELSE
        -- Modo de solo simulación
        EXECUTE 'SELECT COUNT(*) FROM (' || v_query || ') t' INTO v_registros_eliminados;
        
        RETURN QUERY 
        SELECT 
            'SIMULACIÓN' as operacion,
            v_registros_eliminados as registros_afectados,
            'N/A' as tamano_liberado,
            'Modo simulación: se eliminarían ' || v_registros_eliminados || ' registros. Ejecutar con p_commit=true para realizar la limpieza.' as mensaje;
    END IF;
    
EXCEPTION WHEN OTHERS THEN
    RETURN QUERY 
    SELECT 
        'ERROR' as operacion,
        -1 as registros_afectados,
        '0 bytes' as tamano_liberado,
        'Error: ' || SQLERRM as mensaje;
END;
$$;


ALTER FUNCTION public.limpiar_auditoria_antigua(p_dias_retencion integer, p_tabla text, p_commit boolean) OWNER TO postgres;

--
-- Name: limpiar_bitacora_mantenimiento(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.limpiar_bitacora_mantenimiento(dias_retener integer DEFAULT 90) RETURNS integer
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    v_registros_eliminados INTEGER;
BEGIN
    DELETE FROM public.bitacora_mantenimiento
    WHERE fecha_ejecucion < (CURRENT_DATE - (dias_retener * INTERVAL '1 day'))
    AND tipo != 'ERROR';
    
    GET DIAGNOSTICS v_registros_eliminados = ROW_COUNT;
    
    -- Registrar la limpieza
    INSERT INTO public.bitacora_mantenimiento (
        tipo,
        descripcion,
        ejecutado_por,
        detalles
    ) VALUES (
        'LIMPIEZA',
        'Limpieza de registros antiguos de la bitácora',
        current_user,
        format('Se eliminaron %s registros con más de %s días de antigüedad', 
               v_registros_eliminados, dias_retener)
    );
    
    RETURN v_registros_eliminados;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING 'Error al limpiar la bitácora de mantenimiento: %', SQLERRM;
        RETURN -1;
END;
$$;


ALTER FUNCTION public.limpiar_bitacora_mantenimiento(dias_retener integer) OWNER TO postgres;

--
-- Name: FUNCTION limpiar_bitacora_mantenimiento(dias_retener integer); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.limpiar_bitacora_mantenimiento(dias_retener integer) IS 'Limpia registros antiguos de la bitácora de mantenimiento.';


--
-- Name: limpiar_bitacora_mantenimiento(integer, boolean); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.limpiar_bitacora_mantenimiento(p_dias_retener integer DEFAULT 90, p_mantener_errores boolean DEFAULT true) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_registros_eliminados INTEGER;
    v_total_registros INTEGER;
    v_registros_mantenidos INTEGER;
BEGIN
    -- Contar registros antes de la limpieza
    SELECT COUNT(*) INTO v_total_registros FROM public.bitacora_mantenimiento;
    
    -- Eliminar registros antiguos
    DELETE FROM public.bitacora_mantenimiento
    WHERE fecha_ejecucion < (CURRENT_DATE - (p_dias_retener * INTERVAL '1 day'))
    AND (NOT p_mantener_errores OR exito = TRUE);
    
    -- Obtener estadísticas
    GET DIAGNOSTICS v_registros_eliminados = ROW_COUNT;
    v_registros_mantenidos := v_total_registros - v_registros_eliminados;
    
    -- Registrar la limpieza
    PERFORM public.registrar_mantenimiento(
        'LIMPIEZA',
        format('Limpieza de registros de mantenimiento (conservados %s de %s registros)', 
              v_registros_mantenidos, v_total_registros),
        NULL,
        TRUE,
        format('Se eliminaron %s registros con más de %s días de antigüedad', 
              v_registros_eliminados, p_dias_retener)
    );
    
    RETURN v_registros_eliminados;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING 'Error al limpiar la bitácora de mantenimiento: %', SQLERRM;
        RETURN -1;
END;
$$;


ALTER FUNCTION public.limpiar_bitacora_mantenimiento(p_dias_retener integer, p_mantener_errores boolean) OWNER TO postgres;

--
-- Name: FUNCTION limpiar_bitacora_mantenimiento(p_dias_retener integer, p_mantener_errores boolean); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.limpiar_bitacora_mantenimiento(p_dias_retener integer, p_mantener_errores boolean) IS 'Elimina registros antiguos de la bitácora de mantenimiento.
Parámetros:
- p_dias_retener: Número de días de registros a conservar (por defecto 90)
- p_mantener_errores: Si es TRUE, conserva los registros de error';


--
-- Name: limpiar_datos_prueba(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.limpiar_datos_prueba() RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_test_id TEXT := 'TEST-DESM-' || substr(md5(random()::text), 1, 8);
BEGIN
    -- Eliminar eventos de prueba
    DELETE FROM eventos_neumaticos 
    WHERE id IN (SELECT id FROM temp_evento);
    
    -- Eliminar neumáticos de prueba
    DELETE FROM neumaticos 
    WHERE id IN (SELECT id FROM temp_neumatico);
    
    -- Limpiar bitácoras de prueba
    DELETE FROM bitacora_operaciones_neumaticos 
    WHERE observaciones LIKE '%' || v_test_id || '%';
    
    DELETE FROM bitacora_operaciones 
    WHERE descripcion LIKE '%' || v_test_id || '%';
    
    RAISE NOTICE 'Datos de prueba limpiados correctamente';
END;
$$;


ALTER FUNCTION public.limpiar_datos_prueba() OWNER TO postgres;

--
-- Name: limpiar_datos_prueba_mejorada(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.limpiar_datos_prueba_mejorada() RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Eliminar eventos de prueba
    DELETE FROM eventos_neumaticos WHERE 
        (datos_evento->>'es_prueba')::boolean = true
        OR (datos_evento->>'test_id') IS NOT NULL;
    
    -- Eliminar neumáticos de prueba
    DELETE FROM neumaticos WHERE 
        numero_serie LIKE 'TEST-%' 
        OR (datos_adicionales->>'es_prueba')::boolean = true;
    
    -- Limpiar registros de errores de prueba
    DELETE FROM errores_aplicacion 
    WHERE nombre_funcion LIKE '%prueba%' 
       OR (detalles->>'test_id') IS NOT NULL;
    
    RAISE NOTICE 'Datos de prueba limpiados correctamente.';
END;
$$;


ALTER FUNCTION public.limpiar_datos_prueba_mejorada() OWNER TO postgres;

--
-- Name: manejar_desmontaje_neumatico(uuid, integer, numeric, text, uuid, uuid, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.manejar_desmontaje_neumatico(p_neumatico_id uuid, p_odometro_vehiculo_en_evento integer, p_profundidad_medida numeric DEFAULT NULL::numeric, p_destino_desmontaje text DEFAULT 'EN_STOCK'::text, p_almacen_destino_id uuid DEFAULT NULL::uuid, p_usuario_id uuid DEFAULT NULL::uuid, p_timestamp_evento timestamp without time zone DEFAULT now()) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_odometro_instalacion_neumatico INTEGER;
    v_km_recorridos_vida_calculados INTEGER;
    v_estado_anterior_neumatico public.estado_neumatico_enum;
    v_vehiculo_anterior_neumatico UUID;
    v_posicion_anterior_neumatico UUID;
    v_profundidad_remanente_evento NUMERIC(5,2);
    v_kilometraje_vida_actual_neumatico INTEGER;
    v_kilometraje_acumulado_neumatico INTEGER;
    v_profundidad_inicio_vida_actual NUMERIC(5,2);
    v_evento_id UUID;
BEGIN
    -- Validar parámetros obligatorios
    IF p_neumatico_id IS NULL THEN
        RAISE EXCEPTION 'El ID del neumático no puede ser nulo';
    END IF;
    
    -- Establecer valor predeterminado para la profundidad si es nulo
    v_profundidad_remanente_evento := COALESCE(p_profundidad_medida, 15.00);

    -- Obtener el estado actual del neumático con bloqueo para evitar condiciones de carrera
    SELECT 
        n.estado_actual, n.ubicacion_actual_vehiculo_id, n.ubicacion_actual_posicion_id,
        n.odometro_instalacion_vida_actual, n.kilometraje_vida_actual, n.kilometraje_acumulado,
        n.profundidad_inicio_vida_actual_mm
    INTO 
        v_estado_anterior_neumatico, v_vehiculo_anterior_neumatico, v_posicion_anterior_neumatico,
        v_odometro_instalacion_neumatico, v_kilometraje_vida_actual_neumatico, v_kilometraje_acumulado_neumatico,
        v_profundidad_inicio_vida_actual
    FROM neumaticos n 
    WHERE n.id = p_neumatico_id 
    FOR UPDATE;

    -- Calcular kilómetros recorridos en esta vida
    IF p_odometro_vehiculo_en_evento IS NOT NULL AND v_odometro_instalacion_neumatico IS NOT NULL 
       AND p_odometro_vehiculo_en_evento >= v_odometro_instalacion_neumatico THEN
        v_km_recorridos_vida_calculados := p_odometro_vehiculo_en_evento - v_odometro_instalacion_neumatico;
    ELSE
        v_km_recorridos_vida_calculados := COALESCE(v_kilometraje_vida_actual_neumatico, 0); 
    END IF;

    -- Actualizar el neumático con los nuevos valores
    UPDATE neumaticos
    SET 
        estado_actual = p_destino_desmontaje,
        ubicacion_actual_vehiculo_id = NULL,
        ubicacion_actual_posicion_id = NULL,
        ubicacion_almacen_id = CASE WHEN p_destino_desmontaje = 'EN_STOCK' THEN p_almacen_destino_id ELSE ubicacion_almacen_id END,
        profundidad_remanente_actual_mm = v_profundidad_remanente_evento,
        fecha_ultima_medicion_profundidad = p_timestamp_evento,
        kilometraje_vida_actual = v_km_recorridos_vida_calculados,
        kilometraje_acumulado = v_kilometraje_acumulado_neumatico + COALESCE(v_km_recorridos_vida_calculados, 0),
        odometro_instalacion_vida_actual = NULL,
        fecha_ultimo_evento = p_timestamp_evento,
        actualizado_en = NOW(),
        actualizado_por = p_usuario_id
    WHERE id = p_neumatico_id;

    -- Si hay suficiente información, actualizar la tasa de desgaste real
    IF v_profundidad_remanente_evento IS NOT NULL AND v_km_recorridos_vida_calculados > 0 AND v_profundidad_inicio_vida_actual IS NOT NULL THEN
        PERFORM public.actualizar_tasa_desgaste_real(
            p_neumatico_id,
            v_profundidad_inicio_vida_actual,
            v_profundidad_remanente_evento,
            v_km_recorridos_vida_calculados
        );
    END IF;

    -- Registrar el evento de desmontaje
    INSERT INTO eventos_neumaticos (
        id,
        neumatico_id,
        tipo_evento,
        timestamp_evento,
        odometro_vehiculo_en_evento,
        vehiculo_id,
        posicion_id,
        usuario_id,
        datos_evento,
        notas,
        destino_desmontaje,
        almacen_destino_id
    ) VALUES (
        gen_random_uuid(),
        p_neumatico_id,
        'DESMONTAJE',
        p_timestamp_evento,
        p_odometro_vehiculo_en_evento,
        v_vehiculo_anterior_neumatico,
        v_posicion_anterior_neumatico,
        p_usuario_id,
        jsonb_build_object(
            'profundidad_medida', v_profundidad_remanente_evento,
            'motivo', 'Desmontaje programado',
            'kilometros_vida', v_km_recorridos_vida_calculados
        ),
        'Desmontaje registrado por el sistema. Estado destino: ' || COALESCE(p_destino_desmontaje::TEXT, 'NO ESPECIFICADO'),
        p_destino_desmontaje,
        p_almacen_destino_id
    ) RETURNING id INTO v_evento_id;

    -- Registrar la operación en la bitácora
    INSERT INTO public.bitacora_operaciones_neumaticos (
        neumatico_id,
        tipo_operacion,
        fecha_operacion,
        usuario_id,
        vehiculo_id,
        posicion_neumatico_id,
        odometro,
        profundidad_medida_mm,
        notas
    ) VALUES (
        p_neumatico_id,
        'DESMONTAJE',
        p_timestamp_evento,
        p_usuario_id,
        v_vehiculo_anterior_neumatico,
        v_posicion_anterior_neumatico,
        p_odometro_vehiculo_en_evento,
        v_profundidad_remanente_evento,
        'Desmontaje registrado por el sistema. Estado destino: ' || COALESCE(p_destino_desmontaje::TEXT, 'NO ESPECIFICADO')
    );
    
    -- No es necesario retornar nada ya que la función es de tipo VOID

EXCEPTION WHEN OTHERS THEN
    DECLARE
        v_username TEXT;
    BEGIN
        -- Obtener el nombre de usuario para el registro de error
        SELECT username INTO v_username 
        FROM usuarios 
        WHERE id = p_usuario_id 
        LIMIT 1;
        
        -- Registrar el error en la tabla de errores
        INSERT INTO public.errores_aplicacion (
            nombre_funcion, 
            mensaje_error, 
            detalles, 
            creado_por
        ) VALUES (
            'manejar_desmontaje_neumatico', 
            SQLERRM,
            jsonb_build_object(
                'neumatico_id', COALESCE(p_neumatico_id::TEXT, 'NULL'),
                'usuario_id', COALESCE(p_usuario_id::TEXT, 'NULL'),
                'sqlstate', SQLSTATE,
                'error_context', pg_caller_function_name()
            ), 
            COALESCE(v_username, 'SISTEMA')
        );
        
        -- Relanzar el error para que se propague
        RAISE EXCEPTION 'Error en manejar_desmontaje_neumatico: %', SQLERRM;
    END;
END;
$$;


ALTER FUNCTION public.manejar_desmontaje_neumatico(p_neumatico_id uuid, p_odometro_vehiculo_en_evento integer, p_profundidad_medida numeric, p_destino_desmontaje text, p_almacen_destino_id uuid, p_usuario_id uuid, p_timestamp_evento timestamp without time zone) OWNER TO postgres;

--
-- Name: FUNCTION manejar_desmontaje_neumatico(p_neumatico_id uuid, p_odometro_vehiculo_en_evento integer, p_profundidad_medida numeric, p_destino_desmontaje text, p_almacen_destino_id uuid, p_usuario_id uuid, p_timestamp_evento timestamp without time zone); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.manejar_desmontaje_neumatico(p_neumatico_id uuid, p_odometro_vehiculo_en_evento integer, p_profundidad_medida numeric, p_destino_desmontaje text, p_almacen_destino_id uuid, p_usuario_id uuid, p_timestamp_evento timestamp without time zone) IS 'Maneja el desmontaje de neumáticos, actualizando su estado y registrando el evento correspondiente.';


--
-- Name: manejar_desmontaje_neumatico(uuid, integer, numeric, text, uuid, uuid, timestamp with time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.manejar_desmontaje_neumatico(p_neumatico_id uuid, p_odometro_vehiculo_en_evento integer, p_profundidad_medida numeric DEFAULT NULL::numeric, p_destino_desmontaje text DEFAULT 'EN_STOCK'::text, p_almacen_destino_id uuid DEFAULT NULL::uuid, p_usuario_id uuid DEFAULT NULL::uuid, p_timestamp_evento timestamp with time zone DEFAULT now()) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    -- Variables para configuraciones
    v_old_statement_timeout TEXT;
    v_old_lock_timeout TEXT;
    
    -- Variables para almacenar el estado actual del neumático
    v_odometro_instalacion_neumatico INTEGER;
    v_km_recorridos_vida_calculados INTEGER;
    v_estado_anterior_neumatico public.estado_neumatico_enum;
    v_vehiculo_anterior_neumatico UUID;
    v_posicion_anterior_neumatico UUID;
    v_estado_actual estado_neumatico_enum;
    v_actualizado BOOLEAN;
    v_profundidad_remanente_evento NUMERIC(5,2);
    v_kilometraje_vida_actual_neumatico INTEGER;
    v_kilometraje_acumulado_neumatico INTEGER;
    v_vehiculo_id UUID;
    v_posicion_id UUID;
    v_evento_id UUID;
    v_bitacora_id UUID;
    
    -- Variables para el manejo del destino de desmontaje
    v_destino_desmontaje_enum estado_neumatico_enum;
    v_ubicacion_almacen_id UUID;
    v_vida_actual_neumatico INTEGER;
    v_profundidad_inicio_vida_actual NUMERIC(5,2);
BEGIN
    -- Configurar timeouts para evitar bloqueos prolongados
    BEGIN
        -- Guardar los valores actuales de los timeouts
        SHOW statement_timeout INTO v_old_statement_timeout;
        SHOW lock_timeout INTO v_old_lock_timeout;
        
        -- Establecer nuevos timeouts (30 segundos)
        EXECUTE 'SET LOCAL statement_timeout = ''30s''';
        EXECUTE 'SET LOCAL lock_timeout = ''30s''';
    EXCEPTION WHEN OTHERS THEN
        -- Si hay algún error al configurar los timeouts, continuar de todos modos
        RAISE NOTICE 'No se pudieron configurar los timeouts: %', SQLERRM;
    END;
    
    -- Validar parámetros obligatorios
    IF p_neumatico_id IS NULL THEN
        RAISE EXCEPTION 'El ID del neumático no puede ser nulo';
    END IF;
    
    -- Obtener el estado actual del neumático para asegurarnos de que es 'INSTALADO'
    SELECT estado_actual INTO v_estado_actual 
    FROM neumaticos 
    WHERE id = p_neumatico_id;
    
    IF v_estado_actual IS DISTINCT FROM 'INSTALADO'::estado_neumatico_enum THEN
        RAISE EXCEPTION 'El neumático no está instalado. Estado actual: %', v_estado_actual;
    END IF;
    
    -- Establecer valor predeterminado para la profundidad si es nulo
    v_profundidad_remanente_evento := COALESCE(p_profundidad_medida, 15.00);
    
    -- Convertir el destino de desmontaje al tipo enum correspondiente
    BEGIN
        v_destino_desmontaje_enum := p_destino_desmontaje::estado_neumatico_enum;
    EXCEPTION WHEN OTHERS THEN
        v_destino_desmontaje_enum := 'EN_STOCK';
        RAISE NOTICE 'Valor de destino_desmontaje no válido: %. Usando EN_STOCK por defecto.', p_destino_desmontaje;
    END;

    -- Obtener el estado actual del neumático con bloqueo para evitar condiciones de carrera
    -- Usamos NOWAIT para fallar inmediatamente si el registro ya está bloqueado
    SELECT 
        n.estado_actual, n.ubicacion_actual_vehiculo_id, n.ubicacion_actual_posicion_id,
        n.odometro_instalacion_vida_actual, n.kilometraje_vida_actual, n.kilometraje_acumulado,
        n.profundidad_inicio_vida_actual_mm,
        n.ubicacion_almacen_id  -- Asegurarnos de obtener este valor también
    INTO 
        v_estado_anterior_neumatico, v_vehiculo_anterior_neumatico, v_posicion_anterior_neumatico,
        v_odometro_instalacion_neumatico, v_kilometraje_vida_actual_neumatico, v_kilometraje_acumulado_neumatico,
        v_profundidad_inicio_vida_actual,
        v_ubicacion_almacen_id  -- Variable que necesitamos declarar
    FROM neumaticos n 
    WHERE n.id = p_neumatico_id 
    FOR UPDATE NOWAIT;  -- Fallará inmediatamente si el registro ya está bloqueado

    -- Calcular kilómetros recorridos en esta vida
    IF p_odometro_vehiculo_en_evento IS NOT NULL AND v_odometro_instalacion_neumatico IS NOT NULL 
       AND p_odometro_vehiculo_en_evento >= v_odometro_instalacion_neumatico THEN
        v_km_recorridos_vida_calculados := p_odometro_vehiculo_en_evento - v_odometro_instalacion_neumatico;
    ELSE
        v_km_recorridos_vida_calculados := COALESCE(v_kilometraje_vida_actual_neumatico, 0); 
    END IF;

    -- Actualizar el neumático en una sola operación atómica
    -- Primero, desactivar temporalmente los triggers problemáticos
    EXECUTE 'ALTER TABLE neumaticos DISABLE TRIGGER tr_registrar_cambio_estado';
    EXECUTE 'ALTER TABLE neumaticos DISABLE TRIGGER tr_actualizar_metricas_rendimiento';
    
    -- Realizar la actualización
    IF v_destino_desmontaje_enum = 'EN_STOCK' THEN
        -- Para estado 'EN_STOCK', establecer ubicación en almacén
        UPDATE neumaticos
        SET 
            estado_actual = 'EN_STOCK'::estado_neumatico_enum,
            ubicacion_actual_vehiculo_id = NULL,
            ubicacion_actual_posicion_id = NULL,
            ubicacion_almacen_id = p_almacen_destino_id,
            profundidad_remanente_actual_mm = v_profundidad_remanente_evento,
            fecha_ultima_medicion_profundidad = p_timestamp_evento,
            kilometraje_vida_actual = v_km_recorridos_vida_calculados,
            kilometraje_acumulado = v_kilometraje_acumulado_neumatico + COALESCE(v_km_recorridos_vida_calculados, 0),
            odometro_instalacion_vida_actual = NULL,
            fecha_ultimo_evento = p_timestamp_evento,
            actualizado_en = NOW(),
            actualizado_por = p_usuario_id
        WHERE id = p_neumatico_id
        RETURNING estado_actual INTO v_estado_actual;
    ELSE
        -- Para otros estados, solo limpiar la ubicación
        UPDATE neumaticos
        SET 
            estado_actual = v_destino_desmontaje_enum::estado_neumatico_enum,
            ubicacion_actual_vehiculo_id = NULL,
            ubicacion_actual_posicion_id = NULL,
            ubicacion_almacen_id = NULL,
            profundidad_remanente_actual_mm = v_profundidad_remanente_evento,
            fecha_ultima_medicion_profundidad = p_timestamp_evento,
            kilometraje_vida_actual = v_km_recorridos_vida_calculados,
            kilometraje_acumulado = v_kilometraje_acumulado_neumatico + COALESCE(v_km_recorridos_vida_calculados, 0),
            odometro_instalacion_vida_actual = NULL,
            fecha_ultimo_evento = p_timestamp_evento,
            actualizado_en = NOW(),
            actualizado_por = p_usuario_id
        WHERE id = p_neumatico_id
        RETURNING estado_actual INTO v_estado_actual;
    END IF;
    
    -- Verificar si se actualizó el registro
    IF v_estado_actual IS NULL THEN
        -- Reactivar los triggers antes de lanzar la excepción
        EXECUTE 'ALTER TABLE neumaticos ENABLE TRIGGER tr_registrar_cambio_estado';
        EXECUTE 'ALTER TABLE neumaticos ENABLE TRIGGER tr_actualizar_metricas_rendimiento';
        RAISE EXCEPTION 'No se pudo actualizar el neumático. Puede que el registro no exista o haya sido eliminado.';
    END IF;
    
    -- Registrar manualmente el cambio de estado
    INSERT INTO historial_estados_neumaticos (
        neumatico_id,
        estado_anterior,
        estado_nuevo,
        usuario_id,
        comentario,
        fecha_cambio
    ) VALUES (
        p_neumatico_id,
        v_estado_anterior_neumatico::VARCHAR(50),
        v_estado_actual::VARCHAR(50),
        p_usuario_id,
        'Cambio de estado por desmontaje a ' || v_destino_desmontaje_enum::TEXT,
        NOW()
    );
    
    -- Actualizar manualmente las métricas de rendimiento
    PERFORM public.actualizar_metricas_rendimiento_manual(
        p_neumatico_id => p_neumatico_id,
        p_profundidad_remanente => v_profundidad_remanente_evento,
        p_kilometraje_vida_actual => v_km_recorridos_vida_calculados,
        p_vida_actual => v_vida_actual_neumatico
    );
    
    -- Reactivar los triggers
    EXECUTE 'ALTER TABLE neumaticos ENABLE TRIGGER tr_registrar_cambio_estado';
    EXECUTE 'ALTER TABLE neumaticos ENABLE TRIGGER tr_actualizar_metricas_rendimiento';
    
    -- Verificar si la actualización fue exitosa
    IF v_estado_actual IS NULL THEN
        RAISE EXCEPTION 'No se pudo actualizar el neumático. Puede que el registro haya sido modificado por otra transacción.';
    END IF;
    
    -- Registrar manualmente el cambio de estado en el historial
    PERFORM registrar_cambio_estado_manual(
        p_neumatico_id => p_neumatico_id,
        p_estado_anterior => v_estado_anterior_neumatico,
        p_estado_nuevo => v_estado_actual,
        p_usuario_id => p_usuario_id,
        p_comentario => 'Cambio de estado por desmontaje a ' || v_destino_desmontaje_enum::TEXT
    );
    
    -- Actualizar las métricas de rendimiento manualmente
    PERFORM public.actualizar_metricas_rendimiento_manual(
        p_neumatico_id => p_neumatico_id,
        p_profundidad_remanente => v_profundidad_remanente_evento,
        p_kilometraje_vida_actual => v_km_recorridos_vida_calculados,
        p_vida_actual => v_vida_actual_neumatico
    );
    
    -- No es necesario registrar manualmente el cambio de estado
    -- ya que el trigger lo hará automáticamente
    -- Solo verificamos si el estado cambió para propósitos de registro
    IF v_estado_anterior_neumatico IS DISTINCT FROM v_estado_actual THEN
        RAISE NOTICE 'Estado del neumático cambiado de % a %', v_estado_anterior_neumatico, v_estado_actual;
    END IF;

    -- Si hay suficiente información, actualizar la tasa de desgaste real
    IF v_profundidad_remanente_evento IS NOT NULL AND v_km_recorridos_vida_calculados > 0 AND v_profundidad_inicio_vida_actual IS NOT NULL THEN
        PERFORM public.actualizar_tasa_desgaste_real(
            p_neumatico_id,
            v_profundidad_inicio_vida_actual,
            v_profundidad_remanente_evento,
            v_km_recorridos_vida_calculados
        );
    END IF;

    -- Registrar el evento de desmontaje
    INSERT INTO eventos_neumaticos (
            id,
            neumatico_id,
            tipo_evento,
            timestamp_evento,
            odometro_vehiculo_en_evento,
            vehiculo_id,
            posicion_id,
            usuario_id,
            datos_evento,
            notas,
            destino_desmontaje,
            almacen_destino_id
        ) VALUES (
            gen_random_uuid(),
            p_neumatico_id,
            'DESMONTAJE'::tipo_evento_neumatico_enum,
            p_timestamp_evento,
            p_odometro_vehiculo_en_evento,
            v_vehiculo_anterior_neumatico,
            v_posicion_anterior_neumatico,
            p_usuario_id,
            jsonb_build_object(
                'profundidad_medida', v_profundidad_remanente_evento,
                'motivo', 'Desmontaje programado',
                'kilometros_vida', v_km_recorridos_vida_calculados
            ),
            'Desmontaje registrado por el sistema. Estado destino: ' || COALESCE(p_destino_desmontaje::TEXT, 'NO ESPECIFICADO'),
            v_destino_desmontaje_enum,
            p_almacen_destino_id
        ) RETURNING id INTO v_evento_id;

    -- Registrar la operación en la bitácora
    INSERT INTO public.bitacora_operaciones_neumaticos (
        neumatico_id,
        tipo_operacion,
        fecha_operacion,
        usuario_id,
        vehiculo_id,
        posicion_neumatico_id,
        odometro,
        profundidad_medida_mm,
        notas
    ) VALUES (
        p_neumatico_id,
        'DESMONTAJE',
        p_timestamp_evento,
        p_usuario_id,
        v_vehiculo_anterior_neumatico,
        v_posicion_anterior_neumatico,
        p_odometro_vehiculo_en_evento,
        v_profundidad_remanente_evento,
        'Desmontaje registrado por el sistema. Estado destino: ' || COALESCE(p_destino_desmontaje::TEXT, 'NO ESPECIFICADO')
    );
    
    -- Restaurar los timeouts a sus valores originales
    BEGIN
        IF v_old_statement_timeout IS NOT NULL THEN
            EXECUTE 'SET LOCAL statement_timeout = ' || quote_literal(v_old_statement_timeout);
        END IF;
        
        IF v_old_lock_timeout IS NOT NULL THEN
            EXECUTE 'SET LOCAL lock_timeout = ' || quote_literal(v_old_lock_timeout);
        END IF;
    EXCEPTION WHEN OTHERS THEN
        -- Si hay algún error al restaurar los timeouts, solo registrar el error
        RAISE NOTICE 'No se pudieron restaurar los timeouts: %', SQLERRM;
    END;

    -- No es necesario retornar nada ya que la función es de tipo VOID

EXCEPTION WHEN OTHERS THEN
    -- Asegurarse de restaurar los timeouts y el trigger incluso si hay un error
    BEGIN
        -- Intentar volver a habilitar el trigger si se deshabilitó
        BEGIN
            EXECUTE 'ALTER TABLE neumaticos ENABLE TRIGGER tr_registrar_cambio_estado';
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'No se pudo volver a habilitar el trigger: %', SQLERRM;
        END;
        
        -- Restaurar timeouts
        IF v_old_statement_timeout IS NOT NULL THEN
            BEGIN
                EXECUTE 'SET LOCAL statement_timeout = ' || quote_literal(v_old_statement_timeout);
            EXCEPTION WHEN OTHERS THEN
                RAISE NOTICE 'No se pudo restaurar statement_timeout: %', SQLERRM;
            END;
        END IF;
        
        IF v_old_lock_timeout IS NOT NULL THEN
            BEGIN
                EXECUTE 'SET LOCAL lock_timeout = ' || quote_literal(v_old_lock_timeout);
            EXCEPTION WHEN OTHERS THEN
                RAISE NOTICE 'No se pudo restaurar lock_timeout: %', SQLERRM;
            END;
        END IF;
        
        -- Relanzar el error original
        RAISE;
    END;
    DECLARE
        v_username TEXT;
    BEGIN
        -- Obtener el nombre de usuario para el registro de error
        SELECT username INTO v_username 
        FROM usuarios 
        WHERE id = p_usuario_id 
        LIMIT 1;
        
        -- Registrar el error en la tabla de errores
        INSERT INTO public.errores_aplicacion (
            nombre_funcion, 
            mensaje_error, 
            detalles, 
            creado_por
        ) VALUES (
            'manejar_desmontaje_neumatico', 
            SQLERRM,
            jsonb_build_object(
                'neumatico_id', COALESCE(p_neumatico_id::TEXT, 'NULL'),
                'usuario_id', COALESCE(p_usuario_id::TEXT, 'NULL'),
                'sqlstate', SQLSTATE,
                'error_context', 'Error en manejar_desmontaje_neumatico'
            ), 
            COALESCE(v_username, 'SISTEMA')
        );
        
        -- Relanzar el error para que se propague
        RAISE EXCEPTION 'Error en manejar_desmontaje_neumatico: %', SQLERRM;
    END;
END;
$$;


ALTER FUNCTION public.manejar_desmontaje_neumatico(p_neumatico_id uuid, p_odometro_vehiculo_en_evento integer, p_profundidad_medida numeric, p_destino_desmontaje text, p_almacen_destino_id uuid, p_usuario_id uuid, p_timestamp_evento timestamp with time zone) OWNER TO postgres;

--
-- Name: manejar_evento_desmontaje(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.manejar_evento_desmontaje() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_neumatico_id UUID;
    v_odometro_instalacion_neumatico INTEGER;
    v_odometro_evento INTEGER;
    v_km_recorridos_vida_calculados INTEGER;
    v_estado_anterior_neumatico public.estado_neumatico_enum;
    v_vehiculo_anterior_neumatico UUID;
    v_posicion_anterior_neumatico UUID;
    v_profundidad_remanente_evento NUMERIC(5,2);
    v_kilometraje_vida_actual_neumatico INTEGER;
    v_kilometraje_acumulado_neumatico INTEGER;
    v_profundidad_inicio_vida_actual_para_tasa NUMERIC(5,2);
    v_bitacora_operacion_id UUID;
    v_es_retirado BOOLEAN;
    v_error_message TEXT;

BEGIN
    -- Solo procesar eventos de desmontaje
    IF NEW.tipo_evento != 'DESMONTAJE' THEN
        RETURN NEW; 
    END IF;
    
    -- Inicializar variables
    v_neumatico_id := NEW.neumatico_id;
    v_odometro_evento := NEW.odometro_vehiculo_en_evento;
    v_profundidad_remanente_evento := NEW.profundidad_remanente_mm;
    v_es_retirado := (NEW.destino_desmontaje IN ('EN_REENCAUCHE', 'DESECHADO'));

    -- Obtener datos actuales del neumático SIN BLOQUEAR LA FILA
    SELECT 
        n.estado_actual, n.ubicacion_actual_vehiculo_id, n.ubicacion_actual_posicion_id,
        n.odometro_instalacion_vida_actual, n.kilometraje_vida_actual, n.kilometraje_acumulado,
        n.profundidad_inicio_vida_actual_mm, n.profundidad_remanente_actual_mm
    INTO 
        v_estado_anterior_neumatico, v_vehiculo_anterior_neumatico, v_posicion_anterior_neumatico,
        v_odometro_instalacion_neumatico, v_kilometraje_vida_actual_neumatico, v_kilometraje_acumulado_neumatico,
        v_profundidad_inicio_vida_actual_para_tasa, v_profundidad_remanente_evento
    FROM neumaticos n 
    WHERE n.id = v_neumatico_id;

    -- Si no se encontró el neumático, registrar error y salir
    IF v_estado_anterior_neumatico IS NULL THEN
        INSERT INTO public.errores_aplicacion (
            nombre_funcion, mensaje_error, detalles, creado_por
        ) VALUES (
            'manejar_evento_desmontaje',
            'No se encontró el neumático con ID ' || COALESCE(v_neumatico_id::TEXT, 'NULL'),
            jsonb_build_object('evento_id', COALESCE(NEW.id::TEXT, 'NULL')),
            COALESCE((SELECT username FROM usuarios WHERE id = NEW.usuario_id LIMIT 1), 'SISTEMA')
        );
        RETURN NEW; -- Continuar con la operación para evitar errores en cascada
    END IF;

    -- Calcular kilómetros recorridos en esta vida
    IF v_odometro_evento IS NOT NULL AND v_odometro_instalacion_neumatico IS NOT NULL 
       AND v_odometro_evento >= v_odometro_instalacion_neumatico THEN
        v_km_recorridos_vida_calculados := v_odometro_evento - v_odometro_instalacion_neumatico;
    ELSE
        v_km_recorridos_vida_calculados := COALESCE(v_kilometraje_vida_actual_neumatico, 0);
    END IF;

    -- Actualizar el neumático con los nuevos valores
    UPDATE neumaticos
    SET 
        estado_actual = NEW.destino_desmontaje,
        ubicacion_actual_vehiculo_id = CASE WHEN v_es_retirado THEN NULL ELSE ubicacion_actual_vehiculo_id END,
        ubicacion_actual_posicion_id = CASE WHEN v_es_retirado THEN NULL ELSE ubicacion_actual_posicion_id END,
        ubicacion_almacen_id = CASE 
                                WHEN NEW.destino_desmontaje = 'EN_STOCK' THEN NEW.almacen_destino_id
                                ELSE ubicacion_almacen_id
                             END,
        profundidad_remanente_actual_mm = COALESCE(v_profundidad_remanente_evento, profundidad_remanente_actual_mm),
        fecha_ultima_medicion_profundidad = CASE 
                                            WHEN v_profundidad_remanente_evento IS NOT NULL 
                                            THEN COALESCE(NEW.timestamp_evento, NOW())
                                            ELSE fecha_ultima_medicion_profundidad 
                                          END,
        kilometraje_vida_actual = v_km_recorridos_vida_calculados,
        kilometraje_acumulado = v_kilometraje_acumulado_neumatico + v_km_recorridos_vida_calculados,
        odometro_instalacion_vida_actual = CASE WHEN v_es_retirado THEN NULL ELSE odometro_instalacion_vida_actual END,
        profundidad_inicio_vida_actual_mm = CASE 
                                            WHEN v_es_retirado THEN NULL 
                                            ELSE profundidad_inicio_vida_actual_mm 
                                          END,
        tasa_desgaste_actual_mm_km = CASE 
                                    WHEN v_es_retirado THEN NULL 
                                    ELSE tasa_desgaste_actual_mm_km 
                                  END,
        fecha_inicio_vida_actual = CASE WHEN v_es_retirado THEN NULL ELSE fecha_inicio_vida_actual END,
        fecha_ultimo_evento = COALESCE(NEW.timestamp_evento, NOW()),
        actualizado_en = NOW(),
        actualizado_por = NEW.usuario_id
    WHERE id = v_neumatico_id;

    -- Actualizar la tasa de desgaste real si es necesario
    IF v_profundidad_remanente_evento IS NOT NULL 
       AND v_km_recorridos_vida_calculados > 0 
       AND v_profundidad_inicio_vida_actual_para_tasa IS NOT NULL 
       AND v_profundidad_inicio_vida_actual_para_tasa > v_profundidad_remanente_evento
       AND NOT v_es_retirado THEN
        
        -- Llamada CORREGIDA a la función actualizar_tasa_desgaste_real con 4 parámetros
        PERFORM public.actualizar_tasa_desgaste_real(
            v_neumatico_id,                           -- ID del neumático
            v_profundidad_inicio_vida_actual_para_tasa,  -- Profundidad al inicio (mm)
            v_profundidad_remanente_evento,           -- Profundidad al final (mm)
            v_km_recorridos_vida_calculados           -- Kilometraje recorrido (km)
        );
    END IF;

    -- Registrar en bitacora_operaciones
    INSERT INTO public.bitacora_operaciones (
        tipo_operacion, 
        descripcion, 
        fecha_operacion, 
        usuario_id, 
        vehiculo_id, 
        estado_operacion, 
        creado_por, 
        actualizado_por
    ) VALUES (
        'DESMONTAJE'::public.tipo_operacion_enum,
        'Desmontaje del neumático ' || v_neumatico_id::TEXT || 
        ' del vehículo ' || COALESCE(v_vehiculo_anterior_neumatico::TEXT, 'N/A') ||
        '. Destino: ' || COALESCE(NEW.destino_desmontaje::TEXT, 'NO ESPECIFICADO') ||
        CASE WHEN v_km_recorridos_vida_calculados > 0 
             THEN '. Kilómetros recorridos: ' || v_km_recorridos_vida_calculados::TEXT
             ELSE ''
        END,
        COALESCE(NEW.timestamp_evento, NOW()),
        NEW.usuario_id,
        v_vehiculo_anterior_neumatico,
        'COMPLETADA',
        NEW.usuario_id, 
        NEW.usuario_id
    ) RETURNING id INTO v_bitacora_operacion_id;

    -- Registrar en bitacora_operaciones_neumaticos
    INSERT INTO public.bitacora_operaciones_neumaticos (
        operacion_id, 
        neumatico_id, 
        tipo_accion, 
        posicion_neumatico_id, 
        kilometraje_vehiculo_km, 
        profundidad_final_mm, 
        observaciones,
        creado_por, 
        actualizado_por
    ) VALUES (
        v_bitacora_operacion_id, 
        v_neumatico_id, 
        'DESMONTAJE'::public.tipo_accion_operacion_enum, 
        v_posicion_anterior_neumatico, 
        v_odometro_evento, 
        v_profundidad_remanente_evento,
        'Neumático desmontado. Estado anterior: ' || COALESCE(v_estado_anterior_neumatico::TEXT, 'N/A') || 
        '. Destino: ' || COALESCE(NEW.destino_desmontaje::TEXT, 'NO ESPECIFICADO'),
        NEW.usuario_id, 
        NEW.usuario_id
    );
    
    RETURN NEW;
    
EXCEPTION WHEN OTHERS THEN
    -- Registrar el error en la tabla de errores
    INSERT INTO public.errores_aplicacion (
        nombre_funcion,
        mensaje_error,
        detalles,
        creado_por
    ) VALUES (
        'manejar_evento_desmontaje',
        SQLERRM,
        jsonb_build_object(
            'evento_id', COALESCE(NEW.id::TEXT, 'NULL'),
            'neumatico_id', COALESCE(NEW.neumatico_id::TEXT, 'NULL'),
            'sqlstate', SQLSTATE
        ),
        COALESCE((SELECT username FROM usuarios WHERE id = NEW.usuario_id LIMIT 1), 'SISTEMA')
    );

    -- Relanzar el error para que se propague
    RAISE WARNING 'Error en manejar_evento_desmontaje: %', SQLERRM;
    RETURN NEW; -- Importante: devolver NEW para evitar que falle la operación
END;
$$;


ALTER FUNCTION public.manejar_evento_desmontaje() OWNER TO postgres;

--
-- Name: FUNCTION manejar_evento_desmontaje(); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.manejar_evento_desmontaje() IS 'Función de trigger que maneja los eventos de desmontaje de neumáticos.

Actualiza el estado del neumático según el destino del desmontaje y registra
las operaciones realizadas en las bitácoras correspondientes.

Parámetros:
- NEW: Registro del evento de desmontaje que activó el trigger';


--
-- Name: manejar_evento_desmontaje_backup(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.manejar_evento_desmontaje_backup() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Esta es una copia de seguridad de la función original
    -- No se ejecutará, solo está aquí como respaldo
    RETURN NULL;
END;
$$;


ALTER FUNCTION public.manejar_evento_desmontaje_backup() OWNER TO postgres;

--
-- Name: manejar_evento_instalacion(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.manejar_evento_instalacion() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_profundidad_actual_neumatico NUMERIC(5,2);
    v_vida_actual_neumatico INTEGER;
    v_profundidad_inicio_vida_actual NUMERIC(5,2);
    v_modelo_id_neumatico UUID;
BEGIN
    IF NEW.tipo_evento = 'INSTALACION' THEN
        SELECT 
            n.profundidad_remanente_actual_mm, 
            n.vida_actual,
            n.modelo_id
        INTO 
            v_profundidad_actual_neumatico, 
            v_vida_actual_neumatico,
            v_modelo_id_neumatico
        FROM neumaticos n
        WHERE n.id = NEW.neumatico_id
        FOR UPDATE;

        IF v_vida_actual_neumatico = 1 THEN
            SELECT m.profundidad_original_mm
            INTO v_profundidad_inicio_vida_actual
            FROM modelos_neumatico m
            WHERE m.id = v_modelo_id_neumatico; 
        ELSE
            v_profundidad_inicio_vida_actual := v_profundidad_actual_neumatico;
        END IF;

        IF v_profundidad_inicio_vida_actual IS NULL THEN
            SELECT m.profundidad_original_mm 
            INTO v_profundidad_inicio_vida_actual
            FROM modelos_neumatico m
            WHERE m.id = v_modelo_id_neumatico;
            RAISE WARNING 'Profundidad de inicio de vida para neumático % en vida % no estaba pre-establecida o era NULL, usando profundidad original del modelo %', 
                          NEW.neumatico_id, v_vida_actual_neumatico, v_profundidad_inicio_vida_actual;
        END IF;

        UPDATE neumaticos
        SET 
            profundidad_inicio_vida_actual_mm = v_profundidad_inicio_vida_actual,
            profundidad_remanente_actual_mm = v_profundidad_inicio_vida_actual, 
            fecha_inicio_vida_actual = NEW.timestamp_evento,
            kilometraje_vida_actual = 0,
            odometro_instalacion_vida_actual = NEW.odometro_vehiculo_en_evento,
            tasa_desgaste_actual_mm_km = NULL,
            estado_actual = 'INSTALADO',
            ubicacion_actual_vehiculo_id = NEW.vehiculo_id,
            ubicacion_actual_posicion_id = NEW.posicion_id,
            ubicacion_almacen_id = NULL,
            fecha_ultimo_evento = NEW.timestamp_evento,
            actualizado_en = NOW(),
            actualizado_por = NEW.usuario_id
        WHERE id = NEW.neumatico_id;

        NEW.datos_evento = COALESCE(NEW.datos_evento, '{}'::jsonb) || 
                          jsonb_build_object('profundidad_inicio_vida_actual_mm_registrada', v_profundidad_inicio_vida_actual);
    END IF;
    RETURN NEW;
EXCEPTION WHEN OTHERS THEN
    INSERT INTO public.errores_aplicacion 
        (nombre_funcion, mensaje_error, detalles, creado_por)
    VALUES 
        ('manejar_evento_instalacion', SQLERRM, 
         jsonb_build_object('evento_id', COALESCE(NEW.id::text, 'NULL'), 
                          'neumatico_id', COALESCE(NEW.neumatico_id::text, 'NULL'), 
                          'sqlstate', SQLSTATE), 
         COALESCE(NEW.usuario_id::text, 'SISTEMA'));
    RAISE WARNING 'Error en trigger manejar_evento_instalacion: %', SQLERRM;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.manejar_evento_instalacion() OWNER TO postgres;

--
-- Name: manejar_evento_reencauche_salida(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.manejar_evento_reencauche_salida() RETURNS trigger
    LANGUAGE plpgsql
    AS $_$
DECLARE
    v_neumatico_id UUID;
    v_modelo_actual_id UUID;
    v_profundidad_post_reencauche NUMERIC(5,2);
    v_max_vidas_utiles INTEGER;
    v_reencauches_maximos INTEGER;
BEGIN
    -- Obtener datos del neumático
    SELECT 
        n.id, 
        n.modelo_id,
        m.reencauches_maximos,
        m.max_vidas_utiles
    INTO 
        v_neumatico_id, 
        v_modelo_actual_id,
        v_reencauches_maximos,
        v_max_vidas_utiles
    FROM neumaticos n
    JOIN modelos_neumatico m ON n.modelo_id = m.id
    WHERE n.id = NEW.neumatico_id
    FOR UPDATE;

    -- Verificar consistencia entre reencauches_maximos y max_vidas_utiles
    IF v_max_vidas_utiles IS NULL THEN
        RAISE EXCEPTION 'El modelo de neumático no tiene configurado max_vidas_utiles';
    END IF;
    
    -- Verificar consistencia: max_vidas_utiles debe ser igual a reencauches_maximos + 1
    IF v_max_vidas_utiles != COALESCE(v_reencauches_maximos, 0) + 1 THEN
        -- Intentar corregir la inconsistencia
        UPDATE modelos_neumatico
        SET reencauches_maximos = v_max_vidas_utiles - 1
        WHERE id = v_modelo_actual_id
        RETURNING reencauches_maximos INTO v_reencauches_maximos;
        
        RAISE NOTICE 'Corregida inconsistencia en modelo %: reencauches_maximos actualizado a %', 
                     v_modelo_actual_id, v_reencauches_maximos;
    END IF;

    -- Obtener profundidad post-reencauche del evento
    v_profundidad_post_reencauche := NEW.profundidad_post_reencauche_mm;

    -- Verificar si se superó el máximo de vidas útiles
    IF (SELECT vida_actual + 1 FROM neumaticos WHERE id = v_neumatico_id) > v_max_vidas_utiles THEN
        RAISE EXCEPTION 'Se ha alcanzado el número máximo de vidas útiles (%1$) para este neumático', v_max_vidas_utiles;
    END IF;

    -- Actualizar neumático
    UPDATE neumaticos
    SET
        vida_actual = vida_actual + 1,
        reencauches_realizados = reencauches_realizados + 1,
        profundidad_inicio_vida_actual_mm = v_profundidad_post_reencauche,
        profundidad_remanente_actual_mm = v_profundidad_post_reencauche,
        fecha_ultimo_reencauche = NEW.timestamp_evento,
        fecha_inicio_vida_actual = NEW.timestamp_evento,
        kilometraje_vida_actual = 0,
        tasa_desgaste_actual_mm_km = NULL,
        estado_actual = 'EN_STOCK',
        es_reencauchado = TRUE,
        actualizado_en = NOW(),
        actualizado_por = NEW.usuario_id
    WHERE id = v_neumatico_id;

    RETURN NEW;
EXCEPTION WHEN OTHERS THEN
    RAISE EXCEPTION 'Error en manejar_evento_reencauche_salida: %', SQLERRM;
END;
$_$;


ALTER FUNCTION public.manejar_evento_reencauche_salida() OWNER TO postgres;

--
-- Name: FUNCTION manejar_evento_reencauche_salida(); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.manejar_evento_reencauche_salida() IS 'Actualizada el 2025-05-24: Ahora usa timestamp_evento en lugar de NOW() para fechas de reencauche';


--
-- Name: mantenimiento_diario(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.mantenimiento_diario() RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_start_time TIMESTAMPTZ;
    v_duration INTERVAL;
    v_success BOOLEAN := TRUE;
    v_details TEXT := 'Ejecución completada sin errores';
    v_tables TEXT[] := ARRAY['neumaticos', 'eventos_neumaticos', 'auditoria_log', 'modelos_neumatico'];
    v_table TEXT;
BEGIN
    v_start_time := clock_timestamp();
    RAISE NOTICE 'Iniciando mantenimiento_diario()...';

    -- Bloque para capturar errores
    BEGIN
        -- Actualizar estadísticas de tablas principales
        RAISE NOTICE 'Actualizando estadísticas (ANALYZE)...';
        
        -- Usamos un bucle para analizar cada tabla individualmente
        FOREACH v_table IN ARRAY v_tables LOOP
            BEGIN
                EXECUTE format('ANALYZE VERBOSE public.%I', v_table);
                RAISE NOTICE '  - Tabla % analizada', v_table;
            EXCEPTION WHEN OTHERS THEN
                v_success := FALSE;
                v_details := format('%s\nError al analizar %s: %s', 
                                  COALESCE(v_details, ''), v_table, SQLERRM);
                RAISE WARNING 'Error al analizar %: %', v_table, SQLERRM;
            END;
        END LOOP;

        -- Actualizar vistas materializadas (si la función existe)
        IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'actualizar_vistas_materializadas') THEN
            BEGIN
                RAISE NOTICE 'Actualizando vistas materializadas...';
                PERFORM public.actualizar_vistas_materializadas();
            EXCEPTION WHEN OTHERS THEN
                v_success := FALSE;
                v_details := format('%s\nError al actualizar vistas: %s', 
                                  COALESCE(v_details, ''), SQLERRM);
                RAISE WARNING 'Error al actualizar vistas: %', SQLERRM;
            END;
        ELSE
            RAISE NOTICE 'La función actualizar_vistas_materializadas() no existe, omitiendo...';
            v_details := format('%s\nNota: La función actualizar_vistas_materializadas() no existe', 
                              COALESCE(v_details, ''));
        END IF;

    EXCEPTION WHEN OTHERS THEN
        v_success := FALSE;
        GET STACKED DIAGNOSTICS v_details = MESSAGE_TEXT;
        RAISE WARNING 'Error durante mantenimiento_diario(): %', v_details;
    END;

    -- Registrar la ejecución
    v_duration := clock_timestamp() - v_start_time;
    PERFORM public.registrar_mantenimiento(
        'DIARIO', 
        'Mantenimiento diario automático',
        v_duration,
        v_success,
        v_details
    );

    RAISE NOTICE 'Mantenimiento_diario() finalizado. Duración: %, Éxito: %', v_duration, v_success;
END;
$$;


ALTER FUNCTION public.mantenimiento_diario() OWNER TO postgres;

--
-- Name: FUNCTION mantenimiento_diario(); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.mantenimiento_diario() IS 'Realiza tareas de mantenimiento diario incluyendo:
- Actualización de estadísticas (ANALYZE) en tablas principales
- Actualización de vistas materializadas (si existen)
Registra todas las operaciones en la tabla bitacora_mantenimiento.';


--
-- Name: migrar_garantias_existentes(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.migrar_garantias_existentes() RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO garantias_neumaticos (
        neumatico_id,
        proveedor_id,
        tipo_garantia,
        fecha_inicio,
        fecha_fin,
        kilometraje_cubierto,
        meses_cobertura,
        condiciones_url,
        creado_por,
        actualizado_por
    )
    SELECT 
        id,
        garantia_proveedor_id,
        CASE 
            WHEN garantia_km IS NOT NULL AND garantia_meses IS NOT NULL THEN 'AMBOS'
            WHEN garantia_km IS NOT NULL THEN 'KILOMETRAJE'
            WHEN garantia_meses IS NOT NULL THEN 'TIEMPO'
            ELSE 'TIEMPO' -- Valor por defecto
        END,
        COALESCE(garantia_fecha_inicio, fecha_compra),
        CASE 
            WHEN garantia_meses IS NOT NULL THEN 
                COALESCE(garantia_fecha_inicio, fecha_compra) + (garantia_meses::text || ' months')::interval
            ELSE NULL
        END,
        garantia_km,
        garantia_meses,
        garantia_condiciones_url,
        creado_por,
        actualizado_por
    FROM neumaticos
    WHERE (garantia_proveedor_id IS NOT NULL 
       OR garantia_fecha_inicio IS NOT NULL 
       OR garantia_km IS NOT NULL 
       OR garantia_meses IS NOT NULL)
       AND NOT EXISTS (SELECT 1 FROM garantias_neumaticos WHERE neumatico_id = neumaticos.id);
    
    RETURN;
END;
$$;


ALTER FUNCTION public.migrar_garantias_existentes() OWNER TO postgres;

--
-- Name: monitorear_rendimiento_auditoria(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.monitorear_rendimiento_auditoria() RETURNS TABLE(total_registros bigint, tamano_tabla text, tamano_indices text, registros_por_dia bigint, operaciones_por_tabla jsonb, rendimiento_consulta jsonb)
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Obtener estadísticas generales
    RETURN QUERY
    WITH 
    stats AS (
        SELECT 
            COUNT(*) as total,
            pg_size_pretty(pg_total_relation_size('auditoria_log')) as tamano_total,
            pg_size_pretty(pg_indexes_size('auditoria_log')) as tamano_indices
        FROM auditoria_log
    ),
    daily_stats AS (
        SELECT 
            COUNT(*) as registros_diarios
        FROM auditoria_log
        WHERE timestamp_log >= NOW() - INTERVAL '1 day'
    ),
    operaciones_por_tabla AS (
        SELECT 
            jsonb_object_agg(
                nombre_tabla, 
                jsonb_build_object(
                    'total', COUNT(*),
                    'inserts', SUM(CASE WHEN operacion = 'INSERT' THEN 1 ELSE 0 END),
                    'updates', SUM(CASE WHEN operacion = 'UPDATE' THEN 1 ELSE 0 END),
                    'deletes', SUM(CASE WHEN operacion = 'DELETE' THEN 1 ELSE 0 END)
                )
            ) as datos
        FROM (
            SELECT nombre_tabla, operacion, COUNT(*) 
            FROM auditoria_log 
            GROUP BY nombre_tabla, operacion
            ORDER BY COUNT(*) DESC
        ) t
    ),
    rendimiento AS (
        SELECT 
            jsonb_build_object(
                'consulta_promedio', 
                (SELECT ROUND(AVG(total_time)::numeric, 2) 
                 FROM pg_stat_statements 
                 WHERE query LIKE '%auditoria_log%')
            ) as datos
    )
    SELECT 
        s.total,
        s.tamano_total,
        s.tamano_indices,
        ds.registros_diarios,
        ot.datos as operaciones_por_tabla,
        r.datos as rendimiento_consulta
    FROM stats s, daily_stats ds, operaciones_por_tabla ot, rendimiento r;
END;
$$;


ALTER FUNCTION public.monitorear_rendimiento_auditoria() OWNER TO postgres;

--
-- Name: mostrar_resultado_prueba(text, boolean); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.mostrar_resultado_prueba(p_descripcion text, p_resultado boolean) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF p_resultado THEN
        RAISE NOTICE '✅ %', p_descripcion;
    ELSE
        RAISE NOTICE '❌ %', p_descripcion;
    END IF;
END;
$$;


ALTER FUNCTION public.mostrar_resultado_prueba(p_descripcion text, p_resultado boolean) OWNER TO postgres;

--
-- Name: mostrar_resultado_prueba(text, uuid); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.mostrar_resultado_prueba(p_descripcion text, p_neumatico_id uuid) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_resultado numeric;
    v_info record;
    v_mensaje text;
BEGIN
    -- Obtener información del neumático
    SELECT 
        n.numero_serie, 
        n.estado_actual,
        n.vida_actual,
        n.es_reencauchado,
        n.profundidad_remanente_actual_mm,
        n.tasa_desgaste_actual_mm_km,
        mn.tasa_desgaste_esperada_mm_km,
        COALESCE(mn.porcentaje_desgaste_por_vida, 0) as porcentaje_desgaste_por_vida,
        COALESCE(mn.max_vidas_utiles, 10) as max_vidas_utiles
    INTO v_info
    FROM 
        neumaticos n
        LEFT JOIN modelos_neumatico mn ON n.modelo_id = mn.id
    WHERE 
        n.id = p_neumatico_id;
    
    -- Construir mensaje de información
    v_mensaje := E'--------------------------------------------------\n';
    v_mensaje := v_mensaje || 'PRUEBA: ' || p_descripcion || E'\n';
    v_mensaje := v_mensaje || E'--------------------------------------------------\n';
    v_mensaje := v_mensaje || 'Neumático: ' || COALESCE(v_info.numero_serie, 'N/A') || E'\n';
    v_mensaje := v_mensaje || 'Estado: ' || v_info.estado_actual || 
                 ', Vida actual: ' || v_info.vida_actual || 
                 ', Reencauchado: ' || v_info.es_reencauchado || E'\n';
    v_mensaje := v_mensaje || 'Profundidad actual: ' || v_info.profundidad_remanente_actual_mm || ' mm' || E'\n';
    v_mensaje := v_mensaje || 'Tasa actual: ' || COALESCE(v_info.tasa_desgaste_actual_mm_km::text, 'NULL') || 
                 ' mm/km, Tasa esperada: ' || COALESCE(v_info.tasa_desgaste_esperada_mm_km::text, 'NULL') || ' mm/km' || E'\n';
    v_mensaje := v_mensaje || 'Ajuste por reencauche: ' || v_info.porcentaje_desgaste_por_vida || 
                 '%, Máx vidas: ' || v_info.max_vidas_utiles || E'\n';
    
    -- Mostrar información del neumático
    RAISE NOTICE '%', v_mensaje;
    
    -- Calcular vida útil restante
    BEGIN
        v_resultado := public.calcular_vida_util_restante(p_neumatico_id);
        
        -- Mostrar resultado
        IF v_resultado IS NULL THEN
            RAISE NOTICE 'RESULTADO: No se pudo calcular la vida útil restante (NULL)';
        ELSE
            RAISE NOTICE 'RESULTADO: Vida útil restante: % km', v_resultado;
        END IF;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'ERROR al calcular vida útil: %', SQLERRM;
    END;
    
    RAISE NOTICE '--------------------------------------------------%', E'\n';
END;
$$;


ALTER FUNCTION public.mostrar_resultado_prueba(p_descripcion text, p_neumatico_id uuid) OWNER TO postgres;

--
-- Name: mostrar_resumen_auditoria(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.mostrar_resumen_auditoria(p_tabla text) RETURNS TABLE(operacion text, total bigint, primera_entrada text, ultima_entrada text)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        al.operacion::text,
        COUNT(*) as total,
        to_char(MIN(al.timestamp_log), 'YYYY-MM-DD HH24:MI:SS.MS') as primera_entrada,
        to_char(MAX(al.timestamp_log), 'YYYY-MM-DD HH24:MI:SS.MS') as ultima_entrada
    FROM 
        auditoria_log al
    WHERE 
        al.nombre_tabla = p_tabla
        AND al.timestamp_log > NOW() - INTERVAL '1 hour'
    GROUP BY 
        al.operacion
    ORDER BY 
        al.operacion;
END;
$$;


ALTER FUNCTION public.mostrar_resumen_auditoria(p_tabla text) OWNER TO postgres;

--
-- Name: obtener_cambios_motivos_desecho(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.obtener_cambios_motivos_desecho(p_dias_atras integer DEFAULT 7) RETURNS TABLE(id_auditoria bigint, fecha_hora timestamp with time zone, operacion text, usuario text, ip text, datos_antiguos jsonb, datos_nuevos jsonb, cambios jsonb)
    LANGUAGE plpgsql STABLE SECURITY DEFINER
    AS $$
BEGIN
    RETURN QUERY 
    SELECT 
        al.id as id_auditoria,
        al.timestamp_log as fecha_hora,
        al.operacion::text,
        COALESCE(al.usuario_aplicacion_username, al.usuario_db, 'SISTEMA')::text as usuario,
        COALESCE(al.direccion_ip, '0.0.0.0')::text as ip,
        al.datos_antiguos,
        al.datos_nuevos,
        al.cambios
    FROM 
        auditoria_log al
    WHERE 
        al.nombre_tabla = 'motivos_desecho'
        AND al.timestamp_log >= NOW() - (p_dias_atras * INTERVAL '1 day')
        -- Filtrar solo operaciones relevantes
        AND al.operacion IN ('INSERT', 'UPDATE', 'DELETE')
        -- Asegurarse de que al menos uno de los campos de datos no sea nulo
        AND (al.datos_antiguos IS NOT NULL OR al.datos_nuevos IS NOT NULL OR al.cambios IS NOT NULL)
    ORDER BY 
        al.timestamp_log DESC;
END;
$$;


ALTER FUNCTION public.obtener_cambios_motivos_desecho(p_dias_atras integer) OWNER TO postgres;

--
-- Name: FUNCTION obtener_cambios_motivos_desecho(p_dias_atras integer); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.obtener_cambios_motivos_desecho(p_dias_atras integer) IS 'Obtiene los cambios recientes en la tabla motivos_desecho.

Parámetros:
- p_dias_atras: Número de días hacia atrás para buscar cambios (por defecto 7)

Retorna: Registros de auditoría con los cambios realizados, incluyendo:
- id_auditoria: ID del registro de auditoría
- fecha_hora: Cuándo ocurrió el cambio
- operacion: Tipo de operación (INSERT, UPDATE, DELETE)
- usuario: Usuario que realizó la operación
- ip: Dirección IP del usuario
- datos_antiguos: Datos antes del cambio (para UPDATE y DELETE)
- datos_nuevos: Datos después del cambio (para INSERT y UPDATE)
- cambios: Campos específicos que cambiaron (solo para UPDATE)';


--
-- Name: obtener_estadisticas_auditoria(timestamp without time zone, timestamp without time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.obtener_estadisticas_auditoria(p_desde timestamp without time zone DEFAULT (now() - '30 days'::interval), p_hasta timestamp without time zone DEFAULT now()) RETURNS TABLE(nombre_tabla text, operacion text, total bigint, ultima_actividad timestamp without time zone)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        al.nombre_tabla,
        al.operacion,
        COUNT(*) as total,
        MAX(al.timestamp_log) as ultima_actividad
    FROM public.auditoria_log al
    WHERE al.timestamp_log BETWEEN p_desde AND p_hasta
    GROUP BY al.nombre_tabla, al.operacion
    ORDER BY total DESC;
END;
$$;


ALTER FUNCTION public.obtener_estadisticas_auditoria(p_desde timestamp without time zone, p_hasta timestamp without time zone) OWNER TO postgres;

--
-- Name: obtener_estadisticas_auditoria_motivos_desecho(timestamp with time zone, timestamp with time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.obtener_estadisticas_auditoria_motivos_desecho(p_desde timestamp with time zone DEFAULT NULL::timestamp with time zone, p_hasta timestamp with time zone DEFAULT NULL::timestamp with time zone) RETURNS TABLE(total_registros bigint, total_por_operacion jsonb, registros_por_dia jsonb, usuarios_activos jsonb)
    LANGUAGE plpgsql STABLE SECURITY DEFINER
    AS $$
BEGIN
    -- Si no se especifican fechas, usar los últimos 30 días
    IF p_desde IS NULL THEN
        p_desde := NOW() - INTERVAL '30 days';
    END IF;
    
    IF p_hasta IS NULL THEN
        p_hasta := NOW();
    END IF;
    
    -- Primero, obtener el conteo total
    RETURN QUERY 
    WITH 
    -- Conteo total
    total AS (
        SELECT COUNT(*) as total
        FROM auditoria_log
        WHERE nombre_tabla = 'motivos_desecho'
        AND timestamp_log BETWEEN p_desde AND p_hasta
    ),
    -- Conteo por operación (usando subconsulta para evitar anidación de agregaciones)
    operaciones_agrupadas AS (
        SELECT 
            operacion,
            COUNT(*) as cantidad
        FROM 
            auditoria_log
        WHERE 
            nombre_tabla = 'motivos_desecho'
            AND timestamp_log BETWEEN p_desde AND p_hasta
        GROUP BY 
            operacion
    ),
    por_operacion AS (
        SELECT 
            jsonb_object_agg(
                operacion,
                cantidad::text
            ) as datos
        FROM operaciones_agrupadas
    ),
    -- Conteo por día (usando subconsulta para evitar anidación de agregaciones)
    dias_agrupados AS (
        SELECT 
            to_char(date_trunc('day', timestamp_log), 'YYYY-MM-DD') as dia,
            COUNT(*) as cantidad
        FROM 
            auditoria_log
        WHERE 
            nombre_tabla = 'motivos_desecho'
            AND timestamp_log BETWEEN p_desde AND p_hasta
        GROUP BY 
            date_trunc('day', timestamp_log)
        ORDER BY 
            dia
    ),
    por_dia AS (
        SELECT 
            jsonb_object_agg(
                dia,
                cantidad::text
            ) as datos
        FROM dias_agrupados
    ),
    -- Usuarios más activos (usando subconsulta para evitar anidación de agregaciones)
    usuarios_agrupados AS (
        SELECT 
            COALESCE(usuario_aplicacion_username, 'SISTEMA') as usuario,
            COUNT(*) as cantidad
        FROM 
            auditoria_log
        WHERE 
            nombre_tabla = 'motivos_desecho'
            AND timestamp_log BETWEEN p_desde AND p_hasta
        GROUP BY 
            usuario_aplicacion_username
        ORDER BY 
            COUNT(*) DESC
        LIMIT 10
    ),
    usuarios AS (
        SELECT 
            jsonb_object_agg(
                usuario,
                cantidad::text
            ) as datos
        FROM usuarios_agrupados
    )
    SELECT 
        (SELECT total FROM total) as total_registros,
        (SELECT COALESCE(datos, '{}'::jsonb) FROM por_operacion) as total_por_operacion,
        (SELECT COALESCE(datos, '{}'::jsonb) FROM por_dia) as registros_por_dia,
        (SELECT COALESCE(datos, '{}'::jsonb) FROM usuarios) as usuarios_activos;
END;
$$;


ALTER FUNCTION public.obtener_estadisticas_auditoria_motivos_desecho(p_desde timestamp with time zone, p_hasta timestamp with time zone) OWNER TO postgres;

--
-- Name: FUNCTION obtener_estadisticas_auditoria_motivos_desecho(p_desde timestamp with time zone, p_hasta timestamp with time zone); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.obtener_estadisticas_auditoria_motivos_desecho(p_desde timestamp with time zone, p_hasta timestamp with time zone) IS 'Obtiene estadísticas de auditoría para la tabla motivos_desecho.

Parámetros:
- p_desde: Fecha de inicio para el análisis (opcional, por defecto 30 días atrás)
- p_hasta: Fecha de fin para el análisis (opcional, por defecto ahora)

Retorna: Estadísticas de auditoría en formato JSON';


--
-- Name: obtener_estado_mantenimiento(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.obtener_estado_mantenimiento() RETURNS TABLE(ultima_ejecucion timestamp with time zone, tipo_ejecucion text, exito boolean, duracion interval, detalles text)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        bm.fecha_ejecucion,
        bm.tipo::TEXT,
        bm.exito,
        bm.duracion,
        bm.detalles
    FROM public.bitacora_mantenimiento bm
    ORDER BY bm.fecha_ejecucion DESC
    LIMIT 10;
END;
$$;


ALTER FUNCTION public.obtener_estado_mantenimiento() OWNER TO postgres;

--
-- Name: obtener_historial_neumatico(uuid, integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.obtener_historial_neumatico(p_id_neu uuid, p_limit integer DEFAULT 10, p_offset integer DEFAULT 0) RETURNS TABLE(id bigint, operacion text, fecha_hora timestamp with time zone, usuario text, ip text, detalle text, cambios jsonb)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        al.id,
        al.operacion::text,
        al.timestamp_log as fecha_hora,
        COALESCE(al.usuario_aplicacion_username, al.usuario_db) as usuario,
        al.direccion_ip as ip,
        CASE 
            WHEN al.operacion = 'INSERT' THEN 'Nuevo neumático registrado'
            WHEN al.operacion = 'UPDATE' THEN (
                SELECT string_agg(
                    key || ': ' || 
                    COALESCE((value->>'old')::text, 'NULL') || ' → ' || 
                    COALESCE((value->>'new')::text, 'NULL'), 
                    ', '
                )
                FROM jsonb_each(al.cambios)
            )
            WHEN al.operacion = 'DELETE' THEN 'Neumático eliminado'
        END as detalle,
        al.cambios
    FROM auditoria_log al
    WHERE al.nombre_tabla = 'neumaticos'
    AND al.id_entidad = p_id_neu
    ORDER BY al.timestamp_log DESC
    LIMIT p_limit
    OFFSET p_offset;
END;
$$;


ALTER FUNCTION public.obtener_historial_neumatico(p_id_neu uuid, p_limit integer, p_offset integer) OWNER TO postgres;

--
-- Name: FUNCTION obtener_historial_neumatico(p_id_neu uuid, p_limit integer, p_offset integer); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.obtener_historial_neumatico(p_id_neu uuid, p_limit integer, p_offset integer) IS 'Obtiene el historial de cambios de auditoría para un neumático específico.
Parámetros:
- p_id_neu: ID del neumático
- p_limit: número máximo de registros a devolver (por defecto 10)
- p_offset: número de registros a omitir (para paginación, por defecto 0)

Retorna:
- id: ID del registro de auditoría
- operacion: tipo de operación (INSERT/UPDATE/DELETE)
- fecha_hora: cuándo se realizó la operación
- usuario: quién realizó la operación
- ip: dirección IP desde donde se realizó
- detalle: descripción del cambio
- cambios: JSON con los cambios específicos';


--
-- Name: obtener_umbral_inspeccion(text, numeric); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.obtener_umbral_inspeccion(p_clave text, p_valor_default numeric) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_valor numeric;
BEGIN
    -- Intentar obtener el valor de la tabla de parámetros
    SELECT valor::numeric INTO v_valor
    FROM parametros_sistema
    WHERE clave = p_clave;
    
    -- Si no existe, devolver el valor por defecto
    IF v_valor IS NULL THEN
        RETURN p_valor_default;
    END IF;
    
    RETURN v_valor;
EXCEPTION WHEN OTHERS THEN
    -- En caso de error, devolver el valor por defecto
    RETURN p_valor_default;
END;
$$;


ALTER FUNCTION public.obtener_umbral_inspeccion(p_clave text, p_valor_default numeric) OWNER TO postgres;

--
-- Name: probar_calculo_vida_util(uuid); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.probar_calculo_vida_util(p_neumatico_id uuid) RETURNS TABLE(neumatico_id uuid, numero_serie character varying, estado_actual character varying, profundidad_actual numeric, profundidad_minima_retiro numeric, tasa_desgaste_actual numeric, vida_util_restante_km numeric, mensaje text)
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_profundidad_minima_retiro NUMERIC(5,2);
    v_vida_util_restante_km NUMERIC(10,2);
    v_mensaje TEXT;
    v_tasa_desgaste_historica NUMERIC(10,8);
    v_contador_eventos INTEGER;
BEGIN
    -- Obtener la profundidad mínima de retiro del modelo
    SELECT m.profundidad_minima_retiro_mm
    INTO v_profundidad_minima_retiro
    FROM neumaticos n
    JOIN modelos_neumatico m ON n.modelo_id = m.id
    WHERE n.id = p_neumatico_id;
    
    -- Calcular la vida útil restante
    v_vida_util_restante_km := public.calcular_vida_util_restante(p_neumatico_id);
    
    -- Determinar el mensaje según el resultado
    IF v_vida_util_restante_km IS NULL THEN
        v_mensaje := 'No se pudo calcular la vida útil restante';
    ELSIF v_vida_util_restante_km <= 0 THEN
        v_mensaje := 'Neumático en fin de vida útil';
    ELSE
        v_mensaje := 'Vida útil calculada correctamente';
    END IF;
    
    -- Devolver los resultados
    RETURN QUERY 
    SELECT 
        n.id,
        n.numero_serie,
        n.estado_actual::TEXT,
        n.profundidad_remanente_actual_mm,
        v_profundidad_minima_retiro,
        n.tasa_desgaste_actual_mm_km,
        v_vida_util_restante_km,
        v_mensaje
    FROM 
        neumaticos n
    WHERE 
        n.id = p_neumatico_id;
END;
$$;


ALTER FUNCTION public.probar_calculo_vida_util(p_neumatico_id uuid) OWNER TO postgres;

--
-- Name: probar_calculo_vida_util_final(uuid); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.probar_calculo_vida_util_final(p_neumatico_id uuid) RETURNS TABLE(neumatico_id uuid, numero_serie character varying, estado_actual character varying, profundidad_actual numeric, profundidad_minima_retiro numeric, tasa_desgaste_actual numeric, vida_util_restante_km numeric, mensaje text)
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_profundidad_minima_retiro NUMERIC(5,2);
    v_vida_util_restante_km NUMERIC(10,2);
    v_mensaje TEXT;
    v_num_eventos_instalacion INTEGER;
    v_num_eventos_desmontaje INTEGER;
BEGIN
    -- Obtener información del neumático
    RAISE NOTICE 'Obteniendo información del neumático %', p_neumatico_id;
    
    -- Obtener la profundidad mínima de retiro del modelo
    SELECT m.profundidad_minima_retiro_mm
    INTO v_profundidad_minima_retiro
    FROM neumaticos n
    JOIN modelos_neumatico m ON n.modelo_id = m.id
    WHERE n.id = p_neumatico_id;
    
    -- Contar eventos de instalación y desmontaje (sin usar bucle)
    SELECT 
        COUNT(*) FILTER (WHERE e.tipo_evento = 'INSTALACION'),
        COUNT(*) FILTER (WHERE e.tipo_evento = 'DESMONTAJE')
    INTO v_num_eventos_instalacion, v_num_eventos_desmontaje
    FROM eventos_neumaticos e
    WHERE e.neumatico_id = p_neumatico_id;
    
    RAISE NOTICE 'Eventos de instalación: %, Eventos de desmontaje: %', 
                 v_num_eventos_instalacion, v_num_eventos_desmontaje;
    
    -- Calcular la vida útil restante
    BEGIN
        v_vida_util_restante_km := public.calcular_vida_util_restante(p_neumatico_id);
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Error al calcular vida útil: %', SQLERRM;
        v_vida_util_restante_km := NULL;
    END;
    
    -- Determinar el mensaje según el resultado
    IF v_vida_util_restante_km IS NULL THEN
        v_mensaje := 'No se pudo calcular la vida útil restante';
    ELSIF v_vida_util_restante_km <= 0 THEN
        v_mensaje := 'Neumático en fin de vida útil';
    ELSE
        v_mensaje := 'Vida útil calculada correctamente';
    END IF;
    
    -- Devolver los resultados
    RETURN QUERY 
    SELECT 
        n.id,
        n.numero_serie,
        n.estado_actual::TEXT,
        n.profundidad_remanente_actual_mm,
        v_profundidad_minima_retiro,
        COALESCE(n.tasa_desgaste_actual_mm_km, 0) as tasa_desgaste_actual_mm_km,
        v_vida_util_restante_km,
        v_mensaje::TEXT
    FROM 
        neumaticos n
    WHERE 
        n.id = p_neumatico_id;
END;
$$;


ALTER FUNCTION public.probar_calculo_vida_util_final(p_neumatico_id uuid) OWNER TO postgres;

--
-- Name: probar_calculo_vida_util_simple(uuid); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.probar_calculo_vida_util_simple(p_neumatico_id uuid) RETURNS TABLE(neumatico_id uuid, numero_serie character varying, estado_actual character varying, profundidad_actual numeric, profundidad_minima_retiro numeric, tasa_desgaste_actual numeric, vida_util_restante_km numeric, mensaje text)
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_profundidad_minima_retiro NUMERIC(5,2);
    v_vida_util_restante_km NUMERIC(10,2);
    v_mensaje TEXT;
    v_num_eventos_instalacion INTEGER;
    v_num_eventos_desmontaje INTEGER;
BEGIN
    -- Obtener información del neumático
    RAISE NOTICE 'Obteniendo información del neumático %', p_neumatico_id;
    
    -- Obtener la profundidad mínima de retiro del modelo
    SELECT m.profundidad_minima_retiro_mm
    INTO v_profundidad_minima_retiro
    FROM neumaticos n
    JOIN modelos_neumatico m ON n.modelo_id = m.id
    WHERE n.id = p_neumatico_id;
    
    -- Contar eventos de instalación y desmontaje
    SELECT COUNT(*) FILTER (WHERE tipo_evento = 'INSTALACION'),
           COUNT(*) FILTER (WHERE tipo_evento = 'DESMONTAJE')
    INTO v_num_eventos_instalacion, v_num_eventos_desmontaje
    FROM eventos_neumaticos
    WHERE neumatico_id = p_neumatico_id;
    
    RAISE NOTICE 'Eventos de instalación: %, Eventos de desmontaje: %', 
                 v_num_eventos_instalacion, v_num_eventos_desmontaje;
    
    -- Calcular la vida útil restante
    v_vida_util_restante_km := public.calcular_vida_util_restante(p_neumatico_id);
    
    -- Determinar el mensaje según el resultado
    IF v_vida_util_restante_km IS NULL THEN
        v_mensaje := 'No se pudo calcular la vida útil restante';
    ELSIF v_vida_util_restante_km <= 0 THEN
        v_mensaje := 'Neumático en fin de vida útil';
    ELSE
        v_mensaje := 'Vida útil calculada correctamente';
    END IF;
    
    -- Devolver los resultados
    RETURN QUERY 
    SELECT 
        n.id,
        n.numero_serie,
        n.estado_actual::TEXT,
        n.profundidad_remanente_actual_mm,
        v_profundidad_minima_retiro,
        n.tasa_desgaste_actual_mm_km,
        v_vida_util_restante_km,
        v_mensaje::TEXT
    FROM 
        neumaticos n
    WHERE 
        n.id = p_neumatico_id;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error en probar_calculo_vida_util_simple: %', SQLERRM;
        RAISE;
END;
$$;


ALTER FUNCTION public.probar_calculo_vida_util_simple(p_neumatico_id uuid) OWNER TO postgres;

--
-- Name: probar_instalacion_mejorada(text, integer, numeric, boolean, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.probar_instalacion_mejorada(p_numero_serie text, p_odometro integer, p_profundidad_mm numeric DEFAULT NULL::numeric, p_es_prueba boolean DEFAULT true, p_test_id text DEFAULT NULL::text) RETURNS jsonb
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_neumatico_id UUID;
    v_vehiculo_id UUID;
    v_posicion_id UUID;
    v_usuario_id UUID;
    v_evento_id UUID;
    v_resultado JSONB;
    v_test_info JSONB;
BEGIN
    -- Inicializar información de prueba
    v_test_info := jsonb_build_object(
        'es_prueba', p_es_prueba,
        'test_id', p_test_id,
        'fecha_prueba', NOW()
    );
    
    -- Obtener IDs necesarios
    SELECT id INTO v_neumatico_id 
    FROM neumaticos 
    WHERE numero_serie = p_numero_serie
    LIMIT 1;
    
    IF v_neumatico_id IS NULL THEN
        RETURN jsonb_build_object(
            'exito', false,
            'mensaje', 'Neumático no encontrado',
            'datos_prueba', v_test_info
        );
    END IF;
    
    -- Obtener un vehículo, posición y usuario válidos
    SELECT id INTO v_vehiculo_id FROM vehiculos WHERE activo = true LIMIT 1;
    SELECT id INTO v_posicion_id FROM posiciones_neumatico WHERE activo = true LIMIT 1;
    SELECT id INTO v_usuario_id FROM usuarios WHERE activo = true LIMIT 1;
    
    IF v_vehiculo_id IS NULL OR v_posicion_id IS NULL OR v_usuario_id IS NULL THEN
        RETURN jsonb_build_object(
            'exito', false,
            'mensaje', 'No se encontraron vehículo, posición o usuario válidos',
            'datos_prueba', v_test_info
        );
    END IF;
    
    -- Insertar evento de instalación
    INSERT INTO eventos_neumaticos (
        neumatico_id, 
        tipo_evento, 
        usuario_id, 
        vehiculo_id, 
        posicion_id,
        odometro_vehiculo_en_evento, 
        profundidad_remanente_mm,
        presion_psi,
        notas,
        datos_evento
    ) VALUES (
        v_neumatico_id,
        'INSTALACION',
        v_usuario_id,
        v_vehiculo_id,
        v_posicion_id,
        p_odometro,
        p_profundidad_mm,
        100.0, -- Presión por defecto
        'Prueba de instalación mejorada' || 
            CASE WHEN p_test_id IS NOT NULL THEN ' - ' || p_test_id ELSE '' END,
        v_test_info || jsonb_build_object(
            'parametros_prueba', jsonb_build_object(
                'odometro', p_odometro,
                'profundidad_mm', p_profundidad_mm
            )
        )
    )
    RETURNING id, datos_evento INTO v_evento_id, v_resultado;
    
    -- Obtener datos actualizados del neumático
    SELECT jsonb_build_object(
        'neumatico', to_jsonb(n.*),
        'evento', to_jsonb(e.*)
    ) INTO v_resultado
    FROM neumaticos n
    LEFT JOIN eventos_neumaticos e ON e.id = v_evento_id
    WHERE n.id = v_neumatico_id;
    
    -- Agregar información de prueba al resultado
    v_resultado := v_resultado || jsonb_build_object(
        'prueba', v_test_info,
        'exito', true,
        'mensaje', 'Prueba completada con éxito'
    );
    
    RETURN v_resultado;
    
EXCEPTION WHEN OTHERS THEN
    RETURN jsonb_build_object(
        'exito', false,
        'error', SQLERRM,
        'sqlstate', SQLSTATE,
        'datos_prueba', v_test_info || jsonb_build_object(
            'error_context', PG_EXCEPTION_CONTEXT
        )
    );
END;
$$;


ALTER FUNCTION public.probar_instalacion_mejorada(p_numero_serie text, p_odometro integer, p_profundidad_mm numeric, p_es_prueba boolean, p_test_id text) OWNER TO postgres;

--
-- Name: programar_mantenimiento(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.programar_mantenimiento() RETURNS void
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
BEGIN
    -- Verificar si ya existe una tarea programada
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_catalog.pg_extension 
        WHERE extname = 'pg_cron'
    ) THEN
        RAISE NOTICE 'La extensión pg_cron no está instalada. No se puede programar el mantenimiento automático.';
        RETURN;
    END IF;

    -- Programar mantenimiento diario a las 2 AM
    PERFORM cron.schedule(
        'mantenimiento-diario',
        '0 2 * * *',  -- Todos los días a las 2 AM
        'SELECT public.mantenimiento_diario()'
    );

    -- Programar reindexación semanal los domingos a las 3 AM
    PERFORM cron.schedule(
        'reindexacion-semanal',
        '0 3 * * 0',  -- Todos los domingos a las 3 AM
        'SELECT public.reindexar_tabla(''eventos_neumaticos'')'
    );

    RAISE NOTICE 'Tareas de mantenimiento programadas correctamente.';
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING 'Error al programar tareas de mantenimiento: %', SQLERRM;
END;
$$;


ALTER FUNCTION public.programar_mantenimiento() OWNER TO postgres;

--
-- Name: FUNCTION programar_mantenimiento(); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.programar_mantenimiento() IS 'Programa tareas de mantenimiento automático usando pg_cron.';


--
-- Name: programar_tareas_mantenimiento(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.programar_tareas_mantenimiento() RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_resultado TEXT := '';
    v_tiene_pgcron BOOLEAN;
BEGIN
    -- Verificar si pg_cron está instalado
    SELECT EXISTS (
        SELECT 1 FROM pg_extension WHERE extname = 'pg_cron'
    ) INTO v_tiene_pgcron;

    IF NOT v_tiene_pgcron THEN
        RETURN 'La extensión pg_cron no está instalada. No se pueden programar tareas automáticas.';
    END IF;

    -- Eliminar tareas existentes para evitar duplicados
    PERFORM cron.unschedule(jobid) 
    FROM cron.job 
    WHERE jobname IN ('mantenimiento-diario', 'reindexar-semanal', 'limpiar-bitacora-mensual');

    -- Programar mantenimiento diario a las 2 AM
    PERFORM cron.schedule(
        'mantenimiento-diario',
        '0 2 * * *',  -- Todos los días a las 2 AM
        'SELECT public.mantenimiento_diario()'
    );
    v_resultado := v_resultado || 'Mantenimiento diario programado a las 2 AM. ';

    -- Programar reindexación semanal los domingos a las 3 AM
    PERFORM cron.schedule(
        'reindexar-semanal',
        '0 3 * * 0',  -- Todos los domingos a las 3 AM
        'SELECT public.reindexar_tabla(''public'', ''eventos_neumaticos''); ' ||
        'SELECT public.reindexar_tabla(''public'', ''neumaticos'');'
    );
    v_resultado := v_resultado || 'Reindexación semanal programada para los domingos a las 3 AM. ';

    -- Programar limpieza mensual el primer día del mes a la 1 AM
    PERFORM cron.schedule(
        'limpiar-bitacora-mensual',
        '0 1 1 * *',  -- Primer día de cada mes a la 1 AM
        'SELECT public.limpiar_bitacora_mantenimiento(90, true)'
    );
    v_resultado := v_resultado || 'Limpieza mensual de la bitácora programada para el primer día de cada mes.';

    -- Registrar la programación
    PERFORM public.registrar_mantenimiento(
        'PROGRAMACION',
        'Tareas de mantenimiento programadas',
        NULL,
        TRUE,
        v_resultado
    );

    RETURN 'Tareas programadas: ' || v_resultado;
EXCEPTION
    WHEN OTHERS THEN
        DECLARE
            v_error_msg TEXT;
        BEGIN
            GET STACKED DIAGNOSTICS v_error_msg = MESSAGE_TEXT;
            PERFORM public.registrar_mantenimiento(
                'ERROR',
                'Error al programar tareas',
                NULL,
                FALSE,
                'Error: ' || v_error_msg
            );
            RETURN 'Error al programar tareas: ' || v_error_msg;
        END;
END;
$$;


ALTER FUNCTION public.programar_tareas_mantenimiento() OWNER TO postgres;

--
-- Name: registrar_auditoria(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.registrar_auditoria() RETURNS trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    v_old_data JSONB;
    v_new_data JSONB;
    v_changes JSONB;
    v_context JSONB;
    v_current_user_id TEXT;
    v_current_username TEXT;
BEGIN
    -- Obtener el ID y nombre de usuario de la aplicación
    BEGIN
        v_current_user_id := current_setting('app.current_user_id', true);
    EXCEPTION WHEN OTHERS THEN
        v_current_user_id := NULL;
    END;
    
    BEGIN
        v_current_username := current_setting('app.current_username', true);
    EXCEPTION WHEN OTHERS THEN
        v_current_username := session_user;
    END;

    -- Configurar el contexto de la aplicación
    v_context := jsonb_build_object(
        'application_name', current_setting('application_name', true),
        'client_addr', inet_client_addr()::text
    );

    -- Determinar los datos antiguos y nuevos según la operación
    IF TG_OP = 'INSERT' THEN
        v_old_data := NULL;
        v_new_data := to_jsonb(NEW);
        v_changes := v_new_data;
    ELSIF TG_OP = 'UPDATE' THEN
        v_old_data := to_jsonb(OLD);
        v_new_data := to_jsonb(NEW);
        
        -- Calcular solo los campos que cambiaron
        SELECT jsonb_object_agg(key, value) INTO v_changes
        FROM jsonb_each(to_jsonb(NEW)) n
        WHERE (to_jsonb(OLD) ->> key) IS DISTINCT FROM (n.value::text)
           OR (to_jsonb(OLD) ->> key) IS NULL AND n.value IS NOT NULL
           OR (to_jsonb(OLD) ->> key) IS NOT NULL AND n.value IS NULL;
    ELSIF TG_OP = 'DELETE' THEN
        v_old_data := to_jsonb(OLD);
        v_new_data := NULL;
        v_changes := v_old_data;
    END IF;

    -- Insertar el registro de auditoría
    INSERT INTO public.auditoria_log (
        timestamp_log,
        esquema_tabla,
        nombre_tabla,
        operacion,
        usuario_db,
        usuario_aplicacion_id,
        usuario_aplicacion_username,
        id_entidad,
        datos_antiguos,
        datos_nuevos,
        cambios,
        contexto_aplicacion,
        query_ejecutada
    ) VALUES (
        NOW(),
        TG_TABLE_SCHEMA,
        TG_TABLE_NAME,
        TG_OP,
        session_user,
        v_current_user_id::uuid,
        v_current_username,
        CASE 
            WHEN TG_OP = 'DELETE' AND v_old_data ? 'id' THEN (v_old_data->>'id')::uuid 
            WHEN v_new_data ? 'id' THEN (v_new_data->>'id')::uuid
            ELSE NULL
        END,
        v_old_data,
        v_new_data,
        v_changes,
        v_context,
        current_query()
    );

    -- Para INSERT y UPDATE, devolver el nuevo registro
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$;


ALTER FUNCTION public.registrar_auditoria() OWNER TO postgres;

--
-- Name: registrar_auditoria_compuesta(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.registrar_auditoria_compuesta() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_old_data JSONB;
    v_new_data JSONB;
    v_changes JSONB;
    v_record RECORD;
    v_query_text TEXT;
    v_username TEXT;
    v_user_id UUID;
BEGIN
    -- Obtener el texto de la consulta que activó el trigger
    v_query_text := current_query();
    
    -- Obtener información del usuario actual
    v_username := current_user;
    
    -- Intentar obtener el ID de usuario de la aplicación si está disponible
    BEGIN
        v_user_id := NULLIF(current_setting('app.current_user_id', true), '')::UUID;
    EXCEPTION WHEN OTHERS THEN
        v_user_id := NULL;
    END;
    
    -- Determinar los datos antiguos y nuevos según la operación
    IF TG_OP = 'INSERT' THEN
        v_old_data := NULL;
        v_new_data := to_jsonb(NEW);
        v_changes := v_new_data;
    ELSIF TG_OP = 'UPDATE' THEN
        v_old_data := to_jsonb(OLD);
        v_new_data := to_jsonb(NEW);
        
        -- Calcular solo los campos que cambiaron
        v_changes := '{}'::jsonb;
        FOR v_record IN SELECT * FROM jsonb_each(v_new_data) LOOP
            IF (v_old_data->>v_record.key) IS DISTINCT FROM (v_new_data->>v_record.key) THEN
                v_changes := jsonb_set(
                    COALESCE(v_changes, '{}'::jsonb),
                    ARRAY[v_record.key],
                    v_new_data->v_record.key
                );
            END IF;
        END LOOP;
    ELSIF TG_OP = 'DELETE' THEN
        v_old_data := to_jsonb(OLD);
        v_new_data := NULL;
        v_changes := v_old_data;
    END IF;
    
    -- Insertar el registro de auditoría
    INSERT INTO public.auditoria_log (
        esquema_tabla,
        nombre_tabla,
        operacion,
        usuario_db,
        usuario_aplicacion_id,
        usuario_aplicacion_username,
        id_entidad,
        datos_antiguos,
        datos_nuevos,
        cambios,
        query_ejecutada
    ) VALUES (
        TG_TABLE_SCHEMA,
        TG_TABLE_NAME,
        TG_OP,
        v_username,
        v_user_id,
        NULL,  -- Aquí podrías obtener el nombre de usuario de la aplicación si está disponible
        CASE 
            WHEN TG_OP = 'DELETE' THEN (v_old_data->>'id')::uuid 
            ELSE (v_new_data->>'id')::uuid 
        END,
        v_old_data,
        v_new_data,
        v_changes,
        v_query_text
    );
    
    RETURN NULL;
END;
$$;


ALTER FUNCTION public.registrar_auditoria_compuesta() OWNER TO postgres;

--
-- Name: registrar_auditoria_delete(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.registrar_auditoria_delete() RETURNS trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
BEGIN
    -- Insertar el registro de auditoría
    INSERT INTO public.auditoria_log (
        timestamp_log,
        esquema_tabla,
        nombre_tabla,
        operacion,
        usuario_db,
        usuario_aplicacion_id,
        usuario_aplicacion_username,
        id_entidad,
        datos_antiguos,
        datos_nuevos,
        cambios,
        contexto_aplicacion,
        query_ejecutada
    ) VALUES (
        NOW(),
        TG_TABLE_SCHEMA,
        TG_TABLE_NAME,
        TG_OP,
        session_user,
        NULL, -- current_setting('app.current_user_id', true)::uuid,
        NULL, -- current_setting('app.current_username', true),
        OLD.id,
        to_jsonb(OLD),
        NULL,
        to_jsonb(OLD),
        jsonb_build_object(
            'application_name', current_setting('application_name', true),
            'client_addr', inet_client_addr()::text
        ),
        current_query()
    );

    RETURN OLD;
END;
$$;


ALTER FUNCTION public.registrar_auditoria_delete() OWNER TO postgres;

--
-- Name: registrar_cambio_estado_manual(uuid, public.estado_neumatico_enum, public.estado_neumatico_enum, uuid, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.registrar_cambio_estado_manual(p_neumatico_id uuid, p_estado_anterior public.estado_neumatico_enum, p_estado_nuevo public.estado_neumatico_enum, p_usuario_id uuid, p_comentario text) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO historial_estados_neumaticos (
        neumatico_id,
        estado_anterior,
        estado_nuevo,
        usuario_id,
        comentario,
        fecha_cambio
    ) VALUES (
        p_neumatico_id,
        p_estado_anterior::VARCHAR(50),
        p_estado_nuevo::VARCHAR(50),
        p_usuario_id,
        p_comentario,
        NOW()
    ) ON CONFLICT DO NOTHING; -- Evitar errores de duplicados
END;
$$;


ALTER FUNCTION public.registrar_cambio_estado_manual(p_neumatico_id uuid, p_estado_anterior public.estado_neumatico_enum, p_estado_nuevo public.estado_neumatico_enum, p_usuario_id uuid, p_comentario text) OWNER TO postgres;

--
-- Name: registrar_cambio_estado_neumatico(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.registrar_cambio_estado_neumatico() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF TG_OP = 'UPDATE' AND OLD.estado_actual IS DISTINCT FROM NEW.estado_actual THEN
        INSERT INTO historial_estados_neumaticos (
            neumatico_id,
            estado_anterior,
            estado_nuevo,
            usuario_id,
            comentario
        ) VALUES (
            NEW.id,
            OLD.estado_actual,
            NEW.estado_actual,
            NEW.actualizado_por,
            'Cambio de estado automático'
        );
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.registrar_cambio_estado_neumatico() OWNER TO postgres;

--
-- Name: registrar_mantenimiento(character varying, text, interval, boolean, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.registrar_mantenimiento(p_tipo character varying, p_descripcion text, p_duracion interval, p_exito boolean, p_detalles text DEFAULT NULL::text) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO public.bitacora_mantenimiento (
        tipo, 
        descripcion, 
        ejecutado_por, 
        duracion, 
        exito, 
        detalles
    ) VALUES (
        p_tipo,
        p_descripcion,
        current_user,
        p_duracion,
        p_exito,
        COALESCE(p_detalles, 
            CASE WHEN p_exito THEN 'Operación completada con éxito' 
                 ELSE 'Error durante la operación' END)
    );
END;
$$;


ALTER FUNCTION public.registrar_mantenimiento(p_tipo character varying, p_descripcion text, p_duracion interval, p_exito boolean, p_detalles text) OWNER TO postgres;

--
-- Name: registrar_prueba(text, boolean, integer, integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.registrar_prueba(p_descripcion text, p_resultado boolean, INOUT p_contador_pruebas integer, INOUT p_pruebas_exitosas integer, INOUT p_pruebas_fallidas integer) RETURNS record
    LANGUAGE plpgsql
    AS $$
BEGIN
    p_contador_pruebas := p_contador_pruebas + 1;
    IF p_resultado THEN
        p_pruebas_exitosas := p_pruebas_exitosas + 1;
        RAISE NOTICE 'PRUEBA %: ✅ %', p_contador_pruebas, p_descripcion;
    ELSE
        p_pruebas_fallidas := p_pruebas_fallidas + 1;
        RAISE NOTICE 'PRUEBA %: ❌ %', p_contador_pruebas, p_descripcion;
    END IF;
END;
$$;


ALTER FUNCTION public.registrar_prueba(p_descripcion text, p_resultado boolean, INOUT p_contador_pruebas integer, INOUT p_pruebas_exitosas integer, INOUT p_pruebas_fallidas integer) OWNER TO postgres;

--
-- Name: reindexar_tabla(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.reindexar_tabla(nombre_tabla text) RETURNS text
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    v_sql TEXT;
    v_start_time TIMESTAMPTZ;
    v_duration INTERVAL;
    v_result TEXT;
BEGIN
    -- Verificar que la tabla existe
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = nombre_tabla
    ) THEN
        RETURN format('Error: La tabla %I no existe en el esquema public', nombre_tabla);
    END IF;

    v_start_time := clock_timestamp();
    
    -- Reindexar la tabla
    v_sql := format('REINDEX TABLE public.%I', nombre_tabla);
    EXECUTE v_sql;
    
    v_duration := clock_timestamp() - v_start_time;
    
    -- Registrar la acción
    INSERT INTO public.bitacora_mantenimiento (
        tipo, 
        descripcion, 
        ejecutado_por, 
        duracion, 
        exito, 
        detalles
    ) VALUES (
        'REINDEX', 
        format('Reindexación de la tabla %I', nombre_tabla), 
        current_user, 
        v_duration, 
        TRUE, 
        format('Reindexación completada en %s', v_duration)
    );
    
    RETURN format('Tabla %I reindexada correctamente en %s', nombre_tabla, v_duration);
EXCEPTION
    WHEN OTHERS THEN
        v_duration := clock_timestamp() - v_start_time;
        v_result := format('Error al reindexar la tabla %I: %s', nombre_tabla, SQLERRM);
        
        INSERT INTO public.bitacora_mantenimiento (
            tipo, 
            descripcion, 
            ejecutado_por, 
            duracion, 
            exito, 
            detalles
        ) VALUES (
            'REINDEX', 
            format('Error al reindexar %I', nombre_tabla), 
            current_user, 
            v_duration, 
            FALSE, 
            v_result
        );
        
        RETURN v_result;
END;
$$;


ALTER FUNCTION public.reindexar_tabla(nombre_tabla text) OWNER TO postgres;

--
-- Name: FUNCTION reindexar_tabla(nombre_tabla text); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.reindexar_tabla(nombre_tabla text) IS 'Reindexa una tabla de forma segura y registra la operación.';


--
-- Name: reindexar_tabla(text, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.reindexar_tabla(p_esquema text, p_tabla text) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_sql TEXT;
    v_start_time TIMESTAMPTZ;
    v_duration INTERVAL;
    v_result TEXT;
    v_success BOOLEAN := TRUE;
    v_details TEXT;
BEGIN
    v_start_time := clock_timestamp();
    
    -- Verificar que la tabla existe
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_schema = p_esquema 
        AND table_name = p_tabla
    ) THEN
        v_details := format('La tabla %I.%I no existe', p_esquema, p_tabla);
        PERFORM public.registrar_mantenimiento(
            'REINDEX', 
            format('Error: Tabla %I.%I no encontrada', p_esquema, p_tabla),
            clock_timestamp() - v_start_time,
            FALSE,
            v_details
        );
        RETURN v_details;
    END IF;

    -- Reindexar la tabla
    BEGIN
        v_sql := format('REINDEX TABLE %I.%I', p_esquema, p_tabla);
        EXECUTE v_sql;
        v_details := format('Tabla %I.%I reindexada correctamente', p_esquema, p_tabla);
        v_result := v_details;
    EXCEPTION WHEN OTHERS THEN
        v_success := FALSE;
        v_details := format('Error al reindexar %I.%I: %s', p_esquema, p_tabla, SQLERRM);
        v_result := v_details;
        RAISE WARNING '%', v_details;
    END;

    -- Registrar la operación
    v_duration := clock_timestamp() - v_start_time;
    PERFORM public.registrar_mantenimiento(
        'REINDEX',
        format('Reindexación de %I.%I', p_esquema, p_tabla),
        v_duration,
        v_success,
        v_details
    );

    RETURN v_result;
END;
$$;


ALTER FUNCTION public.reindexar_tabla(p_esquema text, p_tabla text) OWNER TO postgres;

--
-- Name: FUNCTION reindexar_tabla(p_esquema text, p_tabla text); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.reindexar_tabla(p_esquema text, p_tabla text) IS 'Reindexa una tabla de forma segura y registra la operación.
Parámetros:
- p_esquema: Nombre del esquema de la tabla
- p_tabla: Nombre de la tabla a reindexar';


--
-- Name: reorganizar_indices_auditoria(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.reorganizar_indices_auditoria() RETURNS TABLE(indice_nombre text, fragmentacion_antes double precision, fragmentacion_despues double precision, tamano_antes text, tamano_despues text, mensaje text)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    WITH indices_auditoria AS (
        SELECT 
            indexname,
            tablename,
            pg_size_pretty(pg_relation_size(quote_ident(indexname)::regclass)) as tamano
        FROM pg_indexes 
        WHERE tablename = 'auditoria_log'
    )
    SELECT 
        ia.indexname::TEXT,
        0.0 as fragmentacion_antes,  -- Esto es un ejemplo, en PostgreSQL necesitarías usar pgstattuple
        0.0 as fragmentacion_despues,
        ia.tamano as tamano_antes,
        ia.tamano as tamano_despues,
        'Reorganización de índices completada. Nota: La medición de fragmentación requiere la extensión pgstattuple.' as mensaje
    FROM indices_auditoria ia;
    
    -- Ejecutar REINDEX en modo concurrente si está disponible (PostgreSQL 12+)
    -- NOTA: Requiere privilegios de superusuario
    -- EXECUTE 'REINDEX (VERBOSE) TABLE CONCURRENTLY auditoria_log';
    
    -- Alternativa para versiones anteriores
    -- EXECUTE 'REINDEX TABLE auditoria_log';
    
    -- Nota: Para una implementación real, considera usar pg_repack o similar
    -- para evitar bloqueos en tablas grandes
END;
$$;


ALTER FUNCTION public.reorganizar_indices_auditoria() OWNER TO postgres;

--
-- Name: test_function_with_vars(uuid); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.test_function_with_vars(p_neumatico_id uuid) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
DECLARE
    -- Constantes
    V_TEST_CONSTANT CONSTANT numeric := 1.6;
    
    -- Variables
    v_var1 numeric;
    v_var2 numeric;
    v_result numeric;
    
    -- Variable problemática (renombrada)
    v_prof_min_ret numeric;
    
BEGIN
    -- Obtener datos de prueba
    SELECT 
        10.5 AS profundidad_actual,
        0.0001 AS tasa_desgaste,
        COALESCE(1.6, V_TEST_CONSTANT) AS prof_min_ret
    INTO 
        v_var1,
        v_var2,
        v_prof_min_ret;
    
    -- Cálculo de prueba
    v_result := (v_var1 - v_prof_min_ret) / v_var2;
    
    RETURN v_result;
    
EXCEPTION WHEN OTHERS THEN
    RETURN NULL;
END;
$$;


ALTER FUNCTION public.test_function_with_vars(p_neumatico_id uuid) OWNER TO postgres;

--
-- Name: test_minimal_function(uuid); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.test_minimal_function(p_neumatico_id uuid) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_test_var numeric;
    v_result numeric;
BEGIN
    -- Simple test function
    v_test_var := 10.5;
    v_result := v_test_var * 2;
    RETURN v_result;
END;
$$;


ALTER FUNCTION public.test_minimal_function(p_neumatico_id uuid) OWNER TO postgres;

--
-- Name: tiene_permiso(uuid, character varying, character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.tiene_permiso(p_usuario_id uuid, p_recurso character varying, p_accion character varying) RETURNS boolean
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    v_tiene_permiso BOOLEAN;
BEGIN
    -- Verificar si el usuario es administrador
    SELECT EXISTS (
        SELECT 1 FROM usuarios_roles ur 
        JOIN roles r ON ur.rol_id = r.id 
        WHERE ur.usuario_id = p_usuario_id 
        AND r.nombre = 'Administrador'
    ) INTO v_tiene_permiso;
    
    IF v_tiene_permiso THEN
        RETURN TRUE;
    END IF;
    
    -- Verificar permiso específico
    SELECT EXISTS (
        SELECT 1
        FROM usuarios_roles ur
        JOIN roles_permisos rp ON ur.rol_id = rp.rol_id
        JOIN permisos p ON rp.permiso_id = p.id
        WHERE ur.usuario_id = p_usuario_id
        AND p.nombre_recurso = p_recurso
        AND p.accion = p_accion
    ) INTO v_tiene_permiso;
    
    RETURN COALESCE(v_tiene_permiso, FALSE);
END;
$$;


ALTER FUNCTION public.tiene_permiso(p_usuario_id uuid, p_recurso character varying, p_accion character varying) OWNER TO postgres;

--
-- Name: verificar_cambios_auditoria(text, text, text, text, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.verificar_cambios_auditoria(p_operacion text, p_tabla text, p_id_entidad text DEFAULT NULL::text, p_campo_verificar text DEFAULT NULL::text, p_valor_esperado text DEFAULT NULL::text) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_audit_record RECORD;
    v_campo_valor text;
    v_resultado boolean := false;
    v_campo_json text;
    v_valor_json text;
    v_cambios_json jsonb;
    v_resultado_text text;
BEGIN
    -- Buscar el registro de auditoría más reciente
    SELECT * INTO v_audit_record
    FROM auditoria_log
    WHERE nombre_tabla = p_tabla
    AND operacion = p_operacion
    AND (p_id_entidad IS NULL OR (datos_nuevos->>'id' = p_id_entidad OR datos_antiguos->>'id' = p_id_entidad))
    ORDER BY timestamp_log DESC
    LIMIT 1;
    
    -- Verificar si se encontró el registro
    IF v_audit_record.id IS NULL THEN
        RAISE NOTICE 'No se encontró registro de auditoría para % en %', p_operacion, p_tabla;
        RETURN 'f';
    END IF;
    
    -- Verificar campo específico si se especificó
    IF p_campo_verificar IS NOT NULL THEN
        -- Para operaciones INSERT, verificar en datos_nuevos
        IF p_operacion = 'INSERT' THEN
            -- Verificar si el campo existe en datos_nuevos
            IF v_audit_record.datos_nuevos ? p_campo_verificar THEN
                v_campo_valor := v_audit_record.datos_nuevos->>p_campo_verificar;
                
                -- Comparar con el valor esperado si se proporcionó
                IF p_valor_esperado IS NOT NULL THEN
                    v_resultado := (v_campo_valor = p_valor_esperado);
                    
                    IF NOT v_resultado THEN
                        RAISE NOTICE 'Valor inesperado para %: Esperado=%, Obtenido=%', 
                            p_campo_verificar, p_valor_esperado, v_campo_valor;
                    END IF;
                ELSE
                    v_resultado := true; -- Solo verificar que el campo existe
                END IF;
            ELSE
                RAISE NOTICE 'Campo % no encontrado en datos_nuevos', p_campo_verificar;
                v_resultado := false;
            END IF;
        
        -- Para operaciones UPDATE, verificar en el campo cambios
        ELSIF p_operacion = 'UPDATE' THEN
            IF v_audit_record.cambios IS NOT NULL THEN
                -- Verificar si el campo está en el objeto de cambios
                IF v_audit_record.cambios ? p_campo_verificar THEN
                    -- Obtener el valor del campo en los cambios
                    v_cambios_json := v_audit_record.cambios->p_campo_verificar;
                    
                    -- Si es un objeto con new/old, tomar el valor 'new'
                    IF jsonb_typeof(v_cambios_json) = 'object' AND v_cambios_json ? 'new' THEN
                        v_campo_valor := v_cambios_json->>'new';
                    ELSE
                        v_campo_valor := v_cambios_json::text;
                    END IF;
                    
                    -- Comparar con el valor esperado si se proporcionó
                    IF p_valor_esperado IS NOT NULL THEN
                        -- Eliminar comillas si el valor es un string
                        IF v_campo_valor IS NOT NULL AND v_campo_valor LIKE '"%"' THEN
                            v_campo_valor := trim(both '"' from v_campo_valor);
                        END IF;
                        
                        v_resultado := (v_campo_valor = p_valor_esperado);
                        
                        IF NOT v_resultado THEN
                            RAISE NOTICE 'Valor inesperado para %: Esperado=%, Obtenido=%', 
                                p_campo_verificar, p_valor_esperado, v_campo_valor;
                        END IF;
                    ELSE
                        v_resultado := true; -- Solo verificar que el campo existe en los cambios
                    END IF;
                ELSE
                    RAISE NOTICE 'Campo % no encontrado en cambios', p_campo_verificar;
                    v_resultado := false;
                END IF;
            ELSE
                RAISE NOTICE 'No hay información de cambios en el registro de auditoría';
                v_resultado := false;
            END IF;
            
        -- Para operaciones DELETE, verificar en datos_antiguos
        ELSIF p_operacion = 'DELETE' THEN
            -- Verificar si el campo existe en datos_antiguos
            IF v_audit_record.datos_antiguos ? p_campo_verificar THEN
                v_campo_valor := v_audit_record.datos_antiguos->>p_campo_verificar;
                
                -- Comparar con el valor esperado si se proporcionó
                IF p_valor_esperado IS NOT NULL THEN
                    v_resultado := (v_campo_valor = p_valor_esperado);
                    
                    IF NOT v_resultado THEN
                        RAISE NOTICE 'Valor inesperado para %: Esperado=%, Obtenido=%', 
                            p_campo_verificar, p_valor_esperado, v_campo_valor;
                    END IF;
                ELSE
                    v_resultado := true; -- Solo verificar que el campo existe
                END IF;
            ELSE
                RAISE NOTICE 'Campo % no encontrado en datos_antiguos', p_campo_verificar;
                v_resultado := false;
            END IF;
        END IF;
    ELSE
        v_resultado := true; -- Solo verificar que existe el registro de auditoría
    END IF;
    
    -- Convertir el resultado booleano a 't' o 'f'
    IF v_resultado THEN
        v_resultado_text := 't';
    ELSE
        v_resultado_text := 'f';
    END IF;
    
    RETURN v_resultado_text;
END;
$$;


ALTER FUNCTION public.verificar_cambios_auditoria(p_operacion text, p_tabla text, p_id_entidad text, p_campo_verificar text, p_valor_esperado text) OWNER TO postgres;

--
-- Name: FUNCTION verificar_cambios_auditoria(p_operacion text, p_tabla text, p_id_entidad text, p_campo_verificar text, p_valor_esperado text); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.verificar_cambios_auditoria(p_operacion text, p_tabla text, p_id_entidad text, p_campo_verificar text, p_valor_esperado text) IS 'Verifica los cambios en la tabla de auditoría para una operación específica.

Parámetros:
- p_operacion: Tipo de operación (INSERT, UPDATE, DELETE)
- p_tabla: Nombre de la tabla auditada
- p_id_entidad: ID de la entidad (opcional)
- p_campo_verificar: Nombre del campo a verificar (opcional)
- p_valor_esperado: Valor esperado del campo (opcional)

Retorna: 
- ''t'' si la verificación es exitosa
- ''f'' si hay un error o la verificación falla';


--
-- Name: verificar_cambios_neumatico(uuid); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.verificar_cambios_neumatico(p_id_neu uuid) RETURNS TABLE(tiene_cambios boolean, ultimo_cambio timestamp with time zone, ultimo_usuario text, total_cambios bigint)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) > 0 as tiene_cambios,
        MAX(al.timestamp_log) as ultimo_cambio,
        MAX(COALESCE(al.usuario_aplicacion_username, al.usuario_db)) as ultimo_usuario,
        COUNT(*) as total_cambios
    FROM auditoria_log al
    WHERE al.nombre_tabla = 'neumaticos'
    AND al.id_entidad = p_id_neu;
END;
$$;


ALTER FUNCTION public.verificar_cambios_neumatico(p_id_neu uuid) OWNER TO postgres;

--
-- Name: FUNCTION verificar_cambios_neumatico(p_id_neu uuid); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.verificar_cambios_neumatico(p_id_neu uuid) IS 'Verifica si hay cambios de auditoría para un neumático específico.
Parámetros:
- p_id_neu: ID del neumático a verificar

Retorna:
- tiene_cambios: true si hay registros de auditoría
- ultimo_cambio: fecha y hora del último cambio
- ultimo_usuario: nombre del último usuario que realizó un cambio
- total_cambios: número total de cambios registrados';


--
-- Name: verificar_estado_tablas(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.verificar_estado_tablas() RETURNS TABLE(esquema text, tabla text, filas_estimadas bigint, tamano text, filas_obsoletas bigint, ultimo_vacuum timestamp with time zone, ultimo_analyze timestamp with time zone, necesita_vacuum boolean, necesita_analyze boolean)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.schemaname::TEXT,
        t.relname::TEXT AS tabla,
        t.n_live_tup AS filas_estimadas,
        pg_size_pretty(pg_total_relation_size(quote_ident(t.schemaname) || '.' || quote_ident(t.relname))) AS tamano,
        t.n_dead_tup AS filas_obsoletas,
        t.last_vacuum,
        t.last_autoanalyze AS ultimo_analyze,
        t.n_dead_tup > 1000 AS necesita_vacuum,
        t.last_autoanalyze < (NOW() - INTERVAL '1 day') AS necesita_analyze
    FROM pg_stat_user_tables t
    ORDER BY 
        t.n_dead_tup DESC NULLS LAST,
        t.last_autoanalyze NULLS FIRST;
END;
$$;


ALTER FUNCTION public.verificar_estado_tablas() OWNER TO postgres;

--
-- Name: verificar_indices_auditoria(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.verificar_indices_auditoria() RETURNS TABLE(tabla_nombre text, columnas text, consultas_recomendadas text, impacto_rendimiento text)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.tabla,
        t.columnas,
        t.consultas_recomendadas,
        t.impacto_rendimiento
    FROM (
        VALUES 
            ('auditoria_log', 'usuario_aplicacion_id', 'CREATE INDEX idx_auditoria_usuario_id ON auditoria_log(usuario_aplicacion_id) WHERE usuario_aplicacion_id IS NOT NULL;', 'Alto para búsquedas por ID de usuario'),
            ('auditoria_log', 'timestamp_log, nombre_tabla', 'CREATE INDEX idx_auditoria_timestamp_tabla ON auditoria_log(timestamp_log, nombre_tabla);', 'Alto para consultas de auditoría por rango de fechas y tabla')
    ) t(tabla, columnas, consultas_recomendadas, impacto_rendimiento)
    WHERE NOT EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE tablename = t.tabla 
        AND indexdef LIKE '%' || t.columnas || '%'
    );
END;
$$;


ALTER FUNCTION public.verificar_indices_auditoria() OWNER TO postgres;

--
-- Name: verificar_neumatico(uuid); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.verificar_neumatico(p_neumatico_id uuid) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_neumatico RECORD;
    v_evento RECORD;
    v_vida_util_restante numeric;
    v_tasa_historica numeric;
    v_eventos_instalacion int;
    v_eventos_desmontaje int;
    v_query text;
BEGIN
    -- Obtener información básica del neumático
    SELECT 
        n.*,
        m.profundidad_minima_retiro_mm,
        m.tasa_desgaste_esperada_mm_km,
        COALESCE(m.porcentaje_desgaste_por_vida, 0) as porcentaje_desgaste_por_vida,
        COALESCE(m.max_vidas_utiles, 10) as max_vidas_utiles
    INTO v_neumatico
    FROM neumaticos n
    LEFT JOIN modelos_neumatico m ON n.modelo_id = m.id
    WHERE n.id = p_neumatico_id;
    
    IF v_neumatico.id IS NULL THEN
        RAISE NOTICE 'No se encontró el neumático con ID: %', p_neumatico_id;
        RETURN;
    END IF;
    
    -- Contar eventos
    SELECT 
        COUNT(*) FILTER (WHERE tipo_evento = 'INSTALACION'),
        COUNT(*) FILTER (WHERE tipo_evento = 'DESMONTAJE')
    INTO v_eventos_instalacion, v_eventos_desmontaje
    FROM eventos_neumaticos
    WHERE neumatico_id = p_neumatico_id;
    
    -- Mostrar información del neumático
    RAISE NOTICE '%', E'\n=== INFORMACIÓN DEL NEUMÁTICO ===';
    RAISE NOTICE 'ID: %', v_neumatico.id;
    RAISE NOTICE 'Número de serie: %', v_neumatico.numero_serie;
    RAISE NOTICE 'Estado: %, Vida actual: %, Reencauchado: %', 
                 v_neumatico.estado_actual, 
                 v_neumatico.vida_actual, 
                 v_neumatico.es_reencauchado;
    RAISE NOTICE 'Profundidad actual: % mm (mínimo: % mm)', 
                 v_neumatico.profundidad_remanente_actual_mm,
                 v_neumatico.profundidad_minima_retiro_mm;
    RAISE NOTICE 'Tasa de desgaste actual: % mm/km (esperada: % mm/km)', 
                 v_neumatico.tasa_desgaste_actual_mm_km, 
                 v_neumatico.tasa_desgaste_esperada_mm_km;
    RAISE NOTICE 'Kilometraje vida actual: % km, Acumulado: % km', 
                 v_neumatico.kilometraje_vida_actual, 
                 v_neumatico.kilometraje_acumulado;
    RAISE NOTICE 'Vida útil restante: % km', v_neumatico.vida_util_restante_km;
    RAISE NOTICE 'Ajuste por reencauche: % %% (máx. % vidas)', 
                 v_neumatico.porcentaje_desgaste_por_vida,
                 v_neumatico.max_vidas_utiles;
    RAISE NOTICE 'Eventos: % instalaciones, % desmontajes', 
                 v_eventos_instalacion, v_eventos_desmontaje;
    
    -- Calcular vida útil restante
    BEGIN
        RAISE NOTICE E'\n=== CÁLCULO DE VIDA ÚTIL RESTANTE ===';
        v_vida_util_restante := public.calcular_vida_util_restante(p_neumatico_id);
        RAISE NOTICE 'Vida útil restante calculada: % km', v_vida_util_restante;
        
        -- Obtener la tasa de desgaste actualizada
        SELECT tasa_desgaste_actual_mm_km INTO v_tasa_historica
        FROM neumaticos WHERE id = p_neumatico_id;
        
        RAISE NOTICE 'Nueva tasa de desgaste: % mm/km', v_tasa_historica;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Error al calcular vida útil restante: %', SQLERRM;
    END;
    
    -- Mostrar eventos recientes
    RAISE NOTICE E'\n=== ÚLTIMOS 5 EVENTOS ===';
    
    v_query := format('SELECT id, tipo_evento, timestamp_evento, ' ||
                      'odometro_vehiculo_en_evento, profundidad_inicial_mm, ' ||
                      'profundidad_remanente_mm, motivo, destino_desmontaje ' ||
                      'FROM eventos_neumaticos ' ||
                      'WHERE neumatico_id = %L ' ||
                      'ORDER BY timestamp_evento DESC LIMIT 5', p_neumatico_id);
    
    FOR v_evento IN EXECUTE v_query
    LOOP
        RAISE NOTICE '- % [%] (odómetro: % km, prof: %/%s mm)%s', 
                     v_evento.tipo_evento,
                     v_evento.timestamp_evento,
                     v_evento.odometro_vehiculo_en_evento,
                     v_evento.profundidad_inicial_mm,
                     CASE WHEN v_evento.profundidad_remanente_mm IS NOT NULL 
                          THEN '→' || v_evento.profundidad_remanente_mm::text 
                          ELSE '' END,
                     CASE 
                         WHEN v_evento.destino_desmontaje IS NOT NULL 
                         THEN ', destino: ' || v_evento.destino_desmontaje
                         WHEN v_evento.motivo IS NOT NULL 
                         THEN ', motivo: ' || v_evento.motivo
                         ELSE ''
                     END;
    END LOOP;
    
    RAISE NOTICE '\n';
    
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error en verificar_neumatico: %', SQLERRM;
END;
$$;


ALTER FUNCTION public.verificar_neumatico(p_neumatico_id uuid) OWNER TO postgres;

--
-- Name: verificar_neumatico_simple(uuid); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.verificar_neumatico_simple(p_neumatico_id uuid) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_neumatico RECORD;
    v_evento RECORD;
    v_query text;
    v_count_instalaciones int;
    v_count_desmontajes int;
BEGIN
    -- Obtener información básica del neumático
    SELECT 
        n.*,
        m.profundidad_minima_retiro_mm,
        m.tasa_desgaste_esperada_mm_km,
        COALESCE(m.porcentaje_desgaste_por_vida, 0) as porcentaje_desgaste_por_vida,
        COALESCE(m.max_vidas_utiles, 10) as max_vidas_utiles
    INTO v_neumatico
    FROM neumaticos n
    LEFT JOIN modelos_neumatico m ON n.modelo_id = m.id
    WHERE n.id = p_neumatico_id;
    
    IF v_neumatico.id IS NULL THEN
        RAISE NOTICE 'No se encontró el neumático con ID: %', p_neumatico_id;
        RETURN;
    END IF;
    
    -- Mostrar información básica
    RAISE NOTICE '%', E'\n=== INFORMACIÓN BÁSICA ===';
    RAISE NOTICE 'ID: %', v_neumatico.id;
    RAISE NOTICE 'Número de serie: %', v_neumatico.numero_serie;
    RAISE NOTICE 'Estado: %, Vida actual: %, Reencauchado: %', 
                 v_neumatico.estado_actual, 
                 v_neumatico.vida_actual, 
                 v_neumatico.es_reencauchado;
    RAISE NOTICE 'Profundidad actual: % mm (mínimo: % mm)', 
                 v_neumatico.profundidad_remanente_actual_mm,
                 v_neumatico.profundidad_minima_retiro_mm;
    RAISE NOTICE 'Tasa de desgaste actual: % mm/km (esperada: % mm/km)', 
                 v_neumatico.tasa_desgaste_actual_mm_km, 
                 v_neumatico.tasa_desgaste_esperada_mm_km;
    RAISE NOTICE 'Kilometraje vida actual: % km, Acumulado: % km', 
                 v_neumatico.kilometraje_vida_actual, 
                 v_neumatico.kilometraje_acumulado;
    RAISE NOTICE 'Vida útil restante: % km', v_neumatico.vida_util_restante_km;
    RAISE NOTICE 'Ajuste por reencauche: % %% (máx. % vidas)', 
                 v_neumatico.porcentaje_desgaste_por_vida,
                 v_neumatico.max_vidas_utiles;
    
    -- Contar eventos
    SELECT 
        COUNT(*) FILTER (WHERE tipo_evento = 'INSTALACION'),
        COUNT(*) FILTER (WHERE tipo_evento = 'DESMONTAJE')
    INTO v_count_instalaciones, v_count_desmontajes
    FROM eventos_neumaticos
    WHERE neumatico_id = p_neumatico_id;
    
    RAISE NOTICE 'Eventos: % instalaciones, % desmontajes', 
                 v_count_instalaciones, v_count_desmontajes;
    
    -- Calcular vida útil restante
    BEGIN
        RAISE NOTICE E'\n=== CÁLCULO DE VIDA ÚTIL RESTANTE ===';
        DECLARE
            v_vida_util_restante numeric;
        BEGIN
            v_vida_util_restante := public.calcular_vida_util_restante(p_neumatico_id);
            RAISE NOTICE 'Vida útil restante calculada: % km', v_vida_util_restante;
            
            -- Obtener la tasa de desgaste actualizada
            SELECT tasa_desgaste_actual_mm_km INTO v_neumatico.tasa_desgaste_actual_mm_km
            FROM neumaticos WHERE id = p_neumatico_id;
            
            RAISE NOTICE 'Nueva tasa de desgaste: % mm/km', v_neumatico.tasa_desgaste_actual_mm_km;
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Error al calcular vida útil restante: %', SQLERRM;
        END;
    END;
    
    -- Mostrar eventos recientes
    RAISE NOTICE E'\n=== ÚLTIMOS 5 EVENTOS ===';
    
    v_query := format('SELECT id, tipo_evento, timestamp_evento, ' ||
                      'odometro_vehiculo_en_evento, ' ||
                      'profundidad_remanente_mm, ' ||
                      'destino_desmontaje ' ||
                      'FROM eventos_neumaticos ' ||
                      'WHERE neumatico_id = %L ' ||
                      'ORDER BY timestamp_evento DESC LIMIT 5', p_neumatico_id);
    
    FOR v_evento IN EXECUTE v_query
    LOOP
        RAISE NOTICE '- % [%] (odómetro: % km, prof: %s mm)%s', 
                     v_evento.tipo_evento,
                     v_evento.timestamp_evento,
                     COALESCE(v_evento.odometro_vehiculo_en_evento::text, 'N/A'),
                     COALESCE(v_evento.profundidad_remanente_mm::text, 'N/A'),
                     CASE 
                         WHEN v_evento.destino_desmontaje IS NOT NULL 
                         THEN ', destino: ' || v_evento.destino_desmontaje
                         ELSE ''
                     END;
    END LOOP;
    
    RAISE NOTICE '\n';
    
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error en verificar_neumatico_simple: %', SQLERRM;
    RAISE NOTICE 'Detalle del error: %', SQLSTATE;
END;
$$;


ALTER FUNCTION public.verificar_neumatico_simple(p_neumatico_id uuid) OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: alertas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alertas (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    tipo_alerta character varying(50) NOT NULL,
    mensaje text NOT NULL,
    nivel_severidad character varying(20) DEFAULT 'INFO'::character varying NOT NULL,
    estado_alerta character varying(20) DEFAULT 'NUEVA'::character varying NOT NULL,
    timestamp_generacion timestamp with time zone DEFAULT now() NOT NULL,
    timestamp_gestion timestamp with time zone,
    usuario_gestion_id uuid,
    neumatico_id uuid,
    vehiculo_id uuid,
    modelo_id uuid,
    almacen_id uuid,
    parametro_id uuid,
    datos_contexto jsonb,
    CONSTRAINT alertas_estado_alerta_check CHECK (((estado_alerta)::text = ANY (ARRAY[('NUEVA'::character varying)::text, ('VISTA'::character varying)::text, ('GESTIONADA'::character varying)::text]))),
    CONSTRAINT alertas_nivel_severidad_check CHECK (((nivel_severidad)::text = ANY (ARRAY[('INFO'::character varying)::text, ('WARN'::character varying)::text, ('CRITICAL'::character varying)::text])))
)
WITH (fillfactor='90');


ALTER TABLE public.alertas OWNER TO postgres;

--
-- Name: TABLE alertas; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.alertas IS 'Alertas generadas por el sistema';


--
-- Name: almacenes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.almacenes (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    codigo character varying(20) NOT NULL,
    nombre character varying(150) NOT NULL,
    tipo character varying(50),
    direccion text,
    activo boolean DEFAULT true NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    creado_por uuid,
    actualizado_en timestamp with time zone,
    actualizado_por uuid
)
WITH (fillfactor='90');


ALTER TABLE public.almacenes OWNER TO postgres;

--
-- Name: TABLE almacenes; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.almacenes IS 'Ubicaciones físicas donde se almacenan los neumáticos';


--
-- Name: auditoria_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auditoria_log (
    id bigint NOT NULL,
    timestamp_log timestamp with time zone DEFAULT now() NOT NULL,
    esquema_tabla character varying(63) NOT NULL,
    nombre_tabla character varying(63) NOT NULL,
    operacion character varying(10) NOT NULL,
    usuario_db character varying(63) DEFAULT CURRENT_USER NOT NULL,
    usuario_aplicacion_id uuid,
    usuario_aplicacion_username character varying(50),
    direccion_ip character varying(45),
    user_agent text,
    id_entidad text,
    datos_antiguos jsonb,
    datos_nuevos jsonb,
    cambios jsonb,
    contexto_aplicacion jsonb,
    query_ejecutada text,
    CONSTRAINT auditoria_log_operacion_check CHECK (((operacion)::text = ANY (ARRAY[('INSERT'::character varying)::text, ('UPDATE'::character varying)::text, ('DELETE'::character varying)::text])))
)
WITH (fillfactor='80');


ALTER TABLE public.auditoria_log OWNER TO postgres;

--
-- Name: TABLE auditoria_log; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.auditoria_log IS 'Registro centralizado de auditoría para todas las operaciones DML en la base de datos';


--
-- Name: COLUMN auditoria_log.id_entidad; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.auditoria_log.id_entidad IS 'Identificador de la entidad afectada (puede ser NULL). Almacena un hash MD5 de las claves primarias para identificar el registro.';


--
-- Name: auditoria_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auditoria_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.auditoria_log_id_seq OWNER TO postgres;

--
-- Name: auditoria_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auditoria_log_id_seq OWNED BY public.auditoria_log.id;


--
-- Name: bitacora_mantenimiento; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bitacora_mantenimiento (
    id integer NOT NULL,
    fecha_ejecucion timestamp with time zone DEFAULT now() NOT NULL,
    tipo character varying(50) NOT NULL,
    descripcion text NOT NULL,
    ejecutado_por name DEFAULT CURRENT_USER NOT NULL,
    duracion interval,
    exito boolean DEFAULT true,
    detalles text
);


ALTER TABLE public.bitacora_mantenimiento OWNER TO postgres;

--
-- Name: TABLE bitacora_mantenimiento; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.bitacora_mantenimiento IS 'Registra la ejecución de tareas de mantenimiento programadas o manuales.';


--
-- Name: COLUMN bitacora_mantenimiento.tipo; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.bitacora_mantenimiento.tipo IS 'Tipo de mantenimiento ejecutado (ej: DIARIO, REINDEX, VACUUM, ANALYZE)';


--
-- Name: bitacora_mantenimiento_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bitacora_mantenimiento_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.bitacora_mantenimiento_id_seq OWNER TO postgres;

--
-- Name: bitacora_mantenimiento_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bitacora_mantenimiento_id_seq OWNED BY public.bitacora_mantenimiento.id;


--
-- Name: bitacora_operaciones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bitacora_operaciones (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tipo_operacion public.tipo_operacion_enum NOT NULL,
    descripcion text NOT NULL,
    fecha_operacion timestamp with time zone DEFAULT now() NOT NULL,
    usuario_id uuid,
    almacen_id uuid,
    vehiculo_id uuid,
    estado_operacion public.estado_operacion_enum NOT NULL,
    duracion_minutos integer,
    costo_estimado numeric(10,2),
    costo_real numeric(10,2),
    proveedor_id uuid,
    observaciones text,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    actualizado_en timestamp with time zone DEFAULT now() NOT NULL,
    creado_por uuid,
    actualizado_por uuid
);


ALTER TABLE public.bitacora_operaciones OWNER TO postgres;

--
-- Name: TABLE bitacora_operaciones; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.bitacora_operaciones IS 'Registra operaciones de mantenimiento realizadas en el taller o en vehículos';


--
-- Name: COLUMN bitacora_operaciones.tipo_operacion; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.bitacora_operaciones.tipo_operacion IS 'Tipo de operación realizada (balanceo, rotación, etc.)';


--
-- Name: COLUMN bitacora_operaciones.estado_operacion; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.bitacora_operaciones.estado_operacion IS 'Estado actual de la operación (PENDIENTE, EN_PROCESO, COMPLETADA, etc.)';


--
-- Name: bitacora_operaciones_neumaticos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bitacora_operaciones_neumaticos (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    operacion_id uuid NOT NULL,
    neumatico_id uuid NOT NULL,
    tipo_accion public.tipo_accion_operacion_enum NOT NULL,
    posicion_neumatico_id uuid,
    profundidad_inicial_mm numeric(5,2),
    profundidad_final_mm numeric(5,2),
    presion_inicial_psi numeric(5,2),
    presion_final_psi numeric(5,2),
    kilometraje_vehiculo_km numeric(10,2),
    observaciones text,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    actualizado_en timestamp with time zone DEFAULT now() NOT NULL,
    creado_por uuid,
    actualizado_por uuid
);


ALTER TABLE public.bitacora_operaciones_neumaticos OWNER TO postgres;

--
-- Name: TABLE bitacora_operaciones_neumaticos; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.bitacora_operaciones_neumaticos IS 'Relación muchos a muchos entre operaciones de mantenimiento y neumáticos';


--
-- Name: COLUMN bitacora_operaciones_neumaticos.tipo_accion; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.bitacora_operaciones_neumaticos.tipo_accion IS 'Tipo de acción realizada sobre el neumático durante la operación';


--
-- Name: configuracion_auditoria; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.configuracion_auditoria (
    nombre_tabla character varying(63) NOT NULL,
    activo boolean DEFAULT true NOT NULL,
    prioridad character varying(20),
    campos_excluidos jsonb DEFAULT '{}'::jsonb,
    creado_en timestamp with time zone DEFAULT now(),
    actualizado_en timestamp with time zone DEFAULT now(),
    CONSTRAINT configuracion_auditoria_prioridad_check CHECK (((prioridad)::text = ANY (ARRAY[('low'::character varying)::text, ('medium'::character varying)::text, ('high'::character varying)::text])))
);


ALTER TABLE public.configuracion_auditoria OWNER TO postgres;

--
-- Name: TABLE configuracion_auditoria; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.configuracion_auditoria IS 'Configuración de auditoría para las tablas del sistema';


--
-- Name: COLUMN configuracion_auditoria.nombre_tabla; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.configuracion_auditoria.nombre_tabla IS 'Nombre de la tabla a auditar';


--
-- Name: COLUMN configuracion_auditoria.activo; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.configuracion_auditoria.activo IS 'Indica si la auditoría está activa para esta tabla';


--
-- Name: COLUMN configuracion_auditoria.prioridad; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.configuracion_auditoria.prioridad IS 'Nivel de prioridad de auditoría (low, medium, high)';


--
-- Name: COLUMN configuracion_auditoria.campos_excluidos; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.configuracion_auditoria.campos_excluidos IS 'Campos que no se auditarán en esta tabla';


--
-- Name: COLUMN configuracion_auditoria.creado_en; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.configuracion_auditoria.creado_en IS 'Fecha de creación del registro';


--
-- Name: COLUMN configuracion_auditoria.actualizado_en; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.configuracion_auditoria.actualizado_en IS 'Fecha de última actualización del registro';


--
-- Name: configuraciones_eje; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.configuraciones_eje (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    tipo_vehiculo_id uuid NOT NULL,
    numero_eje smallint NOT NULL,
    nombre_eje character varying(50) NOT NULL,
    tipo_eje public.tipo_eje_enum NOT NULL,
    numero_posiciones smallint NOT NULL,
    posiciones_duales boolean DEFAULT false NOT NULL,
    permite_reencauchados boolean DEFAULT true NOT NULL,
    neumaticos_por_posicion smallint DEFAULT 1 NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    creado_por uuid,
    actualizado_en timestamp with time zone,
    actualizado_por uuid,
    CONSTRAINT configuraciones_eje_neumaticos_por_posicion_check CHECK ((neumaticos_por_posicion = ANY (ARRAY[1, 2]))),
    CONSTRAINT configuraciones_eje_numero_eje_check CHECK ((numero_eje > 0)),
    CONSTRAINT configuraciones_eje_numero_posiciones_check CHECK (((numero_posiciones >= 1) AND (numero_posiciones <= 6)))
)
WITH (fillfactor='90');


ALTER TABLE public.configuraciones_eje OWNER TO postgres;

--
-- Name: errores_aplicacion; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.errores_aplicacion (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    nombre_funcion text NOT NULL,
    mensaje_error text NOT NULL,
    detalles jsonb,
    creado_por text DEFAULT 'SISTEMA'::text,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    resuelto boolean DEFAULT false,
    resuelto_por text,
    resuelto_en timestamp with time zone,
    comentario_resolucion text
);


ALTER TABLE public.errores_aplicacion OWNER TO postgres;

--
-- Name: TABLE errores_aplicacion; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.errores_aplicacion IS 'Registro de errores de la aplicación para seguimiento y depuración';


--
-- Name: COLUMN errores_aplicacion.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.errores_aplicacion.id IS 'Identificador único del error';


--
-- Name: COLUMN errores_aplicacion.nombre_funcion; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.errores_aplicacion.nombre_funcion IS 'Nombre de la función o procedimiento donde ocurrió el error';


--
-- Name: COLUMN errores_aplicacion.mensaje_error; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.errores_aplicacion.mensaje_error IS 'Mensaje de error generado';


--
-- Name: COLUMN errores_aplicacion.detalles; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.errores_aplicacion.detalles IS 'Información adicional sobre el error en formato JSON';


--
-- Name: COLUMN errores_aplicacion.creado_por; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.errores_aplicacion.creado_por IS 'Usuario o sistema que generó el error';


--
-- Name: COLUMN errores_aplicacion.creado_en; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.errores_aplicacion.creado_en IS 'Fecha y hora en que se registró el error';


--
-- Name: COLUMN errores_aplicacion.resuelto; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.errores_aplicacion.resuelto IS 'Indica si el error ha sido resuelto';


--
-- Name: COLUMN errores_aplicacion.resuelto_por; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.errores_aplicacion.resuelto_por IS 'Usuario que marcó el error como resuelto';


--
-- Name: COLUMN errores_aplicacion.resuelto_en; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.errores_aplicacion.resuelto_en IS 'Fecha y hora en que se resolvió el error';


--
-- Name: COLUMN errores_aplicacion.comentario_resolucion; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.errores_aplicacion.comentario_resolucion IS 'Comentarios sobre la resolución del error';


--
-- Name: especificaciones_desgaste; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.especificaciones_desgaste (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    modelo_neumatico_id uuid NOT NULL,
    tipo_posicion character varying(50) NOT NULL,
    vida_util_km_min integer NOT NULL,
    vida_util_km_max integer NOT NULL,
    descripcion_estado character varying(100) NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    creado_por uuid,
    actualizado_en timestamp with time zone,
    actualizado_por uuid,
    CONSTRAINT especificaciones_desgaste_check_km CHECK ((vida_util_km_min < vida_util_km_max))
);


ALTER TABLE public.especificaciones_desgaste OWNER TO postgres;

--
-- Name: eventos_neumaticos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.eventos_neumaticos (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    neumatico_id uuid NOT NULL,
    tipo_evento public.tipo_evento_neumatico_enum NOT NULL,
    timestamp_evento timestamp with time zone DEFAULT now() NOT NULL,
    usuario_id uuid NOT NULL,
    vehiculo_id uuid,
    posicion_id uuid,
    odometro_vehiculo_en_evento integer,
    profundidad_remanente_mm numeric(5,2),
    presion_psi numeric(5,2),
    costo_evento numeric(10,2),
    moneda_costo character varying(3) DEFAULT 'PEN'::character varying,
    proveedor_servicio_id uuid,
    notas text,
    destino_desmontaje public.estado_neumatico_enum,
    motivo_desecho_id_evento uuid,
    profundidad_post_reencauche_mm numeric(5,2),
    datos_evento jsonb,
    relacion_evento_anterior uuid,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    almacen_destino_id uuid,
    tipo_ruta_id uuid,
    peso_carga_promedio_ton_evento numeric(5,2),
    motivo_reparacion_texto text,
    tipo_dano_detectado_texto text,
    CONSTRAINT chk_destino_desmontaje CHECK (((tipo_evento <> 'DESMONTAJE'::public.tipo_evento_neumatico_enum) OR (destino_desmontaje IS NOT NULL))),
    CONSTRAINT chk_motivo_desecho CHECK ((((tipo_evento <> 'DESECHO'::public.tipo_evento_neumatico_enum) AND ((tipo_evento <> 'DESMONTAJE'::public.tipo_evento_neumatico_enum) OR (destino_desmontaje <> 'DESECHADO'::public.estado_neumatico_enum))) OR (motivo_desecho_id_evento IS NOT NULL))),
    CONSTRAINT chk_profundidad_reencauche CHECK (((tipo_evento <> 'REENCAUCHE_SALIDA'::public.tipo_evento_neumatico_enum) OR (profundidad_post_reencauche_mm IS NOT NULL))),
    CONSTRAINT eventos_neumaticos_costo_evento_check CHECK (((costo_evento IS NULL) OR (costo_evento >= (0)::numeric))),
    CONSTRAINT eventos_neumaticos_odometro_vehiculo_en_evento_check CHECK (((odometro_vehiculo_en_evento IS NULL) OR (odometro_vehiculo_en_evento >= 0))),
    CONSTRAINT eventos_neumaticos_presion_psi_check CHECK (((presion_psi IS NULL) OR (presion_psi > (0)::numeric))),
    CONSTRAINT eventos_neumaticos_profundidad_post_reencauche_mm_check CHECK (((profundidad_post_reencauche_mm IS NULL) OR (profundidad_post_reencauche_mm > (0)::numeric))),
    CONSTRAINT eventos_neumaticos_profundidad_remanente_mm_check CHECK (((profundidad_remanente_mm IS NULL) OR (profundidad_remanente_mm >= (0)::numeric)))
)
WITH (fillfactor='85');


ALTER TABLE public.eventos_neumaticos OWNER TO postgres;

--
-- Name: TABLE eventos_neumaticos; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.eventos_neumaticos IS 'Registro de eventos que afectan el ciclo de vida de los neumáticos';


--
-- Name: COLUMN eventos_neumaticos.tipo_ruta_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.eventos_neumaticos.tipo_ruta_id IS 'Tipo de ruta predominante durante el periodo cubierto hasta este evento.';


--
-- Name: COLUMN eventos_neumaticos.peso_carga_promedio_ton_evento; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.eventos_neumaticos.peso_carga_promedio_ton_evento IS 'Peso promedio de carga estimado durante el uso hasta este evento.';


--
-- Name: COLUMN eventos_neumaticos.motivo_reparacion_texto; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.eventos_neumaticos.motivo_reparacion_texto IS 'Descripción del motivo o síntoma que llevó a la reparación.';


--
-- Name: COLUMN eventos_neumaticos.tipo_dano_detectado_texto; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.eventos_neumaticos.tipo_dano_detectado_texto IS 'Descripción del tipo de daño encontrado en la reparación.';


--
-- Name: fabricantes_neumatico; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fabricantes_neumatico (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    nombre character varying(100) NOT NULL,
    codigo_abreviado character varying(10),
    pais_origen character varying(50),
    sitio_web character varying(255),
    activo boolean DEFAULT true NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    creado_por uuid,
    actualizado_en timestamp with time zone,
    actualizado_por uuid,
    CONSTRAINT fabricantes_neumatico_nombre_length CHECK ((length((nombre)::text) >= 2))
)
WITH (fillfactor='90');


ALTER TABLE public.fabricantes_neumatico OWNER TO postgres;

--
-- Name: garantias_neumaticos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.garantias_neumaticos (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    neumatico_id uuid NOT NULL,
    proveedor_id uuid,
    tipo_garantia character varying(50) NOT NULL,
    fecha_inicio date NOT NULL,
    fecha_fin date,
    kilometraje_cubierto integer,
    meses_cobertura integer,
    condiciones_url text,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    actualizado_en timestamp with time zone,
    creado_por uuid,
    actualizado_por uuid,
    CONSTRAINT chk_fechas_garantia CHECK (((fecha_fin IS NULL) OR (fecha_fin >= fecha_inicio))),
    CONSTRAINT chk_tipo_garantia CHECK (((tipo_garantia)::text = ANY (ARRAY[('KILOMETRAJE'::character varying)::text, ('TIEMPO'::character varying)::text, ('AMBOS'::character varying)::text])))
);


ALTER TABLE public.garantias_neumaticos OWNER TO postgres;

--
-- Name: TABLE garantias_neumaticos; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.garantias_neumaticos IS 'Almacena información detallada sobre las garantías de los neumáticos';


--
-- Name: historial_estados_neumaticos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.historial_estados_neumaticos (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    neumatico_id uuid NOT NULL,
    estado_anterior character varying(50),
    estado_nuevo character varying(50) NOT NULL,
    fecha_cambio timestamp with time zone DEFAULT now() NOT NULL,
    usuario_id uuid,
    comentario text,
    metadata jsonb
);


ALTER TABLE public.historial_estados_neumaticos OWNER TO postgres;

--
-- Name: TABLE historial_estados_neumaticos; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.historial_estados_neumaticos IS 'Registra el historial de cambios de estado de los neumáticos';


--
-- Name: mediciones_profundidad; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mediciones_profundidad (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    neumatico_id uuid NOT NULL,
    fecha_medicion timestamp with time zone DEFAULT now() NOT NULL,
    profundidad_mm numeric(5,2) NOT NULL,
    ubicacion_medicion text NOT NULL,
    metodo_medicion text,
    usuario_id uuid,
    observaciones text,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    actualizado_en timestamp with time zone DEFAULT now() NOT NULL,
    creado_por uuid,
    actualizado_por uuid,
    CONSTRAINT mediciones_profundidad_profundidad_mm_check CHECK (((profundidad_mm >= (0)::numeric) AND (profundidad_mm <= (100)::numeric)))
);


ALTER TABLE public.mediciones_profundidad OWNER TO postgres;

--
-- Name: TABLE mediciones_profundidad; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.mediciones_profundidad IS 'Registra las mediciones de profundidad de la banda de rodadura de los neumáticos';


--
-- Name: COLUMN mediciones_profundidad.profundidad_mm; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.mediciones_profundidad.profundidad_mm IS 'Profundidad medida en milímetros';


--
-- Name: COLUMN mediciones_profundidad.ubicacion_medicion; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.mediciones_profundidad.ubicacion_medicion IS 'Ubicación donde se realizó la medición (ej: posición en el vehículo, almacén, etc.)';


--
-- Name: COLUMN mediciones_profundidad.metodo_medicion; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.mediciones_profundidad.metodo_medicion IS 'Método utilizado para la medición (ej: calibrador, escáner, etc.)';


--
-- Name: modelos_neumatico; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.modelos_neumatico (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    fabricante_id uuid NOT NULL,
    nombre_modelo character varying(100) NOT NULL,
    medida public.medida_neumatico NOT NULL,
    indice_carga character varying(5),
    indice_velocidad character varying(2),
    profundidad_original_mm numeric(5,2) NOT NULL,
    presion_recomendada_psi numeric(5,2),
    permite_reencauche boolean DEFAULT false NOT NULL,
    reencauches_maximos smallint DEFAULT 0,
    patron_dibujo character varying(50),
    tipo_servicio character varying(50),
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    creado_por uuid,
    actualizado_en timestamp with time zone,
    actualizado_por uuid,
    posicion_uso_recomendada public.tipo_eje_enum,
    diseno_predominante_para_eje public.tipo_eje_enum,
    vida_util_teorica_km integer,
    profundidad_minima_retiro_mm numeric(5,2) DEFAULT 1.6 NOT NULL,
    tasa_desgaste_esperada_mm_km numeric(10,8) NOT NULL,
    activo boolean DEFAULT true,
    frecuencia_inspeccion_km integer DEFAULT 5000,
    max_vidas_utiles integer DEFAULT 5,
    porcentaje_desgaste_por_vida numeric(5,2) DEFAULT 10.0,
    CONSTRAINT chk_max_vidas_utiles_positivo CHECK ((max_vidas_utiles > 0)),
    CONSTRAINT chk_porcentaje_desgaste_positivo CHECK ((porcentaje_desgaste_por_vida >= (0)::numeric)),
    CONSTRAINT chk_profundidad_minima_positiva CHECK ((profundidad_minima_retiro_mm > (0)::numeric)),
    CONSTRAINT chk_tasa_desgaste_positiva CHECK ((tasa_desgaste_esperada_mm_km > (0)::numeric)),
    CONSTRAINT modelos_neumatico_presion_recomendada_psi_check CHECK (((presion_recomendada_psi IS NULL) OR (presion_recomendada_psi > (0)::numeric))),
    CONSTRAINT modelos_neumatico_profundidad_minima_retiro_mm_check CHECK (((profundidad_minima_retiro_mm > (0)::numeric) AND (profundidad_minima_retiro_mm <= profundidad_original_mm))),
    CONSTRAINT modelos_neumatico_profundidad_original_mm_check CHECK ((profundidad_original_mm > (0)::numeric)),
    CONSTRAINT modelos_neumatico_reencauches_maximos_check CHECK (((reencauches_maximos >= 0) AND (reencauches_maximos <= 10))),
    CONSTRAINT modelos_neumatico_tasa_desgaste_esperada_check CHECK (((tasa_desgaste_esperada_mm_km IS NULL) OR (tasa_desgaste_esperada_mm_km > (0)::numeric))),
    CONSTRAINT modelos_neumatico_vida_util_teorica_km_check CHECK (((vida_util_teorica_km IS NULL) OR (vida_util_teorica_km > 0)))
)
WITH (fillfactor='90');


ALTER TABLE public.modelos_neumatico OWNER TO postgres;

--
-- Name: TABLE modelos_neumatico; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.modelos_neumatico IS 'Define los diferentes modelos de neumáticos con sus especificaciones técnicas y parámetros de rendimiento esperados';


--
-- Name: COLUMN modelos_neumatico.posicion_uso_recomendada; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.modelos_neumatico.posicion_uso_recomendada IS 'Tipo de eje/posición para la cual este modelo es recomendado (ej. DIRECCION, TRACCION).';


--
-- Name: COLUMN modelos_neumatico.diseno_predominante_para_eje; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.modelos_neumatico.diseno_predominante_para_eje IS '[OPCIONAL] Indica si el diseño del neumático es específicamente para dirección, tracción o libre/arrastre.';


--
-- Name: COLUMN modelos_neumatico.vida_util_teorica_km; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.modelos_neumatico.vida_util_teorica_km IS 'Vida útil teórica del neumático en kilómetros según el fabricante (Lt)';


--
-- Name: COLUMN modelos_neumatico.profundidad_minima_retiro_mm; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.modelos_neumatico.profundidad_minima_retiro_mm IS 'Profundidad mínima del dibujo (en mm) antes de que el neumático deba ser retirado. Debe ser mayor que cero.';


--
-- Name: COLUMN modelos_neumatico.tasa_desgaste_esperada_mm_km; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.modelos_neumatico.tasa_desgaste_esperada_mm_km IS 'Tasa de desgaste esperada en mm por kilómetro. Debe ser mayor que cero.';


--
-- Name: COLUMN modelos_neumatico.activo; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.modelos_neumatico.activo IS 'Indica si el modelo está activo (soft delete)';


--
-- Name: modelos_posiciones_permitidas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.modelos_posiciones_permitidas (
    modelo_neumatico_id uuid NOT NULL,
    posicion_neumatico_id uuid NOT NULL,
    es_recomendado boolean DEFAULT false NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    creado_por uuid
)
WITH (fillfactor='100');


ALTER TABLE public.modelos_posiciones_permitidas OWNER TO postgres;

--
-- Name: TABLE modelos_posiciones_permitidas; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.modelos_posiciones_permitidas IS 'Relación muchos a muchos entre modelos de neumáticos y posiciones permitidas';


--
-- Name: motivos_desecho; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.motivos_desecho (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    codigo character varying(20) NOT NULL,
    descripcion text NOT NULL,
    requiere_evidencia boolean DEFAULT false NOT NULL,
    activo boolean DEFAULT true NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    creado_por uuid,
    actualizado_en timestamp with time zone,
    actualizado_por uuid
)
WITH (fillfactor='95');


ALTER TABLE public.motivos_desecho OWNER TO postgres;

--
-- Name: TABLE motivos_desecho; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.motivos_desecho IS 'Motivos por los que un neumático puede ser dado de baja';


--
-- Name: neumaticos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.neumaticos (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    numero_serie character varying(100),
    dot public.dot_code,
    modelo_id uuid NOT NULL,
    fecha_compra date NOT NULL,
    fecha_fabricacion date,
    costo_compra numeric(10,2),
    moneda_compra character varying(3) DEFAULT 'PEN'::character varying,
    proveedor_compra_id uuid,
    es_reencauchado boolean DEFAULT false NOT NULL,
    vida_actual smallint DEFAULT 1 NOT NULL,
    estado_actual public.estado_neumatico_enum DEFAULT 'EN_STOCK'::public.estado_neumatico_enum NOT NULL,
    ubicacion_actual_vehiculo_id uuid,
    ubicacion_actual_posicion_id uuid,
    fecha_ultimo_evento timestamp with time zone,
    profundidad_inicial_mm numeric(5,2),
    kilometraje_acumulado integer DEFAULT 0 NOT NULL,
    reencauches_realizados smallint DEFAULT 0 NOT NULL,
    fecha_desecho date,
    motivo_desecho_id uuid,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    creado_por uuid,
    actualizado_en timestamp with time zone,
    actualizado_por uuid,
    ubicacion_almacen_id uuid,
    sensor_id character varying(100),
    profundidad_remanente_actual_mm numeric(5,2) NOT NULL,
    fecha_ultima_medicion_profundidad timestamp with time zone,
    kilometraje_vida_actual integer DEFAULT 0,
    fecha_inicio_vida_actual date,
    odometro_instalacion_vida_actual integer,
    tasa_desgaste_actual_mm_km numeric(10,8),
    vida_util_restante_km integer,
    fecha_ultimo_reencauche date,
    activo boolean DEFAULT true,
    proxima_inspeccion_fecha date,
    proxima_inspeccion_km integer,
    profundidad_inicio_vida_actual_mm numeric(5,2),
    CONSTRAINT chk_tasa_desgaste_positiva CHECK (((tasa_desgaste_actual_mm_km IS NULL) OR (tasa_desgaste_actual_mm_km > (0)::numeric))),
    CONSTRAINT chk_ubicacion_mutuamente_exclusiva CHECK ((((ubicacion_almacen_id IS NOT NULL) AND (ubicacion_actual_vehiculo_id IS NULL) AND (ubicacion_actual_posicion_id IS NULL) AND (estado_actual <> 'INSTALADO'::public.estado_neumatico_enum)) OR ((ubicacion_almacen_id IS NULL) AND (ubicacion_actual_vehiculo_id IS NOT NULL) AND (ubicacion_actual_posicion_id IS NOT NULL) AND (estado_actual = 'INSTALADO'::public.estado_neumatico_enum)) OR ((ubicacion_almacen_id IS NULL) AND (ubicacion_actual_vehiculo_id IS NULL) AND (ubicacion_actual_posicion_id IS NULL) AND (estado_actual <> 'INSTALADO'::public.estado_neumatico_enum)))),
    CONSTRAINT chk_vida_util_restante_no_negativa CHECK (((vida_util_restante_km IS NULL) OR (vida_util_restante_km >= 0))),
    CONSTRAINT neumaticos_costo_compra_check CHECK (((costo_compra IS NULL) OR (costo_compra >= (0)::numeric))),
    CONSTRAINT neumaticos_fechas_check CHECK (((fecha_fabricacion IS NULL) OR (fecha_fabricacion <= fecha_compra))),
    CONSTRAINT neumaticos_kilometraje_acumulado_check CHECK ((kilometraje_acumulado >= 0)),
    CONSTRAINT neumaticos_kilometraje_vida_actual_check CHECK ((kilometraje_vida_actual >= 0)),
    CONSTRAINT neumaticos_profundidad_inicial_mm_check CHECK (((profundidad_inicial_mm IS NULL) OR (profundidad_inicial_mm > (0)::numeric))),
    CONSTRAINT neumaticos_profundidad_remanente_check CHECK (((profundidad_remanente_actual_mm IS NULL) OR ((profundidad_remanente_actual_mm >= (0)::numeric) AND (profundidad_remanente_actual_mm <= (50)::numeric)))),
    CONSTRAINT neumaticos_reencauches_realizados_check CHECK ((reencauches_realizados >= 0)),
    CONSTRAINT neumaticos_tasa_desgaste_actual_check CHECK (((tasa_desgaste_actual_mm_km IS NULL) OR (tasa_desgaste_actual_mm_km > (0)::numeric))),
    CONSTRAINT neumaticos_vida_actual_check CHECK (((vida_actual >= 1) AND (vida_actual <= 11))),
    CONSTRAINT neumaticos_vida_util_restante_check CHECK (((vida_util_restante_km IS NULL) OR (vida_util_restante_km >= 0)))
)
WITH (fillfactor='90');


ALTER TABLE public.neumaticos OWNER TO postgres;

--
-- Name: TABLE neumaticos; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.neumaticos IS 'Almacena información sobre neumáticos individuales, incluyendo su estado actual, ubicación y métricas de rendimiento';


--
-- Name: COLUMN neumaticos.profundidad_remanente_actual_mm; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.neumaticos.profundidad_remanente_actual_mm IS 'Profundidad actual de la banda de rodadura (en mm)';


--
-- Name: COLUMN neumaticos.fecha_ultima_medicion_profundidad; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.neumaticos.fecha_ultima_medicion_profundidad IS 'Fecha de la última medición de profundidad';


--
-- Name: COLUMN neumaticos.kilometraje_vida_actual; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.neumaticos.kilometraje_vida_actual IS 'Kilometraje acumulado en la vida actual del neumático';


--
-- Name: COLUMN neumaticos.fecha_inicio_vida_actual; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.neumaticos.fecha_inicio_vida_actual IS 'Fecha de inicio de la vida actual del neumático';


--
-- Name: COLUMN neumaticos.odometro_instalacion_vida_actual; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.neumaticos.odometro_instalacion_vida_actual IS 'Odómetro del vehículo al momento de la instalación para la vida actual';


--
-- Name: COLUMN neumaticos.tasa_desgaste_actual_mm_km; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.neumaticos.tasa_desgaste_actual_mm_km IS 'Tasa de desgaste actual en mm/km';


--
-- Name: COLUMN neumaticos.vida_util_restante_km; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.neumaticos.vida_util_restante_km IS 'Vida útil restante estimada en kilómetros (Lr)';


--
-- Name: COLUMN neumaticos.fecha_ultimo_reencauche; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.neumaticos.fecha_ultimo_reencauche IS 'Fecha del último reencauche realizado';


--
-- Name: COLUMN neumaticos.activo; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.neumaticos.activo IS 'Indica si el neumático está activo (soft delete)';


--
-- Name: COLUMN neumaticos.proxima_inspeccion_fecha; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.neumaticos.proxima_inspeccion_fecha IS 'Fecha recomendada para la próxima inspección del neumático';


--
-- Name: COLUMN neumaticos.proxima_inspeccion_km; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.neumaticos.proxima_inspeccion_km IS 'Kilometraje recomendado para la próxima inspección del neumático';


--
-- Name: mv_desempeno_modelos; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.mv_desempeno_modelos AS
 WITH neumaticos_activos AS (
         SELECT neumaticos.id,
            neumaticos.numero_serie,
            neumaticos.dot,
            neumaticos.modelo_id,
            neumaticos.fecha_compra,
            neumaticos.fecha_fabricacion,
            neumaticos.costo_compra,
            neumaticos.moneda_compra,
            neumaticos.proveedor_compra_id,
            neumaticos.es_reencauchado,
            neumaticos.vida_actual,
            neumaticos.estado_actual,
            neumaticos.ubicacion_actual_vehiculo_id,
            neumaticos.ubicacion_actual_posicion_id,
            neumaticos.fecha_ultimo_evento,
            neumaticos.profundidad_inicial_mm,
            neumaticos.kilometraje_acumulado,
            neumaticos.reencauches_realizados,
            neumaticos.fecha_desecho,
            neumaticos.motivo_desecho_id,
            neumaticos.creado_en,
            neumaticos.creado_por,
            neumaticos.actualizado_en,
            neumaticos.actualizado_por,
            neumaticos.ubicacion_almacen_id,
            neumaticos.sensor_id,
            neumaticos.profundidad_remanente_actual_mm,
            neumaticos.fecha_ultima_medicion_profundidad,
            neumaticos.kilometraje_vida_actual,
            neumaticos.fecha_inicio_vida_actual,
            neumaticos.odometro_instalacion_vida_actual,
            neumaticos.tasa_desgaste_actual_mm_km,
            neumaticos.vida_util_restante_km,
            neumaticos.fecha_ultimo_reencauche,
            neumaticos.activo,
            neumaticos.proxima_inspeccion_fecha,
            neumaticos.proxima_inspeccion_km,
            neumaticos.profundidad_inicio_vida_actual_mm
           FROM public.neumaticos
          WHERE ((neumaticos.estado_actual <> 'DESECHADO'::public.estado_neumatico_enum) AND (neumaticos.estado_actual IS NOT NULL))
        ), estadisticas_modelos AS (
         SELECT mn_1.id AS modelo_id,
            count(DISTINCT n.id) AS total_neumaticos,
            count(DISTINCT
                CASE
                    WHEN (n.estado_actual = 'INSTALADO'::public.estado_neumatico_enum) THEN n.id
                    ELSE NULL::uuid
                END) AS instalados,
            count(DISTINCT
                CASE
                    WHEN (n.estado_actual = 'EN_STOCK'::public.estado_neumatico_enum) THEN n.id
                    ELSE NULL::uuid
                END) AS en_stock,
            count(DISTINCT
                CASE
                    WHEN (n.estado_actual = 'EN_REPARACION'::public.estado_neumatico_enum) THEN n.id
                    ELSE NULL::uuid
                END) AS en_reparacion,
            count(DISTINCT
                CASE
                    WHEN (n.estado_actual = 'EN_REENCAUCHE'::public.estado_neumatico_enum) THEN n.id
                    ELSE NULL::uuid
                END) AS en_reencauche,
            count(DISTINCT
                CASE
                    WHEN (n.estado_actual = 'EN_TRANSITO'::public.estado_neumatico_enum) THEN n.id
                    ELSE NULL::uuid
                END) AS en_transito,
            count(DISTINCT
                CASE
                    WHEN (n.estado_actual = 'DESECHADO'::public.estado_neumatico_enum) THEN n.id
                    ELSE NULL::uuid
                END) AS desechados,
            count(na.id) AS total_activos,
            avg(na.vida_util_restante_km) AS vida_util_promedio_km,
            avg(na.tasa_desgaste_actual_mm_km) AS tasa_desgaste_promedio_mm_km,
            avg(na.profundidad_remanente_actual_mm) AS profundidad_promedio_mm,
            min(na.profundidad_remanente_actual_mm) AS profundidad_minima_mm,
            max(na.profundidad_remanente_actual_mm) AS profundidad_maxima_mm,
            avg(na.kilometraje_vida_actual) AS kilometraje_vida_promedio,
            max(na.kilometraje_vida_actual) AS max_kilometraje_vida,
            min(
                CASE
                    WHEN (na.kilometraje_vida_actual > 0) THEN na.kilometraje_vida_actual
                    ELSE NULL::integer
                END) AS min_kilometraje_vida_no_cero,
            avg(na.vida_actual) AS vida_actual_promedio
           FROM ((public.modelos_neumatico mn_1
             LEFT JOIN public.neumaticos n ON ((mn_1.id = n.modelo_id)))
             LEFT JOIN neumaticos_activos na ON ((n.id = na.id)))
          WHERE ((mn_1.activo = true) AND ((n.id IS NULL) OR (n.estado_actual = ANY (ARRAY['EN_STOCK'::public.estado_neumatico_enum, 'INSTALADO'::public.estado_neumatico_enum, 'EN_REPARACION'::public.estado_neumatico_enum, 'EN_REENCAUCHE'::public.estado_neumatico_enum, 'EN_TRANSITO'::public.estado_neumatico_enum, 'DESECHADO'::public.estado_neumatico_enum]))))
          GROUP BY mn_1.id
        )
 SELECT mn.id AS modelo_id,
    mn.nombre_modelo AS modelo_nombre,
    f.nombre AS fabricante_nombre,
    mn.medida,
    mn.indice_carga,
    mn.indice_velocidad,
    mn.profundidad_original_mm,
    mn.tasa_desgaste_esperada_mm_km,
    mn.vida_util_teorica_km,
    mn.activo AS modelo_activo,
    COALESCE(em.total_neumaticos, (0)::bigint) AS total_neumaticos,
    COALESCE(em.instalados, (0)::bigint) AS instalados,
    COALESCE(em.en_stock, (0)::bigint) AS en_stock,
    COALESCE(em.en_reparacion, (0)::bigint) AS en_reparacion,
    COALESCE(em.en_reencauche, (0)::bigint) AS en_reencauche,
    COALESCE(em.en_transito, (0)::bigint) AS en_transito,
    COALESCE(em.desechados, (0)::bigint) AS desechados,
        CASE
            WHEN (em.total_activos > 0) THEN em.vida_util_promedio_km
            ELSE NULL::numeric
        END AS vida_util_promedio_km,
        CASE
            WHEN (em.total_activos > 0) THEN em.tasa_desgaste_promedio_mm_km
            ELSE NULL::numeric
        END AS tasa_desgaste_promedio_mm_km,
        CASE
            WHEN (em.total_activos > 0) THEN em.profundidad_promedio_mm
            ELSE NULL::numeric
        END AS profundidad_promedio_mm,
        CASE
            WHEN (em.total_activos > 0) THEN em.profundidad_minima_mm
            ELSE NULL::numeric
        END AS profundidad_minima_mm,
        CASE
            WHEN (em.total_activos > 0) THEN em.profundidad_maxima_mm
            ELSE NULL::numeric
        END AS profundidad_maxima_mm,
        CASE
            WHEN (em.total_activos > 0) THEN em.kilometraje_vida_promedio
            ELSE NULL::numeric
        END AS kilometraje_vida_promedio,
        CASE
            WHEN (em.total_activos > 0) THEN em.max_kilometraje_vida
            ELSE NULL::integer
        END AS max_kilometraje_vida,
        CASE
            WHEN (em.total_activos > 0) THEN em.min_kilometraje_vida_no_cero
            ELSE NULL::integer
        END AS min_kilometraje_vida_no_cero,
        CASE
            WHEN (em.total_activos > 0) THEN em.vida_actual_promedio
            ELSE NULL::numeric
        END AS vida_actual_promedio,
    now() AS fecha_actualizacion,
    (COALESCE(em.total_activos, (0)::bigint) > 0) AS tiene_datos_rendimiento
   FROM ((public.modelos_neumatico mn
     LEFT JOIN public.fabricantes_neumatico f ON ((mn.fabricante_id = f.id)))
     LEFT JOIN estadisticas_modelos em ON ((mn.id = em.modelo_id)))
  WHERE (mn.activo = true)
  WITH NO DATA;


ALTER MATERIALIZED VIEW public.mv_desempeno_modelos OWNER TO postgres;

--
-- Name: mv_eventos_recientes; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.mv_eventos_recientes AS
 SELECT e.id,
    e.tipo_evento,
    e.timestamp_evento,
    n.numero_serie,
    e.usuario_id,
    e.vehiculo_id,
    e.datos_evento
   FROM (public.eventos_neumaticos e
     JOIN public.neumaticos n ON ((e.neumatico_id = n.id)))
  WHERE (e.timestamp_evento > (CURRENT_DATE - '30 days'::interval))
  ORDER BY e.timestamp_evento DESC
  WITH NO DATA;


ALTER MATERIALIZED VIEW public.mv_eventos_recientes OWNER TO postgres;

--
-- Name: mv_resumen_neumaticos_estado; Type: MATERIALIZED VIEW; Schema: public; Owner: postgres
--

CREATE MATERIALIZED VIEW public.mv_resumen_neumaticos_estado AS
 SELECT estado_actual,
    count(*) AS cantidad,
    avg(vida_util_restante_km) AS vida_util_promedio_km,
    min(profundidad_remanente_actual_mm) AS profundidad_minima_mm,
    max(profundidad_remanente_actual_mm) AS profundidad_maxima_mm
   FROM public.neumaticos
  GROUP BY estado_actual
  WITH NO DATA;


ALTER MATERIALIZED VIEW public.mv_resumen_neumaticos_estado OWNER TO postgres;

--
-- Name: neumaticos_vista_publica; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.neumaticos_vista_publica AS
 SELECT id,
    numero_serie,
    dot,
    modelo_id,
    fecha_compra,
    fecha_fabricacion,
    estado_actual,
    es_reencauchado,
    vida_actual,
    ubicacion_actual_vehiculo_id,
    ubicacion_actual_posicion_id,
    ubicacion_almacen_id,
    fecha_ultimo_evento,
    kilometraje_acumulado,
    reencauches_realizados
   FROM public.neumaticos;


ALTER VIEW public.neumaticos_vista_publica OWNER TO postgres;

--
-- Name: parametros_inventario; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.parametros_inventario (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    parametro_tipo public.tipo_parametro_inventario_gesneu_enum NOT NULL,
    modelo_id uuid NOT NULL,
    ubicacion_almacen_id uuid,
    valor_numerico numeric(10,2),
    valor_texto text,
    activo boolean DEFAULT true NOT NULL,
    notas text,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    creado_por uuid,
    actualizado_en timestamp with time zone,
    actualizado_por uuid
);


ALTER TABLE public.parametros_inventario OWNER TO postgres;

--
-- Name: TABLE parametros_inventario; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.parametros_inventario IS 'Parámetros configurables para la gestión de inventario de neumáticos';


--
-- Name: parametros_rendimiento_esperado_modelo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.parametros_rendimiento_esperado_modelo (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    modelo_id uuid NOT NULL,
    tipo_eje_aplicacion public.tipo_eje_enum NOT NULL,
    km_esperado_vida_original_min integer,
    km_esperado_vida_original_max integer,
    notas text,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    creado_por uuid,
    actualizado_en timestamp with time zone,
    actualizado_por uuid,
    CONSTRAINT parametros_rendimiento_esper_km_esperado_vida_original_mi_check CHECK (((km_esperado_vida_original_min IS NULL) OR (km_esperado_vida_original_min >= 0))),
    CONSTRAINT parametros_rendimiento_esperado_modelo_check CHECK (((km_esperado_vida_original_max IS NULL) OR (km_esperado_vida_original_max >= COALESCE(km_esperado_vida_original_min, 0))))
);


ALTER TABLE public.parametros_rendimiento_esperado_modelo OWNER TO postgres;

--
-- Name: TABLE parametros_rendimiento_esperado_modelo; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.parametros_rendimiento_esperado_modelo IS 'Almacena los parámetros de rendimiento esperado para cada modelo de neumático según el tipo de eje de aplicación';


--
-- Name: parametros_sistema; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.parametros_sistema (
    id integer NOT NULL,
    clave character varying(100) NOT NULL,
    valor text NOT NULL,
    descripcion text,
    creado_en timestamp with time zone DEFAULT now(),
    actualizado_en timestamp with time zone DEFAULT now(),
    creado_por character varying(100) DEFAULT 'SISTEMA'::character varying,
    actualizado_por character varying(100) DEFAULT 'SISTEMA'::character varying
);


ALTER TABLE public.parametros_sistema OWNER TO postgres;

--
-- Name: parametros_sistema_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.parametros_sistema_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.parametros_sistema_id_seq OWNER TO postgres;

--
-- Name: parametros_sistema_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.parametros_sistema_id_seq OWNED BY public.parametros_sistema.id;


--
-- Name: permisos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.permisos (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    nombre_recurso character varying(100) NOT NULL,
    accion character varying(100) NOT NULL,
    descripcion text,
    creado_en timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.permisos OWNER TO postgres;

--
-- Name: TABLE permisos; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.permisos IS 'Permisos granulares del sistema';


--
-- Name: posiciones_neumatico; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.posiciones_neumatico (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    configuracion_eje_id uuid NOT NULL,
    codigo_posicion character varying(10) NOT NULL,
    etiqueta_posicion character varying(50),
    lado public.lado_vehiculo_enum NOT NULL,
    posicion_relativa smallint NOT NULL,
    es_interna boolean DEFAULT false NOT NULL,
    es_direccion boolean DEFAULT false NOT NULL,
    es_traccion boolean DEFAULT false NOT NULL,
    requiere_neumatico_especifico boolean DEFAULT false NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    creado_por uuid,
    actualizado_en timestamp with time zone,
    actualizado_por uuid,
    CONSTRAINT posiciones_neumatico_posicion_relativa_check CHECK ((posicion_relativa > 0))
)
WITH (fillfactor='95');


ALTER TABLE public.posiciones_neumatico OWNER TO postgres;

--
-- Name: proveedores; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.proveedores (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    nombre character varying(150) NOT NULL,
    tipo public.tipoproveedorenum,
    ruc character varying(11),
    contacto_principal text,
    telefono character varying(50),
    email character varying(100),
    direccion text,
    activo boolean DEFAULT true NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    creado_por uuid,
    actualizado_en timestamp with time zone,
    actualizado_por uuid,
    CONSTRAINT proveedores_ruc_check CHECK (((ruc IS NULL) OR (((ruc)::text ~ '^10[0-9]{9}$'::text) OR ((ruc)::text ~ '^20[0-9]{9}$'::text) OR ((ruc)::text ~ '^1[5-9][0-9]{9}$'::text) OR ((ruc)::text ~ '^5[0-9][0-9]{9}$'::text) OR ((ruc)::text ~ '^(2[7-9]|[3-9][0-9])[0-9]{10}$'::text))))
)
WITH (fillfactor='95');


ALTER TABLE public.proveedores OWNER TO postgres;

--
-- Name: TABLE proveedores; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.proveedores IS 'Proveedores de neumáticos y servicios relacionados';


--
-- Name: CONSTRAINT proveedores_ruc_check ON proveedores; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON CONSTRAINT proveedores_ruc_check ON public.proveedores IS 'Valida que el RUC tenga un formato válido según las reglas peruanas. 
Formatos aceptados:
- Persona natural: 10 + 9 dígitos (total 11)
- Persona jurídica: 20 + 9 dígitos (total 11)
- Empresas públicas: 15-19 + 9 dígitos (total 11)
- Empresas privadas: 50-59 + 9 dígitos (total 11)
- Entidades extranjeras: 27-99 + 9 dígitos (total 11)
Los RUCs pueden ser NULL si no se dispone de ellos.';


--
-- Name: registros_odometro; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.registros_odometro (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    vehiculo_id uuid NOT NULL,
    odometro integer NOT NULL,
    fecha_medicion timestamp with time zone DEFAULT now() NOT NULL,
    fuente character varying(50) DEFAULT 'manual'::character varying,
    creado_por uuid,
    notas text,
    CONSTRAINT registros_odometro_fuente_check CHECK (((fuente)::text <> ''::text)),
    CONSTRAINT registros_odometro_odometro_check CHECK ((odometro >= 0))
);


ALTER TABLE public.registros_odometro OWNER TO postgres;

--
-- Name: TABLE registros_odometro; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.registros_odometro IS 'Registros históricos de lecturas de odómetro de los vehículos';


--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion text,
    es_rol_sistema boolean DEFAULT false NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    creado_por uuid,
    actualizado_en timestamp with time zone,
    actualizado_por uuid
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: TABLE roles; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.roles IS 'Roles de usuario en el sistema';


--
-- Name: roles_permisos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles_permisos (
    rol_id uuid NOT NULL,
    permiso_id uuid NOT NULL,
    asignado_en timestamp with time zone DEFAULT now() NOT NULL,
    asignado_por uuid
);


ALTER TABLE public.roles_permisos OWNER TO postgres;

--
-- Name: TABLE roles_permisos; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.roles_permisos IS 'Relación muchos a muchos entre roles y permisos';


--
-- Name: rutas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rutas (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    codigo character varying(20) NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion text,
    distancia_total_km numeric(10,2) NOT NULL,
    ida_vuelta boolean DEFAULT true NOT NULL,
    activa boolean DEFAULT true NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    creado_por uuid,
    actualizado_en timestamp with time zone,
    actualizado_por uuid
);


ALTER TABLE public.rutas OWNER TO postgres;

--
-- Name: tareas_programadas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tareas_programadas (
    id integer NOT NULL,
    nombre_tarea character varying(100) NOT NULL,
    descripcion text,
    frecuencia_dias integer DEFAULT 1 NOT NULL,
    ultima_ejecucion timestamp with time zone,
    proxima_ejecucion timestamp with time zone,
    activa boolean DEFAULT true,
    script_sql text,
    creado_en timestamp with time zone DEFAULT now(),
    creado_por character varying(100) DEFAULT 'SISTEMA'::character varying,
    actualizado_en timestamp with time zone,
    actualizado_por character varying(100)
);


ALTER TABLE public.tareas_programadas OWNER TO postgres;

--
-- Name: tareas_programadas_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tareas_programadas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tareas_programadas_id_seq OWNER TO postgres;

--
-- Name: tareas_programadas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tareas_programadas_id_seq OWNED BY public.tareas_programadas.id;


--
-- Name: tipos_ruta; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tipos_ruta (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    nombre_ruta character varying(150) NOT NULL,
    descripcion text,
    distancia_total_km_ciclo numeric(8,2),
    distancia_trocha_km_ciclo numeric(8,2) DEFAULT 0,
    distancia_asfalto_km_ciclo numeric(8,2) DEFAULT 0,
    distancia_otro_terreno_km_ciclo numeric(8,2) DEFAULT 0,
    porcentaje_promedio_con_carga numeric(5,2),
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    creado_por uuid,
    actualizado_en timestamp with time zone,
    actualizado_por uuid,
    CONSTRAINT chk_porc_carga_ruta_gesneu CHECK (((porcentaje_promedio_con_carga IS NULL) OR ((porcentaje_promedio_con_carga >= (0)::numeric) AND (porcentaje_promedio_con_carga <= (100)::numeric))))
);


ALTER TABLE public.tipos_ruta OWNER TO postgres;

--
-- Name: TABLE tipos_ruta; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.tipos_ruta IS 'Define perfiles de rutas o ciclos operativos con sus características de terreno y carga.';


--
-- Name: tipos_vehiculo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tipos_vehiculo (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion text,
    categoria_principal character varying(50),
    subtipo character varying(50),
    ejes_standard smallint DEFAULT 2 NOT NULL,
    activo boolean DEFAULT true NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    creado_por uuid,
    actualizado_en timestamp with time zone,
    actualizado_por uuid,
    CONSTRAINT tipos_vehiculo_ejes_standard_check CHECK (((ejes_standard >= 1) AND (ejes_standard <= 10)))
)
WITH (fillfactor='95');


ALTER TABLE public.tipos_vehiculo OWNER TO postgres;

--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuarios (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    username character varying(50) NOT NULL,
    nombre_completo character varying(200),
    email character varying(100),
    password_hash text,
    activo boolean DEFAULT true NOT NULL,
    ultimo_login timestamp with time zone,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    creado_por uuid,
    actualizado_en timestamp with time zone,
    actualizado_por uuid
)
WITH (fillfactor='95');


ALTER TABLE public.usuarios OWNER TO postgres;

--
-- Name: TABLE usuarios; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.usuarios IS 'Usuarios del sistema con acceso a la aplicación';


--
-- Name: usuarios_roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuarios_roles (
    usuario_id uuid NOT NULL,
    rol_id uuid NOT NULL,
    asignado_en timestamp with time zone DEFAULT now() NOT NULL,
    asignado_por uuid
);


ALTER TABLE public.usuarios_roles OWNER TO postgres;

--
-- Name: TABLE usuarios_roles; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.usuarios_roles IS 'Relación muchos a muchos entre usuarios y roles';


--
-- Name: v_auditoria_motivos_desecho; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_auditoria_motivos_desecho AS
 SELECT id,
    timestamp_log AS fecha_hora,
    operacion,
    COALESCE(usuario_aplicacion_username, 'SISTEMA'::character varying) AS usuario,
    COALESCE(direccion_ip, '0.0.0.0'::character varying) AS direccion_ip,
    datos_antiguos,
    datos_nuevos,
    cambios,
    ((datos_nuevos ->> 'id'::text))::uuid AS motivo_id,
    (datos_nuevos ->> 'codigo'::text) AS codigo_motivo,
    (datos_nuevos ->> 'descripcion'::text) AS descripcion,
    ((datos_nuevos ->> 'requiere_evidencia'::text))::boolean AS requiere_evidencia,
    ((datos_nuevos ->> 'activo'::text))::boolean AS activo
   FROM public.auditoria_log al
  WHERE ((nombre_tabla)::text = 'motivos_desecho'::text)
  ORDER BY timestamp_log DESC;


ALTER VIEW public.v_auditoria_motivos_desecho OWNER TO postgres;

--
-- Name: VIEW v_auditoria_motivos_desecho; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON VIEW public.v_auditoria_motivos_desecho IS 'Vista para consultar los registros de auditoría de la tabla motivos_desecho. 

Incluye todos los cambios realizados en la tabla con información detallada de cada operación.';


--
-- Name: vehiculos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vehiculos (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    tipo_vehiculo_id uuid NOT NULL,
    placa public.placa_vehiculo,
    vin character varying(17),
    numero_economico character varying(50) NOT NULL,
    marca character varying(50),
    modelo_vehiculo character varying(50),
    anio_fabricacion smallint,
    fecha_alta date DEFAULT CURRENT_DATE NOT NULL,
    fecha_baja date,
    activo boolean DEFAULT true NOT NULL,
    odometro_actual integer,
    fecha_ultimo_odometro timestamp with time zone,
    ubicacion_actual character varying(100),
    notas text,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    creado_por uuid,
    actualizado_en timestamp with time zone,
    actualizado_por uuid,
    peso_carga_maxima_diseno_ton numeric(5,2),
    CONSTRAINT vehiculos_anio_fabricacion_check CHECK (((anio_fabricacion >= 1900) AND ((anio_fabricacion)::numeric <= (EXTRACT(year FROM CURRENT_DATE) + (1)::numeric)))),
    CONSTRAINT vehiculos_fecha_baja_check CHECK (((fecha_baja IS NULL) OR (fecha_baja >= fecha_alta))),
    CONSTRAINT vehiculos_odometro_actual_check CHECK (((odometro_actual IS NULL) OR (odometro_actual >= 0)))
)
WITH (fillfactor='90');


ALTER TABLE public.vehiculos OWNER TO postgres;

--
-- Name: TABLE vehiculos; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.vehiculos IS 'Vehículos de la flota que utilizan neumáticos';


--
-- Name: COLUMN vehiculos.peso_carga_maxima_diseno_ton; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.vehiculos.peso_carga_maxima_diseno_ton IS 'Capacidad máxima de carga de diseño del vehículo en toneladas.';


--
-- Name: vw_auditoria; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_auditoria AS
 SELECT id,
    timestamp_log,
    nombre_tabla,
    operacion,
    usuario_db,
    id_entidad,
    datos_antiguos,
    datos_nuevos,
    cambios,
    contexto_aplicacion,
    query_ejecutada,
        CASE
            WHEN ((operacion)::text = 'INSERT'::text) THEN 'Nuevo registro'::text
            WHEN ((operacion)::text = 'UPDATE'::text) THEN 'Actualización'::text
            WHEN ((operacion)::text = 'DELETE'::text) THEN 'Eliminación'::text
            ELSE NULL::text
        END AS tipo_operacion
   FROM public.auditoria_log
  ORDER BY timestamp_log DESC;


ALTER VIEW public.vw_auditoria OWNER TO postgres;

--
-- Name: auditoria_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auditoria_log ALTER COLUMN id SET DEFAULT nextval('public.auditoria_log_id_seq'::regclass);


--
-- Name: bitacora_mantenimiento id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bitacora_mantenimiento ALTER COLUMN id SET DEFAULT nextval('public.bitacora_mantenimiento_id_seq'::regclass);


--
-- Name: parametros_sistema id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parametros_sistema ALTER COLUMN id SET DEFAULT nextval('public.parametros_sistema_id_seq'::regclass);


--
-- Name: tareas_programadas id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tareas_programadas ALTER COLUMN id SET DEFAULT nextval('public.tareas_programadas_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
\.


--
-- Data for Name: alertas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alertas (id, tipo_alerta, mensaje, nivel_severidad, estado_alerta, timestamp_generacion, timestamp_gestion, usuario_gestion_id, neumatico_id, vehiculo_id, modelo_id, almacen_id, parametro_id, datos_contexto) FROM stdin;
\.


--
-- Data for Name: almacenes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.almacenes (id, codigo, nombre, tipo, direccion, activo, creado_en, creado_por, actualizado_en, actualizado_por) FROM stdin;
00000000-0000-0000-0000-000000000001	ALM-PRIN	Almacén Principal	PRINCIPAL	Bodega Central, Nave 1, Avenida Principal #123	t	2025-05-19 12:35:59.100954-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-19 13:06:31.172085-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
7ba80f86-477e-48b5-b6fe-2cd7f3b72260	ALM-PRUEBA	Almacén de Prueba	\N	Calle Falsa 123	t	2025-05-19 13:42:18.867633-05	\N	\N	\N
\.


--
-- Data for Name: auditoria_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auditoria_log (id, timestamp_log, esquema_tabla, nombre_tabla, operacion, usuario_db, usuario_aplicacion_id, usuario_aplicacion_username, direccion_ip, user_agent, id_entidad, datos_antiguos, datos_nuevos, cambios, contexto_aplicacion, query_ejecutada) FROM stdin;
1	2025-05-19 13:06:31.172085-05	public	almacenes	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "tipo": "PRINCIPAL", "activo": true, "codigo": "ALM-PRIN", "nombre": "Almacén Principal", "creado_en": "2025-05-19T12:35:59.100954-05:00", "direccion": "Bodega Central, Nave 1, Calle Ficticia #123", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": null, "actualizado_por": null}	{"id": "00000000-0000-0000-0000-000000000001", "tipo": "PRINCIPAL", "activo": true, "codigo": "ALM-PRIN", "nombre": "Almacén Principal", "creado_en": "2025-05-19T12:35:59.100954-05:00", "direccion": "Bodega Central, Nave 1, Avenida Principal #123", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": "2025-05-19T13:06:31.172085-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12"}	{"id": "00000000-0000-0000-0000-000000000001", "tipo": "PRINCIPAL", "codigo": "ALM-PRIN", "nombre": "Almacén Principal", "creado_en": "2025-05-19T12:35:59.100954-05:00", "direccion": "Bodega Central, Nave 1, Avenida Principal #123", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": "2025-05-19T13:06:31.172085-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12"}	{"client_addr": "127.0.0.1/32", "application_name": "psql"}	\n-- Actualizar un almacén\nUPDATE public.almacenes\nSET \n    direccion = 'Bodega Central, Nave 1, Avenida Principal #123',\n    actualizado_en = NOW(),\n    actualizado_por = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'\nWHERE codigo = 'ALM-PRIN';
2	2025-05-19 13:13:06.112904-05	public	almacenes	INSERT	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000003	\N	{"id": "00000000-0000-0000-0000-000000000003", "tipo": "TEMPORAL", "activo": true, "codigo": "ALM-TEST", "nombre": "Almacén de Prueba", "creado_en": "2025-05-19T13:13:06.112904-05:00", "direccion": "Ubicación de prueba", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": null, "actualizado_por": null}	{"id": "00000000-0000-0000-0000-000000000003", "tipo": "TEMPORAL", "activo": true, "codigo": "ALM-TEST", "nombre": "Almacén de Prueba", "creado_en": "2025-05-19T13:13:06.112904-05:00", "direccion": "Ubicación de prueba", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": null, "actualizado_por": null}	{"client_addr": "127.0.0.1/32", "application_name": "psql"}	\n-- Insertar un almacén de prueba\nINSERT INTO public.almacenes (\n    id,\n    codigo,\n    nombre,\n    tipo,\n    direccion,\n    activo,\n    creado_por\n) VALUES (\n    '00000000-0000-0000-0000-000000000003',\n    'ALM-TEST',\n    'Almacén de Prueba',\n    'TEMPORAL',\n    'Ubicación de prueba',\n    true,\n    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'\n);\n\n-- Verificar que se insertó correctamente\nSELECT id, codigo, nombre FROM public.almacenes WHERE codigo = 'ALM-TEST';\n\n-- Eliminar el almacén de prueba\nDELETE FROM public.almacenes WHERE codigo = 'ALM-TEST' RETURNING id;\n\n-- Verificar los registros de auditoría\nSELECT \n    id,\n    to_char(timestamp_log, 'YYYY-MM-DD HH24:MI:SS') as fecha_hora,\n    nombre_tabla,\n    operacion,\n    usuario_db as usuario,\n    id_entidad\nFROM public.auditoria_log\nWHERE nombre_tabla = 'almacenes'\nORDER BY timestamp_log DESC\nLIMIT 5;
3	2025-05-19 13:13:06.112904-05	public	almacenes	DELETE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000003	{"id": "00000000-0000-0000-0000-000000000003", "tipo": "TEMPORAL", "activo": true, "codigo": "ALM-TEST", "nombre": "Almacén de Prueba", "creado_en": "2025-05-19T13:13:06.112904-05:00", "direccion": "Ubicación de prueba", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": null, "actualizado_por": null}	\N	{"id": "00000000-0000-0000-0000-000000000003", "tipo": "TEMPORAL", "activo": true, "codigo": "ALM-TEST", "nombre": "Almacén de Prueba", "creado_en": "2025-05-19T13:13:06.112904-05:00", "direccion": "Ubicación de prueba", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": null, "actualizado_por": null}	{"client_addr": "127.0.0.1/32", "application_name": "psql"}	\n-- Insertar un almacén de prueba\nINSERT INTO public.almacenes (\n    id,\n    codigo,\n    nombre,\n    tipo,\n    direccion,\n    activo,\n    creado_por\n) VALUES (\n    '00000000-0000-0000-0000-000000000003',\n    'ALM-TEST',\n    'Almacén de Prueba',\n    'TEMPORAL',\n    'Ubicación de prueba',\n    true,\n    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'\n);\n\n-- Verificar que se insertó correctamente\nSELECT id, codigo, nombre FROM public.almacenes WHERE codigo = 'ALM-TEST';\n\n-- Eliminar el almacén de prueba\nDELETE FROM public.almacenes WHERE codigo = 'ALM-TEST' RETURNING id;\n\n-- Verificar los registros de auditoría\nSELECT \n    id,\n    to_char(timestamp_log, 'YYYY-MM-DD HH24:MI:SS') as fecha_hora,\n    nombre_tabla,\n    operacion,\n    usuario_db as usuario,\n    id_entidad\nFROM public.auditoria_log\nWHERE nombre_tabla = 'almacenes'\nORDER BY timestamp_log DESC\nLIMIT 5;
31	2025-05-19 15:20:54.246329-05	public	roles_permisos	DELETE	postgres	\N	\N	\N	\N	fec1ccea-481f-a39f-3efe-37a0999140f4	{"rol_id": "00000000-0000-0000-0000-000000000005", "permiso_id": "00000000-0000-0000-0001-000000000005", "asignado_en": "2025-05-19T15:17:00.969862-05:00", "asignado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12"}	{}	{"status": "audit-simple"}	{"timestamp": "2025-05-19 15:20:54.246329-05", "current_user": "postgres", "session_user": "postgres", "current_database": "ges_neu_bd"}	DELETE FROM public.roles_permisos\nWHERE rol_id = '00000000-0000-0000-0000-000000000005'\nAND permiso_id = '00000000-0000-0000-0001-000000000005';
4	2025-05-19 13:13:06.112904-05	public	almacenes	DELETE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000003	{"id": "00000000-0000-0000-0000-000000000003", "tipo": "TEMPORAL", "activo": true, "codigo": "ALM-TEST", "nombre": "Almacén de Prueba", "creado_en": "2025-05-19T13:13:06.112904-05:00", "direccion": "Ubicación de prueba", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": null, "actualizado_por": null}	\N	{"id": "00000000-0000-0000-0000-000000000003", "tipo": "TEMPORAL", "activo": true, "codigo": "ALM-TEST", "nombre": "Almacén de Prueba", "creado_en": "2025-05-19T13:13:06.112904-05:00", "direccion": "Ubicación de prueba", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": null, "actualizado_por": null}	{"client_addr": "127.0.0.1/32", "application_name": "psql"}	\n-- Insertar un almacén de prueba\nINSERT INTO public.almacenes (\n    id,\n    codigo,\n    nombre,\n    tipo,\n    direccion,\n    activo,\n    creado_por\n) VALUES (\n    '00000000-0000-0000-0000-000000000003',\n    'ALM-TEST',\n    'Almacén de Prueba',\n    'TEMPORAL',\n    'Ubicación de prueba',\n    true,\n    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'\n);\n\n-- Verificar que se insertó correctamente\nSELECT id, codigo, nombre FROM public.almacenes WHERE codigo = 'ALM-TEST';\n\n-- Eliminar el almacén de prueba\nDELETE FROM public.almacenes WHERE codigo = 'ALM-TEST' RETURNING id;\n\n-- Verificar los registros de auditoría\nSELECT \n    id,\n    to_char(timestamp_log, 'YYYY-MM-DD HH24:MI:SS') as fecha_hora,\n    nombre_tabla,\n    operacion,\n    usuario_db as usuario,\n    id_entidad\nFROM public.auditoria_log\nWHERE nombre_tabla = 'almacenes'\nORDER BY timestamp_log DESC\nLIMIT 5;
5	2025-05-19 13:42:18.867633-05	public	almacenes	INSERT	postgres	\N	\N	\N	\N	7ba80f86-477e-48b5-b6fe-2cd7f3b72260	\N	{"id": "7ba80f86-477e-48b5-b6fe-2cd7f3b72260", "tipo": null, "activo": true, "codigo": "ALM-PRUEBA", "nombre": "Almacén de Prueba", "creado_en": "2025-05-19T13:42:18.867633-05:00", "direccion": "Calle Falsa 123", "creado_por": null, "actualizado_en": null, "actualizado_por": null}	{"id": "7ba80f86-477e-48b5-b6fe-2cd7f3b72260", "tipo": null, "activo": true, "codigo": "ALM-PRUEBA", "nombre": "Almacén de Prueba", "creado_en": "2025-05-19T13:42:18.867633-05:00", "direccion": "Calle Falsa 123", "creado_por": null, "actualizado_en": null, "actualizado_por": null}	{"client_addr": "127.0.0.1/32", "application_name": "psql"}	INSERT INTO almacenes (codigo, nombre, direccion, activo) VALUES ('ALM-PRUEBA', 'Almacén de Prueba', 'Calle Falsa 123', true) RETURNING id;
6	2025-05-19 13:42:18.867633-05	public	almacenes	INSERT	postgres	\N	\N	\N	\N	7ba80f86-477e-48b5-b6fe-2cd7f3b72260	\N	{"id": "7ba80f86-477e-48b5-b6fe-2cd7f3b72260", "tipo": null, "activo": true, "codigo": "ALM-PRUEBA", "nombre": "Almacén de Prueba", "creado_en": "2025-05-19T13:42:18.867633-05:00", "direccion": "Calle Falsa 123", "creado_por": null, "actualizado_en": null, "actualizado_por": null}	{"id": "7ba80f86-477e-48b5-b6fe-2cd7f3b72260", "tipo": null, "activo": true, "codigo": "ALM-PRUEBA", "nombre": "Almacén de Prueba", "creado_en": "2025-05-19T13:42:18.867633-05:00", "direccion": "Calle Falsa 123", "creado_por": null, "actualizado_en": null, "actualizado_por": null}	{"client_addr": "127.0.0.1/32", "application_name": "psql"}	INSERT INTO almacenes (codigo, nombre, direccion, activo) VALUES ('ALM-PRUEBA', 'Almacén de Prueba', 'Calle Falsa 123', true) RETURNING id;
7	2025-05-19 14:34:58.93076-05	public	roles	INSERT	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000999	\N	{"id": "00000000-0000-0000-0000-000000000999", "nombre": "Rol de Prueba", "creado_en": "2025-05-19T14:34:58.93076-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "descripcion": "Rol para probar la auditoría", "actualizado_en": null, "es_rol_sistema": false, "actualizado_por": null}	{"id": "00000000-0000-0000-0000-000000000999", "nombre": "Rol de Prueba", "creado_en": "2025-05-19T14:34:58.93076-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "descripcion": "Rol para probar la auditoría", "actualizado_en": null, "es_rol_sistema": false, "actualizado_por": null}	{"client_addr": "127.0.0.1/32", "application_name": "psql"}	\n-- Verificar estructura de la tabla roles\nSELECT \n    column_name, \n    data_type, \n    is_nullable, \n    column_default\nFROM \n    information_schema.columns\nWHERE \n    table_schema = 'public' \n    AND table_name = 'roles'\nORDER BY \n    ordinal_position;\n\n-- Crear un nuevo rol de prueba\nINSERT INTO roles (id, nombre, descripcion, creado_por)\nSELECT \n    '00000000-0000-0000-0000-000000000999'::uuid,\n    'Rol de Prueba',\n    'Rol para probar la auditoría',\n    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'  -- ID de usuario existente\nWHERE NOT EXISTS (\n    SELECT 1 FROM roles WHERE id = '00000000-0000-0000-0000-000000000999'\n);\n\n-- Verificar el rol creado\nSELECT * FROM roles WHERE nombre = 'Rol de Prueba';\n\n-- Asignar un permiso al nuevo rol\nINSERT INTO roles_permisos (rol_id, permiso_id, asignado_en, asignado_por)\nSELECT \n    '00000000-0000-0000-0000-000000000999' as rol_id,\n    p.id as permiso_id,\n    NOW() as asignado_en,\n    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12' as asignado_por\nFROM \n    permisos p\nWHERE \n    p.id = '00000000-0000-0000-0001-000000000001'  -- Un permiso de ejemplo\n    AND NOT EXISTS (\n        SELECT 1 \n        FROM roles_permisos \n        WHERE rol_id = '00000000-0000-0000-0000-000000000999' \n        AND permiso_id = p.id\n    )\nLIMIT 1;\n\n-- Verificar los registros de auditoría\nSELECT \n    timestamp_log,\n    nombre_tabla,\n    operacion,\n    id_entidad,\n    usuario_db,\n    LEFT(query_ejecutada, 100) as query,\n    jsonb_pretty(datos_nuevos) as datos_nuevos,\n    jsonb_pretty(datos_antiguos) as datos_antiguos,\n    jsonb_pretty(cambios) as cambios\nFROM \n    public.auditoria_log\nWHERE \n    nombre_tabla IN ('roles_permisos', 'roles')\nORDER BY \n    timestamp_log DESC\nLIMIT 10;
28	2025-05-19 15:17:00.969862-05	public	roles_permisos	INSERT	postgres	\N	\N	\N	\N	fec1ccea-481f-a39f-3efe-37a0999140f4	{}	{"rol_id": "00000000-0000-0000-0000-000000000005", "permiso_id": "00000000-0000-0000-0001-000000000005", "asignado_en": "2025-05-19T15:17:00.969862-05:00", "asignado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12"}	{"status": "audit-simple"}	{"timestamp": "2025-05-19 15:17:00.969862-05", "current_user": "postgres", "session_user": "postgres", "current_database": "ges_neu_bd"}	\n-- Función de auditoría simplificada\nCREATE OR REPLACE FUNCTION public.auditoria_simple()\nRETURNS TRIGGER\nLANGUAGE plpgsql\nAS $$\nDECLARE\n    v_operation TEXT := TG_OP;\n    v_table_name TEXT := TG_TABLE_NAME;\n    v_schema_name TEXT := TG_TABLE_SCHEMA;\n    v_user_name TEXT := session_user;\n    v_query TEXT := current_query();\n    v_record_id TEXT;\n    v_old_data JSONB;\n    v_new_data JSONB;\nBEGIN\n    -- Obtener los datos antiguos y nuevos\n    IF v_operation = 'DELETE' THEN\n        v_old_data := to_jsonb(OLD);\n        v_new_data := '{}'::jsonb;\n        v_record_id := md5((OLD).rol_id::text || (OLD).permiso_id::text);\n    ELSIF v_operation = 'UPDATE' THEN\n        v_old_data := to_jsonb(OLD);\n        v_new_data := to_jsonb(NEW);\n        v_record_id := md5((NEW).rol_id::text || (NEW).permiso_id::text);\n    ELSE -- INSERT\n        v_old_data := '{}'::jsonb;\n        v_new_data := to_jsonb(NEW);\n        v_record_id := md5((NEW).rol_id::text || (NEW).permiso_id::text);\n    END IF;\n    \n    -- Insertar un registro de auditoría\n    INSERT INTO public.auditoria_log (\n        esquema_tabla,\n        nombre_tabla,\n        operacion,\n        usuario_db,\n        id_entidad,\n        query_ejecutada,\n        datos_nuevos,\n        datos_antiguos,\n        cambios,\n        contexto_aplicacion\n    ) VALUES (\n        v_schema_name,\n        v_table_name,\n        v_operation,\n        v_user_name,\n        v_record_id::uuid,\n        v_query,\n        v_new_data,\n        v_old_data,\n        jsonb_build_object('status', 'audit-simple'),\n        jsonb_build_object(\n            'timestamp', NOW()::text,\n            'session_user', session_user,\n            'current_user', current_user,\n            'current_database', current_database()\n        )\n    );\n\n    -- Devolver el registro apropiado\n    IF v_operation = 'DELETE' THEN\n        RETURN OLD;\n    ELSE\n        RETURN NEW;\n    END IF;\nEXCEPTION WHEN OTHERS THEN\n    -- Registrar el error en la tabla de auditoría\n    INSERT INTO public.auditoria_log (\n        esquema_tabla,\n        nombre_tabla,\n        operacion,\n        usuario_db,\n        query_ejecutada,\n        datos_nuevos,\n        contexto_aplicacion\n    ) VALUES (\n        v_schema_name,\n        v_table_name,\n        'ERROR',\n        v_user_name,\n        v_query,\n        jsonb_build_object(\n            'error', SQLERRM,\n            'sqlstate', SQLSTATE\n        ),\n        jsonb_build_object(\n            'context', 'Error en auditoría simplificada',\n            'error_detail', SQLERRM,\n            'operation', v_operation,\n            'table', v_schema_name || '.' || v_table_name\n        )\n    );\n    \n    -- Relanzar el error original\n    RAISE WARNING 'Error en auditoría simplificada: %', SQLERRM;\n    \n    -- Devolver el registro apropiado según la operación\n    IF v_operation = 'DELETE' THEN\n        RETURN OLD;\n    ELSE\n        RETURN NEW;\n    END IF;\nEND;\n$$;\n\n-- Actualizar el disparador\nDROP TRIGGER IF EXISTS tr_auditoria_simple_roles_permisos ON public.roles_permisos;\n\nCREATE TRIGGER tr_auditoria_simple_roles_permisos\nAFTER INSERT OR UPDATE OR DELETE ON public.roles_permisos\nFOR EACH ROW EXECUTE FUNCTION public.auditoria_simple();\n\n-- Verificar que el disparador se creó correctamente\nSELECT \n    tgname AS trigger_name,\n    tgenabled AS status,\n    CASE tgenabled\n        WHEN 'O' THEN 'ENABLED'\n        WHEN 'D' THEN 'DISABLED'\n        WHEN 'R' THEN 'REPLICA'\n        WHEN 'A' THEN 'ALWAYS'\n    END AS status_description,\n    pg_get_triggerdef(oid) AS definition\nFROM \n    pg_trigger\nWHERE \n    tgrelid = 'public.roles_permisos'::regclass\n    AND tgname = 'tr_auditoria_simple_roles_permisos';\n\n-- Realizar una inserción de prueba\nINSERT INTO public.roles_permisos (\n    rol_id,\n    permiso_id,\n    asignado_en,\n    asignado_por\n) VALUES (\n    '00000000-0000-0000-0000-000000000005',  -- Rol de Consulta\n    '00000000-0000-0000-0001-000000000005',  -- Permiso de cambiar estado de usuarios\n    NOW(),\n    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'   -- Usuario existente\n) ON CONFLICT (rol_id, permiso_id) DO NOTHING;\n\n-- Verificar los registros de auditoría\nSELECT \n    id,\n    timestamp_log,\n    nombre_tabla,\n    operacion,\n    id_entidad,\n    usuario_db,\n    LEFT(COALESCE(query_ejecutada, ''), 100) as query,\n    jsonb_pretty(COALESCE(datos_nuevos, '{}'::jsonb)) as datos_nuevos,\n    jsonb_pretty(COALESCE(datos_antiguos, '{}'::jsonb)) as datos_antiguos,\n    jsonb_pretty(COALESCE(cambios, '{}'::jsonb)) as cambios,\n    jsonb_pretty(COALESCE(contexto_aplicacion, '{}'::jsonb)) as contexto\nFROM \n    public.auditoria_log\nWHERE \n    nombre_tabla = 'roles_permisos'\n    AND timestamp_log > NOW() - INTERVAL '15 minutes'\nORDER BY \n    timestamp_log DESC\nLIMIT 5;
34	2025-05-19 15:29:05.64206-05	public	roles_permisos	INSERT	postgres	\N	\N	\N	\N	fec1ccea-481f-a39f-3efe-37a0999140f4	{}	{"rol_id": "00000000-0000-0000-0000-000000000005", "permiso_id": "00000000-0000-0000-0001-000000000005", "asignado_en": "2025-05-19T15:29:05.64206-05:00", "asignado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12"}	{"status": "audit-simple"}	{"timestamp": "2025-05-19 15:29:05.64206-05", "current_user": "postgres", "session_user": "postgres", "current_database": "ges_neu_bd"}	\n-- 1. Verificar el estado actual de roles_permisos\nSELECT * FROM public.roles_permisos \nWHERE rol_id = '00000000-0000-0000-0000-000000000005' \nAND permiso_id = '00000000-0000-0000-0001-000000000005';\n\n-- 2. Insertar un nuevo registro de prueba\nINSERT INTO public.roles_permisos (\n    rol_id,\n    permiso_id,\n    asignado_en,\n    asignado_por\n) VALUES (\n    '00000000-0000-0000-0000-000000000005',  -- Rol de Consulta\n    '00000000-0000-0000-0001-000000000005',  -- Permiso de cambiar estado de usuarios\n    NOW(),\n    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'   -- Usuario existente\n) ON CONFLICT (rol_id, permiso_id) DO NOTHING;\n\n-- 3. Verificar la auditoría después de la inserción\nSELECT \n    id,\n    timestamp_log,\n    operacion,\n    usuario_db,\n    jsonb_pretty(datos_nuevos) as datos_nuevos\nFROM \n    public.auditoria_log\nWHERE \n    nombre_tabla = 'roles_permisos'\n    AND timestamp_log > NOW() - INTERVAL '1 hour'\nORDER BY \n    timestamp_log DESC\nLIMIT 5;
37	2025-05-19 15:33:09.737394-05	public	roles_permisos	UPDATE	postgres	\N	\N	\N	\N	fec1ccea-481f-a39f-3efe-37a0999140f4	{"rol_id": "00000000-0000-0000-0000-000000000005", "permiso_id": "00000000-0000-0000-0001-000000000005", "asignado_en": "2025-05-19T15:29:05.64206-05:00", "asignado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12"}	{"rol_id": "00000000-0000-0000-0000-000000000005", "permiso_id": "00000000-0000-0000-0001-000000000005", "asignado_en": "2025-05-19T15:29:05.64206-05:00", "asignado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12"}	{"status": "audit-simple"}	{"timestamp": "2025-05-19 15:33:09.737394-05", "current_user": "postgres", "session_user": "postgres", "current_database": "ges_neu_bd"}	\n-- 1. Prueba de Actualización\nUPDATE public.roles_permisos\nSET asignado_por = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'  -- Usar el ID de usuario existente\nWHERE rol_id = '00000000-0000-0000-0000-000000000005'\nAND permiso_id = '00000000-0000-0000-0001-000000000005';\n\n-- Verificar la auditoría después de la actualización\nSELECT \n    id,\n    timestamp_log,\n    operacion,\n    usuario_db,\n    jsonb_pretty(datos_antiguos) as datos_antiguos,\n    jsonb_pretty(datos_nuevos) as datos_nuevos\nFROM \n    public.auditoria_log\nWHERE \n    nombre_tabla = 'roles_permisos'\nORDER BY \n    timestamp_log DESC\nLIMIT 5;\n\n-- 2. Prueba de Eliminación\nDELETE FROM public.roles_permisos\nWHERE rol_id = '00000000-0000-0000-0000-000000000005'\nAND permiso_id = '00000000-0000-0000-0001-000000000005';\n\n-- Verificar la auditoría después de la eliminación\nSELECT \n    id,\n    timestamp_log,\n    operacion,\n    usuario_db,\n    jsonb_pretty(datos_antiguos) as datos_antiguos\nFROM \n    public.auditoria_log\nWHERE \n    nombre_tabla = 'roles_permisos'\nORDER BY \n    timestamp_log DESC\nLIMIT 5;
40	2025-05-19 15:33:09.737394-05	public	roles_permisos	DELETE	postgres	\N	\N	\N	\N	fec1ccea-481f-a39f-3efe-37a0999140f4	{"rol_id": "00000000-0000-0000-0000-000000000005", "permiso_id": "00000000-0000-0000-0001-000000000005", "asignado_en": "2025-05-19T15:29:05.64206-05:00", "asignado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12"}	{}	{"status": "audit-simple"}	{"timestamp": "2025-05-19 15:33:09.737394-05", "current_user": "postgres", "session_user": "postgres", "current_database": "ges_neu_bd"}	\n-- 1. Prueba de Actualización\nUPDATE public.roles_permisos\nSET asignado_por = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'  -- Usar el ID de usuario existente\nWHERE rol_id = '00000000-0000-0000-0000-000000000005'\nAND permiso_id = '00000000-0000-0000-0001-000000000005';\n\n-- Verificar la auditoría después de la actualización\nSELECT \n    id,\n    timestamp_log,\n    operacion,\n    usuario_db,\n    jsonb_pretty(datos_antiguos) as datos_antiguos,\n    jsonb_pretty(datos_nuevos) as datos_nuevos\nFROM \n    public.auditoria_log\nWHERE \n    nombre_tabla = 'roles_permisos'\nORDER BY \n    timestamp_log DESC\nLIMIT 5;\n\n-- 2. Prueba de Eliminación\nDELETE FROM public.roles_permisos\nWHERE rol_id = '00000000-0000-0000-0000-000000000005'\nAND permiso_id = '00000000-0000-0000-0001-000000000005';\n\n-- Verificar la auditoría después de la eliminación\nSELECT \n    id,\n    timestamp_log,\n    operacion,\n    usuario_db,\n    jsonb_pretty(datos_antiguos) as datos_antiguos\nFROM \n    public.auditoria_log\nWHERE \n    nombre_tabla = 'roles_permisos'\nORDER BY \n    timestamp_log DESC\nLIMIT 5;
92	2025-05-19 18:44:52.035511-05	public	motivos_desecho	DELETE	postgres	\N	admin	192.168.1.100	\N	770c0fb7-1c5a-4280-847d-2a32208a6c5b	{"id": "770c0fb7-1c5a-4280-847d-2a32208a6c5b", "deleted_at": "2025-05-19T18:44:52.035511-05:00"}	\N	\N	\N	\N
64	2025-05-19 17:13:20.503477-05	public	modelos_neumatico	UPDATE	postgres	\N	admin	192.168.1.100	\N	aed63bc0-a774-4463-9b30-cdf674df29d9	\N	\N	{"nombre_modelo": {"new": "[TEST] Modelo Prueba (Actualizado)", "old": "[TEST] Modelo Prueba"}, "reencauches_maximos": {"new": "4", "old": "3"}, "presion_recomendada_psi": {"new": "105.00", "old": "100.00"}}	\N	\N
65	2025-05-19 17:13:20.503477-05	public	modelos_neumatico	DELETE	postgres	\N	admin	192.168.1.100	\N	aed63bc0-a774-4463-9b30-cdf674df29d9	{"id": "aed63bc0-a774-4463-9b30-cdf674df29d9", "deleted_at": "2025-05-19T17:13:20.503477-05:00"}	\N	\N	\N	\N
59	2025-05-19 17:06:31.71471-05	public	fabricantes_neumatico	INSERT	postgres	\N	admin	192.168.1.100	\N	59e870c7-e27a-4973-bc3c-c35db97926d7	\N	{"id": "59e870c7-e27a-4973-bc3c-c35db97926d7", "created_at": "2025-05-19T17:06:31.71471-05:00"}	\N	\N	\N
60	2025-05-19 17:06:31.717958-05	public	fabricantes_neumatico	UPDATE	postgres	\N	admin	192.168.1.100	\N	59e870c7-e27a-4973-bc3c-c35db97926d7	\N	\N	{"nombre": {"new": "[TEST] Fabricante de Prueba (Actualizado)", "old": "[TEST] Fabricante de Prueba"}, "pais_origen": {"new": "México", "old": "Perú"}}	\N	\N
61	2025-05-19 17:06:31.719992-05	public	fabricantes_neumatico	UPDATE	postgres	\N	admin	192.168.1.100	\N	59e870c7-e27a-4973-bc3c-c35db97926d7	\N	\N	{"activo": {"new": "false", "old": "true"}}	\N	\N
62	2025-05-19 17:06:31.721624-05	public	fabricantes_neumatico	DELETE	postgres	\N	admin	192.168.1.100	\N	59e870c7-e27a-4973-bc3c-c35db97926d7	{"id": "59e870c7-e27a-4973-bc3c-c35db97926d7", "deleted_at": "2025-05-19T17:06:31.721624-05:00"}	\N	\N	\N	\N
63	2025-05-19 17:13:20.503477-05	public	modelos_neumatico	INSERT	postgres	\N	admin	192.168.1.100	\N	aed63bc0-a774-4463-9b30-cdf674df29d9	\N	{"id": "aed63bc0-a774-4463-9b30-cdf674df29d9", "created_at": "2025-05-19T17:13:20.503477-05:00"}	\N	\N	\N
91	2025-05-19 18:44:52.035511-05	public	motivos_desecho	UPDATE	postgres	\N	admin	192.168.1.100	\N	770c0fb7-1c5a-4280-847d-2a32208a6c5b	\N	\N	{"activo": {"new": "false", "old": "true"}}	\N	\N
76	2025-05-19 18:30:06.25038-05	public	modelos_posiciones_permitidas	INSERT	postgres	\N	admin	192.168.1.100	\N	\N	\N	{"creado_en": "2025-05-19T18:30:06.25038-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "created_at": "2025-05-19T18:30:06.25038-05:00", "es_recomendado": true, "modelo_neumatico_id": "00000000-0000-0000-0000-000000000001", "posicion_neumatico_id": "00000000-0000-0000-0000-000000000001"}	\N	\N	\N
77	2025-05-19 18:30:06.25038-05	public	modelos_posiciones_permitidas	UPDATE	postgres	\N	admin	192.168.1.100	\N	\N	\N	\N	{"es_recomendado": {"new": "false", "old": "true"}}	\N	\N
78	2025-05-19 18:30:06.25038-05	public	modelos_posiciones_permitidas	DELETE	postgres	\N	admin	192.168.1.100	\N	\N	{"creado_en": "2025-05-19T18:30:06.25038-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "deleted_at": "2025-05-19T18:30:06.25038-05:00", "es_recomendado": false, "modelo_neumatico_id": "00000000-0000-0000-0000-000000000001", "posicion_neumatico_id": "00000000-0000-0000-0000-000000000001"}	\N	\N	\N	\N
79	2025-05-19 18:32:51.638423-05	public	motivos_desecho	INSERT	postgres	\N	admin	192.168.1.100	\N	306a3fdf-855e-4f48-9fbe-e5fab2e7125b	\N	{"id": "306a3fdf-855e-4f48-9fbe-e5fab2e7125b", "created_at": "2025-05-19T18:32:51.638423-05:00"}	\N	\N	\N
80	2025-05-19 18:32:51.638423-05	public	motivos_desecho	UPDATE	postgres	\N	admin	192.168.1.100	\N	306a3fdf-855e-4f48-9fbe-e5fab2e7125b	\N	\N	{"descripcion": {"new": "Motivo de prueba actualizado", "old": "Motivo de prueba para auditoría"}, "requiere_evidencia": {"new": "false", "old": "true"}}	\N	\N
81	2025-05-19 18:32:51.638423-05	public	motivos_desecho	UPDATE	postgres	\N	admin	192.168.1.100	\N	306a3fdf-855e-4f48-9fbe-e5fab2e7125b	\N	\N	{"activo": {"new": "false", "old": "true"}}	\N	\N
82	2025-05-19 18:32:51.638423-05	public	motivos_desecho	DELETE	postgres	\N	admin	192.168.1.100	\N	306a3fdf-855e-4f48-9fbe-e5fab2e7125b	{"id": "306a3fdf-855e-4f48-9fbe-e5fab2e7125b", "deleted_at": "2025-05-19T18:32:51.638423-05:00"}	\N	\N	\N	\N
89	2025-05-19 18:44:52.035511-05	public	motivos_desecho	INSERT	postgres	\N	admin	192.168.1.100	\N	770c0fb7-1c5a-4280-847d-2a32208a6c5b	\N	{"id": "770c0fb7-1c5a-4280-847d-2a32208a6c5b", "created_at": "2025-05-19T18:44:52.035511-05:00"}	\N	\N	\N
90	2025-05-19 18:44:52.035511-05	public	motivos_desecho	UPDATE	postgres	\N	admin	192.168.1.100	\N	770c0fb7-1c5a-4280-847d-2a32208a6c5b	\N	\N	{"descripcion": {"new": "Motivo de prueba actualizado", "old": "Motivo de prueba para auditoría"}, "requiere_evidencia": {"new": "false", "old": "true"}}	\N	\N
94	2025-05-19 21:44:38.282601-05	public	modelos_neumatico	INSERT	postgres	\N	\N	\N	\N	51bec9d7-c28c-4273-a79e-f9388e54130f	\N	{"id": "51bec9d7-c28c-4273-a79e-f9388e54130f", "medida": "295/80R22.5", "creado_en": "2025-05-19T21:44:38.282601-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "indice_carga": null, "fabricante_id": "00000000-0000-0000-0000-000000000001", "nombre_modelo": "X-MULTI Z", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": null, "indice_velocidad": null, "permite_reencauche": false, "reencauches_maximos": 0, "presion_recomendada_psi": null, "profundidad_original_mm": 15.00, "posicion_uso_recomendada": "DIRECCION"}	\N	\N	DO $$\nDECLARE\n    v_modelo_xmultiz_id UUID;\n    v_modelo_xmultid2_id UUID;\n    v_admin_id UUID;\nBEGIN\n    -- Obtener ID del administrador\n    SELECT id INTO v_admin_id FROM public.usuarios WHERE username = 'admin' LIMIT 1;\n    \n    -- Verificar si el modelo XMULTIZ existe, si no, crearlo\n    SELECT id INTO v_modelo_xmultiz_id \n    FROM public.modelos_neumatico \n    WHERE nombre_modelo ILIKE '%X-MULTI Z%' OR nombre_modelo ILIKE '%XMULTIZ%' \n    LIMIT 1;\n    \n    IF v_modelo_xmultiz_id IS NULL THEN\n        -- Insertar el modelo XMULTIZ\n        INSERT INTO public.modelos_neumatico (\n            fabricante_id, \n            nombre_modelo, \n            medida, \n            profundidad_original_mm,\n            posicion_uso_recomendada,\n            creado_por\n        ) VALUES (\n            (SELECT id FROM public.fabricantes_neumatico WHERE nombre = 'Michelin' LIMIT 1),\n            'X-MULTI Z',\n            '295/80R22.5',\n            15.0,\n            'DIRECCION',\n            v_admin_id\n        ) RETURNING id INTO v_modelo_xmultiz_id;\n        \n        RAISE NOTICE 'Modelo X-MULTI Z creado con ID: %', v_modelo_xmultiz_id;\n    END IF;\n    \n    -- Verificar si el modelo XMULTID2 existe, si no, crearlo\n    SELECT id INTO v_modelo_xmultid2_id \n    FROM public.modelos_neumatico \n    WHERE nombre_modelo ILIKE '%X-MULTI D2%' OR nombre_modelo ILIKE '%XMULTID2%' \n    LIMIT 1;\n    \n    IF v_modelo_xmultid2_id IS NULL THEN\n        -- Insertar el modelo XMULTID2\n        INSERT INTO public.modelos_neumatico (\n            fabricante_id, \n            nombre_modelo, \n            medida, \n            profundidad_original_mm,\n            posicion_uso_recomendada,\n            creado_por\n        ) VALUES (\n            (SELECT id FROM public.fabricantes_neumatico WHERE nombre = 'Michelin' LIMIT 1),\n            'X-MULTI D2',\n            '295/80R22.5',\n            15.0,\n            'TRACCION',\n            v_admin_id\n        ) RETURNING id INTO v_modelo_xmultid2_id;\n        \n        RAISE NOTICE 'Modelo X-MULTI D2 creado con ID: %', v_modelo_xmultid2_id;\n    END IF;\n    \n    -- Insertar parámetros de rendimiento para XMULTIZ (posición delantera)\n    INSERT INTO public.parametros_rendimiento_esperado_modelo (\n        modelo_id,\n        tipo_eje_aplicacion,\n        km_esperado_vida_original_min,\n        km_esperado_vida_original_max,\n        notas,\n        creado_por\n    ) VALUES (\n        v_modelo_xmultiz_id,\n        'DIRECCION',\n        60000,\n        100000,\n        'Vida útil esperada para posición delantera',\n        v_admin_id\n    ) ON CONFLICT (modelo_id, tipo_eje_aplicacion) DO NOTHING;\n    \n    -- Insertar parámetros de rendimiento para XMULTID2 (posición de tracción)\n    INSERT INTO public.parametros_rendimiento_esperado_modelo (\n        modelo_id,\n        tipo_eje_aplicacion,\n        km_esperado_vida_original_min,\n        km_esperado_vida_original_max,\n        notas,\n        creado_por\n    ) VALUES (\n        v_modelo_xmultid2_id,\n        'TRACCION',\n        100000,\n        120000,\n        'Vida útil esperada para posición de tracción',\n        v_admin_id\n    ) ON CONFLICT (modelo_id, tipo_eje_aplicacion) DO NOTHING;\n    \nEXCEPTION WHEN OTHERS THEN\n    RAISE WARNING 'Error al insertar datos de ejemplo: %', SQLERRM;\nEND $$;
95	2025-05-19 21:44:38.282601-05	public	modelos_neumatico	INSERT	postgres	\N	\N	\N	\N	55f58bfd-2dfb-4bdb-b9b6-1b3da75a867e	\N	{"id": "55f58bfd-2dfb-4bdb-b9b6-1b3da75a867e", "medida": "295/80R22.5", "creado_en": "2025-05-19T21:44:38.282601-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "indice_carga": null, "fabricante_id": "00000000-0000-0000-0000-000000000001", "nombre_modelo": "X-MULTI D2", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": null, "indice_velocidad": null, "permite_reencauche": false, "reencauches_maximos": 0, "presion_recomendada_psi": null, "profundidad_original_mm": 15.00, "posicion_uso_recomendada": "TRACCION"}	\N	\N	DO $$\nDECLARE\n    v_modelo_xmultiz_id UUID;\n    v_modelo_xmultid2_id UUID;\n    v_admin_id UUID;\nBEGIN\n    -- Obtener ID del administrador\n    SELECT id INTO v_admin_id FROM public.usuarios WHERE username = 'admin' LIMIT 1;\n    \n    -- Verificar si el modelo XMULTIZ existe, si no, crearlo\n    SELECT id INTO v_modelo_xmultiz_id \n    FROM public.modelos_neumatico \n    WHERE nombre_modelo ILIKE '%X-MULTI Z%' OR nombre_modelo ILIKE '%XMULTIZ%' \n    LIMIT 1;\n    \n    IF v_modelo_xmultiz_id IS NULL THEN\n        -- Insertar el modelo XMULTIZ\n        INSERT INTO public.modelos_neumatico (\n            fabricante_id, \n            nombre_modelo, \n            medida, \n            profundidad_original_mm,\n            posicion_uso_recomendada,\n            creado_por\n        ) VALUES (\n            (SELECT id FROM public.fabricantes_neumatico WHERE nombre = 'Michelin' LIMIT 1),\n            'X-MULTI Z',\n            '295/80R22.5',\n            15.0,\n            'DIRECCION',\n            v_admin_id\n        ) RETURNING id INTO v_modelo_xmultiz_id;\n        \n        RAISE NOTICE 'Modelo X-MULTI Z creado con ID: %', v_modelo_xmultiz_id;\n    END IF;\n    \n    -- Verificar si el modelo XMULTID2 existe, si no, crearlo\n    SELECT id INTO v_modelo_xmultid2_id \n    FROM public.modelos_neumatico \n    WHERE nombre_modelo ILIKE '%X-MULTI D2%' OR nombre_modelo ILIKE '%XMULTID2%' \n    LIMIT 1;\n    \n    IF v_modelo_xmultid2_id IS NULL THEN\n        -- Insertar el modelo XMULTID2\n        INSERT INTO public.modelos_neumatico (\n            fabricante_id, \n            nombre_modelo, \n            medida, \n            profundidad_original_mm,\n            posicion_uso_recomendada,\n            creado_por\n        ) VALUES (\n            (SELECT id FROM public.fabricantes_neumatico WHERE nombre = 'Michelin' LIMIT 1),\n            'X-MULTI D2',\n            '295/80R22.5',\n            15.0,\n            'TRACCION',\n            v_admin_id\n        ) RETURNING id INTO v_modelo_xmultid2_id;\n        \n        RAISE NOTICE 'Modelo X-MULTI D2 creado con ID: %', v_modelo_xmultid2_id;\n    END IF;\n    \n    -- Insertar parámetros de rendimiento para XMULTIZ (posición delantera)\n    INSERT INTO public.parametros_rendimiento_esperado_modelo (\n        modelo_id,\n        tipo_eje_aplicacion,\n        km_esperado_vida_original_min,\n        km_esperado_vida_original_max,\n        notas,\n        creado_por\n    ) VALUES (\n        v_modelo_xmultiz_id,\n        'DIRECCION',\n        60000,\n        100000,\n        'Vida útil esperada para posición delantera',\n        v_admin_id\n    ) ON CONFLICT (modelo_id, tipo_eje_aplicacion) DO NOTHING;\n    \n    -- Insertar parámetros de rendimiento para XMULTID2 (posición de tracción)\n    INSERT INTO public.parametros_rendimiento_esperado_modelo (\n        modelo_id,\n        tipo_eje_aplicacion,\n        km_esperado_vida_original_min,\n        km_esperado_vida_original_max,\n        notas,\n        creado_por\n    ) VALUES (\n        v_modelo_xmultid2_id,\n        'TRACCION',\n        100000,\n        120000,\n        'Vida útil esperada para posición de tracción',\n        v_admin_id\n    ) ON CONFLICT (modelo_id, tipo_eje_aplicacion) DO NOTHING;\n    \nEXCEPTION WHEN OTHERS THEN\n    RAISE WARNING 'Error al insertar datos de ejemplo: %', SQLERRM;\nEND $$;
96	2025-05-19 22:41:52.537336-05	public	tipos_ruta	INSERT	postgres	\N	\N	\N	\N	bbc286cb-2a60-497e-b50e-30e3ba22598f	\N	{"id": "bbc286cb-2a60-497e-b50e-30e3ba22598f", "creado_en": "2025-05-19T22:41:52.537336-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "descripcion": "Ruta de prueba para verificar auditoría", "nombre_ruta": "RUTA_PRUEBA_AUDITORIA", "actualizado_en": null, "actualizado_por": null, "distancia_total_km_ciclo": 100.50, "distancia_trocha_km_ciclo": 30.25, "distancia_asfalto_km_ciclo": 70.25, "porcentaje_promedio_con_carga": 75.00, "distancia_otro_terreno_km_ciclo": 0.00}	\N	\N	\N
97	2025-05-19 22:42:11.40623-05	public	tipos_ruta	UPDATE	postgres	\N	\N	\N	\N	bbc286cb-2a60-497e-b50e-30e3ba22598f	{"id": "bbc286cb-2a60-497e-b50e-30e3ba22598f", "creado_en": "2025-05-19T22:41:52.537336-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "descripcion": "Ruta de prueba para verificar auditoría", "nombre_ruta": "RUTA_PRUEBA_AUDITORIA", "actualizado_en": null, "actualizado_por": null, "distancia_total_km_ciclo": 100.50, "distancia_trocha_km_ciclo": 30.25, "distancia_asfalto_km_ciclo": 70.25, "porcentaje_promedio_con_carga": 75.00, "distancia_otro_terreno_km_ciclo": 0.00}	{"id": "bbc286cb-2a60-497e-b50e-30e3ba22598f", "creado_en": "2025-05-19T22:41:52.537336-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "descripcion": "Ruta de prueba para verificar auditoría (actualizada)", "nombre_ruta": "RUTA_PRUEBA_AUDITORIA", "actualizado_en": null, "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "distancia_total_km_ciclo": 100.50, "distancia_trocha_km_ciclo": 30.25, "distancia_asfalto_km_ciclo": 70.25, "porcentaje_promedio_con_carga": 80.00, "distancia_otro_terreno_km_ciclo": 0.00}	{"descripcion": "Ruta de prueba para verificar auditoría (actualizada)", "porcentaje_promedio_con_carga": "80.00"}	\N	\N
98	2025-05-19 22:43:15.627476-05	public	parametros_rendimiento_esperado_modelo	UPDATE	postgres	\N	\N	\N	\N	633a39bf-fd5c-4e4e-9cbd-354f484edbe1	{"id": "633a39bf-fd5c-4e4e-9cbd-354f484edbe1", "notas": "Parámetros actualizados después de revisión", "creado_en": "2025-05-19T22:17:28.423587-05:00", "modelo_id": "51bec9d7-c28c-4273-a79e-f9388e54130f", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": "2025-05-19T22:30:39.20287-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "tipo_eje_aplicacion": "DIRECCION", "km_esperado_vida_original_max": 125000, "km_esperado_vida_original_min": 85000}	{"id": "633a39bf-fd5c-4e4e-9cbd-354f484edbe1", "notas": "Parámetro actualizado para prueba de auditoría", "creado_en": "2025-05-19T22:17:28.423587-05:00", "modelo_id": "51bec9d7-c28c-4273-a79e-f9388e54130f", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": "2025-05-19T22:30:39.20287-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "tipo_eje_aplicacion": "DIRECCION", "km_esperado_vida_original_max": 125000, "km_esperado_vida_original_min": 82000}	{"notas": "Parámetro actualizado para prueba de auditoría", "km_esperado_vida_original_min": "82000"}	\N	\N
99	2025-05-19 22:51:54.86388-05	public	tipos_ruta	DELETE	postgres	\N	\N	\N	\N	bbc286cb-2a60-497e-b50e-30e3ba22598f	{"id": "bbc286cb-2a60-497e-b50e-30e3ba22598f", "creado_en": "2025-05-19T22:41:52.537336-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "descripcion": "Ruta de prueba para verificar auditoría (actualizada)", "nombre_ruta": "RUTA_PRUEBA_AUDITORIA", "actualizado_en": null, "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "distancia_total_km_ciclo": 100.50, "distancia_trocha_km_ciclo": 30.25, "distancia_asfalto_km_ciclo": 70.25, "porcentaje_promedio_con_carga": 80.00, "distancia_otro_terreno_km_ciclo": 0.00}	\N	\N	\N	\N
100	2025-05-19 23:18:18.950347-05	public	parametros_inventario	INSERT	postgres	\N	\N	\N	\N	336f690f-2cea-42f6-afd8-bb5d055c363e	\N	{"id": "336f690f-2cea-42f6-afd8-bb5d055c363e", "notas": "Parámetro de prueba para auditoría", "activo": true, "creado_en": "2025-05-19T23:18:18.950347-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "valor_texto": "Stock mínimo para reorden", "actualizado_en": null, "parametro_tipo": "STOCK_MINIMO", "valor_numerico": 5.00, "actualizado_por": null, "ubicacion_almacen_id": "00000000-0000-0000-0000-000000000001"}	\N	\N	\N
101	2025-05-19 23:21:48.242584-05	public	parametros_inventario	UPDATE	postgres	\N	\N	\N	\N	336f690f-2cea-42f6-afd8-bb5d055c363e	{"id": "336f690f-2cea-42f6-afd8-bb5d055c363e", "notas": "Parámetro de prueba para auditoría", "activo": true, "creado_en": "2025-05-19T23:18:18.950347-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "valor_texto": "Stock mínimo para reorden", "actualizado_en": null, "parametro_tipo": "STOCK_MINIMO", "valor_numerico": 5.00, "actualizado_por": null, "ubicacion_almacen_id": "00000000-0000-0000-0000-000000000001"}	{"id": "336f690f-2cea-42f6-afd8-bb5d055c363e", "notas": "Parámetro actualizado para prueba de auditoría", "activo": true, "creado_en": "2025-05-19T23:18:18.950347-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "valor_texto": "Stock mínimo para reorden", "actualizado_en": null, "parametro_tipo": "STOCK_MINIMO", "valor_numerico": 7.50, "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "ubicacion_almacen_id": "00000000-0000-0000-0000-000000000001"}	{"notas": "Parámetro actualizado para prueba de auditoría", "valor_numerico": "7.50"}	\N	\N
102	2025-05-19 23:22:57.987049-05	public	parametros_inventario	DELETE	postgres	\N	\N	\N	\N	336f690f-2cea-42f6-afd8-bb5d055c363e	{"id": "336f690f-2cea-42f6-afd8-bb5d055c363e", "notas": "Parámetro actualizado para prueba de auditoría", "activo": true, "creado_en": "2025-05-19T23:18:18.950347-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "valor_texto": "Stock mínimo para reorden", "actualizado_en": null, "parametro_tipo": "STOCK_MINIMO", "valor_numerico": 7.50, "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "ubicacion_almacen_id": "00000000-0000-0000-0000-000000000001"}	\N	\N	\N	\N
112	2025-05-21 18:54:21.731185-05	public	parametros_rendimiento_esperado_modelo	INSERT	postgres	\N	\N	\N	\N	2aa5e2c1-d0ab-442b-84a6-bc42107cae3d	\N	{"id": "2aa5e2c1-d0ab-442b-84a6-bc42107cae3d", "notas": "Parámetro de prueba", "creado_en": "2025-05-21T18:54:21.733108-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": null, "actualizado_por": null, "tipo_eje_aplicacion": "DIRECCION", "km_esperado_vida_original_max": 120000, "km_esperado_vida_original_min": 80000}	\N	\N	\N
105	2025-05-21 18:41:04.021514-05	public	parametros_rendimiento_esperado_modelo	INSERT	postgres	\N	\N	\N	\N	bf3230b9-ea58-4381-bb6d-d720d90e6aea	\N	{"id": "bf3230b9-ea58-4381-bb6d-d720d90e6aea", "notas": "Parámetro de prueba", "creado_en": "2025-05-21T18:41:04.023721-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": null, "actualizado_por": null, "tipo_eje_aplicacion": "DIRECCION", "km_esperado_vida_original_max": 120000, "km_esperado_vida_original_min": 80000}	\N	\N	\N
106	2025-05-21 18:41:04.039286-05	public	parametros_rendimiento_esperado_modelo	UPDATE	postgres	\N	\N	\N	\N	bf3230b9-ea58-4381-bb6d-d720d90e6aea	{"id": "bf3230b9-ea58-4381-bb6d-d720d90e6aea", "notas": "Parámetro de prueba", "creado_en": "2025-05-21T18:41:04.023721-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": null, "actualizado_por": null, "tipo_eje_aplicacion": "DIRECCION", "km_esperado_vida_original_max": 120000, "km_esperado_vida_original_min": 80000}	{"id": "bf3230b9-ea58-4381-bb6d-d720d90e6aea", "notas": "Parámetro de prueba", "creado_en": "2025-05-21T18:41:04.023721-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": "2025-05-21T18:41:04.040232-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "tipo_eje_aplicacion": "DIRECCION", "km_esperado_vida_original_max": 130000, "km_esperado_vida_original_min": 80000}	{"km_esperado_vida_original_max": "130000"}	\N	\N
107	2025-05-21 18:41:04.04361-05	public	parametros_rendimiento_esperado_modelo	DELETE	postgres	\N	\N	\N	\N	bf3230b9-ea58-4381-bb6d-d720d90e6aea	{"id": "bf3230b9-ea58-4381-bb6d-d720d90e6aea", "notas": "Parámetro de prueba", "creado_en": "2025-05-21T18:41:04.023721-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": "2025-05-21T18:41:04.040232-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "tipo_eje_aplicacion": "DIRECCION", "km_esperado_vida_original_max": 130000, "km_esperado_vida_original_min": 80000}	\N	\N	\N	\N
108	2025-05-21 18:46:39.885472-05	public	parametros_rendimiento_esperado_modelo	INSERT	postgres	\N	\N	\N	\N	c4949874-2a20-4526-9308-6e193d872d52	\N	{"id": "c4949874-2a20-4526-9308-6e193d872d52", "notas": null, "creado_en": "2025-05-21T18:46:39.885472-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": null, "actualizado_por": null, "tipo_eje_aplicacion": "TRACCION", "km_esperado_vida_original_max": 150000, "km_esperado_vida_original_min": 100000}	\N	\N	\N
109	2025-05-21 18:50:17.388197-05	public	parametros_rendimiento_esperado_modelo	INSERT	postgres	\N	\N	\N	\N	470ee2f9-91a7-44b0-bec2-3f6378341347	\N	{"id": "470ee2f9-91a7-44b0-bec2-3f6378341347", "notas": "Parámetro de prueba", "creado_en": "2025-05-21T18:50:17.389936-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": null, "actualizado_por": null, "tipo_eje_aplicacion": "DIRECCION", "km_esperado_vida_original_max": 120000, "km_esperado_vida_original_min": 80000}	\N	\N	\N
110	2025-05-21 18:50:17.401757-05	public	parametros_rendimiento_esperado_modelo	UPDATE	postgres	\N	\N	\N	\N	470ee2f9-91a7-44b0-bec2-3f6378341347	{"id": "470ee2f9-91a7-44b0-bec2-3f6378341347", "notas": "Parámetro de prueba", "creado_en": "2025-05-21T18:50:17.389936-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": null, "actualizado_por": null, "tipo_eje_aplicacion": "DIRECCION", "km_esperado_vida_original_max": 120000, "km_esperado_vida_original_min": 80000}	{"id": "470ee2f9-91a7-44b0-bec2-3f6378341347", "notas": "Parámetro de prueba", "creado_en": "2025-05-21T18:50:17.389936-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": "2025-05-21T18:50:17.402643-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "tipo_eje_aplicacion": "DIRECCION", "km_esperado_vida_original_max": 130000, "km_esperado_vida_original_min": 80000}	{"km_esperado_vida_original_max": "130000"}	\N	\N
111	2025-05-21 18:50:17.405886-05	public	parametros_rendimiento_esperado_modelo	DELETE	postgres	\N	\N	\N	\N	470ee2f9-91a7-44b0-bec2-3f6378341347	{"id": "470ee2f9-91a7-44b0-bec2-3f6378341347", "notas": "Parámetro de prueba", "creado_en": "2025-05-21T18:50:17.389936-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": "2025-05-21T18:50:17.402643-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "tipo_eje_aplicacion": "DIRECCION", "km_esperado_vida_original_max": 130000, "km_esperado_vida_original_min": 80000}	\N	\N	\N	\N
113	2025-05-21 18:54:21.74391-05	public	parametros_rendimiento_esperado_modelo	UPDATE	postgres	\N	\N	\N	\N	2aa5e2c1-d0ab-442b-84a6-bc42107cae3d	{"id": "2aa5e2c1-d0ab-442b-84a6-bc42107cae3d", "notas": "Parámetro de prueba", "creado_en": "2025-05-21T18:54:21.733108-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": null, "actualizado_por": null, "tipo_eje_aplicacion": "DIRECCION", "km_esperado_vida_original_max": 120000, "km_esperado_vida_original_min": 80000}	{"id": "2aa5e2c1-d0ab-442b-84a6-bc42107cae3d", "notas": "Parámetro de prueba", "creado_en": "2025-05-21T18:54:21.733108-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": "2025-05-21T18:54:21.7448-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "tipo_eje_aplicacion": "DIRECCION", "km_esperado_vida_original_max": 130000, "km_esperado_vida_original_min": 80000}	{"km_esperado_vida_original_max": "130000"}	\N	\N
114	2025-05-21 18:54:21.74831-05	public	parametros_rendimiento_esperado_modelo	DELETE	postgres	\N	\N	\N	\N	2aa5e2c1-d0ab-442b-84a6-bc42107cae3d	{"id": "2aa5e2c1-d0ab-442b-84a6-bc42107cae3d", "notas": "Parámetro de prueba", "creado_en": "2025-05-21T18:54:21.733108-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": "2025-05-21T18:54:21.7448-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "tipo_eje_aplicacion": "DIRECCION", "km_esperado_vida_original_max": 130000, "km_esperado_vida_original_min": 80000}	\N	\N	\N	\N
116	2025-05-21 22:06:54.216837-05	public	fabricantes_neumatico	INSERT	postgres	\N	\N	\N	\N	7f631e5e-cf90-4350-9890-e44bf313627b	\N	{"id": "7f631e5e-cf90-4350-9890-e44bf313627b", "activo": true, "nombre": "Bridgestone", "creado_en": "2025-05-21T22:06:54.216837-05:00", "sitio_web": null, "creado_por": null, "pais_origen": "Japón", "actualizado_en": null, "actualizado_por": null, "codigo_abreviado": "BRI"}	\N	\N	\n                    INSERT INTO fabricantes_neumatico (nombre, codigo_abreviado, pais_origen, activo, creado_en)\n                    VALUES ($1, $2, $3, true, NOW())\n                    RETURNING id\n                
117	2025-05-21 22:06:54.216837-05	public	fabricantes_neumatico	INSERT	postgres	\N	\N	\N	\N	45992f67-19ef-42ab-8af8-5d6eb7d142e3	\N	{"id": "45992f67-19ef-42ab-8af8-5d6eb7d142e3", "activo": true, "nombre": "Goodyear", "creado_en": "2025-05-21T22:06:54.216837-05:00", "sitio_web": null, "creado_por": null, "pais_origen": "Estados Unidos", "actualizado_en": null, "actualizado_por": null, "codigo_abreviado": "GOO"}	\N	\N	\n                    INSERT INTO fabricantes_neumatico (nombre, codigo_abreviado, pais_origen, activo, creado_en)\n                    VALUES ($1, $2, $3, true, NOW())\n                    RETURNING id\n                
118	2025-05-21 22:06:54.216837-05	public	fabricantes_neumatico	INSERT	postgres	\N	\N	\N	\N	2a22130d-4b35-4ea3-90af-37be5f74d48c	\N	{"id": "2a22130d-4b35-4ea3-90af-37be5f74d48c", "activo": true, "nombre": "Pirelli", "creado_en": "2025-05-21T22:06:54.216837-05:00", "sitio_web": null, "creado_por": null, "pais_origen": "Italia", "actualizado_en": null, "actualizado_por": null, "codigo_abreviado": "PIR"}	\N	\N	\n                    INSERT INTO fabricantes_neumatico (nombre, codigo_abreviado, pais_origen, activo, creado_en)\n                    VALUES ($1, $2, $3, true, NOW())\n                    RETURNING id\n                
119	2025-05-21 22:06:54.216837-05	public	fabricantes_neumatico	INSERT	postgres	\N	\N	\N	\N	94959e9a-bb96-4235-b09b-9db7f071ab8e	\N	{"id": "94959e9a-bb96-4235-b09b-9db7f071ab8e", "activo": true, "nombre": "Continental", "creado_en": "2025-05-21T22:06:54.216837-05:00", "sitio_web": null, "creado_por": null, "pais_origen": "Alemania", "actualizado_en": null, "actualizado_por": null, "codigo_abreviado": "CON"}	\N	\N	\n                    INSERT INTO fabricantes_neumatico (nombre, codigo_abreviado, pais_origen, activo, creado_en)\n                    VALUES ($1, $2, $3, true, NOW())\n                    RETURNING id\n                
120	2025-05-21 23:07:50.338349-05	public	proveedores	UPDATE	postgres	\N	\N	\N	\N	aee67a19-af2d-4b9d-94cf-27d86e09b369	{"id": "aee67a19-af2d-4b9d-94cf-27d86e09b369", "ruc": "XAXX010101000", "tipo": "FABRICANTE", "email": "proveedor@ejemplo.com", "activo": true, "nombre": "Nuevo Nombre Proveedor SA", "telefono": "123456789", "creado_en": "2025-05-19T16:12:52.118923-05:00", "direccion": "Av. Ejemplo 123, Lima", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": "2025-05-19T16:27:03.31491-05:00", "actualizado_por": null, "contacto_principal": "Juan Pérez"}	{"id": "aee67a19-af2d-4b9d-94cf-27d86e09b369", "ruc": "010101000", "tipo": "FABRICANTE", "email": "proveedor@ejemplo.com", "activo": true, "nombre": "Nuevo Nombre Proveedor SA", "telefono": "123456789", "creado_en": "2025-05-19T16:12:52.118923-05:00", "direccion": "Av. Ejemplo 123, Lima", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": "2025-05-19T16:27:03.31491-05:00", "actualizado_por": null, "contacto_principal": "Juan Pérez"}	{"ruc": {"new": "010101000", "old": "XAXX010101000"}}	\N	UPDATE proveedores \nSET ruc = REGEXP_REPLACE(ruc, '[^0-9]', '', 'g')\nWHERE ruc IS NOT NULL;
121	2025-05-21 23:07:55.760131-05	public	proveedores	UPDATE	postgres	\N	\N	\N	\N	aee67a19-af2d-4b9d-94cf-27d86e09b369	{"id": "aee67a19-af2d-4b9d-94cf-27d86e09b369", "ruc": "010101000", "tipo": "FABRICANTE", "email": "proveedor@ejemplo.com", "activo": true, "nombre": "Nuevo Nombre Proveedor SA", "telefono": "123456789", "creado_en": "2025-05-19T16:12:52.118923-05:00", "direccion": "Av. Ejemplo 123, Lima", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": "2025-05-19T16:27:03.31491-05:00", "actualizado_por": null, "contacto_principal": "Juan Pérez"}	{"id": "aee67a19-af2d-4b9d-94cf-27d86e09b369", "ruc": "00010101000", "tipo": "FABRICANTE", "email": "proveedor@ejemplo.com", "activo": true, "nombre": "Nuevo Nombre Proveedor SA", "telefono": "123456789", "creado_en": "2025-05-19T16:12:52.118923-05:00", "direccion": "Av. Ejemplo 123, Lima", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": "2025-05-19T16:27:03.31491-05:00", "actualizado_por": null, "contacto_principal": "Juan Pérez"}	{"ruc": {"new": "00010101000", "old": "010101000"}}	\N	UPDATE proveedores \nSET ruc = LPAD(ruc, 11, '0')\nWHERE ruc IS NOT NULL AND LENGTH(ruc) <= 11;
122	2025-05-21 23:10:11.458903-05	public	proveedores	UPDATE	postgres	\N	\N	\N	\N	aee67a19-af2d-4b9d-94cf-27d86e09b369	{"id": "aee67a19-af2d-4b9d-94cf-27d86e09b369", "ruc": "00010101000", "tipo": "FABRICANTE", "email": "proveedor@ejemplo.com", "activo": true, "nombre": "Nuevo Nombre Proveedor SA", "telefono": "123456789", "creado_en": "2025-05-19T16:12:52.118923-05:00", "direccion": "Av. Ejemplo 123, Lima", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": "2025-05-19T16:27:03.31491-05:00", "actualizado_por": null, "contacto_principal": "Juan Pérez"}	{"id": "aee67a19-af2d-4b9d-94cf-27d86e09b369", "ruc": "20010101000", "tipo": "FABRICANTE", "email": "proveedor@ejemplo.com", "activo": true, "nombre": "Nuevo Nombre Proveedor SA", "telefono": "123456789", "creado_en": "2025-05-19T16:12:52.118923-05:00", "direccion": "Av. Ejemplo 123, Lima", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": "2025-05-19T16:27:03.31491-05:00", "actualizado_por": null, "contacto_principal": "Juan Pérez"}	{"ruc": {"new": "20010101000", "old": "00010101000"}}	\N	UPDATE proveedores \nSET ruc = '20' || SUBSTRING(ruc, 3)\nWHERE ruc IS NOT NULL AND ruc NOT LIKE '20%';
123	2025-05-21 23:11:57.212851-05	public	proveedores	INSERT	postgres	\N	\N	\N	\N	d1bbd8da-922d-4b9b-98b3-ab77ac0019ea	\N	{"id": "d1bbd8da-922d-4b9b-98b3-ab77ac0019ea", "ruc": "20123456789", "tipo": null, "email": null, "activo": true, "nombre": "Prueba 1", "telefono": null, "creado_en": "2025-05-21T23:11:57.212851-05:00", "direccion": null, "creado_por": null, "actualizado_en": null, "actualizado_por": null, "contacto_principal": null}	\N	\N	INSERT INTO proveedores (nombre, ruc) \nVALUES ('Prueba 1', '20123456789');
124	2025-05-21 23:11:57.218729-05	public	proveedores	INSERT	postgres	\N	\N	\N	\N	f5fed807-8882-4d3e-8373-dcca0bcf7b8a	\N	{"id": "f5fed807-8882-4d3e-8373-dcca0bcf7b8a", "ruc": "20000000005", "tipo": null, "email": null, "activo": true, "nombre": "Prueba 3", "telefono": null, "creado_en": "2025-05-21T23:11:57.218729-05:00", "direccion": null, "creado_por": null, "actualizado_en": null, "actualizado_por": null, "contacto_principal": null}	\N	\N	INSERT INTO proveedores (nombre, ruc) \nVALUES ('Prueba 3', '205');
125	2025-05-21 23:11:57.219693-05	public	proveedores	INSERT	postgres	\N	\N	\N	\N	57e6f759-35ef-43d2-85d3-9607ff599c04	\N	{"id": "57e6f759-35ef-43d2-85d3-9607ff599c04", "ruc": "20102030405", "tipo": null, "email": null, "activo": true, "nombre": "Prueba 4", "telefono": null, "creado_en": "2025-05-21T23:11:57.219693-05:00", "direccion": null, "creado_por": null, "actualizado_en": null, "actualizado_por": null, "contacto_principal": null}	\N	\N	INSERT INTO proveedores (nombre, ruc) \nVALUES ('Prueba 4', '10203040506');
127	2025-05-22 00:19:32.129673-05	public	registros_odometro	UPDATE	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin	\N	\N	f67ac8c9-3a87-4b7e-b646-3367ac2cfe5f	{"notas": "Registro automático", "fuente": "sistema", "odometro": 15800, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "fecha_medicion": "2025-05-22T00:11:42.540618-05:00"}	{"notas": "Actualización de prueba", "fuente": "sistema", "odometro": 15850, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "fecha_medicion": "2025-05-22T00:11:42.540618-05:00"}	{"notas": "Actualización de prueba", "odometro": 15850}	\N	\N
358	2025-05-27 18:31:12.012882-05	public	eventos_neumaticos	INSERT	postgres	\N	\N	\N	\N	89a53121-98f3-4bcd-ae7f-b5a05b4fa9fd	\N	{"id": "89a53121-98f3-4bcd-ae7f-b5a05b4fa9fd", "notas": null, "creado_en": "2025-05-27T18:31:12.012882-05:00", "usuario_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "presion_psi": null, "tipo_evento": "DESMONTAJE", "vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "costo_evento": null, "datos_evento": {"es_retirado": false, "vida_actual": 1, "vidas_maximas": 5, "es_recuperable": true, "kilometraje_vida_actual": 0, "tasa_desgaste_actual_mm_km": null, "profundidad_remanente_actual_mm": 10.00, "profundidad_inicio_vida_actual_mm": 15.00}, "moneda_costo": "PEN", "neumatico_id": "0e2f0e46-2da7-4880-8af1-42518ac26c15", "tipo_ruta_id": null, "timestamp_evento": "2025-05-27T18:31:12.012882-05:00", "almacen_destino_id": null, "destino_desmontaje": "EN_REENCAUCHE", "proveedor_servicio_id": null, "motivo_reparacion_texto": null, "motivo_desecho_id_evento": null, "profundidad_remanente_mm": null, "relacion_evento_anterior": null, "tipo_dano_detectado_texto": null, "odometro_vehiculo_en_evento": 10000, "peso_carga_promedio_ton_evento": null, "profundidad_post_reencauche_mm": null}	\N	\N	\N
365	2025-05-27 18:32:00.312736-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	3d986345-b3fb-4dd1-90b2-346934941389	{"id": "3d986345-b3fb-4dd1-90b2-346934941389", "dot": null, "activo": true, "creado_en": "2025-05-27T18:32:00.303244-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-26b30be035", "estado_actual": "EN_REENCAUCHE", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:32:00.303244-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:32:00.312736-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "3d986345-b3fb-4dd1-90b2-346934941389", "dot": null, "activo": true, "creado_en": "2025-05-27T18:32:00.303244-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-26b30be035", "estado_actual": "EN_REENCAUCHE", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:32:00.312736-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:32:00.312736-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"profundidad_inicio_vida_actual_mm": {"new": null, "old": "15.00"}}	\N	\N
339	2025-05-27 17:33:25.904859-05	public	neumaticos	INSERT	postgres	\N	\N	\N	\N	e9c3ea71-53b2-412d-a3ce-6b134d558892	\N	{"id": "e9c3ea71-53b2-412d-a3ce-6b134d558892", "dot": null, "activo": true, "creado_en": "2025-05-27T17:33:25.904859-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-17ba394d49", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T17:33:25.904859-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T17:33:25.904859-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	\N	\N	\N
137	2025-05-22 23:29:33.055872-05	public	modelos_neumatico	INSERT	postgres	\N	\N	\N	\N	6618f954-8d68-4923-a951-bb22e15ebb97	\N	{"id": "6618f954-8d68-4923-a951-bb22e15ebb97", "activo": true, "medida": "295/75R22.5", "creado_en": "2025-05-22T23:29:33.055872-05:00", "creado_por": null, "indice_carga": null, "fabricante_id": "00000000-0000-0000-0000-000000000001", "nombre_modelo": "Modelo Prueba Vida Útil", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": null, "indice_velocidad": null, "permite_reencauche": false, "reencauches_maximos": 0, "vida_util_teorica_km": 200000, "presion_recomendada_psi": null, "profundidad_original_mm": 15.00, "posicion_uso_recomendada": null, "diseno_predominante_para_eje": null, "profundidad_minima_retiro_mm": 1.60, "tasa_desgaste_esperada_mm_km": 0.00050000}	\N	\N	WITH modelo_insertado AS (\n    INSERT INTO modelos_neumatico (\n        fabricante_id, \n        nombre_modelo, \n        medida, \n        profundidad_original_mm,\n        profundidad_minima_retiro_mm,\n        tasa_desgaste_esperada_mm_km,\n        vida_util_teorica_km\n    ) VALUES (\n        (SELECT id FROM fabricantes_neumatico LIMIT 1),\n        'Modelo Prueba Vida Útil',\n        '295/75R22.5',\n        15.0,\n        1.6,\n        0.0005,\n        200000\n    ) RETURNING *\n)\nSELECT 'Modelo insertado:' AS info, * FROM modelo_insertado;
138	2025-05-22 23:29:33.07387-05	public	modelos_neumatico	DELETE	postgres	\N	\N	\N	\N	6618f954-8d68-4923-a951-bb22e15ebb97	{"id": "6618f954-8d68-4923-a951-bb22e15ebb97", "activo": true, "medida": "295/75R22.5", "creado_en": "2025-05-22T23:29:33.055872-05:00", "creado_por": null, "deleted_at": "2025-05-22T23:29:33.07387-05:00", "indice_carga": null, "fabricante_id": "00000000-0000-0000-0000-000000000001", "nombre_modelo": "Modelo Prueba Vida Útil", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": null, "indice_velocidad": null, "permite_reencauche": false, "reencauches_maximos": 0, "vida_util_teorica_km": 200000, "presion_recomendada_psi": null, "profundidad_original_mm": 15.00, "posicion_uso_recomendada": null, "diseno_predominante_para_eje": null, "profundidad_minima_retiro_mm": 1.60, "tasa_desgaste_esperada_mm_km": 0.00050000}	\N	\N	\N	WITH eliminados AS (\n    DELETE FROM modelos_neumatico \n    WHERE nombre_modelo = 'Modelo Prueba Vida Útil' \n    RETURNING id\n)\nSELECT 'Modelos eliminados:' AS accion, COUNT(*) AS total FROM eliminados;
340	2025-05-27 17:46:56.814398-05	public	neumaticos	INSERT	postgres	\N	\N	\N	\N	e99dd95d-4280-4705-a4aa-f83dd29c0171	\N	{"id": "e99dd95d-4280-4705-a4aa-f83dd29c0171", "dot": null, "activo": true, "creado_en": "2025-05-27T17:46:56.814398-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-938377c49a", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T17:46:56.814398-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T17:46:56.814398-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	\N	\N	\N
359	2025-05-27 18:31:34.836198-05	public	neumaticos	INSERT	postgres	\N	\N	\N	\N	a91b9b5a-fd3e-485e-86d0-3a1c2325d40b	\N	{"id": "a91b9b5a-fd3e-485e-86d0-3a1c2325d40b", "dot": null, "activo": true, "creado_en": "2025-05-27T18:31:34.836198-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-e683a91175", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:31:34.836198-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:31:34.836198-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	\N	\N	\N
360	2025-05-27 18:31:34.851548-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	a91b9b5a-fd3e-485e-86d0-3a1c2325d40b	{"id": "a91b9b5a-fd3e-485e-86d0-3a1c2325d40b", "dot": null, "activo": true, "creado_en": "2025-05-27T18:31:34.836198-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-e683a91175", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:31:34.836198-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:31:34.836198-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "a91b9b5a-fd3e-485e-86d0-3a1c2325d40b", "dot": null, "activo": true, "creado_en": "2025-05-27T18:31:34.836198-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-e683a91175", "estado_actual": "EN_REENCAUCHE", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:31:34.836198-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:31:34.851548-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"estado_actual": {"new": "EN_REENCAUCHE", "old": "INSTALADO"}, "fecha_ultimo_evento": {"new": "2025-05-27T18:31:34.851548-05:00", "old": "2025-05-27T18:31:34.836198-05:00"}, "ubicacion_actual_posicion_id": {"new": null, "old": "dddddddd-dddd-dddd-dddd-dddddddddddd"}, "ubicacion_actual_vehiculo_id": {"new": null, "old": "06abeeaf-0d42-4032-94a8-c46f3d6ee709"}}	\N	\N
331	2025-05-27 17:19:14.217844-05	public	neumaticos	INSERT	postgres	\N	\N	\N	\N	0dd8d980-1fbb-4611-8298-038a69bc9582	\N	{"id": "0dd8d980-1fbb-4611-8298-038a69bc9582", "dot": null, "activo": true, "creado_en": "2025-05-27T17:19:14.217844-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-f680f19ec5", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T17:19:14.217844-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T17:19:14.217844-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	\N	\N	\N
341	2025-05-27 18:28:29.953019-05	public	neumaticos	INSERT	postgres	\N	\N	\N	\N	008e61e4-207c-4c06-ab5c-3425450a7ce1	\N	{"id": "008e61e4-207c-4c06-ab5c-3425450a7ce1", "dot": null, "activo": true, "creado_en": "2025-05-27T18:28:29.953019-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-402fe12e40", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:28:29.953019-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:28:29.953019-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	\N	\N	\N
332	2025-05-27 17:20:05.119664-05	public	neumaticos	INSERT	postgres	\N	\N	\N	\N	8b879b54-eda4-4bc6-9593-cd5242588d7c	\N	{"id": "8b879b54-eda4-4bc6-9593-cd5242588d7c", "dot": null, "activo": true, "creado_en": "2025-05-27T17:20:05.119664-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-d567ce9a81", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T17:20:05.119664-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T17:20:05.119664-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	\N	\N	\N
344	2025-05-27 18:29:28.574478-05	public	neumaticos	INSERT	postgres	\N	\N	\N	\N	235b4401-4bc0-4523-b9f8-5b912bb45f61	\N	{"id": "235b4401-4bc0-4523-b9f8-5b912bb45f61", "dot": null, "activo": true, "creado_en": "2025-05-27T18:29:28.574478-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-1e503f8b69", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:29:28.574478-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:29:28.574478-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	\N	\N	\N
333	2025-05-27 17:22:19.80177-05	public	neumaticos	INSERT	postgres	\N	\N	\N	\N	60e9e8c8-0648-4f57-ba3b-8f5c62ea36eb	\N	{"id": "60e9e8c8-0648-4f57-ba3b-8f5c62ea36eb", "dot": null, "activo": true, "creado_en": "2025-05-27T17:22:19.80177-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-0407b809cd", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T17:22:19.80177-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T17:22:19.80177-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	\N	\N	\N
347	2025-05-27 18:30:10.067322-05	public	neumaticos	INSERT	postgres	\N	\N	\N	\N	a55368a0-6f59-42d3-9554-1daeec552a68	\N	{"id": "a55368a0-6f59-42d3-9554-1daeec552a68", "dot": null, "activo": true, "creado_en": "2025-05-27T18:30:10.067322-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-15e80f32c9", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:30:10.067322-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:30:10.067322-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	\N	\N	\N
348	2025-05-27 18:30:10.076367-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	a55368a0-6f59-42d3-9554-1daeec552a68	{"id": "a55368a0-6f59-42d3-9554-1daeec552a68", "dot": null, "activo": true, "creado_en": "2025-05-27T18:30:10.067322-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-15e80f32c9", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:30:10.067322-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:30:10.067322-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "a55368a0-6f59-42d3-9554-1daeec552a68", "dot": null, "activo": true, "creado_en": "2025-05-27T18:30:10.067322-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-15e80f32c9", "estado_actual": "EN_REENCAUCHE", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:30:10.067322-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:30:10.076367-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"estado_actual": {"new": "EN_REENCAUCHE", "old": "INSTALADO"}, "fecha_ultimo_evento": {"new": "2025-05-27T18:30:10.076367-05:00", "old": "2025-05-27T18:30:10.067322-05:00"}, "ubicacion_actual_posicion_id": {"new": null, "old": "dddddddd-dddd-dddd-dddd-dddddddddddd"}, "ubicacion_actual_vehiculo_id": {"new": null, "old": "06abeeaf-0d42-4032-94a8-c46f3d6ee709"}}	\N	\N
349	2025-05-27 18:30:10.076367-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	a55368a0-6f59-42d3-9554-1daeec552a68	{"id": "a55368a0-6f59-42d3-9554-1daeec552a68", "dot": null, "activo": true, "creado_en": "2025-05-27T18:30:10.067322-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-15e80f32c9", "estado_actual": "EN_REENCAUCHE", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:30:10.067322-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:30:10.076367-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "a55368a0-6f59-42d3-9554-1daeec552a68", "dot": null, "activo": true, "creado_en": "2025-05-27T18:30:10.067322-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-15e80f32c9", "estado_actual": "EN_REENCAUCHE", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:30:10.076367-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:30:10.076367-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"profundidad_inicio_vida_actual_mm": {"new": null, "old": "15.00"}}	\N	\N
334	2025-05-27 17:23:33.700102-05	public	neumaticos	INSERT	postgres	\N	\N	\N	\N	060366ed-07ec-4d0d-8d3d-f97821717ffb	\N	{"id": "060366ed-07ec-4d0d-8d3d-f97821717ffb", "dot": null, "activo": true, "creado_en": "2025-05-27T17:23:33.700102-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-98cf53c501", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T17:23:33.700102-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T17:23:33.700102-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	\N	\N	\N
350	2025-05-27 18:30:10.076367-05	public	eventos_neumaticos	INSERT	postgres	\N	\N	\N	\N	b6eae463-c170-40e8-9fdf-ced466cbb9e6	\N	{"id": "b6eae463-c170-40e8-9fdf-ced466cbb9e6", "notas": null, "creado_en": "2025-05-27T18:30:10.076367-05:00", "usuario_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "presion_psi": null, "tipo_evento": "DESMONTAJE", "vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "costo_evento": null, "datos_evento": {"es_retirado": false, "vida_actual": 1, "vidas_maximas": 5, "es_recuperable": true, "kilometraje_vida_actual": 0, "tasa_desgaste_actual_mm_km": null, "profundidad_remanente_actual_mm": 10.00, "profundidad_inicio_vida_actual_mm": 15.00}, "moneda_costo": "PEN", "neumatico_id": "a55368a0-6f59-42d3-9554-1daeec552a68", "tipo_ruta_id": null, "timestamp_evento": "2025-05-27T18:30:10.076367-05:00", "almacen_destino_id": null, "destino_desmontaje": "EN_REENCAUCHE", "proveedor_servicio_id": null, "motivo_reparacion_texto": null, "motivo_desecho_id_evento": null, "profundidad_remanente_mm": null, "relacion_evento_anterior": null, "tipo_dano_detectado_texto": null, "odometro_vehiculo_en_evento": 10000, "peso_carga_promedio_ton_evento": null, "profundidad_post_reencauche_mm": null}	\N	\N	\N
361	2025-05-27 18:31:34.851548-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	a91b9b5a-fd3e-485e-86d0-3a1c2325d40b	{"id": "a91b9b5a-fd3e-485e-86d0-3a1c2325d40b", "dot": null, "activo": true, "creado_en": "2025-05-27T18:31:34.836198-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-e683a91175", "estado_actual": "EN_REENCAUCHE", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:31:34.836198-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:31:34.851548-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "a91b9b5a-fd3e-485e-86d0-3a1c2325d40b", "dot": null, "activo": true, "creado_en": "2025-05-27T18:31:34.836198-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-e683a91175", "estado_actual": "EN_REENCAUCHE", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:31:34.851548-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:31:34.851548-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"profundidad_inicio_vida_actual_mm": {"new": null, "old": "15.00"}}	\N	\N
362	2025-05-27 18:31:34.851548-05	public	eventos_neumaticos	INSERT	postgres	\N	\N	\N	\N	f14d2fb7-55d3-4617-b0b5-32cd96dea8ac	\N	{"id": "f14d2fb7-55d3-4617-b0b5-32cd96dea8ac", "notas": null, "creado_en": "2025-05-27T18:31:34.851548-05:00", "usuario_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "presion_psi": null, "tipo_evento": "DESMONTAJE", "vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "costo_evento": null, "datos_evento": {"es_retirado": false, "vida_actual": 1, "vidas_maximas": 5, "es_recuperable": true, "kilometraje_vida_actual": 0, "tasa_desgaste_actual_mm_km": null, "profundidad_remanente_actual_mm": 10.00, "profundidad_inicio_vida_actual_mm": 15.00}, "moneda_costo": "PEN", "neumatico_id": "a91b9b5a-fd3e-485e-86d0-3a1c2325d40b", "tipo_ruta_id": null, "timestamp_evento": "2025-05-27T18:31:34.851548-05:00", "almacen_destino_id": null, "destino_desmontaje": "EN_REENCAUCHE", "proveedor_servicio_id": null, "motivo_reparacion_texto": null, "motivo_desecho_id_evento": null, "profundidad_remanente_mm": null, "relacion_evento_anterior": null, "tipo_dano_detectado_texto": null, "odometro_vehiculo_en_evento": 10000, "peso_carga_promedio_ton_evento": null, "profundidad_post_reencauche_mm": null}	\N	\N	\N
335	2025-05-27 17:24:42.966298-05	public	eventos_neumaticos	INSERT	postgres	\N	\N	\N	\N	11428698-7129-4728-bdd1-8ff977e8938f	\N	{"id": "11428698-7129-4728-bdd1-8ff977e8938f", "notas": null, "creado_en": "2025-05-27T17:24:42.966298-05:00", "usuario_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "presion_psi": null, "tipo_evento": "DESMONTAJE", "vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "costo_evento": null, "datos_evento": null, "moneda_costo": "PEN", "neumatico_id": "060366ed-07ec-4d0d-8d3d-f97821717ffb", "tipo_ruta_id": null, "timestamp_evento": "2025-05-27T17:24:42.966298-05:00", "almacen_destino_id": null, "destino_desmontaje": "EN_REENCAUCHE", "proveedor_servicio_id": null, "motivo_reparacion_texto": null, "motivo_desecho_id_evento": null, "profundidad_remanente_mm": null, "relacion_evento_anterior": null, "tipo_dano_detectado_texto": null, "odometro_vehiculo_en_evento": 10000, "peso_carga_promedio_ton_evento": null, "profundidad_post_reencauche_mm": null}	\N	\N	\N
351	2025-05-27 18:30:36.824245-05	public	neumaticos	INSERT	postgres	\N	\N	\N	\N	1dee9c2a-b855-44c8-b5ef-8a6ed6bbfdda	\N	{"id": "1dee9c2a-b855-44c8-b5ef-8a6ed6bbfdda", "dot": null, "activo": true, "creado_en": "2025-05-27T18:30:36.824245-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-e061815996", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:30:36.824245-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:30:36.824245-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	\N	\N	\N
352	2025-05-27 18:30:36.833039-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	1dee9c2a-b855-44c8-b5ef-8a6ed6bbfdda	{"id": "1dee9c2a-b855-44c8-b5ef-8a6ed6bbfdda", "dot": null, "activo": true, "creado_en": "2025-05-27T18:30:36.824245-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-e061815996", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:30:36.824245-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:30:36.824245-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "1dee9c2a-b855-44c8-b5ef-8a6ed6bbfdda", "dot": null, "activo": true, "creado_en": "2025-05-27T18:30:36.824245-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-e061815996", "estado_actual": "EN_REENCAUCHE", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:30:36.824245-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:30:36.833039-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"estado_actual": {"new": "EN_REENCAUCHE", "old": "INSTALADO"}, "fecha_ultimo_evento": {"new": "2025-05-27T18:30:36.833039-05:00", "old": "2025-05-27T18:30:36.824245-05:00"}, "ubicacion_actual_posicion_id": {"new": null, "old": "dddddddd-dddd-dddd-dddd-dddddddddddd"}, "ubicacion_actual_vehiculo_id": {"new": null, "old": "06abeeaf-0d42-4032-94a8-c46f3d6ee709"}}	\N	\N
363	2025-05-27 18:32:00.303244-05	public	neumaticos	INSERT	postgres	\N	\N	\N	\N	3d986345-b3fb-4dd1-90b2-346934941389	\N	{"id": "3d986345-b3fb-4dd1-90b2-346934941389", "dot": null, "activo": true, "creado_en": "2025-05-27T18:32:00.303244-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-26b30be035", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:32:00.303244-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:32:00.303244-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	\N	\N	\N
173	2025-05-26 18:09:35.967875-05	public	eventos_neumaticos	INSERT	postgres	\N	\N	\N	\N	04fac6b2-6679-40a3-b3cc-f28b51bc34b7	\N	{"id": "04fac6b2-6679-40a3-b3cc-f28b51bc34b7", "notas": null, "creado_en": "2025-05-26T18:09:35.967875-05:00", "usuario_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "posicion_id": null, "presion_psi": null, "tipo_evento": "DESMONTAJE", "vehiculo_id": null, "costo_evento": null, "datos_evento": null, "moneda_costo": "PEN", "neumatico_id": "00000000-0000-0000-0000-000000000001", "tipo_ruta_id": null, "timestamp_evento": "2025-05-26T18:09:35.967875-05:00", "almacen_destino_id": null, "destino_desmontaje": "EN_STOCK", "proveedor_servicio_id": null, "motivo_reparacion_texto": null, "motivo_desecho_id_evento": null, "profundidad_remanente_mm": 12.50, "relacion_evento_anterior": null, "tipo_dano_detectado_texto": null, "odometro_vehiculo_en_evento": null, "peso_carga_promedio_ton_evento": null, "profundidad_post_reencauche_mm": null}	\N	\N	\N
336	2025-05-27 17:28:34.297643-05	public	neumaticos	INSERT	postgres	\N	\N	\N	\N	877231d5-7c90-42ae-b216-83c15e931ae7	\N	{"id": "877231d5-7c90-42ae-b216-83c15e931ae7", "dot": null, "activo": true, "creado_en": "2025-05-27T17:28:34.297643-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-c17bc3dbd3", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T17:28:34.297643-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T17:28:34.297643-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	\N	\N	\N
353	2025-05-27 18:30:36.833039-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	1dee9c2a-b855-44c8-b5ef-8a6ed6bbfdda	{"id": "1dee9c2a-b855-44c8-b5ef-8a6ed6bbfdda", "dot": null, "activo": true, "creado_en": "2025-05-27T18:30:36.824245-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-e061815996", "estado_actual": "EN_REENCAUCHE", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:30:36.824245-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:30:36.833039-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "1dee9c2a-b855-44c8-b5ef-8a6ed6bbfdda", "dot": null, "activo": true, "creado_en": "2025-05-27T18:30:36.824245-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-e061815996", "estado_actual": "EN_REENCAUCHE", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:30:36.833039-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:30:36.833039-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"profundidad_inicio_vida_actual_mm": {"new": null, "old": "15.00"}}	\N	\N
354	2025-05-27 18:30:36.833039-05	public	eventos_neumaticos	INSERT	postgres	\N	\N	\N	\N	e663fedf-cc42-4d41-af75-886bd9b85d50	\N	{"id": "e663fedf-cc42-4d41-af75-886bd9b85d50", "notas": null, "creado_en": "2025-05-27T18:30:36.833039-05:00", "usuario_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "presion_psi": null, "tipo_evento": "DESMONTAJE", "vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "costo_evento": null, "datos_evento": {"es_retirado": false, "vida_actual": 1, "vidas_maximas": 5, "es_recuperable": true, "kilometraje_vida_actual": 0, "tasa_desgaste_actual_mm_km": null, "profundidad_remanente_actual_mm": 10.00, "profundidad_inicio_vida_actual_mm": 15.00}, "moneda_costo": "PEN", "neumatico_id": "1dee9c2a-b855-44c8-b5ef-8a6ed6bbfdda", "tipo_ruta_id": null, "timestamp_evento": "2025-05-27T18:30:36.833039-05:00", "almacen_destino_id": null, "destino_desmontaje": "EN_REENCAUCHE", "proveedor_servicio_id": null, "motivo_reparacion_texto": null, "motivo_desecho_id_evento": null, "profundidad_remanente_mm": null, "relacion_evento_anterior": null, "tipo_dano_detectado_texto": null, "odometro_vehiculo_en_evento": 10000, "peso_carga_promedio_ton_evento": null, "profundidad_post_reencauche_mm": null}	\N	\N	\N
364	2025-05-27 18:32:00.312736-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	3d986345-b3fb-4dd1-90b2-346934941389	{"id": "3d986345-b3fb-4dd1-90b2-346934941389", "dot": null, "activo": true, "creado_en": "2025-05-27T18:32:00.303244-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-26b30be035", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:32:00.303244-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:32:00.303244-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "3d986345-b3fb-4dd1-90b2-346934941389", "dot": null, "activo": true, "creado_en": "2025-05-27T18:32:00.303244-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-26b30be035", "estado_actual": "EN_REENCAUCHE", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:32:00.303244-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:32:00.312736-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"estado_actual": {"new": "EN_REENCAUCHE", "old": "INSTALADO"}, "fecha_ultimo_evento": {"new": "2025-05-27T18:32:00.312736-05:00", "old": "2025-05-27T18:32:00.303244-05:00"}, "ubicacion_actual_posicion_id": {"new": null, "old": "dddddddd-dddd-dddd-dddd-dddddddddddd"}, "ubicacion_actual_vehiculo_id": {"new": null, "old": "06abeeaf-0d42-4032-94a8-c46f3d6ee709"}}	\N	\N
174	2025-05-26 21:13:31.459054-05	public	eventos_neumaticos	INSERT	postgres	\N	\N	\N	\N	17dce29f-f11a-46f1-9cf8-6a2fd9a22f67	\N	{"id": "17dce29f-f11a-46f1-9cf8-6a2fd9a22f67", "notas": null, "creado_en": "2025-05-26T21:13:31.459054-05:00", "usuario_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "posicion_id": null, "presion_psi": null, "tipo_evento": "DESMONTAJE", "vehiculo_id": null, "costo_evento": null, "datos_evento": null, "moneda_costo": "PEN", "neumatico_id": "00000000-0000-0000-0000-000000000001", "tipo_ruta_id": null, "timestamp_evento": "2025-05-26T21:13:31.459054-05:00", "almacen_destino_id": null, "destino_desmontaje": "EN_STOCK", "proveedor_servicio_id": null, "motivo_reparacion_texto": null, "motivo_desecho_id_evento": null, "profundidad_remanente_mm": 12.50, "relacion_evento_anterior": null, "tipo_dano_detectado_texto": null, "odometro_vehiculo_en_evento": null, "peso_carga_promedio_ton_evento": null, "profundidad_post_reencauche_mm": null}	\N	\N	\N
175	2025-05-26 21:24:31.933428-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_STOCK", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T21:22:54.620308-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": null, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T21:24:31.933428-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": null, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"estado_actual": {"new": "EN_REPARACION", "old": "EN_STOCK"}}	\N	\N
176	2025-05-26 21:28:28.722866-05	public	neumaticos	INSERT	postgres	\N	\N	\N	\N	d1eba5a3-f460-457a-9aec-094fd5381628	\N	{"id": "d1eba5a3-f460-457a-9aec-094fd5381628", "dot": null, "activo": true, "creado_en": "2025-05-26T21:28:28.722866-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": null, "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-26", "numero_serie": null, "estado_actual": "EN_STOCK", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T21:28:28.722866-05:00", "actualizado_por": null, "es_reencauchado": false, "fecha_fabricacion": "2025-04-26", "motivo_desecho_id": null, "fecha_ultimo_evento": null, "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 15.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	\N	\N	\N
177	2025-05-26 21:29:43.825282-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	d1eba5a3-f460-457a-9aec-094fd5381628	{"id": "d1eba5a3-f460-457a-9aec-094fd5381628", "dot": null, "activo": true, "creado_en": "2025-05-26T21:28:28.722866-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": null, "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-26", "numero_serie": null, "estado_actual": "EN_STOCK", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T21:28:28.722866-05:00", "actualizado_por": null, "es_reencauchado": false, "fecha_fabricacion": "2025-04-26", "motivo_desecho_id": null, "fecha_ultimo_evento": null, "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 15.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "d1eba5a3-f460-457a-9aec-094fd5381628", "dot": null, "activo": true, "creado_en": "2025-05-26T21:28:28.722866-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": null, "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-26", "numero_serie": null, "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T21:29:43.825282-05:00", "actualizado_por": null, "es_reencauchado": false, "fecha_fabricacion": "2025-04-26", "motivo_desecho_id": null, "fecha_ultimo_evento": null, "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 14.80, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"estado_actual": {"new": "EN_REPARACION", "old": "EN_STOCK"}, "profundidad_remanente_actual_mm": {"new": "14.80", "old": "15.50"}}	\N	\N
178	2025-05-26 21:30:08.607586-05	public	neumaticos	DELETE	postgres	\N	\N	\N	\N	d1eba5a3-f460-457a-9aec-094fd5381628	{"id": "d1eba5a3-f460-457a-9aec-094fd5381628", "dot": null, "activo": true, "creado_en": "2025-05-26T21:28:28.722866-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": null, "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-26", "numero_serie": null, "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T21:29:43.825282-05:00", "actualizado_por": null, "es_reencauchado": false, "fecha_fabricacion": "2025-04-26", "motivo_desecho_id": null, "fecha_ultimo_evento": null, "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 14.80, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	\N	\N	\N	\N
179	2025-05-26 21:33:58.670724-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T21:24:31.933428-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": null, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T21:33:58.670724-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": null, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 14.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"proxima_inspeccion_km": {"new": "5000", "old": null}, "profundidad_remanente_actual_mm": {"new": "14.50", "old": null}}	\N	\N
180	2025-05-26 21:37:45.939699-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T21:33:58.670724-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": null, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 14.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T21:37:45.939699-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 25800, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "25800", "old": null}, "profundidad_remanente_actual_mm": {"new": "12.50", "old": "14.50"}}	\N	\N
209	2025-05-27 01:42:58.635408-05	public	modelos_neumatico	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "activo": true, "medida": "295/80R22.5", "creado_en": "2025-05-19T12:21:17.269955-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "indice_carga": null, "fabricante_id": "00000000-0000-0000-0000-000000000001", "nombre_modelo": "X Line Energy Z", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": null, "indice_velocidad": null, "max_vidas_utiles": 5, "permite_reencauche": true, "reencauches_maximos": 0, "vida_util_teorica_km": null, "presion_recomendada_psi": null, "profundidad_original_mm": 15.00, "frecuencia_inspeccion_km": 5000, "posicion_uso_recomendada": "OTRO", "diseno_predominante_para_eje": "OTRO", "porcentaje_desgaste_por_vida": 10.00, "profundidad_minima_retiro_mm": 1.60, "tasa_desgaste_esperada_mm_km": null}	{"id": "00000000-0000-0000-0000-000000000001", "activo": true, "medida": "295/80R22.5", "creado_en": "2025-05-19T12:21:17.269955-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "indice_carga": null, "fabricante_id": "00000000-0000-0000-0000-000000000001", "nombre_modelo": "X Line Energy Z", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": null, "indice_velocidad": null, "max_vidas_utiles": 5, "permite_reencauche": true, "reencauches_maximos": 0, "vida_util_teorica_km": null, "presion_recomendada_psi": null, "profundidad_original_mm": 15.00, "frecuencia_inspeccion_km": 5000, "posicion_uso_recomendada": "OTRO", "diseno_predominante_para_eje": "OTRO", "porcentaje_desgaste_por_vida": 10.00, "profundidad_minima_retiro_mm": 1.60, "tasa_desgaste_esperada_mm_km": 0.00010000}	{"tasa_desgaste_esperada_mm_km": {"new": "0.00010000", "old": null}}	\N	UPDATE modelos_neumatico\nSET tasa_desgaste_esperada_mm_km = 0.0001\nWHERE tasa_desgaste_esperada_mm_km IS NULL\nRETURNING id, nombre_modelo, tasa_desgaste_esperada_mm_km;
181	2025-05-26 22:07:33.457998-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T21:37:45.939699-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 25800, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.457998-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 21800, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 15.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "21800", "old": "25800"}, "tasa_desgaste_actual_mm_km": {"new": "0.00040000", "old": null}, "profundidad_remanente_actual_mm": {"new": "15.00", "old": "12.50"}}	\N	\N
182	2025-05-26 22:07:33.457998-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.457998-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 21800, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 15.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.457998-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 33500, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "33500", "old": "21800"}, "profundidad_remanente_actual_mm": {"new": "12.50", "old": "15.00"}}	\N	\N
183	2025-05-26 22:07:33.468681-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.457998-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 33500, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.468681-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 27250, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 2.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "27250", "old": "33500"}, "profundidad_remanente_actual_mm": {"new": "2.00", "old": "12.50"}}	\N	\N
184	2025-05-26 22:07:33.468681-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.468681-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 27250, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 2.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.468681-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 1000, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "1000", "old": "27250"}, "profundidad_remanente_actual_mm": {"new": "12.50", "old": "2.00"}}	\N	\N
185	2025-05-26 22:07:33.473864-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.468681-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 1000, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.473864-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 27250, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 1.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "27250", "old": "1000"}, "profundidad_remanente_actual_mm": {"new": "1.50", "old": "12.50"}}	\N	\N
186	2025-05-26 22:07:33.473864-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.473864-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 27250, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 1.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.473864-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": null, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": null, "old": "27250"}, "profundidad_remanente_actual_mm": {"new": "12.50", "old": "1.50"}}	\N	\N
187	2025-05-26 22:07:33.478922-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.473864-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": null, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.478922-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 27250, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00100000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 15.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "27250", "old": null}, "tasa_desgaste_actual_mm_km": {"new": "0.00100000", "old": "0.00040000"}, "profundidad_remanente_actual_mm": {"new": "15.00", "old": "12.50"}}	\N	\N
188	2025-05-26 22:07:33.478922-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.478922-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 27250, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00100000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 15.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.478922-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 13400, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "13400", "old": "27250"}, "tasa_desgaste_actual_mm_km": {"new": "0.00040000", "old": "0.00100000"}, "profundidad_remanente_actual_mm": {"new": "12.50", "old": "15.00"}}	\N	\N
189	2025-05-26 22:07:33.481712-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.478922-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 13400, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.481712-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 27250, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00010000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 15.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "27250", "old": "13400"}, "tasa_desgaste_actual_mm_km": {"new": "0.00010000", "old": "0.00040000"}, "profundidad_remanente_actual_mm": {"new": "15.00", "old": "12.50"}}	\N	\N
190	2025-05-26 22:07:33.481712-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.481712-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 27250, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00010000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 15.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.481712-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 134000, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "134000", "old": "27250"}, "tasa_desgaste_actual_mm_km": {"new": "0.00040000", "old": "0.00010000"}, "profundidad_remanente_actual_mm": {"new": "12.50", "old": "15.00"}}	\N	\N
191	2025-05-26 22:07:33.484491-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.481712-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 134000, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.484491-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 27250, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "27250", "old": "134000"}, "profundidad_remanente_actual_mm": {"new": "10.00", "old": "12.50"}}	\N	\N
192	2025-05-26 22:07:33.484491-05	public	modelos_neumatico	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "activo": true, "medida": "295/80R22.5", "creado_en": "2025-05-19T12:21:17.269955-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "indice_carga": null, "fabricante_id": "00000000-0000-0000-0000-000000000001", "nombre_modelo": "X Line Energy Z", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": null, "indice_velocidad": null, "max_vidas_utiles": 5, "permite_reencauche": true, "reencauches_maximos": 0, "vida_util_teorica_km": null, "presion_recomendada_psi": null, "profundidad_original_mm": 15.00, "frecuencia_inspeccion_km": 5000, "posicion_uso_recomendada": "OTRO", "diseno_predominante_para_eje": "OTRO", "porcentaje_desgaste_por_vida": 10.00, "profundidad_minima_retiro_mm": 1.60, "tasa_desgaste_esperada_mm_km": null}	{"id": "00000000-0000-0000-0000-000000000001", "activo": true, "medida": "295/80R22.5", "creado_en": "2025-05-19T12:21:17.269955-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "indice_carga": null, "fabricante_id": "00000000-0000-0000-0000-000000000001", "nombre_modelo": "X Line Energy Z", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": null, "indice_velocidad": null, "max_vidas_utiles": 5, "permite_reencauche": true, "reencauches_maximos": 0, "vida_util_teorica_km": null, "presion_recomendada_psi": null, "profundidad_original_mm": 15.00, "frecuencia_inspeccion_km": 5000, "posicion_uso_recomendada": "OTRO", "diseno_predominante_para_eje": "OTRO", "porcentaje_desgaste_por_vida": 10.00, "profundidad_minima_retiro_mm": 3.00, "tasa_desgaste_esperada_mm_km": null}	{"profundidad_minima_retiro_mm": {"new": "3.00", "old": "1.60"}}	\N	SELECT * FROM probar_calculo_vida_util(10.0, 3.0, 0.0004);
193	2025-05-26 22:07:33.484491-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.484491-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 27250, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.484491-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 17500, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "17500", "old": "27250"}, "profundidad_remanente_actual_mm": {"new": "12.50", "old": "10.00"}}	\N	\N
194	2025-05-26 22:07:33.484491-05	public	modelos_neumatico	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "activo": true, "medida": "295/80R22.5", "creado_en": "2025-05-19T12:21:17.269955-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "indice_carga": null, "fabricante_id": "00000000-0000-0000-0000-000000000001", "nombre_modelo": "X Line Energy Z", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": null, "indice_velocidad": null, "max_vidas_utiles": 5, "permite_reencauche": true, "reencauches_maximos": 0, "vida_util_teorica_km": null, "presion_recomendada_psi": null, "profundidad_original_mm": 15.00, "frecuencia_inspeccion_km": 5000, "posicion_uso_recomendada": "OTRO", "diseno_predominante_para_eje": "OTRO", "porcentaje_desgaste_por_vida": 10.00, "profundidad_minima_retiro_mm": 3.00, "tasa_desgaste_esperada_mm_km": null}	{"id": "00000000-0000-0000-0000-000000000001", "activo": true, "medida": "295/80R22.5", "creado_en": "2025-05-19T12:21:17.269955-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "indice_carga": null, "fabricante_id": "00000000-0000-0000-0000-000000000001", "nombre_modelo": "X Line Energy Z", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": null, "indice_velocidad": null, "max_vidas_utiles": 5, "permite_reencauche": true, "reencauches_maximos": 0, "vida_util_teorica_km": null, "presion_recomendada_psi": null, "profundidad_original_mm": 15.00, "frecuencia_inspeccion_km": 5000, "posicion_uso_recomendada": "OTRO", "diseno_predominante_para_eje": "OTRO", "porcentaje_desgaste_por_vida": 10.00, "profundidad_minima_retiro_mm": 1.60, "tasa_desgaste_esperada_mm_km": null}	{"profundidad_minima_retiro_mm": {"new": "1.60", "old": "3.00"}}	\N	SELECT * FROM probar_calculo_vida_util(10.0, 3.0, 0.0004);
195	2025-05-26 22:07:33.487625-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.484491-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 17500, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.487625-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 27250, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 30.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "27250", "old": "17500"}, "profundidad_remanente_actual_mm": {"new": "30.00", "old": "12.50"}}	\N	\N
196	2025-05-26 22:07:33.487625-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.487625-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 27250, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 30.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.487625-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 71000, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "71000", "old": "27250"}, "profundidad_remanente_actual_mm": {"new": "12.50", "old": "30.00"}}	\N	\N
197	2025-05-26 22:07:33.490104-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.487625-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 71000, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.490104-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 27250, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00001000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 15.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "27250", "old": "71000"}, "tasa_desgaste_actual_mm_km": {"new": "0.00001000", "old": "0.00040000"}, "profundidad_remanente_actual_mm": {"new": "15.00", "old": "12.50"}}	\N	\N
198	2025-05-26 22:07:33.490104-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.490104-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 27250, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00001000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 15.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.490104-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 200000, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "200000", "old": "27250"}, "tasa_desgaste_actual_mm_km": {"new": "0.00040000", "old": "0.00001000"}, "profundidad_remanente_actual_mm": {"new": "12.50", "old": "15.00"}}	\N	\N
199	2025-05-26 22:07:33.492536-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.490104-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 200000, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.492536-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 27250, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": null, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "27250", "old": "200000"}, "profundidad_remanente_actual_mm": {"new": null, "old": "12.50"}}	\N	\N
200	2025-05-26 22:07:33.492536-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.492536-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 27250, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": null, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.492536-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": null, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": null, "old": "27250"}, "profundidad_remanente_actual_mm": {"new": "12.50", "old": null}}	\N	\N
201	2025-05-26 22:07:33.495238-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.492536-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": null, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.495238-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 27250, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 15.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "27250", "old": null}, "profundidad_remanente_actual_mm": {"new": "15.00", "old": "12.50"}}	\N	\N
202	2025-05-26 22:07:33.495238-05	public	modelos_neumatico	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "activo": true, "medida": "295/80R22.5", "creado_en": "2025-05-19T12:21:17.269955-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "indice_carga": null, "fabricante_id": "00000000-0000-0000-0000-000000000001", "nombre_modelo": "X Line Energy Z", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": null, "indice_velocidad": null, "max_vidas_utiles": 5, "permite_reencauche": true, "reencauches_maximos": 0, "vida_util_teorica_km": null, "presion_recomendada_psi": null, "profundidad_original_mm": 15.00, "frecuencia_inspeccion_km": 5000, "posicion_uso_recomendada": "OTRO", "diseno_predominante_para_eje": "OTRO", "porcentaje_desgaste_por_vida": 10.00, "profundidad_minima_retiro_mm": 1.60, "tasa_desgaste_esperada_mm_km": null}	{"id": "00000000-0000-0000-0000-000000000001", "activo": true, "medida": "295/80R22.5", "creado_en": "2025-05-19T12:21:17.269955-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "indice_carga": null, "fabricante_id": "00000000-0000-0000-0000-000000000001", "nombre_modelo": "X Line Energy Z", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": null, "indice_velocidad": null, "max_vidas_utiles": 5, "permite_reencauche": true, "reencauches_maximos": 0, "vida_util_teorica_km": null, "presion_recomendada_psi": null, "profundidad_original_mm": 15.00, "frecuencia_inspeccion_km": 5000, "posicion_uso_recomendada": "OTRO", "diseno_predominante_para_eje": "OTRO", "porcentaje_desgaste_por_vida": 10.00, "profundidad_minima_retiro_mm": null, "tasa_desgaste_esperada_mm_km": null}	{"profundidad_minima_retiro_mm": {"new": null, "old": "1.60"}}	\N	SELECT * FROM probar_calculo_vida_util(15.0, NULL, 0.0004);
203	2025-05-26 22:07:33.495238-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.495238-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 27250, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 15.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.495238-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 33500, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "33500", "old": "27250"}, "profundidad_remanente_actual_mm": {"new": "12.50", "old": "15.00"}}	\N	\N
204	2025-05-26 22:07:33.495238-05	public	modelos_neumatico	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "activo": true, "medida": "295/80R22.5", "creado_en": "2025-05-19T12:21:17.269955-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "indice_carga": null, "fabricante_id": "00000000-0000-0000-0000-000000000001", "nombre_modelo": "X Line Energy Z", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": null, "indice_velocidad": null, "max_vidas_utiles": 5, "permite_reencauche": true, "reencauches_maximos": 0, "vida_util_teorica_km": null, "presion_recomendada_psi": null, "profundidad_original_mm": 15.00, "frecuencia_inspeccion_km": 5000, "posicion_uso_recomendada": "OTRO", "diseno_predominante_para_eje": "OTRO", "porcentaje_desgaste_por_vida": 10.00, "profundidad_minima_retiro_mm": null, "tasa_desgaste_esperada_mm_km": null}	{"id": "00000000-0000-0000-0000-000000000001", "activo": true, "medida": "295/80R22.5", "creado_en": "2025-05-19T12:21:17.269955-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "indice_carga": null, "fabricante_id": "00000000-0000-0000-0000-000000000001", "nombre_modelo": "X Line Energy Z", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": null, "indice_velocidad": null, "max_vidas_utiles": 5, "permite_reencauche": true, "reencauches_maximos": 0, "vida_util_teorica_km": null, "presion_recomendada_psi": null, "profundidad_original_mm": 15.00, "frecuencia_inspeccion_km": 5000, "posicion_uso_recomendada": "OTRO", "diseno_predominante_para_eje": "OTRO", "porcentaje_desgaste_por_vida": 10.00, "profundidad_minima_retiro_mm": 1.60, "tasa_desgaste_esperada_mm_km": null}	{"profundidad_minima_retiro_mm": {"new": "1.60", "old": null}}	\N	SELECT * FROM probar_calculo_vida_util(15.0, NULL, 0.0004);
205	2025-05-26 22:07:33.499288-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.495238-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 33500, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.499288-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 27250, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 15.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "27250", "old": "33500"}, "tasa_desgaste_actual_mm_km": {"new": null, "old": "0.00040000"}, "profundidad_remanente_actual_mm": {"new": "15.00", "old": "12.50"}}	\N	\N
206	2025-05-26 22:07:33.499288-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.499288-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 27250, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 15.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.499288-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 26800, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "26800", "old": "27250"}, "tasa_desgaste_actual_mm_km": {"new": "0.00040000", "old": null}, "profundidad_remanente_actual_mm": {"new": "12.50", "old": "15.00"}}	\N	\N
207	2025-05-27 01:42:58.635408-05	public	modelos_neumatico	UPDATE	postgres	\N	\N	\N	\N	51bec9d7-c28c-4273-a79e-f9388e54130f	{"id": "51bec9d7-c28c-4273-a79e-f9388e54130f", "activo": true, "medida": "295/80R22.5", "creado_en": "2025-05-19T21:44:38.282601-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "indice_carga": null, "fabricante_id": "00000000-0000-0000-0000-000000000001", "nombre_modelo": "X-MULTI Z", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": null, "indice_velocidad": null, "max_vidas_utiles": 5, "permite_reencauche": false, "reencauches_maximos": 0, "vida_util_teorica_km": null, "presion_recomendada_psi": null, "profundidad_original_mm": 15.00, "frecuencia_inspeccion_km": 5000, "posicion_uso_recomendada": "DIRECCION", "diseno_predominante_para_eje": "OTRO", "porcentaje_desgaste_por_vida": 10.00, "profundidad_minima_retiro_mm": 1.60, "tasa_desgaste_esperada_mm_km": null}	{"id": "51bec9d7-c28c-4273-a79e-f9388e54130f", "activo": true, "medida": "295/80R22.5", "creado_en": "2025-05-19T21:44:38.282601-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "indice_carga": null, "fabricante_id": "00000000-0000-0000-0000-000000000001", "nombre_modelo": "X-MULTI Z", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": null, "indice_velocidad": null, "max_vidas_utiles": 5, "permite_reencauche": false, "reencauches_maximos": 0, "vida_util_teorica_km": null, "presion_recomendada_psi": null, "profundidad_original_mm": 15.00, "frecuencia_inspeccion_km": 5000, "posicion_uso_recomendada": "DIRECCION", "diseno_predominante_para_eje": "OTRO", "porcentaje_desgaste_por_vida": 10.00, "profundidad_minima_retiro_mm": 1.60, "tasa_desgaste_esperada_mm_km": 0.00010000}	{"tasa_desgaste_esperada_mm_km": {"new": "0.00010000", "old": null}}	\N	UPDATE modelos_neumatico\nSET tasa_desgaste_esperada_mm_km = 0.0001\nWHERE tasa_desgaste_esperada_mm_km IS NULL\nRETURNING id, nombre_modelo, tasa_desgaste_esperada_mm_km;
208	2025-05-27 01:42:58.635408-05	public	modelos_neumatico	UPDATE	postgres	\N	\N	\N	\N	55f58bfd-2dfb-4bdb-b9b6-1b3da75a867e	{"id": "55f58bfd-2dfb-4bdb-b9b6-1b3da75a867e", "activo": true, "medida": "295/80R22.5", "creado_en": "2025-05-19T21:44:38.282601-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "indice_carga": null, "fabricante_id": "00000000-0000-0000-0000-000000000001", "nombre_modelo": "X-MULTI D2", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": null, "indice_velocidad": null, "max_vidas_utiles": 5, "permite_reencauche": false, "reencauches_maximos": 0, "vida_util_teorica_km": null, "presion_recomendada_psi": null, "profundidad_original_mm": 15.00, "frecuencia_inspeccion_km": 5000, "posicion_uso_recomendada": "TRACCION", "diseno_predominante_para_eje": "OTRO", "porcentaje_desgaste_por_vida": 10.00, "profundidad_minima_retiro_mm": 1.60, "tasa_desgaste_esperada_mm_km": null}	{"id": "55f58bfd-2dfb-4bdb-b9b6-1b3da75a867e", "activo": true, "medida": "295/80R22.5", "creado_en": "2025-05-19T21:44:38.282601-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "indice_carga": null, "fabricante_id": "00000000-0000-0000-0000-000000000001", "nombre_modelo": "X-MULTI D2", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": null, "indice_velocidad": null, "max_vidas_utiles": 5, "permite_reencauche": false, "reencauches_maximos": 0, "vida_util_teorica_km": null, "presion_recomendada_psi": null, "profundidad_original_mm": 15.00, "frecuencia_inspeccion_km": 5000, "posicion_uso_recomendada": "TRACCION", "diseno_predominante_para_eje": "OTRO", "porcentaje_desgaste_por_vida": 10.00, "profundidad_minima_retiro_mm": 1.60, "tasa_desgaste_esperada_mm_km": 0.00010000}	{"tasa_desgaste_esperada_mm_km": {"new": "0.00010000", "old": null}}	\N	UPDATE modelos_neumatico\nSET tasa_desgaste_esperada_mm_km = 0.0001\nWHERE tasa_desgaste_esperada_mm_km IS NULL\nRETURNING id, nombre_modelo, tasa_desgaste_esperada_mm_km;
337	2025-05-27 17:30:47.047877-05	public	neumaticos	INSERT	postgres	\N	\N	\N	\N	ea9a2fba-6917-47cd-9728-46a74f0e22a3	\N	{"id": "ea9a2fba-6917-47cd-9728-46a74f0e22a3", "dot": null, "activo": true, "creado_en": "2025-05-27T17:30:47.047877-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-e319998dbf", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T17:30:47.047877-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T17:30:47.047877-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	\N	\N	\N
355	2025-05-27 18:31:12.002237-05	public	neumaticos	INSERT	postgres	\N	\N	\N	\N	0e2f0e46-2da7-4880-8af1-42518ac26c15	\N	{"id": "0e2f0e46-2da7-4880-8af1-42518ac26c15", "dot": null, "activo": true, "creado_en": "2025-05-27T18:31:12.002237-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-beb9612d4b", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:31:12.002237-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:31:12.002237-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	\N	\N	\N
356	2025-05-27 18:31:12.012882-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	0e2f0e46-2da7-4880-8af1-42518ac26c15	{"id": "0e2f0e46-2da7-4880-8af1-42518ac26c15", "dot": null, "activo": true, "creado_en": "2025-05-27T18:31:12.002237-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-beb9612d4b", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:31:12.002237-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:31:12.002237-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "0e2f0e46-2da7-4880-8af1-42518ac26c15", "dot": null, "activo": true, "creado_en": "2025-05-27T18:31:12.002237-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-beb9612d4b", "estado_actual": "EN_REENCAUCHE", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:31:12.002237-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:31:12.012882-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"estado_actual": {"new": "EN_REENCAUCHE", "old": "INSTALADO"}, "fecha_ultimo_evento": {"new": "2025-05-27T18:31:12.012882-05:00", "old": "2025-05-27T18:31:12.002237-05:00"}, "ubicacion_actual_posicion_id": {"new": null, "old": "dddddddd-dddd-dddd-dddd-dddddddddddd"}, "ubicacion_actual_vehiculo_id": {"new": null, "old": "06abeeaf-0d42-4032-94a8-c46f3d6ee709"}}	\N	\N
357	2025-05-27 18:31:12.012882-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	0e2f0e46-2da7-4880-8af1-42518ac26c15	{"id": "0e2f0e46-2da7-4880-8af1-42518ac26c15", "dot": null, "activo": true, "creado_en": "2025-05-27T18:31:12.002237-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-beb9612d4b", "estado_actual": "EN_REENCAUCHE", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:31:12.002237-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:31:12.012882-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "0e2f0e46-2da7-4880-8af1-42518ac26c15", "dot": null, "activo": true, "creado_en": "2025-05-27T18:31:12.002237-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-beb9612d4b", "estado_actual": "EN_REENCAUCHE", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:31:12.012882-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:31:12.012882-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"profundidad_inicio_vida_actual_mm": {"new": null, "old": "15.00"}}	\N	\N
213	2025-05-27 02:49:44.337832-05	public	fabricantes_neumatico	INSERT	postgres	\N	\N	\N	\N	11111111-1111-1111-1111-111111111110	\N	{"id": "11111111-1111-1111-1111-111111111110", "activo": true, "nombre": "Fabricante de Prueba", "creado_en": "2025-05-27T02:49:44.337832-05:00", "sitio_web": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "pais_origen": "País de Prueba", "actualizado_en": null, "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "codigo_abreviado": null}	\N	\N	INSERT INTO fabricantes_neumatico (id, nombre, pais_origen, activo, creado_por, actualizado_por)\nSELECT \n    '11111111-1111-1111-1111-111111111110',\n    'Fabricante de Prueba',\n    'País de Prueba',\n    true,\n    (SELECT id FROM usuarios LIMIT 1),\n    (SELECT id FROM usuarios LIMIT 1)\nWHERE NOT EXISTS (\n    SELECT 1 FROM fabricantes_neumatico WHERE id = '11111111-1111-1111-1111-111111111110'\n);
214	2025-05-27 02:49:44.348094-05	public	modelos_neumatico	INSERT	postgres	\N	\N	\N	\N	11111111-1111-1111-1111-111111111111	\N	{"id": "11111111-1111-1111-1111-111111111111", "activo": true, "medida": "295/75R22.5", "creado_en": "2025-05-27T02:49:44.348094-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "indice_carga": null, "fabricante_id": "11111111-1111-1111-1111-111111111110", "nombre_modelo": "Neumático de Prueba", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "indice_velocidad": null, "max_vidas_utiles": 5, "permite_reencauche": false, "reencauches_maximos": 0, "vida_util_teorica_km": null, "presion_recomendada_psi": null, "profundidad_original_mm": 16.00, "frecuencia_inspeccion_km": 5000, "posicion_uso_recomendada": null, "diseno_predominante_para_eje": null, "porcentaje_desgaste_por_vida": 10.00, "profundidad_minima_retiro_mm": 2.00, "tasa_desgaste_esperada_mm_km": 0.00010000}	\N	\N	INSERT INTO modelos_neumatico (\n    id, fabricante_id, nombre_modelo, medida, \n    profundidad_original_mm, profundidad_minima_retiro_mm,\n    tasa_desgaste_esperada_mm_km, activo,\n    creado_por, actualizado_por\n) VALUES (\n    '11111111-1111-1111-1111-111111111111', \n    '11111111-1111-1111-1111-111111111110',\n    'Neumático de Prueba', \n    '295/75R22.5',\n    16.0, 2.0, 0.0001, true,\n    (SELECT id FROM usuarios LIMIT 1),\n    (SELECT id FROM usuarios LIMIT 1)\n) ON CONFLICT (id) DO NOTHING;
215	2025-05-27 02:55:14.384488-05	public	neumaticos	INSERT	postgres	\N	\N	\N	\N	55555555-5555-5555-5555-555555555555	\N	{"id": "55555555-5555-5555-5555-555555555555", "dot": null, "activo": true, "creado_en": "2025-05-27T02:55:14.384488-05:00", "modelo_id": "51bec9d7-c28c-4273-a79e-f9388e54130f", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-NEW-001", "estado_actual": "EN_STOCK", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-27T02:55:14.384488-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": null, "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 15.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	\N	\N	\N
216	2025-05-27 02:56:45.653215-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	55555555-5555-5555-5555-555555555555	{"id": "55555555-5555-5555-5555-555555555555", "dot": null, "activo": true, "creado_en": "2025-05-27T02:55:14.384488-05:00", "modelo_id": "51bec9d7-c28c-4273-a79e-f9388e54130f", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-NEW-001", "estado_actual": "EN_STOCK", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-27T02:55:14.384488-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": null, "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 15.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "55555555-5555-5555-5555-555555555555", "dot": null, "activo": true, "creado_en": "2025-05-27T02:55:14.384488-05:00", "modelo_id": "51bec9d7-c28c-4273-a79e-f9388e54130f", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-NEW-001", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-27T02:56:45.653215-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T02:56:45.653215-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": "2025-05-27", "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 15.00, "odometro_instalacion_vida_actual": 10000, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"estado_actual": {"new": "INSTALADO", "old": "EN_STOCK"}, "fecha_ultimo_evento": {"new": "2025-05-27T02:56:45.653215-05:00", "old": null}, "fecha_inicio_vida_actual": {"new": "2025-05-27", "old": null}, "ubicacion_actual_posicion_id": {"new": "dddddddd-dddd-dddd-dddd-dddddddddddd", "old": null}, "ubicacion_actual_vehiculo_id": {"new": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "old": null}, "odometro_instalacion_vida_actual": {"new": "10000", "old": null}, "profundidad_inicio_vida_actual_mm": {"new": "15.00", "old": null}}	\N	\N
217	2025-05-27 02:56:45.653215-05	public	eventos_neumaticos	INSERT	postgres	\N	\N	\N	\N	accbaa2c-247e-4f1d-b768-9803ad5d113d	\N	{"id": "accbaa2c-247e-4f1d-b768-9803ad5d113d", "notas": "Prueba de instalación de neumático nuevo", "creado_en": "2025-05-27T02:56:45.653215-05:00", "usuario_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "presion_psi": 110.00, "tipo_evento": "INSTALACION", "vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "costo_evento": null, "datos_evento": {"profundidad_inicio_vida_actual_mm_registrada": 15.00}, "moneda_costo": "PEN", "neumatico_id": "55555555-5555-5555-5555-555555555555", "tipo_ruta_id": null, "timestamp_evento": "2025-05-27T02:56:45.653215-05:00", "almacen_destino_id": null, "destino_desmontaje": null, "proveedor_servicio_id": null, "motivo_reparacion_texto": null, "motivo_desecho_id_evento": null, "profundidad_remanente_mm": 15.00, "relacion_evento_anterior": null, "tipo_dano_detectado_texto": null, "odometro_vehiculo_en_evento": 10000, "peso_carga_promedio_ton_evento": null, "profundidad_post_reencauche_mm": null}	\N	\N	\N
218	2025-05-27 03:01:19.763414-05	public	neumaticos	INSERT	postgres	\N	\N	\N	\N	66666666-6666-6666-6666-666666666666	\N	{"id": "66666666-6666-6666-6666-666666666666", "dot": null, "activo": true, "creado_en": "2025-05-27T03:01:19.763414-05:00", "modelo_id": "51bec9d7-c28c-4273-a79e-f9388e54130f", "sensor_id": null, "creado_por": null, "vida_actual": 2, "costo_compra": 750.00, "fecha_compra": "2024-11-28", "numero_serie": "TEST-USED-001", "estado_actual": "EN_STOCK", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-27T03:01:19.763414-05:00", "actualizado_por": null, "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": null, "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 15000, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": 50000, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	\N	\N	\N
219	2025-05-27 03:01:19.771471-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	66666666-6666-6666-6666-666666666666	{"id": "66666666-6666-6666-6666-666666666666", "dot": null, "activo": true, "creado_en": "2025-05-27T03:01:19.763414-05:00", "modelo_id": "51bec9d7-c28c-4273-a79e-f9388e54130f", "sensor_id": null, "creado_por": null, "vida_actual": 2, "costo_compra": 750.00, "fecha_compra": "2024-11-28", "numero_serie": "TEST-USED-001", "estado_actual": "EN_STOCK", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-27T03:01:19.763414-05:00", "actualizado_por": null, "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": null, "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 15000, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": 50000, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "66666666-6666-6666-6666-666666666666", "dot": null, "activo": true, "creado_en": "2025-05-27T03:01:19.763414-05:00", "modelo_id": "51bec9d7-c28c-4273-a79e-f9388e54130f", "sensor_id": null, "creado_por": null, "vida_actual": 2, "costo_compra": 750.00, "fecha_compra": "2024-11-28", "numero_serie": "TEST-USED-001", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-27T03:01:19.771471-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T03:01:19.771471-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": 109000, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": "2025-05-27", "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": 65000, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 12.50}	{"estado_actual": {"new": "INSTALADO", "old": "EN_STOCK"}, "fecha_ultimo_evento": {"new": "2025-05-27T03:01:19.771471-05:00", "old": null}, "vida_util_restante_km": {"new": "109000", "old": null}, "kilometraje_vida_actual": {"new": "0", "old": "15000"}, "fecha_inicio_vida_actual": {"new": "2025-05-27", "old": null}, "ubicacion_actual_posicion_id": {"new": "dddddddd-dddd-dddd-dddd-dddddddddddd", "old": null}, "ubicacion_actual_vehiculo_id": {"new": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "old": null}, "odometro_instalacion_vida_actual": {"new": "65000", "old": "50000"}, "profundidad_inicio_vida_actual_mm": {"new": "12.50", "old": "15.00"}}	\N	\N
220	2025-05-27 03:01:19.771471-05	public	eventos_neumaticos	INSERT	postgres	\N	\N	\N	\N	86bcd99a-8cd1-411b-bdff-56bea06ab0b5	\N	{"id": "86bcd99a-8cd1-411b-bdff-56bea06ab0b5", "notas": "Prueba de instalación de neumático usado (vida > 1)", "creado_en": "2025-05-27T03:01:19.771471-05:00", "usuario_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "presion_psi": 105.00, "tipo_evento": "INSTALACION", "vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "costo_evento": null, "datos_evento": {"profundidad_inicio_vida_actual_mm_registrada": 12.50}, "moneda_costo": "PEN", "neumatico_id": "66666666-6666-6666-6666-666666666666", "tipo_ruta_id": null, "timestamp_evento": "2025-05-27T03:01:19.771471-05:00", "almacen_destino_id": null, "destino_desmontaje": null, "proveedor_servicio_id": null, "motivo_reparacion_texto": null, "motivo_desecho_id_evento": null, "profundidad_remanente_mm": 12.50, "relacion_evento_anterior": null, "tipo_dano_detectado_texto": null, "odometro_vehiculo_en_evento": 65000, "peso_carga_promedio_ton_evento": null, "profundidad_post_reencauche_mm": null}	\N	\N	\N
221	2025-05-27 03:18:49.597271-05	public	neumaticos	INSERT	postgres	\N	\N	\N	\N	11111111-1111-1111-1111-111111111111	\N	{"id": "11111111-1111-1111-1111-111111111111", "dot": null, "activo": true, "creado_en": "2025-05-27T03:18:49.597271-05:00", "modelo_id": "51bec9d7-c28c-4273-a79e-f9388e54130f", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-INST-001", "estado_actual": "EN_STOCK", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-27T03:18:49.597271-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": null, "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 15.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	\N	\N	\N
366	2025-05-27 18:32:00.312736-05	public	eventos_neumaticos	INSERT	postgres	\N	\N	\N	\N	b7e050ab-829c-4127-a8aa-147ced3084e4	\N	{"id": "b7e050ab-829c-4127-a8aa-147ced3084e4", "notas": null, "creado_en": "2025-05-27T18:32:00.312736-05:00", "usuario_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "presion_psi": null, "tipo_evento": "DESMONTAJE", "vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "costo_evento": null, "datos_evento": {"es_retirado": false, "vida_actual": 1, "vidas_maximas": 5, "es_recuperable": true, "kilometraje_vida_actual": 0, "tasa_desgaste_actual_mm_km": null, "profundidad_remanente_actual_mm": 10.00, "profundidad_inicio_vida_actual_mm": 15.00}, "moneda_costo": "PEN", "neumatico_id": "3d986345-b3fb-4dd1-90b2-346934941389", "tipo_ruta_id": null, "timestamp_evento": "2025-05-27T18:32:00.312736-05:00", "almacen_destino_id": null, "destino_desmontaje": "EN_REENCAUCHE", "proveedor_servicio_id": null, "motivo_reparacion_texto": null, "motivo_desecho_id_evento": null, "profundidad_remanente_mm": null, "relacion_evento_anterior": null, "tipo_dano_detectado_texto": null, "odometro_vehiculo_en_evento": 10000, "peso_carga_promedio_ton_evento": null, "profundidad_post_reencauche_mm": null}	\N	\N	\N
367	2025-05-27 18:55:48.92463-05	public	neumaticos	INSERT	postgres	\N	\N	\N	\N	9046ee36-f52f-4737-a621-24393ae7b2f9	\N	{"id": "9046ee36-f52f-4737-a621-24393ae7b2f9", "dot": null, "activo": true, "creado_en": "2025-05-27T18:55:48.92463-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-44b9414fc0", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "USD", "actualizado_en": "2025-05-27T18:55:48.92463-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:55:48.92463-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": 10000, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	\N	\N	\N
368	2025-05-27 18:56:24.081571-05	public	neumaticos	INSERT	postgres	\N	\N	\N	\N	7bdb45b1-070c-4285-89e5-4afe1e09758f	\N	{"id": "7bdb45b1-070c-4285-89e5-4afe1e09758f", "dot": null, "activo": true, "creado_en": "2025-05-27T18:56:24.081571-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-ef3f24635b", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "USD", "actualizado_en": "2025-05-27T18:56:24.081571-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:56:24.081571-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": 10000, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	\N	\N	\N
370	2025-05-27 18:58:21.265831-05	public	neumaticos	INSERT	postgres	\N	\N	\N	\N	1c47f273-0577-428c-b8ff-060b36cae727	\N	{"id": "1c47f273-0577-428c-b8ff-060b36cae727", "dot": null, "activo": true, "creado_en": "2025-05-27T18:58:21.265831-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-01c6fd8707", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "USD", "actualizado_en": "2025-05-27T18:58:21.265831-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:58:21.265831-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": 10000, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	\N	\N	\N
372	2025-05-27 19:00:01.354643-05	public	neumaticos	INSERT	postgres	\N	\N	\N	\N	952a0f71-37dd-46ec-a742-68edbb5b4949	\N	{"id": "952a0f71-37dd-46ec-a742-68edbb5b4949", "dot": null, "activo": true, "creado_en": "2025-05-27T19:00:01.354643-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-7fa42f2fbf", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "USD", "actualizado_en": "2025-05-27T19:00:01.354643-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T19:00:01.354643-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": 10000, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	\N	\N	\N
374	2025-05-27 19:01:52.342075-05	public	neumaticos	INSERT	postgres	\N	\N	\N	\N	48f567fc-bda6-439c-8d94-d4fcf1dab095	\N	{"id": "48f567fc-bda6-439c-8d94-d4fcf1dab095", "dot": null, "activo": true, "creado_en": "2025-05-27T19:01:52.342075-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-9430046ec8", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "USD", "actualizado_en": "2025-05-27T19:01:52.342075-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T19:01:52.342075-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": 10000, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	\N	\N	\N
376	2025-05-27 19:03:39.721738-05	public	neumaticos	INSERT	postgres	\N	\N	\N	\N	39e353da-8436-4822-ac54-3f8952196e39	\N	{"id": "39e353da-8436-4822-ac54-3f8952196e39", "dot": null, "activo": true, "creado_en": "2025-05-27T19:03:39.721738-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-a65efc0e6b", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "USD", "actualizado_en": "2025-05-27T19:03:39.721738-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T19:03:39.721738-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": 10000, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	\N	\N	\N
378	2025-05-27 19:05:24.446863-05	public	neumaticos	INSERT	postgres	\N	\N	\N	\N	fdb5b128-2182-4cbe-848a-abb9dc7706e1	\N	{"id": "fdb5b128-2182-4cbe-848a-abb9dc7706e1", "dot": null, "activo": true, "creado_en": "2025-05-27T19:05:24.446863-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-87a215158d", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "USD", "actualizado_en": "2025-05-27T19:05:24.446863-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T19:05:24.446863-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": 10000, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	\N	\N	\N
380	2025-05-27 19:05:24.457336-05	public	eventos_neumaticos	INSERT	postgres	\N	\N	\N	\N	81d63ed6-64c9-4758-ac7d-8802918b062f	\N	{"id": "81d63ed6-64c9-4758-ac7d-8802918b062f", "notas": null, "creado_en": "2025-05-27T19:05:24.457336-05:00", "usuario_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "presion_psi": null, "tipo_evento": "DESMONTAJE", "vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "costo_evento": null, "datos_evento": {"motivo": "Prueba de desmontaje", "test_id": "TEST-DESM-36495e21"}, "moneda_costo": "PEN", "neumatico_id": "fdb5b128-2182-4cbe-848a-abb9dc7706e1", "tipo_ruta_id": null, "timestamp_evento": "2025-05-27T19:05:24.457336-05:00", "almacen_destino_id": null, "destino_desmontaje": "EN_REENCAUCHE", "proveedor_servicio_id": null, "motivo_reparacion_texto": null, "motivo_desecho_id_evento": null, "profundidad_remanente_mm": 8.50, "relacion_evento_anterior": null, "tipo_dano_detectado_texto": null, "odometro_vehiculo_en_evento": 15000, "peso_carga_promedio_ton_evento": null, "profundidad_post_reencauche_mm": null}	\N	\N	\N
381	2025-05-27 19:39:10.658464-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	55555555-5555-5555-5555-555555555555	{"id": "55555555-5555-5555-5555-555555555555", "dot": null, "activo": true, "creado_en": "2025-05-27T02:55:14.384488-05:00", "modelo_id": "51bec9d7-c28c-4273-a79e-f9388e54130f", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-NEW-001", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-27T02:56:45.653215-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T02:56:45.653215-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": "2025-05-27", "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 15.00, "odometro_instalacion_vida_actual": 10000, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "55555555-5555-5555-5555-555555555555", "dot": null, "activo": true, "creado_en": "2025-05-27T02:55:14.384488-05:00", "modelo_id": "51bec9d7-c28c-4273-a79e-f9388e54130f", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-NEW-001", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T02:56:45.653215-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": 134000, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": "2025-05-27", "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 15.00, "odometro_instalacion_vida_actual": 10000, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"vida_util_restante_km": {"new": "134000", "old": null}}	\N	\N
382	2025-05-27 19:39:10.658464-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	11111111-1111-1111-1111-111111111111	{"id": "11111111-1111-1111-1111-111111111111", "dot": null, "activo": true, "creado_en": "2025-05-27T03:18:49.597271-05:00", "modelo_id": "51bec9d7-c28c-4273-a79e-f9388e54130f", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-INST-001", "estado_actual": "EN_STOCK", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-27T03:18:49.597271-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": null, "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 15.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "11111111-1111-1111-1111-111111111111", "dot": null, "activo": true, "creado_en": "2025-05-27T03:18:49.597271-05:00", "modelo_id": "51bec9d7-c28c-4273-a79e-f9388e54130f", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-INST-001", "estado_actual": "EN_STOCK", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": null, "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": 134000, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 15.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "134000", "old": null}}	\N	\N
383	2025-05-27 19:39:10.658464-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	7c61a3cd-97c1-4442-858f-0d7e5d3bb68e	{"id": "7c61a3cd-97c1-4442-858f-0d7e5d3bb68e", "dot": null, "activo": true, "creado_en": "2025-05-23T00:15:26.760524-05:00", "modelo_id": "eef2159d-1098-49d6-ae0f-b795a8f4c968", "sensor_id": null, "creado_por": null, "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-23", "numero_serie": "TEST-c136b84f", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-23T00:15:26.760524-05:00", "actualizado_por": null, "es_reencauchado": false, "fecha_fabricacion": "2025-04-23", "motivo_desecho_id": null, "fecha_ultimo_evento": null, "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 15000, "vida_util_restante_km": 550, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": "2025-04-23", "proxima_inspeccion_fecha": "2025-06-08", "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "00000000-0000-0000-0000-000000000001", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 8.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "7c61a3cd-97c1-4442-858f-0d7e5d3bb68e", "dot": null, "activo": true, "creado_en": "2025-05-23T00:15:26.760524-05:00", "modelo_id": "eef2159d-1098-49d6-ae0f-b795a8f4c968", "sensor_id": null, "creado_por": null, "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-23", "numero_serie": "TEST-c136b84f", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": null, "es_reencauchado": false, "fecha_fabricacion": "2025-04-23", "motivo_desecho_id": null, "fecha_ultimo_evento": null, "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 15000, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": "2025-04-23", "proxima_inspeccion_fecha": "2025-06-08", "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "00000000-0000-0000-0000-000000000001", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 8.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": null, "old": "550"}}	\N	\N
384	2025-05-27 19:39:10.658464-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	23e8641a-e649-45d5-86d2-914c1f546f77	{"id": "23e8641a-e649-45d5-86d2-914c1f546f77", "dot": null, "activo": true, "creado_en": "2025-05-23T00:17:54.377345-05:00", "modelo_id": "86050a4c-a11f-4471-a3a1-922b3d49d3b3", "sensor_id": null, "creado_por": null, "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-23", "numero_serie": "TEST-24fceded", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-23T00:17:54.377345-05:00", "actualizado_por": null, "es_reencauchado": false, "fecha_fabricacion": "2025-04-23", "motivo_desecho_id": null, "fecha_ultimo_evento": null, "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 15000, "vida_util_restante_km": 550, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": "2025-04-23", "proxima_inspeccion_fecha": "2025-06-08", "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "0d7a489a-44b4-40e6-a957-3dd294416c85", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 8.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "23e8641a-e649-45d5-86d2-914c1f546f77", "dot": null, "activo": true, "creado_en": "2025-05-23T00:17:54.377345-05:00", "modelo_id": "86050a4c-a11f-4471-a3a1-922b3d49d3b3", "sensor_id": null, "creado_por": null, "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-23", "numero_serie": "TEST-24fceded", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": null, "es_reencauchado": false, "fecha_fabricacion": "2025-04-23", "motivo_desecho_id": null, "fecha_ultimo_evento": null, "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 15000, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": "2025-04-23", "proxima_inspeccion_fecha": "2025-06-08", "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "0d7a489a-44b4-40e6-a957-3dd294416c85", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 8.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": null, "old": "550"}}	\N	\N
385	2025-05-27 19:39:10.658464-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	00000000-0000-0000-0000-000000000001	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-26T22:07:33.499288-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 26800, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "00000000-0000-0000-0000-000000000001", "dot": null, "activo": true, "creado_en": "2025-05-19T12:32:03.435954-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": null, "fecha_compra": "2025-05-19", "numero_serie": "SN-DEL-IZQ-001", "estado_actual": "EN_REPARACION", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-26T21:13:31.459054-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": 5000, "vida_util_restante_km": 27250, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00040000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 12.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "27250", "old": "26800"}}	\N	\N
386	2025-05-27 19:39:10.658464-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	0dd8d980-1fbb-4611-8298-038a69bc9582	{"id": "0dd8d980-1fbb-4611-8298-038a69bc9582", "dot": null, "activo": true, "creado_en": "2025-05-27T17:19:14.217844-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-f680f19ec5", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T17:19:14.217844-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T17:19:14.217844-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "0dd8d980-1fbb-4611-8298-038a69bc9582", "dot": null, "activo": true, "creado_en": "2025-05-27T17:19:14.217844-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-f680f19ec5", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T17:19:14.217844-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": 84000, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"vida_util_restante_km": {"new": "84000", "old": null}}	\N	\N
387	2025-05-27 19:39:10.658464-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	8b879b54-eda4-4bc6-9593-cd5242588d7c	{"id": "8b879b54-eda4-4bc6-9593-cd5242588d7c", "dot": null, "activo": true, "creado_en": "2025-05-27T17:20:05.119664-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-d567ce9a81", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T17:20:05.119664-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T17:20:05.119664-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "8b879b54-eda4-4bc6-9593-cd5242588d7c", "dot": null, "activo": true, "creado_en": "2025-05-27T17:20:05.119664-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-d567ce9a81", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T17:20:05.119664-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": 84000, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"vida_util_restante_km": {"new": "84000", "old": null}}	\N	\N
388	2025-05-27 19:39:10.658464-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	60e9e8c8-0648-4f57-ba3b-8f5c62ea36eb	{"id": "60e9e8c8-0648-4f57-ba3b-8f5c62ea36eb", "dot": null, "activo": true, "creado_en": "2025-05-27T17:22:19.80177-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-0407b809cd", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T17:22:19.80177-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T17:22:19.80177-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "60e9e8c8-0648-4f57-ba3b-8f5c62ea36eb", "dot": null, "activo": true, "creado_en": "2025-05-27T17:22:19.80177-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-0407b809cd", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T17:22:19.80177-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": 84000, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"vida_util_restante_km": {"new": "84000", "old": null}}	\N	\N
389	2025-05-27 19:39:10.658464-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	060366ed-07ec-4d0d-8d3d-f97821717ffb	{"id": "060366ed-07ec-4d0d-8d3d-f97821717ffb", "dot": null, "activo": true, "creado_en": "2025-05-27T17:23:33.700102-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-98cf53c501", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T17:23:33.700102-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T17:23:33.700102-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "060366ed-07ec-4d0d-8d3d-f97821717ffb", "dot": null, "activo": true, "creado_en": "2025-05-27T17:23:33.700102-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-98cf53c501", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T17:23:33.700102-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": 84000, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"vida_util_restante_km": {"new": "84000", "old": null}}	\N	\N
390	2025-05-27 19:39:10.658464-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	877231d5-7c90-42ae-b216-83c15e931ae7	{"id": "877231d5-7c90-42ae-b216-83c15e931ae7", "dot": null, "activo": true, "creado_en": "2025-05-27T17:28:34.297643-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-c17bc3dbd3", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T17:28:34.297643-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T17:28:34.297643-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "877231d5-7c90-42ae-b216-83c15e931ae7", "dot": null, "activo": true, "creado_en": "2025-05-27T17:28:34.297643-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-c17bc3dbd3", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T17:28:34.297643-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": 84000, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"vida_util_restante_km": {"new": "84000", "old": null}}	\N	\N
391	2025-05-27 19:39:10.658464-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	ea9a2fba-6917-47cd-9728-46a74f0e22a3	{"id": "ea9a2fba-6917-47cd-9728-46a74f0e22a3", "dot": null, "activo": true, "creado_en": "2025-05-27T17:30:47.047877-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-e319998dbf", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T17:30:47.047877-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T17:30:47.047877-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "ea9a2fba-6917-47cd-9728-46a74f0e22a3", "dot": null, "activo": true, "creado_en": "2025-05-27T17:30:47.047877-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-e319998dbf", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T17:30:47.047877-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": 84000, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"vida_util_restante_km": {"new": "84000", "old": null}}	\N	\N
392	2025-05-27 19:39:10.658464-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	e9c3ea71-53b2-412d-a3ce-6b134d558892	{"id": "e9c3ea71-53b2-412d-a3ce-6b134d558892", "dot": null, "activo": true, "creado_en": "2025-05-27T17:33:25.904859-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-17ba394d49", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T17:33:25.904859-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T17:33:25.904859-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "e9c3ea71-53b2-412d-a3ce-6b134d558892", "dot": null, "activo": true, "creado_en": "2025-05-27T17:33:25.904859-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-17ba394d49", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T17:33:25.904859-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": 84000, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"vida_util_restante_km": {"new": "84000", "old": null}}	\N	\N
393	2025-05-27 19:39:10.658464-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	e99dd95d-4280-4705-a4aa-f83dd29c0171	{"id": "e99dd95d-4280-4705-a4aa-f83dd29c0171", "dot": null, "activo": true, "creado_en": "2025-05-27T17:46:56.814398-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-938377c49a", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T17:46:56.814398-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T17:46:56.814398-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "e99dd95d-4280-4705-a4aa-f83dd29c0171", "dot": null, "activo": true, "creado_en": "2025-05-27T17:46:56.814398-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-938377c49a", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T17:46:56.814398-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": 84000, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"vida_util_restante_km": {"new": "84000", "old": null}}	\N	\N
394	2025-05-27 19:39:10.658464-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	008e61e4-207c-4c06-ab5c-3425450a7ce1	{"id": "008e61e4-207c-4c06-ab5c-3425450a7ce1", "dot": null, "activo": true, "creado_en": "2025-05-27T18:28:29.953019-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-402fe12e40", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:28:29.953019-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:28:29.953019-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "008e61e4-207c-4c06-ab5c-3425450a7ce1", "dot": null, "activo": true, "creado_en": "2025-05-27T18:28:29.953019-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-402fe12e40", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:28:29.953019-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": 84000, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"vida_util_restante_km": {"new": "84000", "old": null}}	\N	\N
395	2025-05-27 19:39:10.658464-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	a91b9b5a-fd3e-485e-86d0-3a1c2325d40b	{"id": "a91b9b5a-fd3e-485e-86d0-3a1c2325d40b", "dot": null, "activo": true, "creado_en": "2025-05-27T18:31:34.836198-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-e683a91175", "estado_actual": "EN_REENCAUCHE", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:31:34.851548-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:31:34.851548-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "a91b9b5a-fd3e-485e-86d0-3a1c2325d40b", "dot": null, "activo": true, "creado_en": "2025-05-27T18:31:34.836198-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-e683a91175", "estado_actual": "EN_REENCAUCHE", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:31:34.851548-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": 84000, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "84000", "old": null}}	\N	\N
396	2025-05-27 19:39:10.658464-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	235b4401-4bc0-4523-b9f8-5b912bb45f61	{"id": "235b4401-4bc0-4523-b9f8-5b912bb45f61", "dot": null, "activo": true, "creado_en": "2025-05-27T18:29:28.574478-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-1e503f8b69", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:29:28.574478-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:29:28.574478-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "235b4401-4bc0-4523-b9f8-5b912bb45f61", "dot": null, "activo": true, "creado_en": "2025-05-27T18:29:28.574478-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-1e503f8b69", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:29:28.574478-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": 84000, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"vida_util_restante_km": {"new": "84000", "old": null}}	\N	\N
397	2025-05-27 19:39:10.658464-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	a55368a0-6f59-42d3-9554-1daeec552a68	{"id": "a55368a0-6f59-42d3-9554-1daeec552a68", "dot": null, "activo": true, "creado_en": "2025-05-27T18:30:10.067322-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-15e80f32c9", "estado_actual": "EN_REENCAUCHE", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:30:10.076367-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:30:10.076367-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "a55368a0-6f59-42d3-9554-1daeec552a68", "dot": null, "activo": true, "creado_en": "2025-05-27T18:30:10.067322-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-15e80f32c9", "estado_actual": "EN_REENCAUCHE", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:30:10.076367-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": 84000, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "84000", "old": null}}	\N	\N
398	2025-05-27 19:39:10.658464-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	1dee9c2a-b855-44c8-b5ef-8a6ed6bbfdda	{"id": "1dee9c2a-b855-44c8-b5ef-8a6ed6bbfdda", "dot": null, "activo": true, "creado_en": "2025-05-27T18:30:36.824245-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-e061815996", "estado_actual": "EN_REENCAUCHE", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:30:36.833039-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:30:36.833039-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "1dee9c2a-b855-44c8-b5ef-8a6ed6bbfdda", "dot": null, "activo": true, "creado_en": "2025-05-27T18:30:36.824245-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-e061815996", "estado_actual": "EN_REENCAUCHE", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:30:36.833039-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": 84000, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "84000", "old": null}}	\N	\N
399	2025-05-27 19:39:10.658464-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	0e2f0e46-2da7-4880-8af1-42518ac26c15	{"id": "0e2f0e46-2da7-4880-8af1-42518ac26c15", "dot": null, "activo": true, "creado_en": "2025-05-27T18:31:12.002237-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-beb9612d4b", "estado_actual": "EN_REENCAUCHE", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:31:12.012882-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:31:12.012882-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "0e2f0e46-2da7-4880-8af1-42518ac26c15", "dot": null, "activo": true, "creado_en": "2025-05-27T18:31:12.002237-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-beb9612d4b", "estado_actual": "EN_REENCAUCHE", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:31:12.012882-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": 84000, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "84000", "old": null}}	\N	\N
400	2025-05-27 19:39:10.658464-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	3d986345-b3fb-4dd1-90b2-346934941389	{"id": "3d986345-b3fb-4dd1-90b2-346934941389", "dot": null, "activo": true, "creado_en": "2025-05-27T18:32:00.303244-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-26b30be035", "estado_actual": "EN_REENCAUCHE", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T18:32:00.312736-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:32:00.312736-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "3d986345-b3fb-4dd1-90b2-346934941389", "dot": null, "activo": true, "creado_en": "2025-05-27T18:32:00.303244-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-26b30be035", "estado_actual": "EN_REENCAUCHE", "fecha_desecho": null, "moneda_compra": "MXN", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:32:00.312736-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": 84000, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"vida_util_restante_km": {"new": "84000", "old": null}}	\N	\N
401	2025-05-27 19:39:10.658464-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	9046ee36-f52f-4737-a621-24393ae7b2f9	{"id": "9046ee36-f52f-4737-a621-24393ae7b2f9", "dot": null, "activo": true, "creado_en": "2025-05-27T18:55:48.92463-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-44b9414fc0", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "USD", "actualizado_en": "2025-05-27T18:55:48.92463-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:55:48.92463-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": 10000, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "9046ee36-f52f-4737-a621-24393ae7b2f9", "dot": null, "activo": true, "creado_en": "2025-05-27T18:55:48.92463-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-44b9414fc0", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "USD", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:55:48.92463-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": 84000, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": 10000, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"vida_util_restante_km": {"new": "84000", "old": null}}	\N	\N
402	2025-05-27 19:39:10.658464-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	7bdb45b1-070c-4285-89e5-4afe1e09758f	{"id": "7bdb45b1-070c-4285-89e5-4afe1e09758f", "dot": null, "activo": true, "creado_en": "2025-05-27T18:56:24.081571-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-ef3f24635b", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "USD", "actualizado_en": "2025-05-27T18:56:24.081571-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:56:24.081571-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": 10000, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "7bdb45b1-070c-4285-89e5-4afe1e09758f", "dot": null, "activo": true, "creado_en": "2025-05-27T18:56:24.081571-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-ef3f24635b", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "USD", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:56:24.081571-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": 84000, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": 10000, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"vida_util_restante_km": {"new": "84000", "old": null}}	\N	\N
403	2025-05-27 19:39:10.658464-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	1c47f273-0577-428c-b8ff-060b36cae727	{"id": "1c47f273-0577-428c-b8ff-060b36cae727", "dot": null, "activo": true, "creado_en": "2025-05-27T18:58:21.265831-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-01c6fd8707", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "USD", "actualizado_en": "2025-05-27T18:58:21.265831-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:58:21.265831-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": 10000, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "1c47f273-0577-428c-b8ff-060b36cae727", "dot": null, "activo": true, "creado_en": "2025-05-27T18:58:21.265831-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-01c6fd8707", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "USD", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T18:58:21.265831-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": 84000, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": 10000, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"vida_util_restante_km": {"new": "84000", "old": null}}	\N	\N
404	2025-05-27 19:39:10.658464-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	952a0f71-37dd-46ec-a742-68edbb5b4949	{"id": "952a0f71-37dd-46ec-a742-68edbb5b4949", "dot": null, "activo": true, "creado_en": "2025-05-27T19:00:01.354643-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-7fa42f2fbf", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "USD", "actualizado_en": "2025-05-27T19:00:01.354643-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T19:00:01.354643-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": 10000, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "952a0f71-37dd-46ec-a742-68edbb5b4949", "dot": null, "activo": true, "creado_en": "2025-05-27T19:00:01.354643-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-7fa42f2fbf", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "USD", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T19:00:01.354643-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": 84000, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": 10000, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"vida_util_restante_km": {"new": "84000", "old": null}}	\N	\N
405	2025-05-27 19:39:10.658464-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	48f567fc-bda6-439c-8d94-d4fcf1dab095	{"id": "48f567fc-bda6-439c-8d94-d4fcf1dab095", "dot": null, "activo": true, "creado_en": "2025-05-27T19:01:52.342075-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-9430046ec8", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "USD", "actualizado_en": "2025-05-27T19:01:52.342075-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T19:01:52.342075-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": 10000, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "48f567fc-bda6-439c-8d94-d4fcf1dab095", "dot": null, "activo": true, "creado_en": "2025-05-27T19:01:52.342075-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-9430046ec8", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "USD", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T19:01:52.342075-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": 84000, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": 10000, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"vida_util_restante_km": {"new": "84000", "old": null}}	\N	\N
406	2025-05-27 19:39:10.658464-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	39e353da-8436-4822-ac54-3f8952196e39	{"id": "39e353da-8436-4822-ac54-3f8952196e39", "dot": null, "activo": true, "creado_en": "2025-05-27T19:03:39.721738-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-a65efc0e6b", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "USD", "actualizado_en": "2025-05-27T19:03:39.721738-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T19:03:39.721738-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": 10000, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "39e353da-8436-4822-ac54-3f8952196e39", "dot": null, "activo": true, "creado_en": "2025-05-27T19:03:39.721738-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-a65efc0e6b", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "USD", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T19:03:39.721738-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": 84000, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": 10000, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"vida_util_restante_km": {"new": "84000", "old": null}}	\N	\N
407	2025-05-27 19:39:10.658464-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	fdb5b128-2182-4cbe-848a-abb9dc7706e1	{"id": "fdb5b128-2182-4cbe-848a-abb9dc7706e1", "dot": null, "activo": true, "creado_en": "2025-05-27T19:05:24.446863-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-87a215158d", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "USD", "actualizado_en": "2025-05-27T19:05:24.446863-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T19:05:24.446863-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": 10000, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"id": "fdb5b128-2182-4cbe-848a-abb9dc7706e1", "dot": null, "activo": true, "creado_en": "2025-05-27T19:05:24.446863-05:00", "modelo_id": "00000000-0000-0000-0000-000000000001", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-87a215158d", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "USD", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": "2025-04-27", "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T19:05:24.446863-05:00", "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": 84000, "profundidad_inicial_mm": 15.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": "dddddddd-dddd-dddd-dddd-dddddddddddd", "ubicacion_actual_vehiculo_id": "06abeeaf-0d42-4032-94a8-c46f3d6ee709", "profundidad_remanente_actual_mm": 10.00, "odometro_instalacion_vida_actual": 10000, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": 15.00}	{"vida_util_restante_km": {"new": "84000", "old": null}}	\N	\N
408	2025-05-27 19:44:08.366221-05	public	modelos_neumatico	INSERT	postgres	\N	\N	\N	\N	eef2159d-1098-49d6-ae0f-b795a8f4c968	\N	{"id": "eef2159d-1098-49d6-ae0f-b795a8f4c968", "activo": true, "medida": "295/75R22.5", "creado_en": "2025-05-27T19:44:08.366221-05:00", "creado_por": null, "indice_carga": null, "fabricante_id": "00000000-0000-0000-0000-000000000001", "nombre_modelo": "MODELO-DEFAULT-1", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": null, "indice_velocidad": null, "max_vidas_utiles": 4, "permite_reencauche": true, "reencauches_maximos": 3, "vida_util_teorica_km": null, "presion_recomendada_psi": null, "profundidad_original_mm": 14.00, "frecuencia_inspeccion_km": 5000, "posicion_uso_recomendada": null, "diseno_predominante_para_eje": null, "porcentaje_desgaste_por_vida": 15.00, "profundidad_minima_retiro_mm": 2.00, "tasa_desgaste_esperada_mm_km": 0.00010000}	\N	\N	\n-- Insertar modelos faltantes con valores por defecto\nINSERT INTO modelos_neumatico (\n    id,\n    fabricante_id,\n    nombre_modelo,\n    medida,\n    profundidad_original_mm,\n    profundidad_minima_retiro_mm,\n    tasa_desgaste_esperada_mm_km,\n    permite_reencauche,\n    reencauches_maximos,\n    activo,\n    frecuencia_inspeccion_km,\n    max_vidas_utiles,\n    porcentaje_desgaste_por_vida\n) VALUES \n(\n    'eef2159d-1098-49d6-ae0f-b795a8f4c968',\n    (SELECT id FROM fabricantes_neumatico LIMIT 1),  -- Tomar el primer fabricante disponible\n    'MODELO-DEFAULT-1',\n    '295/75R22.5',\n    14.0,\n    2.0,\n    0.0001,\n    true,\n    3,\n    true,\n    5000,\n    4,\n    15.0\n),\n(\n    '86050a4c-a11f-4471-a3a1-922b3d49d3b3',\n    (SELECT id FROM fabricantes_neumatico LIMIT 1),  -- Tomar el primer fabricante disponible\n    'MODELO-DEFAULT-2',\n    '295/75R22.5',\n    14.0,\n    2.0,\n    0.0001,\n    true,\n    3,\n    true,\n    5000,\n    4,\n    15.0\n);\n\n-- Verificar la inserción\nSELECT id, nombre_modelo, tasa_desgaste_esperada_mm_km FROM modelos_neumatico \nWHERE id IN (\n    'eef2159d-1098-49d6-ae0f-b795a8f4c968',\n    '86050a4c-a11f-4471-a3a1-922b3d49d3b3'\n);
409	2025-05-27 19:44:08.366221-05	public	modelos_neumatico	INSERT	postgres	\N	\N	\N	\N	86050a4c-a11f-4471-a3a1-922b3d49d3b3	\N	{"id": "86050a4c-a11f-4471-a3a1-922b3d49d3b3", "activo": true, "medida": "295/75R22.5", "creado_en": "2025-05-27T19:44:08.366221-05:00", "creado_por": null, "indice_carga": null, "fabricante_id": "00000000-0000-0000-0000-000000000001", "nombre_modelo": "MODELO-DEFAULT-2", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": null, "indice_velocidad": null, "max_vidas_utiles": 4, "permite_reencauche": true, "reencauches_maximos": 3, "vida_util_teorica_km": null, "presion_recomendada_psi": null, "profundidad_original_mm": 14.00, "frecuencia_inspeccion_km": 5000, "posicion_uso_recomendada": null, "diseno_predominante_para_eje": null, "porcentaje_desgaste_por_vida": 15.00, "profundidad_minima_retiro_mm": 2.00, "tasa_desgaste_esperada_mm_km": 0.00010000}	\N	\N	\n-- Insertar modelos faltantes con valores por defecto\nINSERT INTO modelos_neumatico (\n    id,\n    fabricante_id,\n    nombre_modelo,\n    medida,\n    profundidad_original_mm,\n    profundidad_minima_retiro_mm,\n    tasa_desgaste_esperada_mm_km,\n    permite_reencauche,\n    reencauches_maximos,\n    activo,\n    frecuencia_inspeccion_km,\n    max_vidas_utiles,\n    porcentaje_desgaste_por_vida\n) VALUES \n(\n    'eef2159d-1098-49d6-ae0f-b795a8f4c968',\n    (SELECT id FROM fabricantes_neumatico LIMIT 1),  -- Tomar el primer fabricante disponible\n    'MODELO-DEFAULT-1',\n    '295/75R22.5',\n    14.0,\n    2.0,\n    0.0001,\n    true,\n    3,\n    true,\n    5000,\n    4,\n    15.0\n),\n(\n    '86050a4c-a11f-4471-a3a1-922b3d49d3b3',\n    (SELECT id FROM fabricantes_neumatico LIMIT 1),  -- Tomar el primer fabricante disponible\n    'MODELO-DEFAULT-2',\n    '295/75R22.5',\n    14.0,\n    2.0,\n    0.0001,\n    true,\n    3,\n    true,\n    5000,\n    4,\n    15.0\n);\n\n-- Verificar la inserción\nSELECT id, nombre_modelo, tasa_desgaste_esperada_mm_km FROM modelos_neumatico \nWHERE id IN (\n    'eef2159d-1098-49d6-ae0f-b795a8f4c968',\n    '86050a4c-a11f-4471-a3a1-922b3d49d3b3'\n);
410	2025-05-27 19:56:51.449932-05	public	modelos_neumatico	INSERT	postgres	\N	\N	\N	\N	3974c96d-f929-4f28-b9e1-79120090a51e	\N	{"id": "3974c96d-f929-4f28-b9e1-79120090a51e", "activo": true, "medida": "295/75R22.5", "creado_en": "2025-05-27T19:56:51.449932-05:00", "creado_por": null, "indice_carga": null, "fabricante_id": "00000000-0000-0000-0000-000000000001", "nombre_modelo": "MODELO-PRUEBA-1", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": null, "indice_velocidad": null, "max_vidas_utiles": 4, "permite_reencauche": false, "reencauches_maximos": 3, "vida_util_teorica_km": null, "presion_recomendada_psi": null, "profundidad_original_mm": 14.00, "frecuencia_inspeccion_km": 5000, "posicion_uso_recomendada": null, "diseno_predominante_para_eje": null, "porcentaje_desgaste_por_vida": 10.00, "profundidad_minima_retiro_mm": 2.00, "tasa_desgaste_esperada_mm_km": 0.00010000}	\N	\N	\n-- Insertar un nuevo modelo\nWITH nuevo_modelo AS (\n    INSERT INTO modelos_neumatico (\n        fabricante_id, \n        nombre_modelo, \n        medida, \n        profundidad_original_mm, \n        profundidad_minima_retiro_mm,\n        tasa_desgaste_esperada_mm_km,\n        reencauches_maximos,\n        activo\n    ) VALUES (\n        (SELECT id FROM fabricantes_neumatico LIMIT 1),  -- Tomar el primer fabricante\n        'MODELO-PRUEBA-1',\n        '295/75R22.5',\n        14.0,\n        2.0,\n        0.0001,\n        3,  -- reencauches_maximos\n        true\n    ) RETURNING id, nombre_modelo, reencauches_maximos, max_vidas_utiles\n)\nSELECT * FROM nuevo_modelo;
411	2025-05-27 19:57:16.853928-05	public	modelos_neumatico	UPDATE	postgres	\N	\N	\N	\N	3974c96d-f929-4f28-b9e1-79120090a51e	{"id": "3974c96d-f929-4f28-b9e1-79120090a51e", "activo": true, "medida": "295/75R22.5", "creado_en": "2025-05-27T19:56:51.449932-05:00", "creado_por": null, "indice_carga": null, "fabricante_id": "00000000-0000-0000-0000-000000000001", "nombre_modelo": "MODELO-PRUEBA-1", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": null, "indice_velocidad": null, "max_vidas_utiles": 4, "permite_reencauche": false, "reencauches_maximos": 3, "vida_util_teorica_km": null, "presion_recomendada_psi": null, "profundidad_original_mm": 14.00, "frecuencia_inspeccion_km": 5000, "posicion_uso_recomendada": null, "diseno_predominante_para_eje": null, "porcentaje_desgaste_por_vida": 10.00, "profundidad_minima_retiro_mm": 2.00, "tasa_desgaste_esperada_mm_km": 0.00010000}	{"id": "3974c96d-f929-4f28-b9e1-79120090a51e", "activo": true, "medida": "295/75R22.5", "creado_en": "2025-05-27T19:56:51.449932-05:00", "creado_por": null, "indice_carga": null, "fabricante_id": "00000000-0000-0000-0000-000000000001", "nombre_modelo": "MODELO-PRUEBA-1", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": null, "indice_velocidad": null, "max_vidas_utiles": 5, "permite_reencauche": false, "reencauches_maximos": 4, "vida_util_teorica_km": null, "presion_recomendada_psi": null, "profundidad_original_mm": 14.00, "frecuencia_inspeccion_km": 5000, "posicion_uso_recomendada": null, "diseno_predominante_para_eje": null, "porcentaje_desgaste_por_vida": 10.00, "profundidad_minima_retiro_mm": 2.00, "tasa_desgaste_esperada_mm_km": 0.00010000}	{"max_vidas_utiles": {"new": "5", "old": "4"}, "reencauches_maximos": {"new": "4", "old": "3"}}	\N	\n-- Actualizar reencauches_maximos\nWITH modelo_actualizado AS (\n    UPDATE modelos_neumatico \n    SET reencauches_maximos = 4  -- Aumentar de 3 a 4\n    WHERE nombre_modelo = 'MODELO-PRUEBA-1'\n    RETURNING id, nombre_modelo, reencauches_maximos, max_vidas_utiles\n)\nSELECT * FROM modelo_actualizado;
412	2025-05-27 20:01:09.473588-05	public	neumaticos	INSERT	postgres	\N	\N	\N	\N	2e960afc-b2b4-408a-85f9-2010b285a32d	\N	{"id": "2e960afc-b2b4-408a-85f9-2010b285a32d", "dot": null, "activo": true, "creado_en": "2025-05-27T20:01:09.473588-05:00", "modelo_id": "3974c96d-f929-4f28-b9e1-79120090a51e", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 4, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-TRIGGER-1", "estado_actual": "EN_STOCK", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-27T20:01:09.473588-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": true, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-05-27T20:01:09.473588-05:00", "proveedor_compra_id": "c532e7c3-85ee-48f8-ad47-8d4e79112881", "ubicacion_almacen_id": "00000000-0000-0000-0000-000000000001", "kilometraje_acumulado": 1000, "proxima_inspeccion_km": null, "vida_util_restante_km": null, "profundidad_inicial_mm": 14.00, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": 0.00010000, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 8.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	\N	\N	\N
413	2025-05-27 21:17:02.158981-05	public	neumaticos	UPDATE	postgres	\N	\N	\N	\N	11111111-1111-1111-1111-111111111111	{"id": "11111111-1111-1111-1111-111111111111", "dot": null, "activo": true, "creado_en": "2025-05-27T03:18:49.597271-05:00", "modelo_id": "51bec9d7-c28c-4273-a79e-f9388e54130f", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-INST-001", "estado_actual": "EN_STOCK", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-27T19:39:10.658464-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": null, "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": 134000, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 15.00, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"id": "11111111-1111-1111-1111-111111111111", "dot": null, "activo": true, "creado_en": "2025-05-27T03:18:49.597271-05:00", "modelo_id": "51bec9d7-c28c-4273-a79e-f9388e54130f", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 1000.00, "fecha_compra": "2025-05-27", "numero_serie": "TEST-INST-001", "estado_actual": "EN_STOCK", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-05-27T21:17:02.158981-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": null, "proveedor_compra_id": null, "ubicacion_almacen_id": null, "kilometraje_acumulado": 0, "proxima_inspeccion_km": null, "vida_util_restante_km": 134000, "profundidad_inicial_mm": null, "reencauches_realizados": 0, "fecha_ultimo_reencauche": null, "kilometraje_vida_actual": 0, "fecha_inicio_vida_actual": null, "proxima_inspeccion_fecha": null, "tasa_desgaste_actual_mm_km": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null, "profundidad_remanente_actual_mm": 2.50, "odometro_instalacion_vida_actual": null, "fecha_ultima_medicion_profundidad": null, "profundidad_inicio_vida_actual_mm": null}	{"profundidad_remanente_actual_mm": {"new": "2.50", "old": "15.00"}}	\N	\N
\.


--
-- Data for Name: bitacora_mantenimiento; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bitacora_mantenimiento (id, fecha_ejecucion, tipo, descripcion, ejecutado_por, duracion, exito, detalles) FROM stdin;
1	2025-05-28 12:15:18.782269-05	DIARIO	Mantenimiento diario automático	postgres	00:00:00.061344	t	Ejecución completada.
2	2025-05-28 12:15:28.915795-05	REINDEX	Reindexación de la tabla neumaticos	postgres	00:00:00.021874	t	Reindexación completada en 00:00:00.021874
3	2025-05-28 12:16:51.138047-05	DIARIO	Mantenimiento diario automático	postgres	00:00:00.024711	t	Ejecución completada.
4	2025-05-28 12:17:11.813293-05	REINDEX	Reindexación de la tabla neumaticos	postgres	00:00:00.003407	t	Reindexación completada en 00:00:00.003407
5	2025-05-28 12:18:01.678969-05	LIMPIEZA	Limpieza de registros antiguos de la bitácora	postgres	\N	t	Se eliminaron 0 registros con más de 90 días de antigüedad
\.


--
-- Data for Name: bitacora_operaciones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bitacora_operaciones (id, tipo_operacion, descripcion, fecha_operacion, usuario_id, almacen_id, vehiculo_id, estado_operacion, duracion_minutos, costo_estimado, costo_real, proveedor_id, observaciones, creado_en, actualizado_en, creado_por, actualizado_por) FROM stdin;
cd26340e-3b30-4c01-b884-8a3b3c0398b8	ROTACION	Rotación de neumáticos completa	2025-05-26 23:41:51.818091-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	00000000-0000-0000-0000-000000000001	06abeeaf-0d42-4032-94a8-c46f3d6ee709	COMPLETADA	60	150.00	\N	\N	\N	2025-05-26 23:41:51.818091-05	2025-05-26 23:41:51.818091-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
6ac02bbb-b8ea-4f73-ba74-d36895020ba3	DESMONTAJE	Neumático desmontado para EN_REENCAUCHE: Desmontado del vehículo 06abeeaf-0d42-4032-94a8-c46f3d6ee709, posición dddddddd-dddd-dddd-dddd-dddddddddddd	2025-05-27 18:30:10.076367-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	06abeeaf-0d42-4032-94a8-c46f3d6ee709	COMPLETADA	\N	\N	\N	\N	\N	2025-05-27 18:30:10.076367-05	2025-05-27 18:30:10.076367-05	\N	\N
9a974da8-575a-4418-a08c-c962ec086d79	DESMONTAJE	Neumático desmontado para EN_REENCAUCHE: Desmontado del vehículo 06abeeaf-0d42-4032-94a8-c46f3d6ee709, posición dddddddd-dddd-dddd-dddd-dddddddddddd	2025-05-27 18:30:36.833039-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	06abeeaf-0d42-4032-94a8-c46f3d6ee709	COMPLETADA	\N	\N	\N	\N	\N	2025-05-27 18:30:36.833039-05	2025-05-27 18:30:36.833039-05	\N	\N
6aa33a7b-7d54-4034-b029-9dcaf05082b0	DESMONTAJE	Neumático desmontado para EN_REENCAUCHE: Desmontado del vehículo 06abeeaf-0d42-4032-94a8-c46f3d6ee709, posición dddddddd-dddd-dddd-dddd-dddddddddddd	2025-05-27 18:31:12.012882-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	06abeeaf-0d42-4032-94a8-c46f3d6ee709	COMPLETADA	\N	\N	\N	\N	\N	2025-05-27 18:31:12.012882-05	2025-05-27 18:31:12.012882-05	\N	\N
f237b0bd-f2d9-444c-901e-6bd596a24715	DESMONTAJE	Neumático desmontado para EN_REENCAUCHE: Desmontado del vehículo 06abeeaf-0d42-4032-94a8-c46f3d6ee709, posición dddddddd-dddd-dddd-dddd-dddddddddddd	2025-05-27 18:31:34.851548-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	06abeeaf-0d42-4032-94a8-c46f3d6ee709	COMPLETADA	\N	\N	\N	\N	\N	2025-05-27 18:31:34.851548-05	2025-05-27 18:31:34.851548-05	\N	\N
cc73f734-a921-4022-8cff-4221be391f7b	DESMONTAJE	Neumático desmontado para EN_REENCAUCHE: Desmontado del vehículo 06abeeaf-0d42-4032-94a8-c46f3d6ee709, posición dddddddd-dddd-dddd-dddd-dddddddddddd	2025-05-27 18:32:00.312736-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	06abeeaf-0d42-4032-94a8-c46f3d6ee709	COMPLETADA	\N	\N	\N	\N	\N	2025-05-27 18:32:00.312736-05	2025-05-27 18:32:00.312736-05	\N	\N
\.


--
-- Data for Name: bitacora_operaciones_neumaticos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bitacora_operaciones_neumaticos (id, operacion_id, neumatico_id, tipo_accion, posicion_neumatico_id, profundidad_inicial_mm, profundidad_final_mm, presion_inicial_psi, presion_final_psi, kilometraje_vehiculo_km, observaciones, creado_en, actualizado_en, creado_por, actualizado_por) FROM stdin;
87e7355e-609e-402d-ba40-f606f90b4d89	cd26340e-3b30-4c01-b884-8a3b3c0398b8	7c61a3cd-97c1-4442-858f-0d7e5d3bb68e	ROTACION	dddddddd-dddd-dddd-dddd-dddddddddddd	8.50	8.30	35.00	36.00	12500.50	Rotación realizada según procedimiento estándar	2025-05-26 23:42:18.961943-05	2025-05-26 23:42:18.961943-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
ba93d450-191a-40ae-a643-32efdff99d26	6ac02bbb-b8ea-4f73-ba74-d36895020ba3	a55368a0-6f59-42d3-9554-1daeec552a68	DESMONTAJE	\N	10.00	\N	\N	\N	\N	\N	2025-05-27 18:30:10.076367-05	2025-05-27 18:30:10.076367-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
7e340331-2522-4b3a-ab5e-09a4044f61d9	9a974da8-575a-4418-a08c-c962ec086d79	1dee9c2a-b855-44c8-b5ef-8a6ed6bbfdda	DESMONTAJE	\N	10.00	\N	\N	\N	\N	\N	2025-05-27 18:30:36.833039-05	2025-05-27 18:30:36.833039-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
8fe57b7c-c0c0-4e7f-9f7c-941109ff92ea	6aa33a7b-7d54-4034-b029-9dcaf05082b0	0e2f0e46-2da7-4880-8af1-42518ac26c15	DESMONTAJE	\N	10.00	\N	\N	\N	\N	\N	2025-05-27 18:31:12.012882-05	2025-05-27 18:31:12.012882-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
7079d9e5-3fb6-4c12-ad1c-582d73032cdc	f237b0bd-f2d9-444c-901e-6bd596a24715	a91b9b5a-fd3e-485e-86d0-3a1c2325d40b	DESMONTAJE	\N	10.00	\N	\N	\N	\N	\N	2025-05-27 18:31:34.851548-05	2025-05-27 18:31:34.851548-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
04af89e1-20d0-496e-910f-3949ea24b723	cc73f734-a921-4022-8cff-4221be391f7b	3d986345-b3fb-4dd1-90b2-346934941389	DESMONTAJE	\N	10.00	\N	\N	\N	\N	\N	2025-05-27 18:32:00.312736-05	2025-05-27 18:32:00.312736-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
\.


--
-- Data for Name: configuracion_auditoria; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.configuracion_auditoria (nombre_tabla, activo, prioridad, campos_excluidos, creado_en, actualizado_en) FROM stdin;
neumaticos	t	medium	["actualizado_en", "actualizado_por", "fecha_ultimo_evento"]	2025-05-19 19:28:33.47577-05	2025-05-19 19:28:33.47577-05
\.


--
-- Data for Name: configuraciones_eje; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.configuraciones_eje (id, tipo_vehiculo_id, numero_eje, nombre_eje, tipo_eje, numero_posiciones, posiciones_duales, permite_reencauchados, neumaticos_por_posicion, creado_en, creado_por, actualizado_en, actualizado_por) FROM stdin;
cccccccc-cccc-cccc-cccc-cccccccccccc	7a957cc2-e201-455b-a951-c245102da748	1	Eje delantero	DIRECCION	2	f	t	1	2025-05-23 16:53:02.0161-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
\.


--
-- Data for Name: errores_aplicacion; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.errores_aplicacion (id, nombre_funcion, mensaje_error, detalles, creado_por, creado_en, resuelto, resuelto_por, resuelto_en, comentario_resolucion) FROM stdin;
a5fd8c90-5ed5-4914-aec9-aef16d43760e	calcular_vida_util_restante	no existe la columna m.profundidad_nueva_mm	{"sqlstate": "42703", "neumatico_id": "00000000-0000-0000-0000-000000000001"}	SISTEMA	2025-05-26 21:33:58.670724-05	f	\N	\N	\N
b9c3b7ea-0c29-4c44-814f-16ad1a8a8018	ejecutar_tareas_programadas	Error ejecutando tarea: actualizar_vida_util_neumaticos	{"error": "no existe la columna «tabla_afectada» en la relación «auditoria_log»", "sqlstate": "42703", "tarea_id": 1}	SISTEMA_TAREAS	2025-05-27 01:53:44.000486-05	f	\N	\N	\N
715f8348-31b5-4127-a277-c919d07f4e80	manejar_evento_desmontaje	el registro a ser actualizado ya fue modificado por una operación disparada por la orden actual	{"sqlstate": "27000", "evento_id": "81d63ed6-64c9-4758-ac7d-8802918b062f", "neumatico_id": "fdb5b128-2182-4cbe-848a-abb9dc7706e1"}	admin	2025-05-27 19:05:24.457336-05	f	\N	\N	\N
\.


--
-- Data for Name: especificaciones_desgaste; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.especificaciones_desgaste (id, modelo_neumatico_id, tipo_posicion, vida_util_km_min, vida_util_km_max, descripcion_estado, creado_en, creado_por, actualizado_en, actualizado_por) FROM stdin;
\.


--
-- Data for Name: eventos_neumaticos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.eventos_neumaticos (id, neumatico_id, tipo_evento, timestamp_evento, usuario_id, vehiculo_id, posicion_id, odometro_vehiculo_en_evento, profundidad_remanente_mm, presion_psi, costo_evento, moneda_costo, proveedor_servicio_id, notas, destino_desmontaje, motivo_desecho_id_evento, profundidad_post_reencauche_mm, datos_evento, relacion_evento_anterior, creado_en, almacen_destino_id, tipo_ruta_id, peso_carga_promedio_ton_evento, motivo_reparacion_texto, tipo_dano_detectado_texto) FROM stdin;
7fc18f03-9cb3-45b4-a377-f5112f897495	00000000-0000-0000-0000-000000000001	INSPECCION	2025-05-19 22:16:44.365683-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	\N	\N	\N	\N	PEN	\N	\N	\N	\N	\N	\N	\N	2025-05-19 22:16:44.365683-05	\N	9d1cb958-e230-430a-8c1f-afd45547ab60	45.50	\N	\N
04fac6b2-6679-40a3-b3cc-f28b51bc34b7	00000000-0000-0000-0000-000000000001	DESMONTAJE	2025-05-26 18:09:35.967875-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	\N	12.50	\N	\N	PEN	\N	\N	EN_STOCK	\N	\N	\N	\N	2025-05-26 18:09:35.967875-05	\N	\N	\N	\N	\N
17dce29f-f11a-46f1-9cf8-6a2fd9a22f67	00000000-0000-0000-0000-000000000001	DESMONTAJE	2025-05-26 21:13:31.459054-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	\N	12.50	\N	\N	PEN	\N	\N	EN_STOCK	\N	\N	\N	\N	2025-05-26 21:13:31.459054-05	\N	\N	\N	\N	\N
accbaa2c-247e-4f1d-b768-9803ad5d113d	55555555-5555-5555-5555-555555555555	INSTALACION	2025-05-27 02:56:45.653215-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	10000	15.00	110.00	\N	PEN	\N	Prueba de instalación de neumático nuevo	\N	\N	\N	{"profundidad_inicio_vida_actual_mm_registrada": 15.00}	\N	2025-05-27 02:56:45.653215-05	\N	\N	\N	\N	\N
86bcd99a-8cd1-411b-bdff-56bea06ab0b5	66666666-6666-6666-6666-666666666666	INSTALACION	2025-05-27 03:01:19.771471-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	65000	12.50	105.00	\N	PEN	\N	Prueba de instalación de neumático usado (vida > 1)	\N	\N	\N	{"profundidad_inicio_vida_actual_mm_registrada": 12.50}	\N	2025-05-27 03:01:19.771471-05	\N	\N	\N	\N	\N
11428698-7129-4728-bdd1-8ff977e8938f	060366ed-07ec-4d0d-8d3d-f97821717ffb	DESMONTAJE	2025-05-27 17:24:42.966298-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	10000	\N	\N	\N	PEN	\N	\N	EN_REENCAUCHE	\N	\N	\N	\N	2025-05-27 17:24:42.966298-05	\N	\N	\N	\N	\N
b6eae463-c170-40e8-9fdf-ced466cbb9e6	a55368a0-6f59-42d3-9554-1daeec552a68	DESMONTAJE	2025-05-27 18:30:10.076367-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	10000	\N	\N	\N	PEN	\N	\N	EN_REENCAUCHE	\N	\N	{"es_retirado": false, "vida_actual": 1, "vidas_maximas": 5, "es_recuperable": true, "kilometraje_vida_actual": 0, "tasa_desgaste_actual_mm_km": null, "profundidad_remanente_actual_mm": 10.00, "profundidad_inicio_vida_actual_mm": 15.00}	\N	2025-05-27 18:30:10.076367-05	\N	\N	\N	\N	\N
e663fedf-cc42-4d41-af75-886bd9b85d50	1dee9c2a-b855-44c8-b5ef-8a6ed6bbfdda	DESMONTAJE	2025-05-27 18:30:36.833039-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	10000	\N	\N	\N	PEN	\N	\N	EN_REENCAUCHE	\N	\N	{"es_retirado": false, "vida_actual": 1, "vidas_maximas": 5, "es_recuperable": true, "kilometraje_vida_actual": 0, "tasa_desgaste_actual_mm_km": null, "profundidad_remanente_actual_mm": 10.00, "profundidad_inicio_vida_actual_mm": 15.00}	\N	2025-05-27 18:30:36.833039-05	\N	\N	\N	\N	\N
89a53121-98f3-4bcd-ae7f-b5a05b4fa9fd	0e2f0e46-2da7-4880-8af1-42518ac26c15	DESMONTAJE	2025-05-27 18:31:12.012882-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	10000	\N	\N	\N	PEN	\N	\N	EN_REENCAUCHE	\N	\N	{"es_retirado": false, "vida_actual": 1, "vidas_maximas": 5, "es_recuperable": true, "kilometraje_vida_actual": 0, "tasa_desgaste_actual_mm_km": null, "profundidad_remanente_actual_mm": 10.00, "profundidad_inicio_vida_actual_mm": 15.00}	\N	2025-05-27 18:31:12.012882-05	\N	\N	\N	\N	\N
f14d2fb7-55d3-4617-b0b5-32cd96dea8ac	a91b9b5a-fd3e-485e-86d0-3a1c2325d40b	DESMONTAJE	2025-05-27 18:31:34.851548-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	10000	\N	\N	\N	PEN	\N	\N	EN_REENCAUCHE	\N	\N	{"es_retirado": false, "vida_actual": 1, "vidas_maximas": 5, "es_recuperable": true, "kilometraje_vida_actual": 0, "tasa_desgaste_actual_mm_km": null, "profundidad_remanente_actual_mm": 10.00, "profundidad_inicio_vida_actual_mm": 15.00}	\N	2025-05-27 18:31:34.851548-05	\N	\N	\N	\N	\N
b7e050ab-829c-4127-a8aa-147ced3084e4	3d986345-b3fb-4dd1-90b2-346934941389	DESMONTAJE	2025-05-27 18:32:00.312736-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	10000	\N	\N	\N	PEN	\N	\N	EN_REENCAUCHE	\N	\N	{"es_retirado": false, "vida_actual": 1, "vidas_maximas": 5, "es_recuperable": true, "kilometraje_vida_actual": 0, "tasa_desgaste_actual_mm_km": null, "profundidad_remanente_actual_mm": 10.00, "profundidad_inicio_vida_actual_mm": 15.00}	\N	2025-05-27 18:32:00.312736-05	\N	\N	\N	\N	\N
81d63ed6-64c9-4758-ac7d-8802918b062f	fdb5b128-2182-4cbe-848a-abb9dc7706e1	DESMONTAJE	2025-05-27 19:05:24.457336-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	15000	8.50	\N	\N	PEN	\N	\N	EN_REENCAUCHE	\N	\N	{"motivo": "Prueba de desmontaje", "test_id": "TEST-DESM-36495e21"}	\N	2025-05-27 19:05:24.457336-05	\N	\N	\N	\N	\N
\.


--
-- Data for Name: fabricantes_neumatico; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fabricantes_neumatico (id, nombre, codigo_abreviado, pais_origen, sitio_web, activo, creado_en, creado_por, actualizado_en, actualizado_por) FROM stdin;
00000000-0000-0000-0000-000000000001	Michelin	MIC	\N	\N	t	2025-05-19 12:21:17.269955-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
7f631e5e-cf90-4350-9890-e44bf313627b	Bridgestone	BRI	Japón	\N	t	2025-05-21 22:06:54.216837-05	\N	\N	\N
45992f67-19ef-42ab-8af8-5d6eb7d142e3	Goodyear	GOO	Estados Unidos	\N	t	2025-05-21 22:06:54.216837-05	\N	\N	\N
2a22130d-4b35-4ea3-90af-37be5f74d48c	Pirelli	PIR	Italia	\N	t	2025-05-21 22:06:54.216837-05	\N	\N	\N
94959e9a-bb96-4235-b09b-9db7f071ab8e	Continental	CON	Alemania	\N	t	2025-05-21 22:06:54.216837-05	\N	\N	\N
11111111-1111-1111-1111-111111111110	Fabricante de Prueba	\N	País de Prueba	\N	t	2025-05-27 02:49:44.337832-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
\.


--
-- Data for Name: garantias_neumaticos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.garantias_neumaticos (id, neumatico_id, proveedor_id, tipo_garantia, fecha_inicio, fecha_fin, kilometraje_cubierto, meses_cobertura, condiciones_url, creado_en, actualizado_en, creado_por, actualizado_por) FROM stdin;
\.


--
-- Data for Name: historial_estados_neumaticos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.historial_estados_neumaticos (id, neumatico_id, estado_anterior, estado_nuevo, fecha_cambio, usuario_id, comentario, metadata) FROM stdin;
05a4b301-8f5b-44a3-88f4-ad7c0b6da983	00000000-0000-0000-0000-000000000001	INSTALADO	EN_STOCK	2025-05-26 18:09:35.967875-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	Cambio de estado automático	\N
ed5118d9-e910-4858-9299-7279ea8d9417	00000000-0000-0000-0000-000000000001	EN_STOCK	INSTALADO	2025-05-26 18:28:14.269663-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	Cambio de estado automático	\N
29094684-f4ce-414b-a771-b2783039f917	00000000-0000-0000-0000-000000000001	INSTALADO	EN_STOCK	2025-05-26 21:13:31.459054-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	Cambio de estado automático	\N
50efed8b-bb8c-407d-ab72-06c8dc2d3de9	00000000-0000-0000-0000-000000000001	EN_STOCK	EN_REPARACION	2025-05-26 21:24:31.933428-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	Cambio de estado automático	\N
b2e3d287-432c-43e2-9077-3e934a779c8b	55555555-5555-5555-5555-555555555555	EN_STOCK	INSTALADO	2025-05-27 02:56:45.653215-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	Cambio de estado automático	\N
e33a4115-dcba-4267-a8b2-e079554dcc92	66666666-6666-6666-6666-666666666666	EN_STOCK	INSTALADO	2025-05-27 03:01:19.771471-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	Cambio de estado automático	\N
eead7881-84e6-4445-b8c8-a04729880f89	a55368a0-6f59-42d3-9554-1daeec552a68	INSTALADO	EN_REENCAUCHE	2025-05-27 18:30:10.076367-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	Cambio de estado automático	\N
b8335c8a-6b78-4a82-a377-6b81bd048749	1dee9c2a-b855-44c8-b5ef-8a6ed6bbfdda	INSTALADO	EN_REENCAUCHE	2025-05-27 18:30:36.833039-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	Cambio de estado automático	\N
fc21a2b2-fd65-4a1c-aefc-028adb708d11	0e2f0e46-2da7-4880-8af1-42518ac26c15	INSTALADO	EN_REENCAUCHE	2025-05-27 18:31:12.012882-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	Cambio de estado automático	\N
f64e3d4c-1e69-42b6-83b2-70ffc7b010ab	a91b9b5a-fd3e-485e-86d0-3a1c2325d40b	INSTALADO	EN_REENCAUCHE	2025-05-27 18:31:34.851548-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	Cambio de estado automático	\N
fc8887f5-1f0c-4450-8570-cf37e0d55a69	3d986345-b3fb-4dd1-90b2-346934941389	INSTALADO	EN_REENCAUCHE	2025-05-27 18:32:00.312736-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	Cambio de estado automático	\N
\.


--
-- Data for Name: mediciones_profundidad; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mediciones_profundidad (id, neumatico_id, fecha_medicion, profundidad_mm, ubicacion_medicion, metodo_medicion, usuario_id, observaciones, creado_en, actualizado_en, creado_por, actualizado_por) FROM stdin;
1e2b5858-76bf-4859-8a7b-e06e64c940cd	7c61a3cd-97c1-4442-858f-0d7e5d3bb68e	2025-05-26 23:42:33.64809-05	8.30	Taller Central	Calibrador digital	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	Medición después de rotación	2025-05-26 23:42:33.64809-05	2025-05-26 23:42:33.64809-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
\.


--
-- Data for Name: modelos_neumatico; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.modelos_neumatico (id, fabricante_id, nombre_modelo, medida, indice_carga, indice_velocidad, profundidad_original_mm, presion_recomendada_psi, permite_reencauche, reencauches_maximos, patron_dibujo, tipo_servicio, creado_en, creado_por, actualizado_en, actualizado_por, posicion_uso_recomendada, diseno_predominante_para_eje, vida_util_teorica_km, profundidad_minima_retiro_mm, tasa_desgaste_esperada_mm_km, activo, frecuencia_inspeccion_km, max_vidas_utiles, porcentaje_desgaste_por_vida) FROM stdin;
51bec9d7-c28c-4273-a79e-f9388e54130f	00000000-0000-0000-0000-000000000001	X-MULTI Z	295/80R22.5	\N	\N	15.00	\N	f	0	\N	\N	2025-05-19 21:44:38.282601-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	DIRECCION	OTRO	\N	1.60	0.00010000	t	5000	5	10.00
55f58bfd-2dfb-4bdb-b9b6-1b3da75a867e	00000000-0000-0000-0000-000000000001	X-MULTI D2	295/80R22.5	\N	\N	15.00	\N	f	0	\N	\N	2025-05-19 21:44:38.282601-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	TRACCION	OTRO	\N	1.60	0.00010000	t	5000	5	10.00
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0000-000000000001	X Line Energy Z	295/80R22.5	\N	\N	15.00	\N	t	0	\N	\N	2025-05-19 12:21:17.269955-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	OTRO	OTRO	\N	1.60	0.00010000	t	5000	5	10.00
11111111-1111-1111-1111-111111111111	11111111-1111-1111-1111-111111111110	Neumático de Prueba	295/75R22.5	\N	\N	16.00	\N	f	0	\N	\N	2025-05-27 02:49:44.348094-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	\N	2.00	0.00010000	t	5000	5	10.00
86050a4c-a11f-4471-a3a1-922b3d49d3b3	00000000-0000-0000-0000-000000000001	MODELO-DEFAULT-2	295/75R22.5	\N	\N	14.00	\N	t	3	\N	\N	2025-05-27 19:44:08.366221-05	\N	\N	\N	\N	\N	\N	2.00	0.00010000	t	5000	4	15.00
3974c96d-f929-4f28-b9e1-79120090a51e	00000000-0000-0000-0000-000000000001	MODELO-PRUEBA-1	295/75R22.5	\N	\N	14.00	\N	f	4	\N	\N	2025-05-27 19:56:51.449932-05	\N	\N	\N	\N	\N	\N	2.00	0.00010000	t	5000	5	10.00
eef2159d-1098-49d6-ae0f-b795a8f4c968	00000000-0000-0000-0000-000000000001	MODELO-DEFAULT-1	295/75R22.5	\N	\N	14.00	\N	t	3	\N	\N	2025-05-27 19:44:08.366221-05	\N	\N	\N	\N	\N	\N	2.00	0.00010000	t	5000	4	15.00
\.


--
-- Data for Name: modelos_posiciones_permitidas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.modelos_posiciones_permitidas (modelo_neumatico_id, posicion_neumatico_id, es_recomendado, creado_en, creado_por) FROM stdin;
\.


--
-- Data for Name: motivos_desecho; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.motivos_desecho (id, codigo, descripcion, requiere_evidencia, activo, creado_en, creado_por, actualizado_en, actualizado_por) FROM stdin;
\.


--
-- Data for Name: neumaticos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.neumaticos (id, numero_serie, dot, modelo_id, fecha_compra, fecha_fabricacion, costo_compra, moneda_compra, proveedor_compra_id, es_reencauchado, vida_actual, estado_actual, ubicacion_actual_vehiculo_id, ubicacion_actual_posicion_id, fecha_ultimo_evento, profundidad_inicial_mm, kilometraje_acumulado, reencauches_realizados, fecha_desecho, motivo_desecho_id, creado_en, creado_por, actualizado_en, actualizado_por, ubicacion_almacen_id, sensor_id, profundidad_remanente_actual_mm, fecha_ultima_medicion_profundidad, kilometraje_vida_actual, fecha_inicio_vida_actual, odometro_instalacion_vida_actual, tasa_desgaste_actual_mm_km, vida_util_restante_km, fecha_ultimo_reencauche, activo, proxima_inspeccion_fecha, proxima_inspeccion_km, profundidad_inicio_vida_actual_mm) FROM stdin;
2e960afc-b2b4-408a-85f9-2010b285a32d	TEST-TRIGGER-1	\N	3974c96d-f929-4f28-b9e1-79120090a51e	2025-05-27	\N	1000.00	PEN	c532e7c3-85ee-48f8-ad47-8d4e79112881	t	4	EN_STOCK	\N	\N	2025-05-27 20:01:09.473588-05	14.00	1000	0	\N	\N	2025-05-27 20:01:09.473588-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-27 20:01:09.473588-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	00000000-0000-0000-0000-000000000001	\N	8.00	\N	0	\N	\N	0.00010000	\N	\N	t	\N	\N	\N
11111111-1111-1111-1111-111111111111	TEST-INST-001	\N	51bec9d7-c28c-4273-a79e-f9388e54130f	2025-05-27	\N	1000.00	PEN	\N	f	1	EN_STOCK	\N	\N	\N	\N	0	0	\N	\N	2025-05-27 03:18:49.597271-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-27 21:17:44.093006-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	2.50	\N	0	\N	\N	\N	134000	\N	t	\N	\N	\N
55555555-5555-5555-5555-555555555555	TEST-NEW-001	\N	51bec9d7-c28c-4273-a79e-f9388e54130f	2025-05-27	\N	1000.00	PEN	\N	f	1	INSTALADO	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	2025-05-27 02:56:45.653215-05	\N	0	0	\N	\N	2025-05-27 02:55:14.384488-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-27 19:39:10.658464-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	15.00	\N	0	2025-05-27	10000	\N	134000	\N	t	\N	\N	15.00
7c61a3cd-97c1-4442-858f-0d7e5d3bb68e	TEST-c136b84f	\N	eef2159d-1098-49d6-ae0f-b795a8f4c968	2025-05-23	2025-04-23	1000.00	PEN	\N	f	1	INSTALADO	06abeeaf-0d42-4032-94a8-c46f3d6ee709	00000000-0000-0000-0000-000000000001	\N	15.00	0	0	\N	\N	2025-05-23 00:15:26.760524-05	\N	2025-05-27 19:39:10.658464-05	\N	\N	\N	8.00	\N	0	2025-04-23	\N	\N	\N	\N	t	2025-06-08	15000	\N
23e8641a-e649-45d5-86d2-914c1f546f77	TEST-24fceded	\N	86050a4c-a11f-4471-a3a1-922b3d49d3b3	2025-05-23	2025-04-23	1000.00	PEN	\N	f	1	INSTALADO	06abeeaf-0d42-4032-94a8-c46f3d6ee709	0d7a489a-44b4-40e6-a957-3dd294416c85	\N	15.00	0	0	\N	\N	2025-05-23 00:17:54.377345-05	\N	2025-05-27 19:39:10.658464-05	\N	\N	\N	8.00	\N	0	2025-04-23	\N	\N	\N	\N	t	2025-06-08	15000	\N
00000000-0000-0000-0000-000000000001	SN-DEL-IZQ-001	\N	00000000-0000-0000-0000-000000000001	2025-05-19	\N	\N	PEN	\N	f	1	EN_REPARACION	\N	\N	2025-05-26 21:13:31.459054-05	\N	0	0	\N	\N	2025-05-19 12:32:03.435954-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-27 19:39:10.658464-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	12.50	\N	0	\N	\N	0.00040000	27250	\N	t	\N	5000	\N
66666666-6666-6666-6666-666666666666	TEST-USED-001	\N	51bec9d7-c28c-4273-a79e-f9388e54130f	2024-11-28	\N	750.00	PEN	\N	f	2	INSTALADO	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	2025-05-27 03:01:19.771471-05	\N	0	0	\N	\N	2025-05-27 03:01:19.763414-05	\N	2025-05-27 03:01:19.771471-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	12.50	\N	0	2025-05-27	65000	\N	109000	\N	t	\N	\N	12.50
a4531dfb-fe91-4556-839b-5110820dd772	TEST-284278	\N	00000000-0000-0000-0000-000000000001	2025-05-25	2025-04-25	1000.00	PEN	\N	f	1	EN_STOCK	\N	\N	\N	32.00	0	0	\N	\N	2025-05-25 11:59:18.505242-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-25 12:06:35.571539-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	00000000-0000-0000-0000-000000000001	\N	32.00	\N	0	\N	\N	0.00100000	30400	\N	t	\N	\N	\N
0dd8d980-1fbb-4611-8298-038a69bc9582	TEST-f680f19ec5	\N	00000000-0000-0000-0000-000000000001	2025-05-27	2025-04-27	1000.00	MXN	\N	f	1	INSTALADO	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	2025-05-27 17:19:14.217844-05	15.00	0	0	\N	\N	2025-05-27 17:19:14.217844-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-27 19:39:10.658464-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	10.00	\N	0	\N	\N	\N	84000	\N	t	\N	\N	15.00
8b879b54-eda4-4bc6-9593-cd5242588d7c	TEST-d567ce9a81	\N	00000000-0000-0000-0000-000000000001	2025-05-27	2025-04-27	1000.00	MXN	\N	f	1	INSTALADO	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	2025-05-27 17:20:05.119664-05	15.00	0	0	\N	\N	2025-05-27 17:20:05.119664-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-27 19:39:10.658464-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	10.00	\N	0	\N	\N	\N	84000	\N	t	\N	\N	15.00
60e9e8c8-0648-4f57-ba3b-8f5c62ea36eb	TEST-0407b809cd	\N	00000000-0000-0000-0000-000000000001	2025-05-27	2025-04-27	1000.00	MXN	\N	f	1	INSTALADO	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	2025-05-27 17:22:19.80177-05	15.00	0	0	\N	\N	2025-05-27 17:22:19.80177-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-27 19:39:10.658464-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	10.00	\N	0	\N	\N	\N	84000	\N	t	\N	\N	15.00
060366ed-07ec-4d0d-8d3d-f97821717ffb	TEST-98cf53c501	\N	00000000-0000-0000-0000-000000000001	2025-05-27	2025-04-27	1000.00	MXN	\N	f	1	INSTALADO	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	2025-05-27 17:23:33.700102-05	15.00	0	0	\N	\N	2025-05-27 17:23:33.700102-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-27 19:39:10.658464-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	10.00	\N	0	\N	\N	\N	84000	\N	t	\N	\N	15.00
877231d5-7c90-42ae-b216-83c15e931ae7	TEST-c17bc3dbd3	\N	00000000-0000-0000-0000-000000000001	2025-05-27	2025-04-27	1000.00	MXN	\N	f	1	INSTALADO	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	2025-05-27 17:28:34.297643-05	15.00	0	0	\N	\N	2025-05-27 17:28:34.297643-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-27 19:39:10.658464-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	10.00	\N	0	\N	\N	\N	84000	\N	t	\N	\N	15.00
ea9a2fba-6917-47cd-9728-46a74f0e22a3	TEST-e319998dbf	\N	00000000-0000-0000-0000-000000000001	2025-05-27	2025-04-27	1000.00	MXN	\N	f	1	INSTALADO	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	2025-05-27 17:30:47.047877-05	15.00	0	0	\N	\N	2025-05-27 17:30:47.047877-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-27 19:39:10.658464-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	10.00	\N	0	\N	\N	\N	84000	\N	t	\N	\N	15.00
e9c3ea71-53b2-412d-a3ce-6b134d558892	TEST-17ba394d49	\N	00000000-0000-0000-0000-000000000001	2025-05-27	2025-04-27	1000.00	MXN	\N	f	1	INSTALADO	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	2025-05-27 17:33:25.904859-05	15.00	0	0	\N	\N	2025-05-27 17:33:25.904859-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-27 19:39:10.658464-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	10.00	\N	0	\N	\N	\N	84000	\N	t	\N	\N	15.00
e99dd95d-4280-4705-a4aa-f83dd29c0171	TEST-938377c49a	\N	00000000-0000-0000-0000-000000000001	2025-05-27	2025-04-27	1000.00	MXN	\N	f	1	INSTALADO	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	2025-05-27 17:46:56.814398-05	15.00	0	0	\N	\N	2025-05-27 17:46:56.814398-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-27 19:39:10.658464-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	10.00	\N	0	\N	\N	\N	84000	\N	t	\N	\N	15.00
008e61e4-207c-4c06-ab5c-3425450a7ce1	TEST-402fe12e40	\N	00000000-0000-0000-0000-000000000001	2025-05-27	2025-04-27	1000.00	MXN	\N	f	1	INSTALADO	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	2025-05-27 18:28:29.953019-05	15.00	0	0	\N	\N	2025-05-27 18:28:29.953019-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-27 19:39:10.658464-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	10.00	\N	0	\N	\N	\N	84000	\N	t	\N	\N	15.00
a91b9b5a-fd3e-485e-86d0-3a1c2325d40b	TEST-e683a91175	\N	00000000-0000-0000-0000-000000000001	2025-05-27	2025-04-27	1000.00	MXN	\N	f	1	EN_REENCAUCHE	\N	\N	2025-05-27 18:31:34.851548-05	15.00	0	0	\N	\N	2025-05-27 18:31:34.836198-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-27 19:39:10.658464-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	10.00	\N	0	\N	\N	\N	84000	\N	t	\N	\N	\N
235b4401-4bc0-4523-b9f8-5b912bb45f61	TEST-1e503f8b69	\N	00000000-0000-0000-0000-000000000001	2025-05-27	2025-04-27	1000.00	MXN	\N	f	1	INSTALADO	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	2025-05-27 18:29:28.574478-05	15.00	0	0	\N	\N	2025-05-27 18:29:28.574478-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-27 19:39:10.658464-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	10.00	\N	0	\N	\N	\N	84000	\N	t	\N	\N	15.00
a55368a0-6f59-42d3-9554-1daeec552a68	TEST-15e80f32c9	\N	00000000-0000-0000-0000-000000000001	2025-05-27	2025-04-27	1000.00	MXN	\N	f	1	EN_REENCAUCHE	\N	\N	2025-05-27 18:30:10.076367-05	15.00	0	0	\N	\N	2025-05-27 18:30:10.067322-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-27 19:39:10.658464-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	10.00	\N	0	\N	\N	\N	84000	\N	t	\N	\N	\N
1dee9c2a-b855-44c8-b5ef-8a6ed6bbfdda	TEST-e061815996	\N	00000000-0000-0000-0000-000000000001	2025-05-27	2025-04-27	1000.00	MXN	\N	f	1	EN_REENCAUCHE	\N	\N	2025-05-27 18:30:36.833039-05	15.00	0	0	\N	\N	2025-05-27 18:30:36.824245-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-27 19:39:10.658464-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	10.00	\N	0	\N	\N	\N	84000	\N	t	\N	\N	\N
0e2f0e46-2da7-4880-8af1-42518ac26c15	TEST-beb9612d4b	\N	00000000-0000-0000-0000-000000000001	2025-05-27	2025-04-27	1000.00	MXN	\N	f	1	EN_REENCAUCHE	\N	\N	2025-05-27 18:31:12.012882-05	15.00	0	0	\N	\N	2025-05-27 18:31:12.002237-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-27 19:39:10.658464-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	10.00	\N	0	\N	\N	\N	84000	\N	t	\N	\N	\N
3d986345-b3fb-4dd1-90b2-346934941389	TEST-26b30be035	\N	00000000-0000-0000-0000-000000000001	2025-05-27	2025-04-27	1000.00	MXN	\N	f	1	EN_REENCAUCHE	\N	\N	2025-05-27 18:32:00.312736-05	15.00	0	0	\N	\N	2025-05-27 18:32:00.303244-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-27 19:39:10.658464-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	10.00	\N	0	\N	\N	\N	84000	\N	t	\N	\N	\N
9046ee36-f52f-4737-a621-24393ae7b2f9	TEST-44b9414fc0	\N	00000000-0000-0000-0000-000000000001	2025-05-27	2025-04-27	1000.00	USD	\N	f	1	INSTALADO	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	2025-05-27 18:55:48.92463-05	15.00	0	0	\N	\N	2025-05-27 18:55:48.92463-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-27 19:39:10.658464-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	10.00	\N	0	\N	10000	\N	84000	\N	t	\N	\N	15.00
7bdb45b1-070c-4285-89e5-4afe1e09758f	TEST-ef3f24635b	\N	00000000-0000-0000-0000-000000000001	2025-05-27	2025-04-27	1000.00	USD	\N	f	1	INSTALADO	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	2025-05-27 18:56:24.081571-05	15.00	0	0	\N	\N	2025-05-27 18:56:24.081571-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-27 19:39:10.658464-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	10.00	\N	0	\N	10000	\N	84000	\N	t	\N	\N	15.00
1c47f273-0577-428c-b8ff-060b36cae727	TEST-01c6fd8707	\N	00000000-0000-0000-0000-000000000001	2025-05-27	2025-04-27	1000.00	USD	\N	f	1	INSTALADO	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	2025-05-27 18:58:21.265831-05	15.00	0	0	\N	\N	2025-05-27 18:58:21.265831-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-27 19:39:10.658464-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	10.00	\N	0	\N	10000	\N	84000	\N	t	\N	\N	15.00
952a0f71-37dd-46ec-a742-68edbb5b4949	TEST-7fa42f2fbf	\N	00000000-0000-0000-0000-000000000001	2025-05-27	2025-04-27	1000.00	USD	\N	f	1	INSTALADO	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	2025-05-27 19:00:01.354643-05	15.00	0	0	\N	\N	2025-05-27 19:00:01.354643-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-27 19:39:10.658464-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	10.00	\N	0	\N	10000	\N	84000	\N	t	\N	\N	15.00
48f567fc-bda6-439c-8d94-d4fcf1dab095	TEST-9430046ec8	\N	00000000-0000-0000-0000-000000000001	2025-05-27	2025-04-27	1000.00	USD	\N	f	1	INSTALADO	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	2025-05-27 19:01:52.342075-05	15.00	0	0	\N	\N	2025-05-27 19:01:52.342075-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-27 19:39:10.658464-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	10.00	\N	0	\N	10000	\N	84000	\N	t	\N	\N	15.00
39e353da-8436-4822-ac54-3f8952196e39	TEST-a65efc0e6b	\N	00000000-0000-0000-0000-000000000001	2025-05-27	2025-04-27	1000.00	USD	\N	f	1	INSTALADO	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	2025-05-27 19:03:39.721738-05	15.00	0	0	\N	\N	2025-05-27 19:03:39.721738-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-27 19:39:10.658464-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	10.00	\N	0	\N	10000	\N	84000	\N	t	\N	\N	15.00
fdb5b128-2182-4cbe-848a-abb9dc7706e1	TEST-87a215158d	\N	00000000-0000-0000-0000-000000000001	2025-05-27	2025-04-27	1000.00	USD	\N	f	1	INSTALADO	06abeeaf-0d42-4032-94a8-c46f3d6ee709	dddddddd-dddd-dddd-dddd-dddddddddddd	2025-05-27 19:05:24.446863-05	15.00	0	0	\N	\N	2025-05-27 19:05:24.446863-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-27 19:39:10.658464-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	10.00	\N	0	\N	10000	\N	84000	\N	t	\N	\N	15.00
\.


--
-- Data for Name: parametros_inventario; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.parametros_inventario (id, parametro_tipo, modelo_id, ubicacion_almacen_id, valor_numerico, valor_texto, activo, notas, creado_en, creado_por, actualizado_en, actualizado_por) FROM stdin;
\.


--
-- Data for Name: parametros_rendimiento_esperado_modelo; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.parametros_rendimiento_esperado_modelo (id, modelo_id, tipo_eje_aplicacion, km_esperado_vida_original_min, km_esperado_vida_original_max, notas, creado_en, creado_por, actualizado_en, actualizado_por) FROM stdin;
fbcc968c-f4c8-46a6-a080-d1700ba7936d	51bec9d7-c28c-4273-a79e-f9388e54130f	TRACCION	90000	130000	Parámetros para neumáticos en posición de tracción	2025-05-19 22:17:28.423587-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
633a39bf-fd5c-4e4e-9cbd-354f484edbe1	51bec9d7-c28c-4273-a79e-f9388e54130f	DIRECCION	82000	125000	Parámetro actualizado para prueba de auditoría	2025-05-19 22:17:28.423587-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-19 22:30:39.20287-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
c4949874-2a20-4526-9308-6e193d872d52	00000000-0000-0000-0000-000000000001	TRACCION	100000	150000	\N	2025-05-21 18:46:39.885472-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
\.


--
-- Data for Name: parametros_sistema; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.parametros_sistema (id, clave, valor, descripcion, creado_en, actualizado_en, creado_por, actualizado_por) FROM stdin;
1	UMBRAL_ALERTA_PROFUNDIDAD_MM	2.0	Distancia mínima de la profundidad actual al mínimo de retiro para alertar	2025-05-27 01:32:31.221822-05	2025-05-27 01:32:31.221822-05	SISTEMA	SISTEMA
2	UMBRAL_CAMBIO_VIDA_UTIL_PORCENTAJE	5	Cambio porcentual en vida útil que dispara actualización de inspección	2025-05-27 01:32:31.221822-05	2025-05-27 01:32:31.221822-05	SISTEMA	SISTEMA
3	UMBRAL_KM_PARA_ALERTA_INSPECCION	500	Kilómetros restantes para la próxima inspección que disparan alerta	2025-05-27 01:32:31.221822-05	2025-05-27 01:32:31.221822-05	SISTEMA	SISTEMA
4	INTERVALO_INSPECCION_KM	10000	Intervalo en kilómetros para la próxima inspección de neumáticos	2025-05-27 11:25:44.43348-05	2025-05-27 11:25:44.43348-05	SISTEMA	SISTEMA
5	INTERVALO_INSPECCION_DIAS	30	Intervalo en días para la próxima inspección de neumáticos	2025-05-27 11:25:44.43348-05	2025-05-27 11:25:44.43348-05	SISTEMA	SISTEMA
\.


--
-- Data for Name: permisos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.permisos (id, nombre_recurso, accion, descripcion, creado_en) FROM stdin;
00000000-0000-0000-0001-000000000001	usuarios	ver	Ver lista de usuarios	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0001-000000000002	usuarios	crear	Crear nuevos usuarios	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0001-000000000003	usuarios	editar	Editar usuarios existentes	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0001-000000000004	usuarios	eliminar	Eliminar usuarios	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0001-000000000005	usuarios	cambiar_estado	Activar/desactivar usuarios	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0002-000000000001	roles	ver	Ver lista de roles	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0002-000000000002	roles	crear	Crear nuevos roles	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0002-000000000003	roles	editar	Editar roles existentes	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0002-000000000004	roles	eliminar	Eliminar roles	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0002-000000000005	roles	asignar_permisos	Asignar/revocar permisos a roles	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0003-000000000001	vehiculos	ver	Ver lista de vehículos	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0003-000000000002	vehiculos	crear	Crear nuevos vehículos	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0003-000000000003	vehiculos	editar	Editar vehículos existentes	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0003-000000000004	vehiculos	eliminar	Eliminar vehículos	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0003-000000000005	vehiculos	cambiar_estado	Activar/desactivar vehículos	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0004-000000000001	neumaticos	ver	Ver lista de neumáticos	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0004-000000000002	neumaticos	crear	Crear nuevos neumáticos	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0004-000000000003	neumaticos	editar	Editar neumáticos existentes	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0004-000000000004	neumaticos	eliminar	Eliminar neumáticos	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0004-000000000005	neumaticos	registrar_evento	Registrar eventos en neumáticos	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0005-000000000001	inventario	ver	Ver estado del inventario	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0005-000000000002	inventario	ajustar	Realizar ajustes de inventario	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0005-000000000003	inventario	reporte	Generar reportes de inventario	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0006-000000000001	mantenimiento	ver	Ver registros de mantenimiento	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0006-000000000002	mantenimiento	registrar	Registrar actividades de mantenimiento	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0006-000000000003	mantenimiento	programar	Programar mantenimientos preventivos	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0007-000000000001	reportes	ver	Ver reportes	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0007-000000000002	reportes	exportar	Exportar reportes	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0008-000000000001	configuracion	ver	Ver configuración del sistema	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0008-000000000002	configuracion	editar	Editar configuración del sistema	2025-05-19 12:07:58.794203-05
00000000-0000-0000-0009-000000000001	auditoria	ver	Ver registros de auditoría	2025-05-19 12:07:58.794203-05
\.


--
-- Data for Name: posiciones_neumatico; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.posiciones_neumatico (id, configuracion_eje_id, codigo_posicion, etiqueta_posicion, lado, posicion_relativa, es_interna, es_direccion, es_traccion, requiere_neumatico_especifico, creado_en, creado_por, actualizado_en, actualizado_por) FROM stdin;
dddddddd-dddd-dddd-dddd-dddddddddddd	cccccccc-cccc-cccc-cccc-cccccccccccc	POS-001	Delantero Izquierdo	IZQUIERDO	1	f	t	t	f	2025-05-23 16:53:02.019804-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
\.


--
-- Data for Name: proveedores; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.proveedores (id, nombre, tipo, ruc, contacto_principal, telefono, email, direccion, activo, creado_en, creado_por, actualizado_en, actualizado_por) FROM stdin;
c532e7c3-85ee-48f8-ad47-8d4e79112881	Proveedor de Prueba 1ddcbbab	\N	\N	\N	123-456-7890	proveedord884f4da@example.com	Calle Falsa 123	t	2025-05-19 16:30:42.934675-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
aee67a19-af2d-4b9d-94cf-27d86e09b369	Nuevo Nombre Proveedor SA	FABRICANTE	20010101000	Juan Pérez	123456789	proveedor@ejemplo.com	Av. Ejemplo 123, Lima	t	2025-05-19 16:12:52.118923-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-05-19 16:27:03.31491-05	\N
d1bbd8da-922d-4b9b-98b3-ab77ac0019ea	Prueba 1	\N	20123456789	\N	\N	\N	\N	t	2025-05-21 23:11:57.212851-05	\N	\N	\N
f5fed807-8882-4d3e-8373-dcca0bcf7b8a	Prueba 3	\N	20000000005	\N	\N	\N	\N	t	2025-05-21 23:11:57.218729-05	\N	\N	\N
57e6f759-35ef-43d2-85d3-9607ff599c04	Prueba 4	\N	20102030405	\N	\N	\N	\N	t	2025-05-21 23:11:57.219693-05	\N	\N	\N
\.


--
-- Data for Name: registros_odometro; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.registros_odometro (id, vehiculo_id, odometro, fecha_medicion, fuente, creado_por, notas) FROM stdin;
7a8d35a4-e3e1-4b25-95fa-c288132505c6	06abeeaf-0d42-4032-94a8-c46f3d6ee709	15000	2025-04-22 00:11:42.540618-05	manual	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	Primer registro de mantenimiento
61181688-9133-45a0-a28b-fba64a311ab8	06abeeaf-0d42-4032-94a8-c46f3d6ee709	15500	2025-05-07 00:11:42.540618-05	manual	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	Segundo registro de mantenimiento
f67ac8c9-3a87-4b7e-b646-3367ac2cfe5f	06abeeaf-0d42-4032-94a8-c46f3d6ee709	15850	2025-05-22 00:11:42.540618-05	sistema	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	Actualización de prueba
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id, nombre, descripcion, es_rol_sistema, creado_en, creado_por, actualizado_en, actualizado_por) FROM stdin;
00000000-0000-0000-0000-000000000001	Administrador	Administrador del sistema con acceso completo	t	2025-05-19 12:11:13.852583-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
00000000-0000-0000-0000-000000000002	Supervisor	Supervisor de operaciones	t	2025-05-19 12:11:13.852583-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
00000000-0000-0000-0000-000000000003	Técnico	Técnico de mantenimiento	t	2025-05-19 12:11:13.852583-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
00000000-0000-0000-0000-000000000004	Operador	Operador de vehículos	t	2025-05-19 12:11:13.852583-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
00000000-0000-0000-0000-000000000005	Consulta	Usuario de solo lectura	t	2025-05-19 12:11:13.852583-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
\.


--
-- Data for Name: roles_permisos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles_permisos (rol_id, permiso_id, asignado_en, asignado_por) FROM stdin;
00000000-0000-0000-0000-000000000005	00000000-0000-0000-0001-000000000001	2025-05-22 00:43:06.235533-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000005	00000000-0000-0000-0002-000000000001	2025-05-22 00:43:06.235533-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000005	00000000-0000-0000-0003-000000000001	2025-05-22 00:43:06.235533-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000005	00000000-0000-0000-0004-000000000001	2025-05-22 00:43:06.235533-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000005	00000000-0000-0000-0005-000000000001	2025-05-22 00:43:06.235533-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000005	00000000-0000-0000-0006-000000000001	2025-05-22 00:43:06.235533-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000005	00000000-0000-0000-0007-000000000001	2025-05-22 00:43:06.235533-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000005	00000000-0000-0000-0008-000000000001	2025-05-22 00:43:06.235533-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000005	00000000-0000-0000-0009-000000000001	2025-05-22 00:43:06.235533-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000004	00000000-0000-0000-0003-000000000001	2025-05-22 00:43:06.239905-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000004	00000000-0000-0000-0004-000000000001	2025-05-22 00:43:06.239905-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000004	00000000-0000-0000-0004-000000000005	2025-05-22 00:43:06.239905-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000003	00000000-0000-0000-0003-000000000001	2025-05-22 00:43:06.240957-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000003	00000000-0000-0000-0004-000000000001	2025-05-22 00:43:06.240957-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000003	00000000-0000-0000-0004-000000000005	2025-05-22 00:43:06.240957-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000003	00000000-0000-0000-0006-000000000001	2025-05-22 00:43:06.240957-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000003	00000000-0000-0000-0006-000000000002	2025-05-22 00:43:06.240957-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000002	00000000-0000-0000-0003-000000000001	2025-05-22 00:43:06.241965-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000002	00000000-0000-0000-0003-000000000003	2025-05-22 00:43:06.241965-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000002	00000000-0000-0000-0004-000000000001	2025-05-22 00:43:06.241965-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000002	00000000-0000-0000-0004-000000000003	2025-05-22 00:43:06.241965-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000002	00000000-0000-0000-0004-000000000005	2025-05-22 00:43:06.241965-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000002	00000000-0000-0000-0005-000000000001	2025-05-22 00:43:06.241965-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000002	00000000-0000-0000-0005-000000000003	2025-05-22 00:43:06.241965-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000002	00000000-0000-0000-0006-000000000001	2025-05-22 00:43:06.241965-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000002	00000000-0000-0000-0007-000000000001	2025-05-22 00:43:06.241965-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0001-000000000001	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0001-000000000002	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0001-000000000003	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0001-000000000004	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0001-000000000005	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0002-000000000001	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0002-000000000002	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0002-000000000003	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0002-000000000004	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0002-000000000005	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0003-000000000001	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0003-000000000002	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0003-000000000003	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0003-000000000004	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0003-000000000005	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0004-000000000001	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0004-000000000002	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0004-000000000003	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0004-000000000004	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0004-000000000005	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0005-000000000001	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0005-000000000002	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0005-000000000003	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0006-000000000001	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0006-000000000002	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0006-000000000003	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0007-000000000001	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0007-000000000002	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0008-000000000001	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0008-000000000002	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
00000000-0000-0000-0000-000000000001	00000000-0000-0000-0009-000000000001	2025-05-19 12:11:13.857808-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
\.


--
-- Data for Name: rutas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.rutas (id, codigo, nombre, descripcion, distancia_total_km, ida_vuelta, activa, creado_en, creado_por, actualizado_en, actualizado_por) FROM stdin;
\.


--
-- Data for Name: tareas_programadas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tareas_programadas (id, nombre_tarea, descripcion, frecuencia_dias, ultima_ejecucion, proxima_ejecucion, activa, script_sql, creado_en, creado_por, actualizado_en, actualizado_por) FROM stdin;
1	actualizar_vida_util_neumaticos	Recalcula la vida útil restante de todos los neumáticos activos	1	2025-05-27 01:53:44.000486-05	2025-05-28 01:53:44.000486-05	t	UPDATE neumaticos SET vida_util_restante_km = public.calcular_vida_util_restante(id) WHERE activo = TRUE;	2025-05-27 01:53:15.655976-05	SISTEMA	2025-05-27 01:53:44.000486-05	SISTEMA
\.


--
-- Data for Name: tipos_ruta; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tipos_ruta (id, nombre_ruta, descripcion, distancia_total_km_ciclo, distancia_trocha_km_ciclo, distancia_asfalto_km_ciclo, distancia_otro_terreno_km_ciclo, porcentaje_promedio_con_carga, creado_en, creado_por, actualizado_en, actualizado_por) FROM stdin;
20000000-0000-0000-0000-000000000001	RUTA_MINA_SUR_CICLO_COMPLETO	Ciclo completo de ida y vuelta a la mina del sur.	650.00	16.60	633.40	0.00	50.00	2025-05-19 22:10:56.993267-05	\N	\N	\N
9d1cb958-e230-430a-8c1f-afd45547ab60	RUTA_MINA_NORTE	Ruta de ida y vuelta a la mina del norte con terreno mixto	550.50	150.25	400.25	0.00	60.00	2025-05-19 22:26:31.079624-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
\.


--
-- Data for Name: tipos_vehiculo; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tipos_vehiculo (id, nombre, descripcion, categoria_principal, subtipo, ejes_standard, activo, creado_en, creado_por, actualizado_en, actualizado_por) FROM stdin;
00000000-0000-0000-0000-000000000005	Tractocamión 2 Ejes	Tractocamión de 2 ejes	Tractocamión	Pesado	2	t	2025-05-19 12:19:24.294531-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
7a957cc2-e201-455b-a951-c245102da748	Tractocamión	Vehículo pesado para transporte de carga	\N	\N	2	t	2025-05-21 22:06:54.203985-05	\N	\N	\N
09bbd6de-e358-4956-a33a-48ebc70e7f05	Volteo	Vehículo para transporte de materiales a granel	\N	\N	2	t	2025-05-21 22:06:54.203985-05	\N	\N	\N
58668524-e461-4705-ba20-509f5e658bc2	Redila	Vehículo con caja abierta para carga general	\N	\N	2	t	2025-05-21 22:06:54.203985-05	\N	\N	\N
aa2c4471-4485-4665-8838-0760df050285	Torton	Vehículo articulado para transporte de carga	\N	\N	2	t	2025-05-21 22:06:54.203985-05	\N	\N	\N
f5c9bb61-3ce7-4371-8a87-81a82ef35424	Rabón	Vehículo rígido de gran capacidad	\N	\N	2	t	2025-05-21 22:06:54.203985-05	\N	\N	\N
11111111-1111-1111-1111-111111111100	Tipo de Prueba	Para pruebas de instalación	\N	\N	2	t	2025-05-27 02:52:01.469645-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuarios (id, username, nombre_completo, email, password_hash, activo, ultimo_login, creado_en, creado_por, actualizado_en, actualizado_por) FROM stdin;
a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin	Administrador del Sistema	admin@gesneu.com	$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW	t	2025-05-19 12:09:50.93248-05	2025-05-19 12:09:50.93248-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
400bd946-6f19-4a2e-8580-d147575a4756	supervisor	Supervisor de Flota	supervisor@empresa.com	$2b$12$IW.bPWqtCRpVZTIPtWz6L.VaaGqvQT190h/3jFWXn9Iz/jUgToq2G	t	\N	2025-05-21 22:06:53.700684-05	\N	\N	\N
36b01b0b-cd42-4235-8c64-44f879a998ff	operador	Operador de Vehículo	operador@empresa.com	$2b$12$MWecxcnKWAiE8E3al.OPc.OxFiZPwJ6Z8FZtfZ8i/0G9NnEDA3enO	t	\N	2025-05-21 22:06:53.700684-05	\N	\N	\N
\.


--
-- Data for Name: usuarios_roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuarios_roles (usuario_id, rol_id, asignado_en, asignado_por) FROM stdin;
a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	00000000-0000-0000-0000-000000000001	2025-05-19 12:11:13.860803-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
\.


--
-- Data for Name: vehiculos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vehiculos (id, tipo_vehiculo_id, placa, vin, numero_economico, marca, modelo_vehiculo, anio_fabricacion, fecha_alta, fecha_baja, activo, odometro_actual, fecha_ultimo_odometro, ubicacion_actual, notas, creado_en, creado_por, actualizado_en, actualizado_por, peso_carga_maxima_diseno_ton) FROM stdin;
06abeeaf-0d42-4032-94a8-c46f3d6ee709	00000000-0000-0000-0000-000000000005	ABC-123	\N	TRAC-001	Volvo	FH16	2022	2025-05-19	\N	t	\N	\N	\N	\N	2025-05-19 12:20:43.428293-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	36.50
22222222-2222-2222-2222-222222222222	11111111-1111-1111-1111-111111111100	TEST123	\N	TEST-001	Marca Prueba	Modelo Prueba	2023	2025-05-27	\N	t	10000	\N	\N	\N	2025-05-27 02:52:01.476288-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N
\.


--
-- Name: auditoria_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auditoria_log_id_seq', 414, true);


--
-- Name: bitacora_mantenimiento_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bitacora_mantenimiento_id_seq', 5, true);


--
-- Name: parametros_sistema_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.parametros_sistema_id_seq', 53, true);


--
-- Name: tareas_programadas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tareas_programadas_id_seq', 1, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: alertas alertas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alertas
    ADD CONSTRAINT alertas_pkey PRIMARY KEY (id);


--
-- Name: almacenes almacenes_codigo_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.almacenes
    ADD CONSTRAINT almacenes_codigo_key UNIQUE (codigo);


--
-- Name: almacenes almacenes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.almacenes
    ADD CONSTRAINT almacenes_pkey PRIMARY KEY (id);


--
-- Name: auditoria_log auditoria_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auditoria_log
    ADD CONSTRAINT auditoria_log_pkey PRIMARY KEY (id);


--
-- Name: bitacora_mantenimiento bitacora_mantenimiento_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bitacora_mantenimiento
    ADD CONSTRAINT bitacora_mantenimiento_pkey PRIMARY KEY (id);


--
-- Name: bitacora_operaciones_neumaticos bitacora_operaciones_neumatic_operacion_id_neumatico_id_tip_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bitacora_operaciones_neumaticos
    ADD CONSTRAINT bitacora_operaciones_neumatic_operacion_id_neumatico_id_tip_key UNIQUE (operacion_id, neumatico_id, tipo_accion);


--
-- Name: bitacora_operaciones_neumaticos bitacora_operaciones_neumaticos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bitacora_operaciones_neumaticos
    ADD CONSTRAINT bitacora_operaciones_neumaticos_pkey PRIMARY KEY (id);


--
-- Name: bitacora_operaciones bitacora_operaciones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bitacora_operaciones
    ADD CONSTRAINT bitacora_operaciones_pkey PRIMARY KEY (id);


--
-- Name: configuracion_auditoria configuracion_auditoria_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.configuracion_auditoria
    ADD CONSTRAINT configuracion_auditoria_pkey PRIMARY KEY (nombre_tabla);


--
-- Name: configuraciones_eje configuraciones_eje_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.configuraciones_eje
    ADD CONSTRAINT configuraciones_eje_pkey PRIMARY KEY (id);


--
-- Name: errores_aplicacion errores_aplicacion_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.errores_aplicacion
    ADD CONSTRAINT errores_aplicacion_pkey PRIMARY KEY (id);


--
-- Name: especificaciones_desgaste especificaciones_desgaste_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.especificaciones_desgaste
    ADD CONSTRAINT especificaciones_desgaste_pkey PRIMARY KEY (id);


--
-- Name: eventos_neumaticos eventos_neumaticos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eventos_neumaticos
    ADD CONSTRAINT eventos_neumaticos_pkey PRIMARY KEY (id);


--
-- Name: fabricantes_neumatico fabricantes_neumatico_codigo_abreviado_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fabricantes_neumatico
    ADD CONSTRAINT fabricantes_neumatico_codigo_abreviado_key UNIQUE (codigo_abreviado);


--
-- Name: fabricantes_neumatico fabricantes_neumatico_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fabricantes_neumatico
    ADD CONSTRAINT fabricantes_neumatico_pkey PRIMARY KEY (id);


--
-- Name: garantias_neumaticos garantias_neumaticos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.garantias_neumaticos
    ADD CONSTRAINT garantias_neumaticos_pkey PRIMARY KEY (id);


--
-- Name: historial_estados_neumaticos historial_estados_neumaticos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.historial_estados_neumaticos
    ADD CONSTRAINT historial_estados_neumaticos_pkey PRIMARY KEY (id);


--
-- Name: mediciones_profundidad mediciones_profundidad_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mediciones_profundidad
    ADD CONSTRAINT mediciones_profundidad_pkey PRIMARY KEY (id);


--
-- Name: modelos_neumatico modelos_neumatico_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modelos_neumatico
    ADD CONSTRAINT modelos_neumatico_pkey PRIMARY KEY (id);


--
-- Name: modelos_posiciones_permitidas modelos_posiciones_permitidas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modelos_posiciones_permitidas
    ADD CONSTRAINT modelos_posiciones_permitidas_pkey PRIMARY KEY (modelo_neumatico_id, posicion_neumatico_id);


--
-- Name: motivos_desecho motivos_desecho_codigo_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.motivos_desecho
    ADD CONSTRAINT motivos_desecho_codigo_key UNIQUE (codigo);


--
-- Name: motivos_desecho motivos_desecho_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.motivos_desecho
    ADD CONSTRAINT motivos_desecho_pkey PRIMARY KEY (id);


--
-- Name: neumaticos neumaticos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.neumaticos
    ADD CONSTRAINT neumaticos_pkey PRIMARY KEY (id);


--
-- Name: parametros_inventario parametros_inventario_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parametros_inventario
    ADD CONSTRAINT parametros_inventario_pkey PRIMARY KEY (id);


--
-- Name: parametros_rendimiento_esperado_modelo parametros_rendimiento_esperado_modelo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parametros_rendimiento_esperado_modelo
    ADD CONSTRAINT parametros_rendimiento_esperado_modelo_pkey PRIMARY KEY (id);


--
-- Name: parametros_sistema parametros_sistema_clave_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parametros_sistema
    ADD CONSTRAINT parametros_sistema_clave_key UNIQUE (clave);


--
-- Name: parametros_sistema parametros_sistema_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parametros_sistema
    ADD CONSTRAINT parametros_sistema_pkey PRIMARY KEY (id);


--
-- Name: permisos permisos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permisos
    ADD CONSTRAINT permisos_pkey PRIMARY KEY (id);


--
-- Name: posiciones_neumatico posiciones_neumatico_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posiciones_neumatico
    ADD CONSTRAINT posiciones_neumatico_pkey PRIMARY KEY (id);


--
-- Name: proveedores proveedores_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proveedores
    ADD CONSTRAINT proveedores_pkey PRIMARY KEY (id);


--
-- Name: proveedores proveedores_ruc_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proveedores
    ADD CONSTRAINT proveedores_ruc_key UNIQUE (ruc);


--
-- Name: registros_odometro registros_odometro_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registros_odometro
    ADD CONSTRAINT registros_odometro_pkey PRIMARY KEY (id);


--
-- Name: roles roles_nombre_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_nombre_key UNIQUE (nombre);


--
-- Name: roles_permisos roles_permisos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles_permisos
    ADD CONSTRAINT roles_permisos_pkey PRIMARY KEY (rol_id, permiso_id);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: rutas rutas_codigo_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rutas
    ADD CONSTRAINT rutas_codigo_key UNIQUE (codigo);


--
-- Name: rutas rutas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rutas
    ADD CONSTRAINT rutas_pkey PRIMARY KEY (id);


--
-- Name: tareas_programadas tareas_programadas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tareas_programadas
    ADD CONSTRAINT tareas_programadas_pkey PRIMARY KEY (id);


--
-- Name: tipos_ruta tipos_ruta_nombre_ruta_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipos_ruta
    ADD CONSTRAINT tipos_ruta_nombre_ruta_key UNIQUE (nombre_ruta);


--
-- Name: tipos_ruta tipos_ruta_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipos_ruta
    ADD CONSTRAINT tipos_ruta_pkey PRIMARY KEY (id);


--
-- Name: tipos_vehiculo tipos_vehiculo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipos_vehiculo
    ADD CONSTRAINT tipos_vehiculo_pkey PRIMARY KEY (id);


--
-- Name: configuraciones_eje uq_configuracion_eje; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.configuraciones_eje
    ADD CONSTRAINT uq_configuracion_eje UNIQUE (tipo_vehiculo_id, numero_eje);


--
-- Name: parametros_inventario uq_parametro_inventario; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parametros_inventario
    ADD CONSTRAINT uq_parametro_inventario UNIQUE (parametro_tipo, modelo_id, ubicacion_almacen_id);


--
-- Name: parametros_inventario uq_parametro_inventario_gesneu; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parametros_inventario
    ADD CONSTRAINT uq_parametro_inventario_gesneu UNIQUE NULLS NOT DISTINCT (parametro_tipo, modelo_id, ubicacion_almacen_id);


--
-- Name: permisos uq_permiso_recurso_accion; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permisos
    ADD CONSTRAINT uq_permiso_recurso_accion UNIQUE (nombre_recurso, accion);


--
-- Name: posiciones_neumatico uq_posicion_neumatico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posiciones_neumatico
    ADD CONSTRAINT uq_posicion_neumatico UNIQUE (configuracion_eje_id, codigo_posicion);


--
-- Name: parametros_rendimiento_esperado_modelo uq_rendimiento_modelo_eje_gesneu; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parametros_rendimiento_esperado_modelo
    ADD CONSTRAINT uq_rendimiento_modelo_eje_gesneu UNIQUE (modelo_id, tipo_eje_aplicacion);


--
-- Name: usuarios usuarios_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_email_key UNIQUE (email);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);


--
-- Name: usuarios_roles usuarios_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios_roles
    ADD CONSTRAINT usuarios_roles_pkey PRIMARY KEY (usuario_id, rol_id);


--
-- Name: usuarios usuarios_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_username_key UNIQUE (username);


--
-- Name: vehiculos vehiculos_numero_economico_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehiculos
    ADD CONSTRAINT vehiculos_numero_economico_key UNIQUE (numero_economico);


--
-- Name: vehiculos vehiculos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehiculos
    ADD CONSTRAINT vehiculos_pkey PRIMARY KEY (id);


--
-- Name: vehiculos vehiculos_placa_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehiculos
    ADD CONSTRAINT vehiculos_placa_key UNIQUE (placa);


--
-- Name: vehiculos vehiculos_vin_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehiculos
    ADD CONSTRAINT vehiculos_vin_key UNIQUE (vin);


--
-- Name: idx_alertas_estado_ts; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_alertas_estado_ts ON public.alertas USING btree (estado_alerta, timestamp_generacion DESC);


--
-- Name: idx_alertas_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_alertas_fecha ON public.alertas USING btree (timestamp_generacion DESC) WHERE ((estado_alerta)::text = 'NUEVA'::text);


--
-- Name: idx_alertas_neumatico; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_alertas_neumatico ON public.alertas USING btree (neumatico_id) WHERE (neumatico_id IS NOT NULL);


--
-- Name: idx_audit_log_cambios_gin; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_log_cambios_gin ON public.auditoria_log USING gin (cambios);


--
-- Name: idx_audit_log_datos_antiguos_gin; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_log_datos_antiguos_gin ON public.auditoria_log USING gin (datos_antiguos);


--
-- Name: idx_audit_log_datos_nuevos_gin; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_log_datos_nuevos_gin ON public.auditoria_log USING gin (datos_nuevos);


--
-- Name: idx_audit_log_id_entidad; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_log_id_entidad ON public.auditoria_log USING btree (id_entidad) WHERE (id_entidad IS NOT NULL);


--
-- Name: idx_audit_log_nombre_tabla_lower; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_log_nombre_tabla_lower ON public.auditoria_log USING btree (lower((nombre_tabla)::text));


--
-- Name: idx_audit_log_operacion_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_log_operacion_timestamp ON public.auditoria_log USING btree (operacion, timestamp_log);


--
-- Name: idx_audit_log_tabla_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_log_tabla_timestamp ON public.auditoria_log USING btree (nombre_tabla, timestamp_log);


--
-- Name: idx_audit_log_usuario_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_log_usuario_timestamp ON public.auditoria_log USING btree (usuario_aplicacion_username, timestamp_log) WHERE (usuario_aplicacion_username IS NOT NULL);


--
-- Name: idx_bitacora_mantenimiento_exito; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_bitacora_mantenimiento_exito ON public.bitacora_mantenimiento USING btree (exito);


--
-- Name: idx_bitacora_mantenimiento_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_bitacora_mantenimiento_fecha ON public.bitacora_mantenimiento USING btree (fecha_ejecucion);


--
-- Name: idx_bitacora_mantenimiento_tipo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_bitacora_mantenimiento_tipo ON public.bitacora_mantenimiento USING btree (tipo);


--
-- Name: idx_bitacora_op_neu_neumatico; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_bitacora_op_neu_neumatico ON public.bitacora_operaciones_neumaticos USING btree (neumatico_id);


--
-- Name: idx_bitacora_op_neu_operacion; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_bitacora_op_neu_operacion ON public.bitacora_operaciones_neumaticos USING btree (operacion_id);


--
-- Name: idx_bitacora_op_neu_posicion; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_bitacora_op_neu_posicion ON public.bitacora_operaciones_neumaticos USING btree (posicion_neumatico_id) WHERE (posicion_neumatico_id IS NOT NULL);


--
-- Name: idx_bitacora_op_neu_tipo_accion; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_bitacora_op_neu_tipo_accion ON public.bitacora_operaciones_neumaticos USING btree (tipo_accion);


--
-- Name: idx_bitacora_operaciones_almacen; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_bitacora_operaciones_almacen ON public.bitacora_operaciones USING btree (almacen_id) WHERE (almacen_id IS NOT NULL);


--
-- Name: idx_bitacora_operaciones_estado; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_bitacora_operaciones_estado ON public.bitacora_operaciones USING btree (estado_operacion);


--
-- Name: idx_bitacora_operaciones_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_bitacora_operaciones_fecha ON public.bitacora_operaciones USING btree (fecha_operacion);


--
-- Name: idx_bitacora_operaciones_vehiculo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_bitacora_operaciones_vehiculo ON public.bitacora_operaciones USING btree (vehiculo_id) WHERE (vehiculo_id IS NOT NULL);


--
-- Name: idx_errores_aplicacion_creado_en; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_errores_aplicacion_creado_en ON public.errores_aplicacion USING btree (creado_en);


--
-- Name: idx_errores_aplicacion_nombre_funcion; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_errores_aplicacion_nombre_funcion ON public.errores_aplicacion USING btree (nombre_funcion);


--
-- Name: idx_errores_aplicacion_resuelto; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_errores_aplicacion_resuelto ON public.errores_aplicacion USING btree (resuelto);


--
-- Name: idx_especificaciones_desgaste_modelo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_especificaciones_desgaste_modelo ON public.especificaciones_desgaste USING btree (modelo_neumatico_id);


--
-- Name: idx_especificaciones_desgaste_tipo_posicion; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_especificaciones_desgaste_tipo_posicion ON public.especificaciones_desgaste USING btree (tipo_posicion);


--
-- Name: idx_eventos_neumatico; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_eventos_neumatico ON public.eventos_neumaticos USING btree (neumatico_id);


--
-- Name: idx_eventos_neumatico_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_eventos_neumatico_fecha ON public.eventos_neumaticos USING btree (neumatico_id, timestamp_evento DESC);


--
-- Name: idx_eventos_neumatico_tipo_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_eventos_neumatico_tipo_fecha ON public.eventos_neumaticos USING btree (neumatico_id, tipo_evento, timestamp_evento DESC);


--
-- Name: idx_eventos_neumaticos_tipo_ruta_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_eventos_neumaticos_tipo_ruta_id ON public.eventos_neumaticos USING btree (tipo_ruta_id);


--
-- Name: idx_eventos_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_eventos_timestamp ON public.eventos_neumaticos USING btree (timestamp_evento DESC);


--
-- Name: idx_eventos_tipo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_eventos_tipo ON public.eventos_neumaticos USING btree (tipo_evento);


--
-- Name: idx_eventos_usuario; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_eventos_usuario ON public.eventos_neumaticos USING btree (usuario_id);


--
-- Name: idx_fabricantes_nombre_unique; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_fabricantes_nombre_unique ON public.fabricantes_neumatico USING btree (public.f_immutable_lower_unaccent((nombre)::text)) WHERE (activo = true);


--
-- Name: idx_garantias_neumatico_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_garantias_neumatico_id ON public.garantias_neumaticos USING btree (neumatico_id);


--
-- Name: idx_garantias_vencimiento; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_garantias_vencimiento ON public.garantias_neumaticos USING btree (fecha_fin) WHERE (fecha_fin IS NOT NULL);


--
-- Name: idx_hist_estados_estado_nuevo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_hist_estados_estado_nuevo ON public.historial_estados_neumaticos USING btree (estado_nuevo);


--
-- Name: idx_hist_estados_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_hist_estados_fecha ON public.historial_estados_neumaticos USING btree (fecha_cambio);


--
-- Name: idx_hist_estados_neumatico_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_hist_estados_neumatico_id ON public.historial_estados_neumaticos USING btree (neumatico_id);


--
-- Name: idx_mediciones_profundidad_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_mediciones_profundidad_fecha ON public.mediciones_profundidad USING btree (fecha_medicion);


--
-- Name: idx_mediciones_profundidad_neumatico_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_mediciones_profundidad_neumatico_id ON public.mediciones_profundidad USING btree (neumatico_id);


--
-- Name: idx_modelos_fabricante; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_modelos_fabricante ON public.modelos_neumatico USING btree (fabricante_id);


--
-- Name: idx_modelos_unique; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_modelos_unique ON public.modelos_neumatico USING btree (fabricante_id, public.f_immutable_lower_unaccent((nombre_modelo)::text), medida) WHERE (fabricante_id IS NOT NULL);


--
-- Name: idx_mv_desempeno_modelos_activo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_mv_desempeno_modelos_activo ON public.mv_desempeno_modelos USING btree (modelo_activo);


--
-- Name: idx_mv_desempeno_modelos_fabricante; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_mv_desempeno_modelos_fabricante ON public.mv_desempeno_modelos USING btree (fabricante_nombre);


--
-- Name: idx_mv_desempeno_modelos_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_mv_desempeno_modelos_id ON public.mv_desempeno_modelos USING btree (modelo_id);


--
-- Name: idx_mv_eventos_recientes_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_mv_eventos_recientes_fecha ON public.mv_eventos_recientes USING btree (timestamp_evento DESC);


--
-- Name: idx_mv_eventos_recientes_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_mv_eventos_recientes_id ON public.mv_eventos_recientes USING btree (id);


--
-- Name: idx_mv_eventos_recientes_serie; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_mv_eventos_recientes_serie ON public.mv_eventos_recientes USING btree (numero_serie);


--
-- Name: idx_mv_resumen_estado; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_mv_resumen_estado ON public.mv_resumen_neumaticos_estado USING btree (estado_actual);


--
-- Name: idx_neumaticos_activos; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_neumaticos_activos ON public.neumaticos USING btree (estado_actual) WHERE (estado_actual <> 'DESECHADO'::public.estado_neumatico_enum);


--
-- Name: idx_neumaticos_activos_compuesto; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_neumaticos_activos_compuesto ON public.neumaticos USING btree (estado_actual, modelo_id, vida_util_restante_km) WHERE (estado_actual <> 'DESECHADO'::public.estado_neumatico_enum);


--
-- Name: idx_neumaticos_dot; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_neumaticos_dot ON public.neumaticos USING btree (dot) WHERE (dot IS NOT NULL);


--
-- Name: idx_neumaticos_estado; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_neumaticos_estado ON public.neumaticos USING btree (estado_actual);


--
-- Name: idx_neumaticos_estado_actual; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_neumaticos_estado_actual ON public.neumaticos USING btree (estado_actual) WHERE (estado_actual <> 'DESECHADO'::public.estado_neumatico_enum);


--
-- Name: idx_neumaticos_estado_ubicacion; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_neumaticos_estado_ubicacion ON public.neumaticos USING btree (estado_actual, ubicacion_actual_vehiculo_id, ubicacion_actual_posicion_id) WHERE (estado_actual = 'INSTALADO'::public.estado_neumatico_enum);


--
-- Name: idx_neumaticos_fechas_compra; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_neumaticos_fechas_compra ON public.neumaticos USING btree (fecha_compra);


--
-- Name: idx_neumaticos_modelo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_neumaticos_modelo ON public.neumaticos USING btree (modelo_id);


--
-- Name: idx_neumaticos_modelo_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_neumaticos_modelo_id ON public.neumaticos USING btree (modelo_id);


--
-- Name: idx_neumaticos_prox_inspeccion; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_neumaticos_prox_inspeccion ON public.neumaticos USING btree (proxima_inspeccion_fecha) WHERE (proxima_inspeccion_fecha IS NOT NULL);


--
-- Name: idx_neumaticos_proximos_desecho; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_neumaticos_proximos_desecho ON public.neumaticos USING btree (estado_actual, fecha_fabricacion) WHERE (estado_actual <> 'DESECHADO'::public.estado_neumatico_enum);


--
-- Name: idx_neumaticos_sensor_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_neumaticos_sensor_id ON public.neumaticos USING btree (sensor_id) WHERE (sensor_id IS NOT NULL);


--
-- Name: idx_neumaticos_serie; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_neumaticos_serie ON public.neumaticos USING btree (numero_serie) WHERE (numero_serie IS NOT NULL);


--
-- Name: idx_neumaticos_tasa_desgaste; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_neumaticos_tasa_desgaste ON public.neumaticos USING btree (tasa_desgaste_actual_mm_km) WHERE (tasa_desgaste_actual_mm_km IS NOT NULL);


--
-- Name: idx_neumaticos_ubicacion; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_neumaticos_ubicacion ON public.neumaticos USING btree (ubicacion_actual_vehiculo_id, ubicacion_actual_posicion_id) WHERE (ubicacion_actual_vehiculo_id IS NOT NULL);


--
-- Name: idx_neumaticos_ubicacion_almacen; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_neumaticos_ubicacion_almacen ON public.neumaticos USING btree (ubicacion_almacen_id) WHERE (ubicacion_almacen_id IS NOT NULL);


--
-- Name: idx_neumaticos_vida_util_restante; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_neumaticos_vida_util_restante ON public.neumaticos USING btree (vida_util_restante_km) WHERE (vida_util_restante_km IS NOT NULL);


--
-- Name: idx_param_inv_tipo_modelo_ubicacion; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_param_inv_tipo_modelo_ubicacion ON public.parametros_inventario USING btree (parametro_tipo, modelo_id, ubicacion_almacen_id) WHERE (activo = true);


--
-- Name: idx_permisos_recurso_accion; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_permisos_recurso_accion ON public.permisos USING btree (nombre_recurso, accion);


--
-- Name: idx_proveedores_nombre_unique; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_proveedores_nombre_unique ON public.proveedores USING btree (public.f_immutable_lower_unaccent((nombre)::text)) WHERE (activo = true);


--
-- Name: idx_registros_odometro_vehiculo_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_registros_odometro_vehiculo_fecha ON public.registros_odometro USING btree (vehiculo_id, fecha_medicion DESC);


--
-- Name: idx_roles_nombre_lower_unaccent; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_roles_nombre_lower_unaccent ON public.roles USING btree (public.f_immutable_lower_unaccent((nombre)::text));


--
-- Name: idx_roles_permisos_permiso_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_roles_permisos_permiso_id ON public.roles_permisos USING btree (permiso_id);


--
-- Name: idx_tipos_vehiculo_nombre; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_tipos_vehiculo_nombre ON public.tipos_vehiculo USING btree (public.f_immutable_lower_unaccent((nombre)::text)) WHERE (activo = true);


--
-- Name: idx_usuarios_roles_rol_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_usuarios_roles_rol_id ON public.usuarios_roles USING btree (rol_id);


--
-- Name: idx_vehiculos_activos; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_vehiculos_activos ON public.vehiculos USING btree (activo) WHERE (activo = true);


--
-- Name: idx_vehiculos_numero_economico; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_vehiculos_numero_economico ON public.vehiculos USING btree (lower((numero_economico)::text)) WHERE (activo = true);


--
-- Name: idx_vehiculos_placa; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_vehiculos_placa ON public.vehiculos USING btree (placa) WHERE ((placa IS NOT NULL) AND (activo = true));


--
-- Name: idx_vehiculos_tipo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_vehiculos_tipo ON public.vehiculos USING btree (tipo_vehiculo_id) WHERE (activo = true);


--
-- Name: uq_idx_neumatico_dot_vida; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_idx_neumatico_dot_vida ON public.neumaticos USING btree (dot, vida_actual) WHERE (dot IS NOT NULL);


--
-- Name: configuracion_auditoria configuracion_auditoria_actualizar_timestamp; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER configuracion_auditoria_actualizar_timestamp BEFORE UPDATE ON public.configuracion_auditoria FOR EACH ROW EXECUTE FUNCTION public.actualizar_timestamp();


--
-- Name: bitacora_operaciones tg_bitacora_operaciones_actualizar_fecha; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tg_bitacora_operaciones_actualizar_fecha BEFORE UPDATE ON public.bitacora_operaciones FOR EACH ROW EXECUTE FUNCTION public.actualizar_fecha_actualizacion();


--
-- Name: bitacora_operaciones_neumaticos tg_bitacora_operaciones_neumaticos_actualizar_fecha; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tg_bitacora_operaciones_neumaticos_actualizar_fecha BEFORE UPDATE ON public.bitacora_operaciones_neumaticos FOR EACH ROW EXECUTE FUNCTION public.actualizar_fecha_actualizacion();


--
-- Name: mediciones_profundidad tg_mediciones_profundidad_actualizar_fecha; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tg_mediciones_profundidad_actualizar_fecha BEFORE UPDATE ON public.mediciones_profundidad FOR EACH ROW EXECUTE FUNCTION public.actualizar_fecha_actualizacion();


--
-- Name: neumaticos tr_actualizar_metricas_rendimiento; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_actualizar_metricas_rendimiento BEFORE INSERT OR UPDATE OF profundidad_remanente_actual_mm, kilometraje_vida_actual, tasa_desgaste_actual_mm_km, vida_actual, ubicacion_actual_vehiculo_id ON public.neumaticos FOR EACH ROW EXECUTE FUNCTION public.actualizar_metricas_rendimiento();


--
-- Name: eventos_neumaticos tr_actualizar_tasa_desgaste_inspeccion; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_actualizar_tasa_desgaste_inspeccion BEFORE INSERT OR UPDATE ON public.eventos_neumaticos FOR EACH ROW WHEN ((new.tipo_evento = 'INSPECCION'::public.tipo_evento_neumatico_enum)) EXECUTE FUNCTION public.actualizar_tasa_desgaste_inspeccion();


--
-- Name: almacenes tr_audit_almacenes; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_audit_almacenes AFTER INSERT OR DELETE OR UPDATE ON public.almacenes FOR EACH ROW EXECUTE FUNCTION public.audit_medium_priority_trigger();


--
-- Name: eventos_neumaticos tr_audit_eventos_neumaticos; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_audit_eventos_neumaticos AFTER INSERT OR DELETE OR UPDATE ON public.eventos_neumaticos FOR EACH ROW EXECUTE FUNCTION public.audit_high_priority_trigger();


--
-- Name: fabricantes_neumatico tr_audit_fabricantes_neumatico; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_audit_fabricantes_neumatico AFTER INSERT OR DELETE OR UPDATE ON public.fabricantes_neumatico FOR EACH ROW EXECUTE FUNCTION public.audit_medium_priority_trigger();


--
-- Name: modelos_neumatico tr_audit_modelos_neumatico; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_audit_modelos_neumatico AFTER INSERT OR DELETE OR UPDATE ON public.modelos_neumatico FOR EACH ROW EXECUTE FUNCTION public.audit_medium_priority_trigger();


--
-- Name: modelos_posiciones_permitidas tr_audit_modelos_posiciones_permitidas; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_audit_modelos_posiciones_permitidas AFTER INSERT OR DELETE OR UPDATE ON public.modelos_posiciones_permitidas FOR EACH ROW EXECUTE FUNCTION public.audit_relation_table_trigger();


--
-- Name: motivos_desecho tr_audit_motivos_desecho; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_audit_motivos_desecho AFTER INSERT OR DELETE OR UPDATE ON public.motivos_desecho FOR EACH ROW EXECUTE FUNCTION public.audit_medium_priority_trigger();


--
-- Name: TRIGGER tr_audit_motivos_desecho ON motivos_desecho; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TRIGGER tr_audit_motivos_desecho ON public.motivos_desecho IS 'Trigger para auditar operaciones CRUD en la tabla motivos_desecho. Registra inserciones, actualizaciones y eliminaciones. \n\nMantenedor: Equipo de Desarrollo\nÚltima actualización: 2025-05-19';


--
-- Name: neumaticos tr_audit_neumaticos; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_audit_neumaticos AFTER INSERT OR DELETE OR UPDATE ON public.neumaticos FOR EACH ROW EXECUTE FUNCTION public.audit_neumaticos_trigger();


--
-- Name: parametros_inventario tr_audit_parametros_inventario; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_audit_parametros_inventario AFTER INSERT OR DELETE OR UPDATE ON public.parametros_inventario FOR EACH ROW EXECUTE FUNCTION public.audit_high_priority_trigger();


--
-- Name: parametros_rendimiento_esperado_modelo tr_audit_parametros_rendimiento_esperado_modelo; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_audit_parametros_rendimiento_esperado_modelo AFTER INSERT OR DELETE OR UPDATE ON public.parametros_rendimiento_esperado_modelo FOR EACH ROW EXECUTE FUNCTION public.audit_high_priority_trigger();


--
-- Name: proveedores tr_audit_proveedores; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_audit_proveedores AFTER INSERT OR DELETE OR UPDATE ON public.proveedores FOR EACH ROW EXECUTE FUNCTION public.audit_medium_priority_trigger();


--
-- Name: registros_odometro tr_audit_registros_odometro; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_audit_registros_odometro AFTER INSERT OR DELETE OR UPDATE ON public.registros_odometro FOR EACH ROW EXECUTE FUNCTION public.audit_registros_odometro();


--
-- Name: tipos_ruta tr_audit_tipos_ruta; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_audit_tipos_ruta AFTER INSERT OR DELETE OR UPDATE ON public.tipos_ruta FOR EACH ROW EXECUTE FUNCTION public.audit_high_priority_trigger();


--
-- Name: eventos_neumaticos tr_manejar_instalacion; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_manejar_instalacion BEFORE INSERT ON public.eventos_neumaticos FOR EACH ROW EXECUTE FUNCTION public.manejar_evento_instalacion();


--
-- Name: eventos_neumaticos tr_manejar_reencauche_salida; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_manejar_reencauche_salida BEFORE INSERT ON public.eventos_neumaticos FOR EACH ROW WHEN ((new.tipo_evento = 'REENCAUCHE_SALIDA'::public.tipo_evento_neumatico_enum)) EXECUTE FUNCTION public.manejar_evento_reencauche_salida();


--
-- Name: neumaticos tr_registrar_cambio_estado; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_registrar_cambio_estado AFTER UPDATE OF estado_actual ON public.neumaticos FOR EACH ROW WHEN ((old.estado_actual IS DISTINCT FROM new.estado_actual)) EXECUTE FUNCTION public.registrar_cambio_estado_neumatico();


--
-- Name: modelos_neumatico trg_actualizar_max_vidas_utiles; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_actualizar_max_vidas_utiles BEFORE INSERT OR UPDATE OF reencauches_maximos, max_vidas_utiles ON public.modelos_neumatico FOR EACH ROW EXECUTE FUNCTION public.actualizar_max_vidas_utiles();


--
-- Name: alertas alertas_almacen_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alertas
    ADD CONSTRAINT alertas_almacen_id_fkey FOREIGN KEY (almacen_id) REFERENCES public.almacenes(id) ON DELETE CASCADE;


--
-- Name: alertas alertas_modelo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alertas
    ADD CONSTRAINT alertas_modelo_id_fkey FOREIGN KEY (modelo_id) REFERENCES public.modelos_neumatico(id) ON DELETE CASCADE;


--
-- Name: alertas alertas_neumatico_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alertas
    ADD CONSTRAINT alertas_neumatico_id_fkey FOREIGN KEY (neumatico_id) REFERENCES public.neumaticos(id) ON DELETE CASCADE;


--
-- Name: alertas alertas_parametro_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alertas
    ADD CONSTRAINT alertas_parametro_id_fkey FOREIGN KEY (parametro_id) REFERENCES public.parametros_inventario(id) ON DELETE SET NULL;


--
-- Name: alertas alertas_usuario_gestion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alertas
    ADD CONSTRAINT alertas_usuario_gestion_id_fkey FOREIGN KEY (usuario_gestion_id) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: alertas alertas_vehiculo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alertas
    ADD CONSTRAINT alertas_vehiculo_id_fkey FOREIGN KEY (vehiculo_id) REFERENCES public.vehiculos(id) ON DELETE CASCADE;


--
-- Name: almacenes almacenes_actualizado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.almacenes
    ADD CONSTRAINT almacenes_actualizado_por_fkey FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: almacenes almacenes_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.almacenes
    ADD CONSTRAINT almacenes_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: auditoria_log auditoria_log_usuario_aplicacion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auditoria_log
    ADD CONSTRAINT auditoria_log_usuario_aplicacion_id_fkey FOREIGN KEY (usuario_aplicacion_id) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: bitacora_operaciones bitacora_operaciones_actualizado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bitacora_operaciones
    ADD CONSTRAINT bitacora_operaciones_actualizado_por_fkey FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: bitacora_operaciones bitacora_operaciones_almacen_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bitacora_operaciones
    ADD CONSTRAINT bitacora_operaciones_almacen_id_fkey FOREIGN KEY (almacen_id) REFERENCES public.almacenes(id) ON DELETE SET NULL;


--
-- Name: bitacora_operaciones bitacora_operaciones_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bitacora_operaciones
    ADD CONSTRAINT bitacora_operaciones_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: bitacora_operaciones_neumaticos bitacora_operaciones_neumaticos_actualizado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bitacora_operaciones_neumaticos
    ADD CONSTRAINT bitacora_operaciones_neumaticos_actualizado_por_fkey FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: bitacora_operaciones_neumaticos bitacora_operaciones_neumaticos_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bitacora_operaciones_neumaticos
    ADD CONSTRAINT bitacora_operaciones_neumaticos_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: bitacora_operaciones_neumaticos bitacora_operaciones_neumaticos_neumatico_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bitacora_operaciones_neumaticos
    ADD CONSTRAINT bitacora_operaciones_neumaticos_neumatico_id_fkey FOREIGN KEY (neumatico_id) REFERENCES public.neumaticos(id) ON DELETE CASCADE;


--
-- Name: bitacora_operaciones_neumaticos bitacora_operaciones_neumaticos_operacion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bitacora_operaciones_neumaticos
    ADD CONSTRAINT bitacora_operaciones_neumaticos_operacion_id_fkey FOREIGN KEY (operacion_id) REFERENCES public.bitacora_operaciones(id) ON DELETE CASCADE;


--
-- Name: bitacora_operaciones_neumaticos bitacora_operaciones_neumaticos_posicion_neumatico_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bitacora_operaciones_neumaticos
    ADD CONSTRAINT bitacora_operaciones_neumaticos_posicion_neumatico_id_fkey FOREIGN KEY (posicion_neumatico_id) REFERENCES public.posiciones_neumatico(id) ON DELETE SET NULL;


--
-- Name: bitacora_operaciones bitacora_operaciones_proveedor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bitacora_operaciones
    ADD CONSTRAINT bitacora_operaciones_proveedor_id_fkey FOREIGN KEY (proveedor_id) REFERENCES public.proveedores(id);


--
-- Name: bitacora_operaciones bitacora_operaciones_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bitacora_operaciones
    ADD CONSTRAINT bitacora_operaciones_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: bitacora_operaciones bitacora_operaciones_vehiculo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bitacora_operaciones
    ADD CONSTRAINT bitacora_operaciones_vehiculo_id_fkey FOREIGN KEY (vehiculo_id) REFERENCES public.vehiculos(id) ON DELETE SET NULL;


--
-- Name: configuraciones_eje configuraciones_eje_actualizado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.configuraciones_eje
    ADD CONSTRAINT configuraciones_eje_actualizado_por_fkey FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: configuraciones_eje configuraciones_eje_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.configuraciones_eje
    ADD CONSTRAINT configuraciones_eje_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: configuraciones_eje configuraciones_eje_tipo_vehiculo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.configuraciones_eje
    ADD CONSTRAINT configuraciones_eje_tipo_vehiculo_id_fkey FOREIGN KEY (tipo_vehiculo_id) REFERENCES public.tipos_vehiculo(id) ON DELETE CASCADE;


--
-- Name: especificaciones_desgaste especificaciones_desgaste_actualizado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.especificaciones_desgaste
    ADD CONSTRAINT especificaciones_desgaste_actualizado_por_fkey FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: especificaciones_desgaste especificaciones_desgaste_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.especificaciones_desgaste
    ADD CONSTRAINT especificaciones_desgaste_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: especificaciones_desgaste especificaciones_desgaste_modelo_neumatico_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.especificaciones_desgaste
    ADD CONSTRAINT especificaciones_desgaste_modelo_neumatico_id_fkey FOREIGN KEY (modelo_neumatico_id) REFERENCES public.modelos_neumatico(id) ON DELETE CASCADE;


--
-- Name: eventos_neumaticos eventos_neumaticos_almacen_destino_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eventos_neumaticos
    ADD CONSTRAINT eventos_neumaticos_almacen_destino_id_fkey FOREIGN KEY (almacen_destino_id) REFERENCES public.almacenes(id) ON DELETE SET NULL;


--
-- Name: eventos_neumaticos eventos_neumaticos_motivo_desecho_id_evento_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eventos_neumaticos
    ADD CONSTRAINT eventos_neumaticos_motivo_desecho_id_evento_fkey FOREIGN KEY (motivo_desecho_id_evento) REFERENCES public.motivos_desecho(id) ON DELETE RESTRICT;


--
-- Name: eventos_neumaticos eventos_neumaticos_neumatico_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eventos_neumaticos
    ADD CONSTRAINT eventos_neumaticos_neumatico_id_fkey FOREIGN KEY (neumatico_id) REFERENCES public.neumaticos(id) ON DELETE CASCADE;


--
-- Name: eventos_neumaticos eventos_neumaticos_posicion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eventos_neumaticos
    ADD CONSTRAINT eventos_neumaticos_posicion_id_fkey FOREIGN KEY (posicion_id) REFERENCES public.posiciones_neumatico(id) ON DELETE SET NULL;


--
-- Name: eventos_neumaticos eventos_neumaticos_proveedor_servicio_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eventos_neumaticos
    ADD CONSTRAINT eventos_neumaticos_proveedor_servicio_id_fkey FOREIGN KEY (proveedor_servicio_id) REFERENCES public.proveedores(id) ON DELETE SET NULL;


--
-- Name: eventos_neumaticos eventos_neumaticos_relacion_evento_anterior_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eventos_neumaticos
    ADD CONSTRAINT eventos_neumaticos_relacion_evento_anterior_fkey FOREIGN KEY (relacion_evento_anterior) REFERENCES public.eventos_neumaticos(id) ON DELETE SET NULL;


--
-- Name: eventos_neumaticos eventos_neumaticos_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eventos_neumaticos
    ADD CONSTRAINT eventos_neumaticos_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE RESTRICT;


--
-- Name: eventos_neumaticos eventos_neumaticos_vehiculo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eventos_neumaticos
    ADD CONSTRAINT eventos_neumaticos_vehiculo_id_fkey FOREIGN KEY (vehiculo_id) REFERENCES public.vehiculos(id) ON DELETE SET NULL;


--
-- Name: fabricantes_neumatico fabricantes_neumatico_actualizado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fabricantes_neumatico
    ADD CONSTRAINT fabricantes_neumatico_actualizado_por_fkey FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: fabricantes_neumatico fabricantes_neumatico_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fabricantes_neumatico
    ADD CONSTRAINT fabricantes_neumatico_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: eventos_neumaticos fk_eventos_neumaticos_tipo_ruta; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eventos_neumaticos
    ADD CONSTRAINT fk_eventos_neumaticos_tipo_ruta FOREIGN KEY (tipo_ruta_id) REFERENCES public.tipos_ruta(id) ON DELETE RESTRICT;


--
-- Name: garantias_neumaticos garantias_neumaticos_actualizado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.garantias_neumaticos
    ADD CONSTRAINT garantias_neumaticos_actualizado_por_fkey FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: garantias_neumaticos garantias_neumaticos_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.garantias_neumaticos
    ADD CONSTRAINT garantias_neumaticos_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: garantias_neumaticos garantias_neumaticos_neumatico_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.garantias_neumaticos
    ADD CONSTRAINT garantias_neumaticos_neumatico_id_fkey FOREIGN KEY (neumatico_id) REFERENCES public.neumaticos(id) ON DELETE CASCADE;


--
-- Name: garantias_neumaticos garantias_neumaticos_proveedor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.garantias_neumaticos
    ADD CONSTRAINT garantias_neumaticos_proveedor_id_fkey FOREIGN KEY (proveedor_id) REFERENCES public.proveedores(id) ON DELETE SET NULL;


--
-- Name: historial_estados_neumaticos historial_estados_neumaticos_neumatico_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.historial_estados_neumaticos
    ADD CONSTRAINT historial_estados_neumaticos_neumatico_id_fkey FOREIGN KEY (neumatico_id) REFERENCES public.neumaticos(id) ON DELETE CASCADE;


--
-- Name: historial_estados_neumaticos historial_estados_neumaticos_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.historial_estados_neumaticos
    ADD CONSTRAINT historial_estados_neumaticos_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: mediciones_profundidad mediciones_profundidad_actualizado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mediciones_profundidad
    ADD CONSTRAINT mediciones_profundidad_actualizado_por_fkey FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: mediciones_profundidad mediciones_profundidad_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mediciones_profundidad
    ADD CONSTRAINT mediciones_profundidad_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: mediciones_profundidad mediciones_profundidad_neumatico_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mediciones_profundidad
    ADD CONSTRAINT mediciones_profundidad_neumatico_id_fkey FOREIGN KEY (neumatico_id) REFERENCES public.neumaticos(id) ON DELETE CASCADE;


--
-- Name: mediciones_profundidad mediciones_profundidad_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mediciones_profundidad
    ADD CONSTRAINT mediciones_profundidad_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: modelos_neumatico modelos_neumatico_actualizado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modelos_neumatico
    ADD CONSTRAINT modelos_neumatico_actualizado_por_fkey FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: modelos_neumatico modelos_neumatico_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modelos_neumatico
    ADD CONSTRAINT modelos_neumatico_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: modelos_neumatico modelos_neumatico_fabricante_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modelos_neumatico
    ADD CONSTRAINT modelos_neumatico_fabricante_id_fkey FOREIGN KEY (fabricante_id) REFERENCES public.fabricantes_neumatico(id) ON DELETE RESTRICT;


--
-- Name: modelos_posiciones_permitidas modelos_posiciones_permitidas_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modelos_posiciones_permitidas
    ADD CONSTRAINT modelos_posiciones_permitidas_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: modelos_posiciones_permitidas modelos_posiciones_permitidas_modelo_neumatico_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modelos_posiciones_permitidas
    ADD CONSTRAINT modelos_posiciones_permitidas_modelo_neumatico_id_fkey FOREIGN KEY (modelo_neumatico_id) REFERENCES public.modelos_neumatico(id) ON DELETE CASCADE;


--
-- Name: modelos_posiciones_permitidas modelos_posiciones_permitidas_posicion_neumatico_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modelos_posiciones_permitidas
    ADD CONSTRAINT modelos_posiciones_permitidas_posicion_neumatico_id_fkey FOREIGN KEY (posicion_neumatico_id) REFERENCES public.posiciones_neumatico(id) ON DELETE CASCADE;


--
-- Name: motivos_desecho motivos_desecho_actualizado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.motivos_desecho
    ADD CONSTRAINT motivos_desecho_actualizado_por_fkey FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: motivos_desecho motivos_desecho_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.motivos_desecho
    ADD CONSTRAINT motivos_desecho_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: neumaticos neumaticos_actualizado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.neumaticos
    ADD CONSTRAINT neumaticos_actualizado_por_fkey FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: neumaticos neumaticos_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.neumaticos
    ADD CONSTRAINT neumaticos_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: neumaticos neumaticos_modelo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.neumaticos
    ADD CONSTRAINT neumaticos_modelo_id_fkey FOREIGN KEY (modelo_id) REFERENCES public.modelos_neumatico(id) ON DELETE RESTRICT;


--
-- Name: neumaticos neumaticos_motivo_desecho_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.neumaticos
    ADD CONSTRAINT neumaticos_motivo_desecho_id_fkey FOREIGN KEY (motivo_desecho_id) REFERENCES public.motivos_desecho(id) ON DELETE RESTRICT;


--
-- Name: neumaticos neumaticos_proveedor_compra_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.neumaticos
    ADD CONSTRAINT neumaticos_proveedor_compra_id_fkey FOREIGN KEY (proveedor_compra_id) REFERENCES public.proveedores(id) ON DELETE SET NULL;


--
-- Name: neumaticos neumaticos_ubicacion_actual_vehiculo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.neumaticos
    ADD CONSTRAINT neumaticos_ubicacion_actual_vehiculo_id_fkey FOREIGN KEY (ubicacion_actual_vehiculo_id) REFERENCES public.vehiculos(id) ON DELETE SET NULL;


--
-- Name: neumaticos neumaticos_ubicacion_almacen_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.neumaticos
    ADD CONSTRAINT neumaticos_ubicacion_almacen_id_fkey FOREIGN KEY (ubicacion_almacen_id) REFERENCES public.almacenes(id) ON DELETE SET NULL;


--
-- Name: parametros_inventario parametros_inventario_actualizado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parametros_inventario
    ADD CONSTRAINT parametros_inventario_actualizado_por_fkey FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: parametros_inventario parametros_inventario_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parametros_inventario
    ADD CONSTRAINT parametros_inventario_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: parametros_inventario parametros_inventario_modelo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parametros_inventario
    ADD CONSTRAINT parametros_inventario_modelo_id_fkey FOREIGN KEY (modelo_id) REFERENCES public.modelos_neumatico(id) ON DELETE CASCADE;


--
-- Name: parametros_inventario parametros_inventario_ubicacion_almacen_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parametros_inventario
    ADD CONSTRAINT parametros_inventario_ubicacion_almacen_id_fkey FOREIGN KEY (ubicacion_almacen_id) REFERENCES public.almacenes(id) ON DELETE SET NULL;


--
-- Name: parametros_rendimiento_esperado_modelo parametros_rendimiento_esperado_modelo_actualizado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parametros_rendimiento_esperado_modelo
    ADD CONSTRAINT parametros_rendimiento_esperado_modelo_actualizado_por_fkey FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: parametros_rendimiento_esperado_modelo parametros_rendimiento_esperado_modelo_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parametros_rendimiento_esperado_modelo
    ADD CONSTRAINT parametros_rendimiento_esperado_modelo_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: parametros_rendimiento_esperado_modelo parametros_rendimiento_esperado_modelo_modelo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parametros_rendimiento_esperado_modelo
    ADD CONSTRAINT parametros_rendimiento_esperado_modelo_modelo_id_fkey FOREIGN KEY (modelo_id) REFERENCES public.modelos_neumatico(id) ON DELETE CASCADE;


--
-- Name: posiciones_neumatico posiciones_neumatico_actualizado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posiciones_neumatico
    ADD CONSTRAINT posiciones_neumatico_actualizado_por_fkey FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: posiciones_neumatico posiciones_neumatico_configuracion_eje_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posiciones_neumatico
    ADD CONSTRAINT posiciones_neumatico_configuracion_eje_id_fkey FOREIGN KEY (configuracion_eje_id) REFERENCES public.configuraciones_eje(id) ON DELETE CASCADE;


--
-- Name: posiciones_neumatico posiciones_neumatico_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posiciones_neumatico
    ADD CONSTRAINT posiciones_neumatico_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: proveedores proveedores_actualizado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proveedores
    ADD CONSTRAINT proveedores_actualizado_por_fkey FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: proveedores proveedores_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proveedores
    ADD CONSTRAINT proveedores_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: registros_odometro registros_odometro_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registros_odometro
    ADD CONSTRAINT registros_odometro_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: registros_odometro registros_odometro_vehiculo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registros_odometro
    ADD CONSTRAINT registros_odometro_vehiculo_id_fkey FOREIGN KEY (vehiculo_id) REFERENCES public.vehiculos(id) ON DELETE CASCADE;


--
-- Name: roles roles_actualizado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_actualizado_por_fkey FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: roles roles_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: roles_permisos roles_permisos_asignado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles_permisos
    ADD CONSTRAINT roles_permisos_asignado_por_fkey FOREIGN KEY (asignado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: roles_permisos roles_permisos_permiso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles_permisos
    ADD CONSTRAINT roles_permisos_permiso_id_fkey FOREIGN KEY (permiso_id) REFERENCES public.permisos(id) ON DELETE CASCADE;


--
-- Name: roles_permisos roles_permisos_rol_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles_permisos
    ADD CONSTRAINT roles_permisos_rol_id_fkey FOREIGN KEY (rol_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- Name: rutas rutas_actualizado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rutas
    ADD CONSTRAINT rutas_actualizado_por_fkey FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: rutas rutas_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rutas
    ADD CONSTRAINT rutas_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: tipos_ruta tipos_ruta_actualizado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipos_ruta
    ADD CONSTRAINT tipos_ruta_actualizado_por_fkey FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: tipos_ruta tipos_ruta_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipos_ruta
    ADD CONSTRAINT tipos_ruta_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: tipos_vehiculo tipos_vehiculo_actualizado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipos_vehiculo
    ADD CONSTRAINT tipos_vehiculo_actualizado_por_fkey FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: tipos_vehiculo tipos_vehiculo_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipos_vehiculo
    ADD CONSTRAINT tipos_vehiculo_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: usuarios usuarios_actualizado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_actualizado_por_fkey FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: usuarios usuarios_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: usuarios_roles usuarios_roles_asignado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios_roles
    ADD CONSTRAINT usuarios_roles_asignado_por_fkey FOREIGN KEY (asignado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: usuarios_roles usuarios_roles_rol_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios_roles
    ADD CONSTRAINT usuarios_roles_rol_id_fkey FOREIGN KEY (rol_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- Name: usuarios_roles usuarios_roles_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios_roles
    ADD CONSTRAINT usuarios_roles_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE CASCADE;


--
-- Name: vehiculos vehiculos_actualizado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehiculos
    ADD CONSTRAINT vehiculos_actualizado_por_fkey FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: vehiculos vehiculos_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehiculos
    ADD CONSTRAINT vehiculos_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: vehiculos vehiculos_tipo_vehiculo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehiculos
    ADD CONSTRAINT vehiculos_tipo_vehiculo_id_fkey FOREIGN KEY (tipo_vehiculo_id) REFERENCES public.tipos_vehiculo(id) ON DELETE RESTRICT;


--
-- Name: neumaticos; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.neumaticos ENABLE ROW LEVEL SECURITY;

--
-- Name: FUNCTION dblink_connect_u(text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.dblink_connect_u(text) TO PUBLIC;


--
-- Name: FUNCTION dblink_connect_u(text, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.dblink_connect_u(text, text) TO PUBLIC;


--
-- Name: FUNCTION pg_stat_statements_reset(userid oid, dbid oid, queryid bigint, minmax_only boolean); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.pg_stat_statements_reset(userid oid, dbid oid, queryid bigint, minmax_only boolean) TO PUBLIC;


--
-- Name: TABLE bitacora_mantenimiento; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.bitacora_mantenimiento TO PUBLIC;


--
-- Name: SEQUENCE bitacora_mantenimiento_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,USAGE ON SEQUENCE public.bitacora_mantenimiento_id_seq TO PUBLIC;


--
-- Name: mv_desempeno_modelos; Type: MATERIALIZED VIEW DATA; Schema: public; Owner: postgres
--

REFRESH MATERIALIZED VIEW public.mv_desempeno_modelos;


--
-- Name: mv_eventos_recientes; Type: MATERIALIZED VIEW DATA; Schema: public; Owner: postgres
--

REFRESH MATERIALIZED VIEW public.mv_eventos_recientes;


--
-- Name: mv_resumen_neumaticos_estado; Type: MATERIALIZED VIEW DATA; Schema: public; Owner: postgres
--

REFRESH MATERIALIZED VIEW public.mv_resumen_neumaticos_estado;


--
-- PostgreSQL database dump complete
--

