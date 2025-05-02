--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4 (Ubuntu 17.4-1.pgdg24.04+2)
-- Dumped by pg_dump version 17.4 (Ubuntu 17.4-1.pgdg24.04+2)

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
-- Name: tipo_eje_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.tipo_eje_enum AS ENUM (
    'DIRECCION',
    'TRACCION',
    'LIBRE',
    'PORTADOR',
    'ARRASTRE'
);


ALTER TYPE public.tipo_eje_enum OWNER TO postgres;

--
-- Name: TYPE tipo_eje_enum; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TYPE public.tipo_eje_enum IS 'Clasificación funcional de los ejes vehiculares';


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
-- Name: f_immutable_lower_unaccent(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.f_immutable_lower_unaccent(text) RETURNS text
    LANGUAGE sql IMMUTABLE STRICT
    AS $_$
SELECT lower(public.unaccent($1));
$_$;


ALTER FUNCTION public.f_immutable_lower_unaccent(text) OWNER TO postgres;

--
-- Name: FUNCTION f_immutable_lower_unaccent(text); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.f_immutable_lower_unaccent(text) IS 'Wrapper IMMUTABLE para lower(unaccent(text)) para usar en índices únicos insensibles a mayúsculas/acentos.';


--
-- Name: fn_actualizar_estado_neumatico(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fn_actualizar_estado_neumatico() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_kilometros_recorridos integer := 0;
    v_odometro_anterior integer;
    v_neumatico_record record;
    v_modelo_record record;
BEGIN
    -- Ya no necesitamos los RAISE NOTICE ahora que sabemos dónde falla
    -- RAISE NOTICE '[TRIGGER FN_ACT_ESTADO] Iniciando...';

    SELECT * INTO v_neumatico_record FROM public.neumaticos WHERE id = NEW.neumatico_id FOR UPDATE;
    SELECT reencauches_maximos INTO v_modelo_record FROM public.modelos_neumatico WHERE id = v_neumatico_record.modelo_id;

    -- Cálculo de Kilometraje
    IF v_neumatico_record.estado_actual = 'INSTALADO' AND NEW.tipo_evento IN ('DESMONTAJE', 'INSPECCION', 'DESECHO') AND NEW.odometro_vehiculo_en_evento IS NOT NULL THEN
        -- *** CORRECCIÓN AQUÍ: Quitar "AND vehiculo_id = v_neumatico_record.ubicacion_actual_vehiculo_id" ***
        SELECT odometro_vehiculo_en_evento INTO v_odometro_anterior
        FROM public.eventos_neumaticos
        WHERE neumatico_id = NEW.neumatico_id
          -- AND vehiculo_id = v_neumatico_record.ubicacion_actual_vehiculo_id -- Condición eliminada
          AND tipo_evento IN ('INSTALACION', 'INSPECCION')
          AND odometro_vehiculo_en_evento IS NOT NULL
          AND timestamp_evento < NEW.timestamp_evento
        ORDER BY timestamp_evento DESC
        LIMIT 1;
        -- RAISE NOTICE '[TRIGGER FN_ACT_ESTADO] Odómetro Anterior Encontrado (Corregido): %', v_odometro_anterior; -- Podrías dejar este si quieres verificar

        IF v_odometro_anterior IS NOT NULL AND NEW.odometro_vehiculo_en_evento > v_odometro_anterior THEN
            v_kilometros_recorridos := NEW.odometro_vehiculo_en_evento - v_odometro_anterior;
        ELSE
             v_kilometros_recorridos := 0;
        END IF;
    ELSE
         v_kilometros_recorridos := 0;
    END IF;

    -- Actualización del Neumático (El CASE se mantiene igual que antes)
    CASE NEW.tipo_evento
        WHEN 'INSTALACION' THEN UPDATE public.neumaticos SET estado_actual = 'INSTALADO', ubicacion_actual_vehiculo_id = NEW.vehiculo_id, ubicacion_actual_posicion_id = NEW.posicion_id, fecha_ultimo_evento = NEW.timestamp_evento, kilometraje_acumulado = 0, actualizado_en = now(), actualizado_por = NEW.usuario_id WHERE id = NEW.neumatico_id;
        WHEN 'DESMONTAJE' THEN UPDATE public.neumaticos SET estado_actual = NEW.destino_desmontaje, ubicacion_actual_vehiculo_id = NULL, ubicacion_actual_posicion_id = NULL, fecha_ultimo_evento = NEW.timestamp_evento, kilometraje_acumulado = v_neumatico_record.kilometraje_acumulado + v_kilometros_recorridos, fecha_desecho = CASE WHEN NEW.destino_desmontaje = 'DESECHADO' THEN NEW.timestamp_evento::date ELSE fecha_desecho END, motivo_desecho_id = CASE WHEN NEW.destino_desmontaje = 'DESECHADO' THEN NEW.motivo_desecho_id_evento ELSE motivo_desecho_id END, actualizado_en = now(), actualizado_por = NEW.usuario_id WHERE id = NEW.neumatico_id;
        WHEN 'INSPECCION' THEN IF v_kilometros_recorridos > 0 THEN UPDATE public.neumaticos SET kilometraje_acumulado = v_neumatico_record.kilometraje_acumulado + v_kilometros_recorridos, fecha_ultimo_evento = NEW.timestamp_evento, actualizado_en = now(), actualizado_por = NEW.usuario_id WHERE id = NEW.neumatico_id; ELSE UPDATE public.neumaticos SET fecha_ultimo_evento = NEW.timestamp_evento, actualizado_en = now(), actualizado_por = NEW.usuario_id WHERE id = NEW.neumatico_id; END IF;
        WHEN 'REPARACION_ENTRADA' THEN UPDATE public.neumaticos SET estado_actual = 'EN_REPARACION', fecha_ultimo_evento = NEW.timestamp_evento, actualizado_en = now(), actualizado_por = NEW.usuario_id WHERE id = NEW.neumatico_id;
        WHEN 'REPARACION_SALIDA' THEN UPDATE public.neumaticos SET estado_actual = 'EN_STOCK', fecha_ultimo_evento = NEW.timestamp_evento, actualizado_en = now(), actualizado_por = NEW.usuario_id WHERE id = NEW.neumatico_id;
        WHEN 'REENCAUCHE_ENTRADA' THEN IF v_neumatico_record.reencauches_realizados >= v_modelo_record.reencauches_maximos THEN RAISE WARNING '[TRIGGER FN_ACT_ESTADO] Neumático ID % enviado a reencauche pero ya alcanzó/superó el límite de % reencauches.', NEW.neumatico_id, v_modelo_record.reencauches_maximos; END IF; UPDATE public.neumaticos SET estado_actual = 'EN_REENCAUCHE', fecha_ultimo_evento = NEW.timestamp_evento, actualizado_en = now(), actualizado_por = NEW.usuario_id WHERE id = NEW.neumatico_id;
        WHEN 'REENCAUCHE_SALIDA' THEN IF v_neumatico_record.reencauches_realizados >= v_modelo_record.reencauches_maximos THEN RAISE EXCEPTION '[TRIGGER FN_ACT_ESTADO] Neumático ID % no puede salir de reencauche. Ya alcanzó/superó el límite de % reencauches.', NEW.neumatico_id, v_modelo_record.reencauches_maximos; END IF; UPDATE public.neumaticos SET reencauches_realizados = v_neumatico_record.reencauches_realizados + 1, vida_actual = v_neumatico_record.vida_actual + 1, estado_actual = 'EN_STOCK', fecha_ultimo_evento = NEW.timestamp_evento, kilometraje_acumulado = 0, profundidad_inicial_mm = NEW.profundidad_post_reencauche_mm, es_reencauchado = true, actualizado_en = now(), actualizado_por = NEW.usuario_id WHERE id = NEW.neumatico_id;
        WHEN 'DESECHO' THEN IF v_neumatico_record.estado_actual != 'DESECHADO' THEN UPDATE public.neumaticos SET estado_actual = 'DESECHADO', fecha_desecho = NEW.timestamp_evento::date, motivo_desecho_id = NEW.motivo_desecho_id_evento, fecha_ultimo_evento = NEW.timestamp_evento, kilometraje_acumulado = v_neumatico_record.kilometraje_acumulado + v_kilometros_recorridos, ubicacion_actual_vehiculo_id = NULL, ubicacion_actual_posicion_id = NULL, actualizado_en = now(), actualizado_por = NEW.usuario_id WHERE id = NEW.neumatico_id; END IF;
        WHEN 'AJUSTE_INVENTARIO' THEN UPDATE public.neumaticos SET fecha_ultimo_evento = NEW.timestamp_evento, actualizado_en = now(), actualizado_por = NEW.usuario_id WHERE id = NEW.neumatico_id;
        ELSE UPDATE public.neumaticos SET fecha_ultimo_evento = NEW.timestamp_evento, actualizado_en = now(), actualizado_por = NEW.usuario_id WHERE id = NEW.neumatico_id;
    END CASE;

    -- RAISE NOTICE '[TRIGGER FN_ACT_ESTADO] Finalizando...';
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_actualizar_estado_neumatico() OWNER TO postgres;

--
-- Name: fn_actualizar_odometro_vehiculo(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fn_actualizar_odometro_vehiculo() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE v_odometro_actual integer; v_fecha_odometro_actual timestamptz;
BEGIN
    IF pg_trigger_depth() > 1 THEN RETURN NEW; END IF;
    SELECT odometro_actual, fecha_ultimo_odometro INTO v_odometro_actual, v_fecha_odometro_actual FROM public.vehiculos WHERE id = NEW.vehiculo_id FOR UPDATE;
    IF v_fecha_odometro_actual IS NULL OR NEW.fecha_medicion >= v_fecha_odometro_actual OR (NEW.odometro > v_odometro_actual AND NEW.fecha_medicion >= v_fecha_odometro_actual) THEN
        UPDATE public.vehiculos SET odometro_actual = NEW.odometro, fecha_ultimo_odometro = NEW.fecha_medicion, actualizado_en = now(), actualizado_por = NEW.creado_por WHERE id = NEW.vehiculo_id;
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_actualizar_odometro_vehiculo() OWNER TO postgres;

--
-- Name: fn_auditoria_registro(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fn_auditoria_registro() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_contexto jsonb; v_usuario_id_app uuid; v_usuario_app_username varchar;
    v_entidad_id uuid; v_datos_antiguos jsonb; v_datos_nuevos jsonb; v_responsable_id uuid;
    v_cambios jsonb; -- Variable para calcular cambios
BEGIN
    IF pg_trigger_depth() > 1 THEN RETURN CASE WHEN TG_OP = 'DELETE' THEN OLD ELSE NEW END; END IF;
    BEGIN
        v_usuario_id_app := current_setting('app.usuario_id', true)::uuid; v_usuario_app_username := current_setting('app.usuario', true);
        v_contexto := jsonb_build_object('endpoint', current_setting('app.endpoint', true), 'metodo', current_setting('app.metodo', true), 'ip', current_setting('app.ip', true));
    EXCEPTION WHEN OTHERS THEN v_usuario_id_app := NULL; v_usuario_app_username := NULL; v_contexto := NULL; END;

    IF (TG_OP = 'DELETE') THEN
        v_entidad_id := OLD.id; v_datos_antiguos := to_jsonb(OLD); v_datos_nuevos := NULL;
        BEGIN v_responsable_id := OLD.actualizado_por; EXCEPTION WHEN OTHERS THEN v_responsable_id := NULL; END;
        v_cambios := v_datos_antiguos - '{creado_en, actualizado_en, creado_por, actualizado_por}'::text[];
    ELSIF (TG_OP = 'UPDATE') THEN
        v_entidad_id := NEW.id; v_datos_antiguos := to_jsonb(OLD); v_datos_nuevos := to_jsonb(NEW);
        BEGIN v_responsable_id := NEW.actualizado_por; EXCEPTION WHEN OTHERS THEN v_responsable_id := NULL; END;
        SELECT jsonb_object_agg(key, value) INTO v_cambios FROM jsonb_each(v_datos_nuevos)
        WHERE key NOT IN ('actualizado_en', 'actualizado_por') AND v_datos_antiguos -> key IS DISTINCT FROM v_datos_nuevos -> key;
    ELSIF (TG_OP = 'INSERT') THEN
        v_entidad_id := NEW.id; v_datos_antiguos := NULL; v_datos_nuevos := to_jsonb(NEW);
        BEGIN v_responsable_id := NEW.creado_por; EXCEPTION WHEN OTHERS THEN v_responsable_id := NULL; END;
        v_cambios := v_datos_nuevos - '{creado_en, actualizado_en, creado_por, actualizado_por}'::text[];
    END IF;

    IF v_usuario_id_app IS NULL THEN
        v_usuario_id_app := v_responsable_id;
        IF v_usuario_id_app IS NOT NULL AND v_usuario_app_username IS NULL THEN
            SELECT username INTO v_usuario_app_username FROM public.usuarios WHERE id = v_usuario_id_app;
        END IF;
    END IF;

    INSERT INTO public.auditoria_log (esquema_tabla, nombre_tabla, operacion, usuario_db, usuario_aplicacion_id, usuario_aplicacion_username, direccion_ip, id_entidad, datos_antiguos, datos_nuevos, cambios, contexto_aplicacion, query_ejecutada)
    VALUES (TG_TABLE_SCHEMA, TG_TABLE_NAME, TG_OP, current_user, v_usuario_id_app, v_usuario_app_username, v_contexto->>'ip', v_entidad_id, v_datos_antiguos, v_datos_nuevos, v_cambios, v_contexto, current_query());

    RETURN CASE WHEN TG_OP = 'DELETE' THEN OLD ELSE NEW END;
END;
$$;


ALTER FUNCTION public.fn_auditoria_registro() OWNER TO postgres;

--
-- Name: fn_validar_modelo_posicion(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fn_validar_modelo_posicion() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE v_modelo_existe boolean; v_posicion_existe boolean;
BEGIN
    SELECT EXISTS (SELECT 1 FROM public.modelos_neumatico WHERE id = NEW.modelo_neumatico_id) INTO v_modelo_existe;
    IF NOT v_modelo_existe THEN RAISE EXCEPTION 'Validación fallida: Modelo de neumático ID % no existe.', NEW.modelo_neumatico_id; END IF;
    SELECT EXISTS (SELECT 1 FROM public.posiciones_neumatico WHERE id = NEW.posicion_neumatico_id) INTO v_posicion_existe;
    IF NOT v_posicion_existe THEN RAISE EXCEPTION 'Validación fallida: Posición de neumático ID % no existe.', NEW.posicion_neumatico_id; END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_validar_modelo_posicion() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

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
    CONSTRAINT alertas_estado_alerta_check CHECK (((estado_alerta)::text = ANY ((ARRAY['NUEVA'::character varying, 'VISTA'::character varying, 'GESTIONADA'::character varying])::text[]))),
    CONSTRAINT alertas_nivel_severidad_check CHECK (((nivel_severidad)::text = ANY ((ARRAY['INFO'::character varying, 'WARN'::character varying, 'CRITICAL'::character varying])::text[])))
);


ALTER TABLE public.alertas OWNER TO postgres;

--
-- Name: TABLE alertas; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.alertas IS '[OPCIONAL] Registra alertas operativas y de mantenimiento generadas por el sistema basadas en reglas de negocio (RF28, RF81).';


--
-- Name: COLUMN alertas.tipo_alerta; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.alertas.tipo_alerta IS 'Clasificación funcional de la alerta.';


--
-- Name: COLUMN alertas.nivel_severidad; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.alertas.nivel_severidad IS 'Indica la criticidad de la alerta.';


--
-- Name: COLUMN alertas.estado_alerta; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.alertas.estado_alerta IS 'Estado del ciclo de vida de la alerta (para seguimiento).';


--
-- Name: COLUMN alertas.timestamp_generacion; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.alertas.timestamp_generacion IS 'Momento exacto en que se generó la alerta.';


--
-- Name: COLUMN alertas.timestamp_gestion; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.alertas.timestamp_gestion IS 'Momento en que la alerta fue marcada como vista o gestionada.';


--
-- Name: COLUMN alertas.usuario_gestion_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.alertas.usuario_gestion_id IS 'Usuario que marcó la alerta como vista o gestionada.';


--
-- Name: COLUMN alertas.parametro_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.alertas.parametro_id IS 'Referencia opcional al parámetro de inventario que originó la alerta.';


--
-- Name: COLUMN alertas.datos_contexto; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.alertas.datos_contexto IS 'JSONB para almacenar detalles específicos de la alerta, como valores medidos, umbrales, etc.';


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
);


ALTER TABLE public.almacenes OWNER TO postgres;

--
-- Name: TABLE almacenes; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.almacenes IS 'Catálogo de almacenes o ubicaciones físicas donde pueden residir los neumáticos.';


--
-- Name: COLUMN almacenes.codigo; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.almacenes.codigo IS 'Código corto y único para identificar la ubicación.';


--
-- Name: COLUMN almacenes.tipo; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.almacenes.tipo IS 'Clasificación funcional de la ubicación.';


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
    id_entidad uuid,
    datos_antiguos jsonb,
    datos_nuevos jsonb,
    cambios jsonb,
    contexto_aplicacion jsonb,
    query_ejecutada text,
    CONSTRAINT auditoria_log_operacion_check CHECK (((operacion)::text = ANY ((ARRAY['INSERT'::character varying, 'UPDATE'::character varying, 'DELETE'::character varying])::text[])))
)
WITH (fillfactor='80');


ALTER TABLE public.auditoria_log OWNER TO postgres;

--
-- Name: TABLE auditoria_log; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.auditoria_log IS 'Tabla centralizada para registrar cambios en tablas auditadas.';


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
    actualizado_en timestamp with time zone,
    CONSTRAINT configuraciones_eje_neumaticos_por_posicion_check CHECK ((neumaticos_por_posicion = ANY (ARRAY[1, 2]))),
    CONSTRAINT configuraciones_eje_numero_eje_check CHECK ((numero_eje > 0)),
    CONSTRAINT configuraciones_eje_numero_posiciones_check CHECK (((numero_posiciones >= 1) AND (numero_posiciones <= 6)))
)
WITH (fillfactor='90');


ALTER TABLE public.configuraciones_eje OWNER TO postgres;

--
-- Name: TABLE configuraciones_eje; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.configuraciones_eje IS 'Define la estructura de ejes para cada tipo de vehículo.';


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

COMMENT ON TABLE public.eventos_neumaticos IS 'Registro histórico de todos los eventos ocurridos a los neumáticos.';


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
-- Name: TABLE fabricantes_neumatico; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.fabricantes_neumatico IS 'Catálogo de fabricantes de neumáticos.';


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
    CONSTRAINT modelos_neumatico_presion_recomendada_psi_check CHECK (((presion_recomendada_psi IS NULL) OR (presion_recomendada_psi > (0)::numeric))),
    CONSTRAINT modelos_neumatico_profundidad_original_mm_check CHECK ((profundidad_original_mm > (0)::numeric)),
    CONSTRAINT modelos_neumatico_reencauches_maximos_check CHECK (((reencauches_maximos >= 0) AND (reencauches_maximos <= 10)))
)
WITH (fillfactor='90');


ALTER TABLE public.modelos_neumatico OWNER TO postgres;

--
-- Name: TABLE modelos_neumatico; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.modelos_neumatico IS 'Catálogo técnico de modelos de neumáticos.';


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

COMMENT ON TABLE public.modelos_posiciones_permitidas IS 'Tabla de asociación para indicar qué modelos se permiten/recomiendan en qué posiciones.';


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

COMMENT ON TABLE public.motivos_desecho IS 'Catálogo de razones por las cuales se desecha un neumático.';


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
    garantia_proveedor_id uuid,
    garantia_fecha_inicio date,
    garantia_km integer,
    garantia_meses integer,
    garantia_condiciones_url text,
    CONSTRAINT chk_ubicacion_mutuamente_exclusiva CHECK ((((ubicacion_almacen_id IS NOT NULL) AND (ubicacion_actual_vehiculo_id IS NULL) AND (ubicacion_actual_posicion_id IS NULL) AND (estado_actual <> 'INSTALADO'::public.estado_neumatico_enum)) OR ((ubicacion_almacen_id IS NULL) AND (ubicacion_actual_vehiculo_id IS NOT NULL) AND (ubicacion_actual_posicion_id IS NOT NULL) AND (estado_actual = 'INSTALADO'::public.estado_neumatico_enum)) OR ((ubicacion_almacen_id IS NULL) AND (ubicacion_actual_vehiculo_id IS NULL) AND (ubicacion_actual_posicion_id IS NULL) AND (estado_actual <> 'INSTALADO'::public.estado_neumatico_enum)))),
    CONSTRAINT neumaticos_costo_compra_check CHECK (((costo_compra IS NULL) OR (costo_compra >= (0)::numeric))),
    CONSTRAINT neumaticos_fechas_check CHECK (((fecha_fabricacion IS NULL) OR (fecha_fabricacion <= fecha_compra))),
    CONSTRAINT neumaticos_kilometraje_acumulado_check CHECK ((kilometraje_acumulado >= 0)),
    CONSTRAINT neumaticos_profundidad_inicial_mm_check CHECK (((profundidad_inicial_mm IS NULL) OR (profundidad_inicial_mm > (0)::numeric))),
    CONSTRAINT neumaticos_reencauches_realizados_check CHECK ((reencauches_realizados >= 0)),
    CONSTRAINT neumaticos_vida_actual_check CHECK (((vida_actual >= 1) AND (vida_actual <= 11)))
)
WITH (fillfactor='90');


ALTER TABLE public.neumaticos OWNER TO postgres;

--
-- Name: TABLE neumaticos; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.neumaticos IS 'Registro de cada neumático físico (una entrada por vida útil).';


--
-- Name: COLUMN neumaticos.vida_actual; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.neumaticos.vida_actual IS '1=Nuevo, 2=1er Reencauche, 3=2do Reencauche, etc.';


--
-- Name: COLUMN neumaticos.kilometraje_acumulado; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.neumaticos.kilometraje_acumulado IS 'Kilometraje acumulado durante la vida actual del neumático.';


--
-- Name: COLUMN neumaticos.ubicacion_almacen_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.neumaticos.ubicacion_almacen_id IS 'FK a almacenes. Indica la ubicación física actual si el neumático NO está instalado en un vehículo (NULL si está instalado).';


--
-- Name: COLUMN neumaticos.sensor_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.neumaticos.sensor_id IS '[FUTURO/OPCIONAL] Identificador único del sensor IoT asociado a este neumático físico.';


--
-- Name: COLUMN neumaticos.garantia_proveedor_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.neumaticos.garantia_proveedor_id IS '[FUTURO/OPCIONAL] Proveedor que otorga la garantía para este neumático.';


--
-- Name: COLUMN neumaticos.garantia_fecha_inicio; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.neumaticos.garantia_fecha_inicio IS '[FUTURO/OPCIONAL] Fecha de inicio de la cobertura de la garantía.';


--
-- Name: COLUMN neumaticos.garantia_km; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.neumaticos.garantia_km IS '[FUTURO/OPCIONAL] Límite de kilómetros cubiertos por la garantía.';


--
-- Name: COLUMN neumaticos.garantia_meses; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.neumaticos.garantia_meses IS '[FUTURO/OPCIONAL] Duración en meses de la garantía.';


--
-- Name: COLUMN neumaticos.garantia_condiciones_url; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.neumaticos.garantia_condiciones_url IS '[FUTURO/OPCIONAL] Enlace a los términos y condiciones de la garantía.';


--
-- Name: CONSTRAINT chk_ubicacion_mutuamente_exclusiva ON neumaticos; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON CONSTRAINT chk_ubicacion_mutuamente_exclusiva ON public.neumaticos IS 'Asegura que un neumático esté en un almacén O instalado en un vehículo/posición, pero no ambos, o sin ubicación definida si no está instalado.';


--
-- Name: parametros_inventario; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.parametros_inventario (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    parametro_tipo character varying(50) NOT NULL,
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

COMMENT ON TABLE public.parametros_inventario IS 'Tabla genérica para configurar parámetros de control de inventario (ej. niveles mínimos/máximos) por modelo y/o ubicación.';


--
-- Name: COLUMN parametros_inventario.parametro_tipo; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.parametros_inventario.parametro_tipo IS 'Nombre clave del parámetro (ej. NIVEL_MINIMO).';


--
-- Name: COLUMN parametros_inventario.modelo_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.parametros_inventario.modelo_id IS 'Modelo al que aplica el parámetro.';


--
-- Name: COLUMN parametros_inventario.ubicacion_almacen_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.parametros_inventario.ubicacion_almacen_id IS 'Ubicación a la que aplica el parámetro (NULL si aplica globalmente al modelo).';


--
-- Name: COLUMN parametros_inventario.valor_numerico; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.parametros_inventario.valor_numerico IS 'Valor numérico del parámetro.';


--
-- Name: COLUMN parametros_inventario.valor_texto; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.parametros_inventario.valor_texto IS 'Valor textual del parámetro.';


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
    actualizado_en timestamp with time zone,
    CONSTRAINT posiciones_neumatico_posicion_relativa_check CHECK ((posicion_relativa > 0))
)
WITH (fillfactor='95');


ALTER TABLE public.posiciones_neumatico OWNER TO postgres;

--
-- Name: TABLE posiciones_neumatico; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.posiciones_neumatico IS 'Define cada posición específica de montaje en un eje.';


--
-- Name: COLUMN posiciones_neumatico.codigo_posicion; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.posiciones_neumatico.codigo_posicion IS 'Código corto y único para la posición dentro de su eje (Ej: LI, LE, RI, RE, C)';


--
-- Name: proveedores; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.proveedores (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    nombre character varying(150) NOT NULL,
    tipo character varying(50),
    rfc character varying(13),
    contacto_principal text,
    telefono character varying(50),
    email character varying(100),
    direccion text,
    activo boolean DEFAULT true NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    creado_por uuid,
    actualizado_en timestamp with time zone,
    actualizado_por uuid,
    CONSTRAINT proveedores_tipo_check CHECK (((tipo)::text = ANY ((ARRAY['FABRICANTE'::character varying, 'DISTRIBUIDOR'::character varying, 'SERVICIO_REPARACION'::character varying, 'SERVICIO_REENCAUCHE'::character varying, 'OTRO'::character varying])::text[])))
)
WITH (fillfactor='95');


ALTER TABLE public.proveedores OWNER TO postgres;

--
-- Name: TABLE proveedores; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.proveedores IS 'Catálogo unificado de proveedores de bienes o servicios.';


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

COMMENT ON TABLE public.registros_odometro IS 'Historial de registros de odómetro para cada vehículo.';


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
-- Name: TABLE tipos_vehiculo; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.tipos_vehiculo IS 'Catálogo de tipos de vehículos.';


--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuarios (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    username character varying(50) NOT NULL,
    nombre_completo character varying(200),
    email character varying(100),
    password_hash text,
    rol character varying(50) DEFAULT 'OPERADOR'::character varying NOT NULL,
    activo boolean DEFAULT true NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    creado_por uuid,
    actualizado_en timestamp with time zone,
    actualizado_por uuid,
    CONSTRAINT usuarios_rol_check CHECK (((rol)::text <> ''::text))
)
WITH (fillfactor='95');


ALTER TABLE public.usuarios OWNER TO postgres;

--
-- Name: TABLE usuarios; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.usuarios IS 'Usuarios del sistema de gestión de neumáticos.';


--
-- Name: COLUMN usuarios.password_hash; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.usuarios.password_hash IS 'Almacena el HASH de la contraseña, NUNCA la contraseña en texto plano.';


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
    CONSTRAINT vehiculos_anio_fabricacion_check CHECK (((anio_fabricacion >= 1900) AND ((anio_fabricacion)::numeric <= (EXTRACT(year FROM CURRENT_DATE) + (1)::numeric)))),
    CONSTRAINT vehiculos_fecha_baja_check CHECK (((fecha_baja IS NULL) OR (fecha_baja >= fecha_alta))),
    CONSTRAINT vehiculos_odometro_actual_check CHECK (((odometro_actual IS NULL) OR (odometro_actual >= 0)))
)
WITH (fillfactor='90');


ALTER TABLE public.vehiculos OWNER TO postgres;

--
-- Name: TABLE vehiculos; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.vehiculos IS 'Registro maestro de los vehículos de la flota.';


--
-- Name: vw_historial_neumaticos; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_historial_neumaticos AS
 SELECT n.id AS neumatico_id,
    n.numero_serie,
    mn.nombre_modelo,
    mn.medida,
    e.id AS evento_id,
    e.tipo_evento,
    e.timestamp_evento,
    u.username AS usuario_registra,
    v.placa,
    v.numero_economico,
    pn.codigo_posicion,
    pn.lado,
    e.odometro_vehiculo_en_evento,
    e.profundidad_remanente_mm,
    e.presion_psi,
    e.costo_evento,
    e.moneda_costo,
    prov.nombre AS proveedor_servicio,
    md.descripcion AS motivo_desecho,
    e.notas,
    e.datos_evento,
    e.relacion_evento_anterior,
    row_number() OVER (PARTITION BY n.id ORDER BY e.timestamp_evento DESC) AS secuencia_evento_desc,
    row_number() OVER (PARTITION BY n.id ORDER BY e.timestamp_evento) AS secuencia_evento_asc
   FROM (((((((public.neumaticos n
     JOIN public.modelos_neumatico mn ON ((n.modelo_id = mn.id)))
     JOIN public.eventos_neumaticos e ON ((n.id = e.neumatico_id)))
     LEFT JOIN public.usuarios u ON ((e.usuario_id = u.id)))
     LEFT JOIN public.vehiculos v ON ((e.vehiculo_id = v.id)))
     LEFT JOIN public.posiciones_neumatico pn ON ((e.posicion_id = pn.id)))
     LEFT JOIN public.proveedores prov ON ((e.proveedor_servicio_id = prov.id)))
     LEFT JOIN public.motivos_desecho md ON ((e.motivo_desecho_id_evento = md.id)))
  ORDER BY n.id, e.timestamp_evento DESC;


ALTER VIEW public.vw_historial_neumaticos OWNER TO postgres;

--
-- Name: VIEW vw_historial_neumaticos; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON VIEW public.vw_historial_neumaticos IS 'Muestra el historial completo de eventos para cada neumático, incluyendo detalles relacionados.';


--
-- Name: vw_inventario_neumaticos; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_inventario_neumaticos AS
 SELECT mn.id AS modelo_id,
    mn.nombre_modelo,
    mn.medida,
    fn.nombre AS fabricante,
    n.estado_actual,
    n.es_reencauchado,
    n.vida_actual,
    count(*) AS cantidad,
    sum(n.costo_compra) FILTER (WHERE ((n.moneda_compra)::text = 'PEN'::text)) AS valor_total_pen,
    sum(n.costo_compra) FILTER (WHERE ((n.moneda_compra)::text = 'USD'::text)) AS valor_total_usd,
    avg(n.kilometraje_acumulado) FILTER (WHERE ((n.estado_actual <> 'EN_STOCK'::public.estado_neumatico_enum) AND (n.kilometraje_acumulado > 0))) AS km_promedio_por_vida,
    min(n.fecha_compra) AS fecha_compra_mas_antigua,
    max(n.fecha_compra) AS fecha_compra_mas_reciente,
    (avg((EXTRACT(epoch FROM (now() - (n.fecha_compra)::timestamp with time zone)) / 86400.0)))::integer AS antiguedad_promedio_dias
   FROM ((public.neumaticos n
     JOIN public.modelos_neumatico mn ON ((n.modelo_id = mn.id)))
     JOIN public.fabricantes_neumatico fn ON ((mn.fabricante_id = fn.id)))
  WHERE (n.estado_actual <> 'DESECHADO'::public.estado_neumatico_enum)
  GROUP BY mn.id, mn.nombre_modelo, mn.medida, fn.nombre, n.estado_actual, n.es_reencauchado, n.vida_actual
  ORDER BY fn.nombre, mn.nombre_modelo, mn.medida, n.estado_actual;


ALTER VIEW public.vw_inventario_neumaticos OWNER TO postgres;

--
-- Name: VIEW vw_inventario_neumaticos; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON VIEW public.vw_inventario_neumaticos IS 'Resume el inventario de neumáticos activos, agrupado por modelo, fabricante, estado y vida.';


--
-- Name: vw_neumaticos_instalados; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_neumaticos_instalados AS
 WITH ultimas_inspecciones AS (
         SELECT ranked.neumatico_id,
            ranked.profundidad_remanente_mm,
            ranked.presion_psi,
            ranked.timestamp_evento
           FROM ( SELECT eventos_neumaticos.neumatico_id,
                    eventos_neumaticos.profundidad_remanente_mm,
                    eventos_neumaticos.presion_psi,
                    eventos_neumaticos.timestamp_evento,
                    row_number() OVER (PARTITION BY eventos_neumaticos.neumatico_id ORDER BY eventos_neumaticos.timestamp_evento DESC) AS rn
                   FROM public.eventos_neumaticos
                  WHERE ((eventos_neumaticos.tipo_evento = 'INSPECCION'::public.tipo_evento_neumatico_enum) AND (eventos_neumaticos.profundidad_remanente_mm IS NOT NULL))) ranked
          WHERE (ranked.rn = 1)
        )
 SELECT n.id AS neumatico_id,
    n.numero_serie,
    n.dot,
    mn.nombre_modelo,
    mn.medida,
    fn.nombre AS fabricante,
    ((mn.indice_carga)::text || (mn.indice_velocidad)::text) AS indice_completo,
    v.placa,
    v.numero_economico,
    tv.nombre AS tipo_vehiculo,
    pn.codigo_posicion,
    pn.etiqueta_posicion,
    pn.lado,
    pn.es_interna,
    ce.nombre_eje,
    ce.tipo_eje,
    n.fecha_ultimo_evento AS fecha_instalacion,
    ui.timestamp_evento AS fecha_ultima_inspeccion,
    ui.profundidad_remanente_mm AS profundidad_actual_mm,
    ui.presion_psi AS presion_actual_psi,
    mn.profundidad_original_mm,
        CASE
            WHEN ((mn.profundidad_original_mm > (0)::numeric) AND (ui.profundidad_remanente_mm IS NOT NULL)) THEN round(((ui.profundidad_remanente_mm / mn.profundidad_original_mm) * 100.0), 1)
            ELSE NULL::numeric
        END AS porcentaje_vida_util_remanente,
    v.odometro_actual AS odometro_vehiculo_actual,
    n.kilometraje_acumulado AS kilometraje_neumatico_acumulado,
    n.vida_actual,
    n.reencauches_realizados
   FROM (((((((public.neumaticos n
     JOIN public.modelos_neumatico mn ON ((n.modelo_id = mn.id)))
     JOIN public.fabricantes_neumatico fn ON ((mn.fabricante_id = fn.id)))
     LEFT JOIN public.vehiculos v ON ((n.ubicacion_actual_vehiculo_id = v.id)))
     LEFT JOIN public.tipos_vehiculo tv ON ((v.tipo_vehiculo_id = tv.id)))
     LEFT JOIN public.posiciones_neumatico pn ON ((n.ubicacion_actual_posicion_id = pn.id)))
     LEFT JOIN public.configuraciones_eje ce ON ((pn.configuracion_eje_id = ce.id)))
     LEFT JOIN ultimas_inspecciones ui ON ((n.id = ui.neumatico_id)))
  WHERE (n.estado_actual = 'INSTALADO'::public.estado_neumatico_enum);


ALTER VIEW public.vw_neumaticos_instalados OWNER TO postgres;

--
-- Name: VIEW vw_neumaticos_instalados; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON VIEW public.vw_neumaticos_instalados IS 'Muestra información detallada de los neumáticos actualmente instalados en vehículos.';


--
-- Name: vw_neumaticos_instalados_optimizada; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_neumaticos_instalados_optimizada AS
 SELECT n.id AS neumatico_id,
    n.numero_serie,
    n.dot,
    mn.nombre_modelo,
    mn.medida,
    fn.nombre AS fabricante,
    ((mn.indice_carga)::text || (mn.indice_velocidad)::text) AS indice_completo,
    v.placa,
    v.numero_economico,
    tv.nombre AS tipo_vehiculo,
    pn.codigo_posicion,
    pn.etiqueta_posicion,
    pn.lado,
    pn.es_interna,
    ce.nombre_eje,
    ce.tipo_eje,
    n.fecha_ultimo_evento AS fecha_instalacion,
    ult.timestamp_evento AS fecha_ultima_inspeccion,
    ult.profundidad_remanente_mm AS profundidad_actual_mm,
    ult.presion_psi AS presion_actual_psi,
    mn.profundidad_original_mm,
        CASE
            WHEN ((mn.profundidad_original_mm > (0)::numeric) AND (ult.profundidad_remanente_mm IS NOT NULL)) THEN round(((ult.profundidad_remanente_mm / mn.profundidad_original_mm) * 100.0), 1)
            ELSE NULL::numeric
        END AS porcentaje_vida_util_remanente,
    v.odometro_actual AS odometro_vehiculo_actual,
    n.kilometraje_acumulado AS kilometraje_neumatico_acumulado,
    n.vida_actual,
    n.reencauches_realizados
   FROM (((((((public.neumaticos n
     JOIN public.modelos_neumatico mn ON ((n.modelo_id = mn.id)))
     JOIN public.fabricantes_neumatico fn ON ((mn.fabricante_id = fn.id)))
     LEFT JOIN public.vehiculos v ON ((n.ubicacion_actual_vehiculo_id = v.id)))
     LEFT JOIN public.tipos_vehiculo tv ON ((v.tipo_vehiculo_id = tv.id)))
     LEFT JOIN public.posiciones_neumatico pn ON ((n.ubicacion_actual_posicion_id = pn.id)))
     LEFT JOIN public.configuraciones_eje ce ON ((pn.configuracion_eje_id = ce.id)))
     LEFT JOIN LATERAL ( SELECT e.profundidad_remanente_mm,
            e.presion_psi,
            e.timestamp_evento
           FROM public.eventos_neumaticos e
          WHERE ((e.neumatico_id = n.id) AND (e.tipo_evento = 'INSPECCION'::public.tipo_evento_neumatico_enum) AND (e.profundidad_remanente_mm IS NOT NULL))
          ORDER BY e.timestamp_evento DESC
         LIMIT 1) ult ON (true))
  WHERE (n.estado_actual = 'INSTALADO'::public.estado_neumatico_enum);


ALTER VIEW public.vw_neumaticos_instalados_optimizada OWNER TO postgres;

--
-- Name: VIEW vw_neumaticos_instalados_optimizada; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON VIEW public.vw_neumaticos_instalados_optimizada IS 'Versión optimizada (con LATERAL JOIN) de la vista de neumáticos instalados.';


--
-- Name: auditoria_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auditoria_log ALTER COLUMN id SET DEFAULT nextval('public.auditoria_log_id_seq'::regclass);


--
-- Data for Name: alertas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alertas (id, tipo_alerta, mensaje, nivel_severidad, estado_alerta, timestamp_generacion, timestamp_gestion, usuario_gestion_id, neumatico_id, vehiculo_id, modelo_id, almacen_id, parametro_id, datos_contexto) FROM stdin;
\.


--
-- Data for Name: almacenes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.almacenes (id, codigo, nombre, tipo, direccion, activo, creado_en, creado_por, actualizado_en, actualizado_por) FROM stdin;
a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1	ALMPRU	Almacén de Pruebas	\N	\N	t	2025-05-01 18:30:48.33761-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	\N	\N
\.


--
-- Data for Name: auditoria_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auditoria_log (id, timestamp_log, esquema_tabla, nombre_tabla, operacion, usuario_db, usuario_aplicacion_id, usuario_aplicacion_username, direccion_ip, user_agent, id_entidad, datos_antiguos, datos_nuevos, cambios, contexto_aplicacion, query_ejecutada) FROM stdin;
180	2025-04-20 15:43:03.533994-05	public	neumaticos	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin	\N	\N	22222222-2222-2222-2222-222222222222	\N	{"id": "22222222-2222-2222-2222-222222222222", "dot": "CDCD3024", "creado_en": "2025-04-20T15:43:03.533994-05:00", "modelo_id": "e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a52", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "vida_actual": 1, "costo_compra": 610.00, "fecha_compra": "2025-04-20", "numero_serie": "SERIE456TEST", "estado_actual": "EN_STOCK", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": null, "actualizado_por": null, "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": null, "proveedor_compra_id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21", "kilometraje_acumulado": 0, "profundidad_inicial_mm": 22.00, "reencauches_realizados": 0, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null}	{"id": "22222222-2222-2222-2222-222222222222", "dot": "CDCD3024", "modelo_id": "e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a52", "vida_actual": 1, "costo_compra": 610.00, "fecha_compra": "2025-04-20", "numero_serie": "SERIE456TEST", "estado_actual": "EN_STOCK", "fecha_desecho": null, "moneda_compra": "PEN", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": null, "proveedor_compra_id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21", "kilometraje_acumulado": 0, "profundidad_inicial_mm": 22.00, "reencauches_realizados": 0, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null}	{"ip": null, "metodo": null, "endpoint": null}	INSERT INTO public.neumaticos\n  (id, numero_serie, dot, modelo_id, fecha_compra, costo_compra, proveedor_compra_id, profundidad_inicial_mm, creado_por)\nVALUES\n  ('22222222-2222-2222-2222-222222222222', -- Nuevo ID Fijo para pruebas\n   'SERIE456TEST',\n   'CDCD3024',\n   'e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a52', -- Modelo: X Line Energy D (11R22.5)\n   '2025-04-20',\n   610.00,\n   'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21', -- Proveedor: Llantas del Sur\n   22.0, -- Profundidad del modelo X Line\n   'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12');
181	2025-04-21 13:36:22.649673-05	public	vehiculos	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	operador01	\N	\N	acd03201-8723-4718-8edb-840eadd3d13f	\N	{"id": "acd03201-8723-4718-8edb-840eadd3d13f", "vin": "VINBUS101XYZ", "marca": "Mercedes Benz", "notas": "Vehículo Bus creado vía API", "placa": "XYZ-789", "activo": true, "creado_en": "2025-04-21T13:36:22.658244-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "fecha_alta": "2025-04-21", "fecha_baja": null, "actualizado_en": null, "actualizado_por": null, "modelo_vehiculo": "O500", "odometro_actual": null, "anio_fabricacion": 2022, "numero_economico": "B-101", "tipo_vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a63", "ubicacion_actual": null, "fecha_ultimo_odometro": null}	{"id": "acd03201-8723-4718-8edb-840eadd3d13f", "vin": "VINBUS101XYZ", "marca": "Mercedes Benz", "notas": "Vehículo Bus creado vía API", "placa": "XYZ-789", "activo": true, "fecha_alta": "2025-04-21", "fecha_baja": null, "modelo_vehiculo": "O500", "odometro_actual": null, "anio_fabricacion": 2022, "numero_economico": "B-101", "tipo_vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a63", "ubicacion_actual": null, "fecha_ultimo_odometro": null}	{"ip": null, "metodo": null, "endpoint": null}	INSERT INTO vehiculos (tipo_vehiculo_id, numero_economico, placa, vin, marca, modelo_vehiculo, anio_fabricacion, fecha_alta, activo, ubicacion_actual, notas, id, fecha_baja, odometro_actual, fecha_ultimo_odometro, creado_en, creado_por, actualizado_en, actualizado_por) VALUES ($1::UUID, $2::VARCHAR, $3::VARCHAR, $4::VARCHAR, $5::VARCHAR, $6::VARCHAR, $7::INTEGER, $8::DATE, $9::BOOLEAN, $10::VARCHAR, $11::VARCHAR, $12::UUID, $13::DATE, $14::INTEGER, $15::TIMESTAMP WITH TIME ZONE, $16::TIMESTAMP WITH TIME ZONE, $17::UUID, $18::TIMESTAMP WITH TIME ZONE, $19::UUID)
182	2025-04-22 09:59:50.621962-05	public	vehiculos	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	operador01	\N	\N	35b22fe3-6b2f-45ee-af5a-bbe75ed50210	\N	{"id": "35b22fe3-6b2f-45ee-af5a-bbe75ed50210", "vin": "VINBUS102XYZ", "marca": "Mercedes Benz", "notas": "Vehículo Bus NUEVO B-102 creado vía API", "placa": "XYZ-102", "activo": true, "creado_en": "2025-04-22T09:59:50.664383-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "fecha_alta": "2025-04-22", "fecha_baja": null, "actualizado_en": null, "actualizado_por": null, "modelo_vehiculo": "O500", "odometro_actual": null, "anio_fabricacion": 2023, "numero_economico": "B-102", "tipo_vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a63", "ubicacion_actual": null, "fecha_ultimo_odometro": null}	{"id": "35b22fe3-6b2f-45ee-af5a-bbe75ed50210", "vin": "VINBUS102XYZ", "marca": "Mercedes Benz", "notas": "Vehículo Bus NUEVO B-102 creado vía API", "placa": "XYZ-102", "activo": true, "fecha_alta": "2025-04-22", "fecha_baja": null, "modelo_vehiculo": "O500", "odometro_actual": null, "anio_fabricacion": 2023, "numero_economico": "B-102", "tipo_vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a63", "ubicacion_actual": null, "fecha_ultimo_odometro": null}	{"ip": null, "metodo": null, "endpoint": null}	INSERT INTO vehiculos (tipo_vehiculo_id, numero_economico, placa, vin, marca, modelo_vehiculo, anio_fabricacion, fecha_alta, activo, ubicacion_actual, notas, id, fecha_baja, odometro_actual, fecha_ultimo_odometro, creado_en, creado_por, actualizado_en, actualizado_por) VALUES ($1::UUID, $2::VARCHAR, $3::VARCHAR, $4::VARCHAR, $5::VARCHAR, $6::VARCHAR, $7::INTEGER, $8::DATE, $9::BOOLEAN, $10::VARCHAR, $11::VARCHAR, $12::UUID, $13::DATE, $14::INTEGER, $15::TIMESTAMP WITH TIME ZONE, $16::TIMESTAMP WITH TIME ZONE, $17::UUID, $18::TIMESTAMP WITH TIME ZONE, $19::UUID)
183	2025-04-22 10:50:44.490378-05	public	vehiculos	UPDATE	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	operador01	\N	\N	35b22fe3-6b2f-45ee-af5a-bbe75ed50210	{"id": "35b22fe3-6b2f-45ee-af5a-bbe75ed50210", "vin": "VINBUS102XYZ", "marca": "Mercedes Benz", "notas": "Vehículo Bus NUEVO B-102 creado vía API", "placa": "XYZ-102", "activo": true, "creado_en": "2025-04-22T09:59:50.664383-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "fecha_alta": "2025-04-22", "fecha_baja": null, "actualizado_en": null, "actualizado_por": null, "modelo_vehiculo": "O500", "odometro_actual": null, "anio_fabricacion": 2023, "numero_economico": "B-102", "tipo_vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a63", "ubicacion_actual": null, "fecha_ultimo_odometro": null}	{"id": "35b22fe3-6b2f-45ee-af5a-bbe75ed50210", "vin": "VINBUS102XYZ", "marca": "Freightliner", "notas": "Marca actualizada y nota añadida vía API PUT", "placa": "XYZ-102", "activo": true, "creado_en": "2025-04-22T09:59:50.664383-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "fecha_alta": "2025-04-22", "fecha_baja": null, "actualizado_en": "2025-04-22T10:50:44.529-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "modelo_vehiculo": "O500", "odometro_actual": null, "anio_fabricacion": 2023, "numero_economico": "B-102", "tipo_vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a63", "ubicacion_actual": null, "fecha_ultimo_odometro": null}	{"marca": "Freightliner", "notas": "Marca actualizada y nota añadida vía API PUT"}	{"ip": null, "metodo": null, "endpoint": null}	UPDATE vehiculos SET marca=$1::VARCHAR, notas=$2::VARCHAR, actualizado_en=$3::TIMESTAMP WITH TIME ZONE, actualizado_por=$4::UUID WHERE vehiculos.id = $5::UUID
184	2025-04-22 15:52:02.682512-05	public	vehiculos	UPDATE	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	operador01	\N	\N	35b22fe3-6b2f-45ee-af5a-bbe75ed50210	{"id": "35b22fe3-6b2f-45ee-af5a-bbe75ed50210", "vin": "VINBUS102XYZ", "marca": "Freightliner", "notas": "Marca actualizada y nota añadida vía API PUT", "placa": "XYZ-102", "activo": true, "creado_en": "2025-04-22T09:59:50.664383-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "fecha_alta": "2025-04-22", "fecha_baja": null, "actualizado_en": "2025-04-22T10:50:44.529-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "modelo_vehiculo": "O500", "odometro_actual": null, "anio_fabricacion": 2023, "numero_economico": "B-102", "tipo_vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a63", "ubicacion_actual": null, "fecha_ultimo_odometro": null}	{"id": "35b22fe3-6b2f-45ee-af5a-bbe75ed50210", "vin": "VINBUS102XYZ", "marca": "Freightliner", "notas": "Marca actualizada y nota añadida vía API PUT", "placa": "XYZ-102", "activo": true, "creado_en": "2025-04-22T09:59:50.664383-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "fecha_alta": "2025-04-22", "fecha_baja": null, "actualizado_en": "2025-04-22T15:52:02.685742-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "modelo_vehiculo": "O500", "odometro_actual": null, "anio_fabricacion": 2023, "numero_economico": "B-102", "tipo_vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a63", "ubicacion_actual": null, "fecha_ultimo_odometro": null}	\N	{"ip": null, "metodo": null, "endpoint": null}	UPDATE vehiculos SET actualizado_en=$1::TIMESTAMP WITH TIME ZONE WHERE vehiculos.id = $2::UUID
185	2025-04-22 16:00:56.749099-05	public	vehiculos	UPDATE	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	operador01	\N	\N	35b22fe3-6b2f-45ee-af5a-bbe75ed50210	{"id": "35b22fe3-6b2f-45ee-af5a-bbe75ed50210", "vin": "VINBUS102XYZ", "marca": "Freightliner", "notas": "Marca actualizada y nota añadida vía API PUT", "placa": "XYZ-102", "activo": true, "creado_en": "2025-04-22T09:59:50.664383-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "fecha_alta": "2025-04-22", "fecha_baja": null, "actualizado_en": "2025-04-22T15:52:02.685742-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "modelo_vehiculo": "O500", "odometro_actual": null, "anio_fabricacion": 2023, "numero_economico": "B-102", "tipo_vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a63", "ubicacion_actual": null, "fecha_ultimo_odometro": null}	{"id": "35b22fe3-6b2f-45ee-af5a-bbe75ed50210", "vin": "VINBUS102XYZ", "marca": "Freightliner", "notas": "Marca actualizada y nota añadida vía API PUT", "placa": "XYZ-102", "activo": false, "creado_en": "2025-04-22T09:59:50.664383-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "fecha_alta": "2025-04-22", "fecha_baja": "2025-04-22", "actualizado_en": "2025-04-22T16:00:56.755693-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "modelo_vehiculo": "O500", "odometro_actual": null, "anio_fabricacion": 2023, "numero_economico": "B-102", "tipo_vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a63", "ubicacion_actual": null, "fecha_ultimo_odometro": null}	{"activo": false, "fecha_baja": "2025-04-22"}	{"ip": null, "metodo": null, "endpoint": null}	UPDATE vehiculos SET activo=$1::BOOLEAN, fecha_baja=$2::DATE, actualizado_en=$3::TIMESTAMP WITH TIME ZONE WHERE vehiculos.id = $4::UUID
186	2025-05-01 18:30:48.33761-05	public	almacenes	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	operador01	\N	\N	a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1	\N	{"id": "a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1", "tipo": null, "activo": true, "codigo": "ALMPRU", "nombre": "Almacén de Pruebas", "creado_en": "2025-05-01T18:30:48.33761-05:00", "direccion": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "actualizado_en": null, "actualizado_por": null}	{"id": "a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1", "tipo": null, "activo": true, "codigo": "ALMPRU", "nombre": "Almacén de Pruebas", "direccion": null}	{"ip": null, "metodo": null, "endpoint": null}	INSERT INTO public.almacenes (id, codigo, nombre, creado_por)\nVALUES ('a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1', 'ALMPRU', 'Almacén de Pruebas', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11')\nON CONFLICT (id) DO NOTHING;
187	2025-05-01 18:30:55.026372-05	public	neumaticos	UPDATE	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	operador01	\N	\N	22222222-2222-2222-2222-222222222222	{"id": "22222222-2222-2222-2222-222222222222", "dot": "CDCD3024", "creado_en": "2025-04-20T15:43:03.533994-05:00", "modelo_id": "e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a52", "sensor_id": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "garantia_km": null, "vida_actual": 1, "costo_compra": 610.00, "fecha_compra": "2025-04-20", "numero_serie": "SERIE456TEST", "estado_actual": "EN_STOCK", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-04-23T09:29:24.072018-05:00", "garantia_meses": null, "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-04-23T09:29:24.072018-05:00", "proveedor_compra_id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21", "ubicacion_almacen_id": null, "garantia_fecha_inicio": null, "garantia_proveedor_id": null, "kilometraje_acumulado": 12000, "profundidad_inicial_mm": 22.00, "reencauches_realizados": 0, "garantia_condiciones_url": null, "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null}	{"id": "22222222-2222-2222-2222-222222222222", "dot": "CDCD3024", "creado_en": "2025-04-20T15:43:03.533994-05:00", "modelo_id": "e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a52", "sensor_id": "SENSOR_XYZ_123", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "garantia_km": 80000, "vida_actual": 1, "costo_compra": 610.00, "fecha_compra": "2025-04-20", "numero_serie": "SERIE456TEST", "estado_actual": "EN_STOCK", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-04-23T09:29:24.072018-05:00", "garantia_meses": 24, "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-04-23T09:29:24.072018-05:00", "proveedor_compra_id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21", "ubicacion_almacen_id": null, "garantia_fecha_inicio": "2025-04-01", "garantia_proveedor_id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21", "kilometraje_acumulado": 12000, "profundidad_inicial_mm": 22.00, "reencauches_realizados": 0, "garantia_condiciones_url": "http://example.com/garantia/llantas-sur", "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null}	{"sensor_id": "SENSOR_XYZ_123", "garantia_km": 80000, "garantia_meses": 24, "garantia_fecha_inicio": "2025-04-01", "garantia_proveedor_id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21", "garantia_condiciones_url": "http://example.com/garantia/llantas-sur"}	{"ip": null, "metodo": null, "endpoint": null}	UPDATE public.neumaticos\nSET\n    sensor_id = 'SENSOR_XYZ_123',\n    garantia_proveedor_id = 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21', -- ID Proveedor Llantas del Sur\n    garantia_fecha_inicio = '2025-04-01',\n    garantia_km = 80000,\n    garantia_meses = 24,\n    garantia_condiciones_url = 'http://example.com/garantia/llantas-sur',\n    actualizado_por = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11' -- ID Usuario operador01\nWHERE id = '22222222-2222-2222-2222-222222222222';
188	2025-05-01 18:31:13.685517-05	public	neumaticos	UPDATE	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	operador01	\N	\N	22222222-2222-2222-2222-222222222222	{"id": "22222222-2222-2222-2222-222222222222", "dot": "CDCD3024", "creado_en": "2025-04-20T15:43:03.533994-05:00", "modelo_id": "e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a52", "sensor_id": "SENSOR_XYZ_123", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "garantia_km": 80000, "vida_actual": 1, "costo_compra": 610.00, "fecha_compra": "2025-04-20", "numero_serie": "SERIE456TEST", "estado_actual": "EN_STOCK", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-04-23T09:29:24.072018-05:00", "garantia_meses": 24, "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-04-23T09:29:24.072018-05:00", "proveedor_compra_id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21", "ubicacion_almacen_id": null, "garantia_fecha_inicio": "2025-04-01", "garantia_proveedor_id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21", "kilometraje_acumulado": 12000, "profundidad_inicial_mm": 22.00, "reencauches_realizados": 0, "garantia_condiciones_url": "http://example.com/garantia/llantas-sur", "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null}	{"id": "22222222-2222-2222-2222-222222222222", "dot": "CDCD3024", "creado_en": "2025-04-20T15:43:03.533994-05:00", "modelo_id": "e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a52", "sensor_id": "SENSOR_XYZ_123", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "garantia_km": 80000, "vida_actual": 1, "costo_compra": 610.00, "fecha_compra": "2025-04-20", "numero_serie": "SERIE456TEST", "estado_actual": "EN_STOCK", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-04-23T09:29:24.072018-05:00", "garantia_meses": 24, "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-04-23T09:29:24.072018-05:00", "proveedor_compra_id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21", "ubicacion_almacen_id": "a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1", "garantia_fecha_inicio": "2025-04-01", "garantia_proveedor_id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21", "kilometraje_acumulado": 12000, "profundidad_inicial_mm": 22.00, "reencauches_realizados": 0, "garantia_condiciones_url": "http://example.com/garantia/llantas-sur", "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null}	{"ubicacion_almacen_id": "a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1"}	{"ip": null, "metodo": null, "endpoint": null}	UPDATE public.neumaticos\nSET\n    ubicacion_almacen_id = 'a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1', -- ID Almacén de Pruebas\n    ubicacion_actual_vehiculo_id = NULL,\n    ubicacion_actual_posicion_id = NULL,\n    estado_actual = 'EN_STOCK', -- Aseguramos estado consistente\n    actualizado_por = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'\nWHERE id = '22222222-2222-2222-2222-222222222222';
189	2025-05-01 18:33:16.744794-05	public	neumaticos	UPDATE	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	operador01	\N	\N	22222222-2222-2222-2222-222222222222	{"id": "22222222-2222-2222-2222-222222222222", "dot": "CDCD3024", "creado_en": "2025-04-20T15:43:03.533994-05:00", "modelo_id": "e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a52", "sensor_id": "SENSOR_XYZ_123", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "garantia_km": 80000, "vida_actual": 1, "costo_compra": 610.00, "fecha_compra": "2025-04-20", "numero_serie": "SERIE456TEST", "estado_actual": "EN_STOCK", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-04-23T09:29:24.072018-05:00", "garantia_meses": 24, "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-04-23T09:29:24.072018-05:00", "proveedor_compra_id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21", "ubicacion_almacen_id": "a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1", "garantia_fecha_inicio": "2025-04-01", "garantia_proveedor_id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21", "kilometraje_acumulado": 12000, "profundidad_inicial_mm": 22.00, "reencauches_realizados": 0, "garantia_condiciones_url": "http://example.com/garantia/llantas-sur", "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null}	{"id": "22222222-2222-2222-2222-222222222222", "dot": "CDCD3024", "creado_en": "2025-04-20T15:43:03.533994-05:00", "modelo_id": "e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a52", "sensor_id": "SENSOR_XYZ_123", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "garantia_km": 80000, "vida_actual": 1, "costo_compra": 610.00, "fecha_compra": "2025-04-20", "numero_serie": "SERIE456TEST", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-04-23T09:29:24.072018-05:00", "garantia_meses": 24, "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-04-23T09:29:24.072018-05:00", "proveedor_compra_id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21", "ubicacion_almacen_id": null, "garantia_fecha_inicio": "2025-04-01", "garantia_proveedor_id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21", "kilometraje_acumulado": 12000, "profundidad_inicial_mm": 22.00, "reencauches_realizados": 0, "garantia_condiciones_url": "http://example.com/garantia/llantas-sur", "ubicacion_actual_posicion_id": "f2eebc99-9c0b-4ef8-bb6d-6bb9bd380a81", "ubicacion_actual_vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a91"}	{"estado_actual": "INSTALADO", "ubicacion_almacen_id": null, "ubicacion_actual_posicion_id": "f2eebc99-9c0b-4ef8-bb6d-6bb9bd380a81", "ubicacion_actual_vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a91"}	{"ip": null, "metodo": null, "endpoint": null}	UPDATE public.neumaticos\nSET\n    ubicacion_almacen_id = NULL, -- <-- Quitar del almacén\n    ubicacion_actual_vehiculo_id = 'f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a91', -- ID Vehículo T-01\n    ubicacion_actual_posicion_id = 'f2eebc99-9c0b-4ef8-bb6d-6bb9bd380a81', -- ID Posicion 1LI\n    estado_actual = 'INSTALADO', -- Estado consistente con instalación\n    actualizado_por = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'\nWHERE id = '22222222-2222-2222-2222-222222222222';
190	2025-05-01 18:33:18.139045-05	public	neumaticos	UPDATE	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	operador01	\N	\N	22222222-2222-2222-2222-222222222222	{"id": "22222222-2222-2222-2222-222222222222", "dot": "CDCD3024", "creado_en": "2025-04-20T15:43:03.533994-05:00", "modelo_id": "e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a52", "sensor_id": "SENSOR_XYZ_123", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "garantia_km": 80000, "vida_actual": 1, "costo_compra": 610.00, "fecha_compra": "2025-04-20", "numero_serie": "SERIE456TEST", "estado_actual": "INSTALADO", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-04-23T09:29:24.072018-05:00", "garantia_meses": 24, "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-04-23T09:29:24.072018-05:00", "proveedor_compra_id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21", "ubicacion_almacen_id": null, "garantia_fecha_inicio": "2025-04-01", "garantia_proveedor_id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21", "kilometraje_acumulado": 12000, "profundidad_inicial_mm": 22.00, "reencauches_realizados": 0, "garantia_condiciones_url": "http://example.com/garantia/llantas-sur", "ubicacion_actual_posicion_id": "f2eebc99-9c0b-4ef8-bb6d-6bb9bd380a81", "ubicacion_actual_vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a91"}	{"id": "22222222-2222-2222-2222-222222222222", "dot": "CDCD3024", "creado_en": "2025-04-20T15:43:03.533994-05:00", "modelo_id": "e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a52", "sensor_id": "SENSOR_XYZ_123", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "garantia_km": 80000, "vida_actual": 1, "costo_compra": 610.00, "fecha_compra": "2025-04-20", "numero_serie": "SERIE456TEST", "estado_actual": "EN_STOCK", "fecha_desecho": null, "moneda_compra": "PEN", "actualizado_en": "2025-04-23T09:29:24.072018-05:00", "garantia_meses": 24, "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "es_reencauchado": false, "fecha_fabricacion": null, "motivo_desecho_id": null, "fecha_ultimo_evento": "2025-04-23T09:29:24.072018-05:00", "proveedor_compra_id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21", "ubicacion_almacen_id": null, "garantia_fecha_inicio": "2025-04-01", "garantia_proveedor_id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21", "kilometraje_acumulado": 12000, "profundidad_inicial_mm": 22.00, "reencauches_realizados": 0, "garantia_condiciones_url": "http://example.com/garantia/llantas-sur", "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null}	{"estado_actual": "EN_STOCK", "ubicacion_actual_posicion_id": null, "ubicacion_actual_vehiculo_id": null}	{"ip": null, "metodo": null, "endpoint": null}	UPDATE public.neumaticos\nSET\n    ubicacion_almacen_id = NULL,\n    ubicacion_actual_vehiculo_id = NULL,\n    ubicacion_actual_posicion_id = NULL,\n    estado_actual = 'EN_STOCK',\n    actualizado_por = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'\nWHERE id = '22222222-2222-2222-2222-222222222222';
191	2025-05-01 18:33:40.763648-05	public	alertas	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	operador01_test	192.168.1.100	\N	4a22565f-2c91-44c4-91fa-e40e1edd7cf3	\N	{"id": "4a22565f-2c91-44c4-91fa-e40e1edd7cf3", "mensaje": "Profundidad crítica detectada en neumático", "modelo_id": null, "almacen_id": null, "tipo_alerta": "PROFUNDIDAD_BAJA", "vehiculo_id": null, "neumatico_id": "22222222-2222-2222-2222-222222222222", "parametro_id": null, "estado_alerta": "NUEVA", "datos_contexto": {"posicion": "1LI", "umbral_minimo_mm": 5.0, "profundidad_medida_mm": 4.5}, "nivel_severidad": "WARN", "timestamp_gestion": null, "usuario_gestion_id": null, "timestamp_generacion": "2025-05-01T18:33:40.763648-05:00"}	{"id": "4a22565f-2c91-44c4-91fa-e40e1edd7cf3", "mensaje": "Profundidad crítica detectada en neumático", "modelo_id": null, "almacen_id": null, "tipo_alerta": "PROFUNDIDAD_BAJA", "vehiculo_id": null, "neumatico_id": "22222222-2222-2222-2222-222222222222", "parametro_id": null, "estado_alerta": "NUEVA", "datos_contexto": {"posicion": "1LI", "umbral_minimo_mm": 5.0, "profundidad_medida_mm": 4.5}, "nivel_severidad": "WARN", "timestamp_gestion": null, "usuario_gestion_id": null, "timestamp_generacion": "2025-05-01T18:33:40.763648-05:00"}	{"ip": "192.168.1.100", "metodo": "POST", "endpoint": "/test/crear_alerta"}	INSERT INTO public.alertas (tipo_alerta, mensaje, nivel_severidad, estado_alerta, neumatico_id, datos_contexto)\nVALUES (\n    'PROFUNDIDAD_BAJA',\n    'Profundidad crítica detectada en neumático',\n    'WARN',\n    'NUEVA',\n    '22222222-2222-2222-2222-222222222222', -- ID Neumático de prueba\n    '{"profundidad_medida_mm": 4.5, "umbral_minimo_mm": 5.0, "posicion": "1LI"}'::jsonb\n) RETURNING id;
192	2025-05-01 18:36:55.390831-05	public	alertas	UPDATE	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13	supervisor01_test	192.168.1.101	\N	4a22565f-2c91-44c4-91fa-e40e1edd7cf3	{"id": "4a22565f-2c91-44c4-91fa-e40e1edd7cf3", "mensaje": "Profundidad crítica detectada en neumático", "modelo_id": null, "almacen_id": null, "tipo_alerta": "PROFUNDIDAD_BAJA", "vehiculo_id": null, "neumatico_id": "22222222-2222-2222-2222-222222222222", "parametro_id": null, "estado_alerta": "NUEVA", "datos_contexto": {"posicion": "1LI", "umbral_minimo_mm": 5.0, "profundidad_medida_mm": 4.5}, "nivel_severidad": "WARN", "timestamp_gestion": null, "usuario_gestion_id": null, "timestamp_generacion": "2025-05-01T18:33:40.763648-05:00"}	{"id": "4a22565f-2c91-44c4-91fa-e40e1edd7cf3", "mensaje": "Profundidad crítica detectada en neumático", "modelo_id": null, "almacen_id": null, "tipo_alerta": "PROFUNDIDAD_BAJA", "vehiculo_id": null, "neumatico_id": "22222222-2222-2222-2222-222222222222", "parametro_id": null, "estado_alerta": "VISTA", "datos_contexto": {"posicion": "1LI", "umbral_minimo_mm": 5.0, "profundidad_medida_mm": 4.5}, "nivel_severidad": "WARN", "timestamp_gestion": "2025-05-01T18:36:55.390831-05:00", "usuario_gestion_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13", "timestamp_generacion": "2025-05-01T18:33:40.763648-05:00"}	{"estado_alerta": "VISTA", "timestamp_gestion": "2025-05-01T18:36:55.390831-05:00", "usuario_gestion_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13"}	{"ip": "192.168.1.101", "metodo": "PUT", "endpoint": "/test/gestionar_alerta"}	UPDATE public.alertas\nSET\n    estado_alerta = 'VISTA',\n    timestamp_gestion = NOW(),\n    usuario_gestion_id = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13' -- ID del supervisor\nWHERE id = '4a22565f-2c91-44c4-91fa-e40e1edd7cf3';
193	2025-05-01 18:39:58.688239-05	public	alertas	DELETE	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin_test	192.168.1.102	\N	4a22565f-2c91-44c4-91fa-e40e1edd7cf3	{"id": "4a22565f-2c91-44c4-91fa-e40e1edd7cf3", "mensaje": "Profundidad crítica detectada en neumático", "modelo_id": null, "almacen_id": null, "tipo_alerta": "PROFUNDIDAD_BAJA", "vehiculo_id": null, "neumatico_id": "22222222-2222-2222-2222-222222222222", "parametro_id": null, "estado_alerta": "VISTA", "datos_contexto": {"posicion": "1LI", "umbral_minimo_mm": 5.0, "profundidad_medida_mm": 4.5}, "nivel_severidad": "WARN", "timestamp_gestion": "2025-05-01T18:36:55.390831-05:00", "usuario_gestion_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13", "timestamp_generacion": "2025-05-01T18:33:40.763648-05:00"}	\N	{"id": "4a22565f-2c91-44c4-91fa-e40e1edd7cf3", "mensaje": "Profundidad crítica detectada en neumático", "modelo_id": null, "almacen_id": null, "tipo_alerta": "PROFUNDIDAD_BAJA", "vehiculo_id": null, "neumatico_id": "22222222-2222-2222-2222-222222222222", "parametro_id": null, "estado_alerta": "VISTA", "datos_contexto": {"posicion": "1LI", "umbral_minimo_mm": 5.0, "profundidad_medida_mm": 4.5}, "nivel_severidad": "WARN", "timestamp_gestion": "2025-05-01T18:36:55.390831-05:00", "usuario_gestion_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13", "timestamp_generacion": "2025-05-01T18:33:40.763648-05:00"}	{"ip": "192.168.1.102", "metodo": "DELETE", "endpoint": "/test/eliminar_alerta"}	DELETE FROM public.alertas WHERE id = '4a22565f-2c91-44c4-91fa-e40e1edd7cf3';
148	2025-04-20 01:42:55.552318-05	public	registros_odometro	DELETE	postgres	\N	\N	\N	\N	be59c166-5f21-43e2-b8d6-c93e6ab2872c	{"id": "be59c166-5f21-43e2-b8d6-c93e6ab2872c", "notas": null, "fuente": "MANUAL_INCORRECTO", "odometro": 71000, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a91", "fecha_medicion": "2025-04-20T00:50:00-05:00"}	\N	{"id": "be59c166-5f21-43e2-b8d6-c93e6ab2872c", "notas": null, "fuente": "MANUAL_INCORRECTO", "odometro": 71000, "vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a91", "fecha_medicion": "2025-04-20T00:50:00-05:00"}	{"ip": null, "metodo": null, "endpoint": null}	DELETE FROM public.registros_odometro;
143	2025-04-20 01:42:55.552318-05	public	registros_odometro	DELETE	postgres	\N	\N	\N	\N	d10b3c60-cadc-493b-aed0-e9c1ed2b7dbd	{"id": "d10b3c60-cadc-493b-aed0-e9c1ed2b7dbd", "notas": null, "fuente": "EVENTO_NEUMATICO", "odometro": 65000, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a91", "fecha_medicion": "2025-04-20T00:36:25-05:00"}	\N	{"id": "d10b3c60-cadc-493b-aed0-e9c1ed2b7dbd", "notas": null, "fuente": "EVENTO_NEUMATICO", "odometro": 65000, "vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a91", "fecha_medicion": "2025-04-20T00:36:25-05:00"}	{"ip": null, "metodo": null, "endpoint": null}	DELETE FROM public.registros_odometro;
144	2025-04-20 01:42:55.552318-05	public	registros_odometro	DELETE	postgres	\N	\N	\N	\N	70c96147-b0d0-4593-91b4-dae660debea5	{"id": "70c96147-b0d0-4593-91b4-dae660debea5", "notas": null, "fuente": "MANUAL", "odometro": 70000, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a91", "fecha_medicion": "2025-04-20T01:00:00-05:00"}	\N	{"id": "70c96147-b0d0-4593-91b4-dae660debea5", "notas": null, "fuente": "MANUAL", "odometro": 70000, "vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a91", "fecha_medicion": "2025-04-20T01:00:00-05:00"}	{"ip": null, "metodo": null, "endpoint": null}	DELETE FROM public.registros_odometro;
145	2025-04-20 01:42:55.552318-05	public	registros_odometro	DELETE	postgres	\N	\N	\N	\N	13d0e27f-287d-4afe-8349-8a141a692079	{"id": "13d0e27f-287d-4afe-8349-8a141a692079", "notas": null, "fuente": "TELEMETRIA_RETRASADA", "odometro": 71000, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a91", "fecha_medicion": "2025-04-20T00:50:00-05:00"}	\N	{"id": "13d0e27f-287d-4afe-8349-8a141a692079", "notas": null, "fuente": "TELEMETRIA_RETRASADA", "odometro": 71000, "vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a91", "fecha_medicion": "2025-04-20T00:50:00-05:00"}	{"ip": null, "metodo": null, "endpoint": null}	DELETE FROM public.registros_odometro;
146	2025-04-20 01:42:55.552318-05	public	registros_odometro	DELETE	postgres	\N	\N	\N	\N	1311be51-e8a2-47ef-8014-a439d890f48d	{"id": "1311be51-e8a2-47ef-8014-a439d890f48d", "notas": null, "fuente": "MANUAL_ERROR", "odometro": 70500, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a91", "fecha_medicion": "2025-04-20T01:10:00-05:00"}	\N	{"id": "1311be51-e8a2-47ef-8014-a439d890f48d", "notas": null, "fuente": "MANUAL_ERROR", "odometro": 70500, "vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a91", "fecha_medicion": "2025-04-20T01:10:00-05:00"}	{"ip": null, "metodo": null, "endpoint": null}	DELETE FROM public.registros_odometro;
147	2025-04-20 01:42:55.552318-05	public	registros_odometro	DELETE	postgres	\N	\N	\N	\N	35394123-dfef-493f-9f27-ae0a19a43b35	{"id": "35394123-dfef-493f-9f27-ae0a19a43b35", "notas": null, "fuente": "TELEMETRIA_CORREGIDA", "odometro": 71500, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a91", "fecha_medicion": "2025-04-20T00:50:00-05:00"}	\N	{"id": "35394123-dfef-493f-9f27-ae0a19a43b35", "notas": null, "fuente": "TELEMETRIA_CORREGIDA", "odometro": 71500, "vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a91", "fecha_medicion": "2025-04-20T00:50:00-05:00"}	{"ip": null, "metodo": null, "endpoint": null}	DELETE FROM public.registros_odometro;
150	2025-04-20 01:42:55.552318-05	public	tipos_vehiculo	DELETE	postgres	\N	\N	\N	\N	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a61	{"id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a61", "activo": true, "nombre": "Tractocamión 6x4", "subtipo": null, "creado_en": "2025-04-19T22:27:29.040586-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "descripcion": null, "ejes_standard": 3, "actualizado_en": null, "actualizado_por": null, "categoria_principal": "Camión"}	\N	{"id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a61", "activo": true, "nombre": "Tractocamión 6x4", "subtipo": null, "descripcion": null, "ejes_standard": 3, "categoria_principal": "Camión"}	{"ip": null, "metodo": null, "endpoint": null}	DELETE FROM public.tipos_vehiculo;
151	2025-04-20 01:42:55.552318-05	public	fabricantes_neumatico	DELETE	postgres	\N	\N	\N	\N	d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41	{"id": "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41", "activo": true, "nombre": "Michelin", "creado_en": "2025-04-19T22:27:29.040586-05:00", "sitio_web": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "pais_origen": "Francia", "actualizado_en": null, "actualizado_por": null, "codigo_abreviado": "MICH"}	\N	{"id": "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41", "activo": true, "nombre": "Michelin", "sitio_web": null, "pais_origen": "Francia", "codigo_abreviado": "MICH"}	{"ip": null, "metodo": null, "endpoint": null}	DELETE FROM public.fabricantes_neumatico;
152	2025-04-20 01:42:55.552318-05	public	motivos_desecho	DELETE	postgres	\N	\N	\N	\N	c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a31	{"id": "c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a31", "activo": true, "codigo": "BAJOREM", "creado_en": "2025-04-19T22:27:29.040586-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "descripcion": "Bajo remanente de banda", "actualizado_en": null, "actualizado_por": null, "requiere_evidencia": false}	\N	{"id": "c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a31", "activo": true, "codigo": "BAJOREM", "descripcion": "Bajo remanente de banda", "requiere_evidencia": false}	{"ip": null, "metodo": null, "endpoint": null}	DELETE FROM public.motivos_desecho;
153	2025-04-20 01:42:55.552318-05	public	motivos_desecho	DELETE	postgres	\N	\N	\N	\N	c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a32	{"id": "c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a32", "activo": true, "codigo": "GOLPCAS", "creado_en": "2025-04-19T22:27:29.040586-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "descripcion": "Golpe en carcasa / Rotura", "actualizado_en": null, "actualizado_por": null, "requiere_evidencia": false}	\N	{"id": "c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a32", "activo": true, "codigo": "GOLPCAS", "descripcion": "Golpe en carcasa / Rotura", "requiere_evidencia": false}	{"ip": null, "metodo": null, "endpoint": null}	DELETE FROM public.motivos_desecho;
154	2025-04-20 01:42:55.552318-05	public	proveedores	DELETE	postgres	\N	\N	\N	\N	b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21	{"id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21", "rfc": "20123456789", "tipo": "DISTRIBUIDOR", "email": null, "activo": true, "nombre": "Proveedor Llantas SAC", "telefono": null, "creado_en": "2025-04-19T22:27:29.040586-05:00", "direccion": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": null, "actualizado_por": null, "contacto_principal": null}	\N	{"id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21", "rfc": "20123456789", "tipo": "DISTRIBUIDOR", "email": null, "activo": true, "nombre": "Proveedor Llantas SAC", "telefono": null, "direccion": null, "contacto_principal": null}	{"ip": null, "metodo": null, "endpoint": null}	DELETE FROM public.proveedores;
155	2025-04-20 01:42:55.552318-05	public	usuarios	DELETE	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N	\N	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	{"id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "rol": "ADMIN", "email": "admin@example.com", "activo": true, "username": "admin", "creado_en": "2025-04-19T22:27:29.040586-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "password_hash": null, "actualizado_en": null, "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "nombre_completo": "Administrador Sistema"}	\N	{"id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "rol": "ADMIN", "email": "admin@example.com", "activo": true, "username": "admin", "password_hash": null, "nombre_completo": "Administrador Sistema"}	{"ip": null, "metodo": null, "endpoint": null}	DELETE FROM public.usuarios;
149	2025-04-20 01:42:55.552318-05	public	vehiculos	DELETE	postgres	\N	operador_test	\N	\N	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a91	{"id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a91", "vin": null, "marca": "Volvo", "notas": null, "placa": "ABC-123", "activo": true, "creado_en": "2025-04-19T22:27:29.040586-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "fecha_alta": "2025-04-19", "fecha_baja": null, "actualizado_en": "2025-04-20T00:44:18.17346-05:00", "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "modelo_vehiculo": null, "odometro_actual": 70500, "anio_fabricacion": null, "numero_economico": "T-01", "tipo_vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a61", "ubicacion_actual": null, "fecha_ultimo_odometro": "2025-04-20T01:10:00-05:00"}	\N	{"id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a91", "vin": null, "marca": "Volvo", "notas": null, "placa": "ABC-123", "activo": true, "fecha_alta": "2025-04-19", "fecha_baja": null, "modelo_vehiculo": null, "odometro_actual": 70500, "anio_fabricacion": null, "numero_economico": "T-01", "tipo_vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a61", "ubicacion_actual": null, "fecha_ultimo_odometro": "2025-04-20T01:10:00-05:00"}	{"ip": null, "metodo": null, "endpoint": null}	DELETE FROM public.vehiculos;
156	2025-04-20 01:42:55.552318-05	public	usuarios	DELETE	postgres	\N	\N	\N	\N	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	{"id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "rol": "OPERADOR", "email": "operador@example.com", "activo": true, "username": "operador_test", "creado_en": "2025-04-19T22:27:29.040586-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "password_hash": "$2a$06$4DYAVDQlf0cqeMZpLyTBaetDAmMaF2TWjddBPR1pe/MCfHlch9che", "actualizado_en": null, "actualizado_por": null, "nombre_completo": "Usuario Operador Prueba"}	\N	{"id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "rol": "OPERADOR", "email": "operador@example.com", "activo": true, "username": "operador_test", "password_hash": "$2a$06$4DYAVDQlf0cqeMZpLyTBaetDAmMaF2TWjddBPR1pe/MCfHlch9che", "nombre_completo": "Usuario Operador Prueba"}	{"ip": null, "metodo": null, "endpoint": null}	DELETE FROM public.usuarios;
157	2025-04-20 01:42:55.552318-05	public	usuarios	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin	\N	\N	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	{"id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "rol": "ADMIN", "email": "admin@tuempresa.com", "activo": true, "username": "admin", "creado_en": "2025-04-20T01:42:55.552318-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "password_hash": "$2a$06$X93kYLu1ZGz.jhaMYrg4NO86nCUGCzkU8hWKli4sFTaZE9b.zFrlW", "actualizado_en": null, "actualizado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "nombre_completo": "Admin Principal"}	{"id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "rol": "ADMIN", "email": "admin@tuempresa.com", "activo": true, "username": "admin", "password_hash": "$2a$06$X93kYLu1ZGz.jhaMYrg4NO86nCUGCzkU8hWKli4sFTaZE9b.zFrlW", "nombre_completo": "Admin Principal"}	{"ip": null, "metodo": null, "endpoint": null}	INSERT INTO public.usuarios (id, username, nombre_completo, email, rol, activo, creado_por, actualizado_por, password_hash) VALUES\n('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', 'admin', 'Admin Principal', 'admin@tuempresa.com', 'ADMIN', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', crypt('admin123', gen_salt('bf'))),\n('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'operador01', 'Juan Perez', 'jperez@tuempresa.com', 'OPERADOR', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', null, crypt('operador123', gen_salt('bf'))),\n('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13', 'supervisor01', 'Maria Garcia', 'mgarcia@tuempresa.com', 'GESTOR', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', null, crypt('supervisor123', gen_salt('bf')));
158	2025-04-20 01:42:55.552318-05	public	usuarios	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin	\N	\N	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	\N	{"id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "rol": "OPERADOR", "email": "jperez@tuempresa.com", "activo": true, "username": "operador01", "creado_en": "2025-04-20T01:42:55.552318-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "password_hash": "$2a$06$oJbb7TRwbqNT.F6WYwBUiuh5TFPYGXXt.KXso36eL3AlvQxYp0nVW", "actualizado_en": null, "actualizado_por": null, "nombre_completo": "Juan Perez"}	{"id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "rol": "OPERADOR", "email": "jperez@tuempresa.com", "activo": true, "username": "operador01", "password_hash": "$2a$06$oJbb7TRwbqNT.F6WYwBUiuh5TFPYGXXt.KXso36eL3AlvQxYp0nVW", "nombre_completo": "Juan Perez"}	{"ip": null, "metodo": null, "endpoint": null}	INSERT INTO public.usuarios (id, username, nombre_completo, email, rol, activo, creado_por, actualizado_por, password_hash) VALUES\n('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', 'admin', 'Admin Principal', 'admin@tuempresa.com', 'ADMIN', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', crypt('admin123', gen_salt('bf'))),\n('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'operador01', 'Juan Perez', 'jperez@tuempresa.com', 'OPERADOR', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', null, crypt('operador123', gen_salt('bf'))),\n('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13', 'supervisor01', 'Maria Garcia', 'mgarcia@tuempresa.com', 'GESTOR', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', null, crypt('supervisor123', gen_salt('bf')));
159	2025-04-20 01:42:55.552318-05	public	usuarios	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin	\N	\N	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13	\N	{"id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13", "rol": "GESTOR", "email": "mgarcia@tuempresa.com", "activo": true, "username": "supervisor01", "creado_en": "2025-04-20T01:42:55.552318-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "password_hash": "$2a$06$mYXk.CtFJ/Xo/LYtIAyVoeQQnt15zoxIIPyyXk8lYj99C7mp2v9Iy", "actualizado_en": null, "actualizado_por": null, "nombre_completo": "Maria Garcia"}	{"id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13", "rol": "GESTOR", "email": "mgarcia@tuempresa.com", "activo": true, "username": "supervisor01", "password_hash": "$2a$06$mYXk.CtFJ/Xo/LYtIAyVoeQQnt15zoxIIPyyXk8lYj99C7mp2v9Iy", "nombre_completo": "Maria Garcia"}	{"ip": null, "metodo": null, "endpoint": null}	INSERT INTO public.usuarios (id, username, nombre_completo, email, rol, activo, creado_por, actualizado_por, password_hash) VALUES\n('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', 'admin', 'Admin Principal', 'admin@tuempresa.com', 'ADMIN', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', crypt('admin123', gen_salt('bf'))),\n('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'operador01', 'Juan Perez', 'jperez@tuempresa.com', 'OPERADOR', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', null, crypt('operador123', gen_salt('bf'))),\n('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13', 'supervisor01', 'Maria Garcia', 'mgarcia@tuempresa.com', 'GESTOR', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', null, crypt('supervisor123', gen_salt('bf')));
160	2025-04-20 01:42:55.552318-05	public	proveedores	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin	\N	\N	b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21	\N	{"id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21", "rfc": "20123456789", "tipo": "DISTRIBUIDOR", "email": null, "activo": true, "nombre": "Llantas del Sur S.A.C.", "telefono": null, "creado_en": "2025-04-20T01:42:55.552318-05:00", "direccion": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": null, "actualizado_por": null, "contacto_principal": null}	{"id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21", "rfc": "20123456789", "tipo": "DISTRIBUIDOR", "email": null, "activo": true, "nombre": "Llantas del Sur S.A.C.", "telefono": null, "direccion": null, "contacto_principal": null}	{"ip": null, "metodo": null, "endpoint": null}	INSERT INTO public.proveedores (id, nombre, tipo, rfc, activo, creado_por) VALUES\n('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21', 'Llantas del Sur S.A.C.', 'DISTRIBUIDOR', '20123456789', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'Reencauchadora El Condor E.I.R.L.', 'SERVICIO_REENCAUCHE', '10987654321', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a23', 'Reparaciones Viales Andinas', 'SERVICIO_REPARACION', '20555666777', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12');
161	2025-04-20 01:42:55.552318-05	public	proveedores	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin	\N	\N	b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22	\N	{"id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22", "rfc": "10987654321", "tipo": "SERVICIO_REENCAUCHE", "email": null, "activo": true, "nombre": "Reencauchadora El Condor E.I.R.L.", "telefono": null, "creado_en": "2025-04-20T01:42:55.552318-05:00", "direccion": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": null, "actualizado_por": null, "contacto_principal": null}	{"id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22", "rfc": "10987654321", "tipo": "SERVICIO_REENCAUCHE", "email": null, "activo": true, "nombre": "Reencauchadora El Condor E.I.R.L.", "telefono": null, "direccion": null, "contacto_principal": null}	{"ip": null, "metodo": null, "endpoint": null}	INSERT INTO public.proveedores (id, nombre, tipo, rfc, activo, creado_por) VALUES\n('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21', 'Llantas del Sur S.A.C.', 'DISTRIBUIDOR', '20123456789', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'Reencauchadora El Condor E.I.R.L.', 'SERVICIO_REENCAUCHE', '10987654321', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a23', 'Reparaciones Viales Andinas', 'SERVICIO_REPARACION', '20555666777', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12');
162	2025-04-20 01:42:55.552318-05	public	proveedores	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin	\N	\N	b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a23	\N	{"id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a23", "rfc": "20555666777", "tipo": "SERVICIO_REPARACION", "email": null, "activo": true, "nombre": "Reparaciones Viales Andinas", "telefono": null, "creado_en": "2025-04-20T01:42:55.552318-05:00", "direccion": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "actualizado_en": null, "actualizado_por": null, "contacto_principal": null}	{"id": "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a23", "rfc": "20555666777", "tipo": "SERVICIO_REPARACION", "email": null, "activo": true, "nombre": "Reparaciones Viales Andinas", "telefono": null, "direccion": null, "contacto_principal": null}	{"ip": null, "metodo": null, "endpoint": null}	INSERT INTO public.proveedores (id, nombre, tipo, rfc, activo, creado_por) VALUES\n('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21', 'Llantas del Sur S.A.C.', 'DISTRIBUIDOR', '20123456789', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'Reencauchadora El Condor E.I.R.L.', 'SERVICIO_REENCAUCHE', '10987654321', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a23', 'Reparaciones Viales Andinas', 'SERVICIO_REPARACION', '20555666777', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12');
163	2025-04-20 01:42:55.552318-05	public	motivos_desecho	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin	\N	\N	c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a31	\N	{"id": "c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a31", "activo": true, "codigo": "BAJOREM", "creado_en": "2025-04-20T01:42:55.552318-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "descripcion": "Bajo remanente de banda", "actualizado_en": null, "actualizado_por": null, "requiere_evidencia": false}	{"id": "c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a31", "activo": true, "codigo": "BAJOREM", "descripcion": "Bajo remanente de banda", "requiere_evidencia": false}	{"ip": null, "metodo": null, "endpoint": null}	INSERT INTO public.motivos_desecho (id, codigo, descripcion, activo, creado_por) VALUES\n('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a31', 'BAJOREM', 'Bajo remanente de banda', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a32', 'GOLPCAS', 'Golpe en carcasa / Rotura', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 'DESGIRR', 'Desgaste irregular severo', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a34', 'VEJEZ', 'Envejecimiento / Cristalización', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12');
169	2025-04-20 01:42:55.552318-05	public	fabricantes_neumatico	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin	\N	\N	d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a43	\N	{"id": "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a43", "activo": true, "nombre": "Bridgestone", "creado_en": "2025-04-20T01:42:55.552318-05:00", "sitio_web": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "pais_origen": "Japón", "actualizado_en": null, "actualizado_por": null, "codigo_abreviado": "BDST"}	{"id": "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a43", "activo": true, "nombre": "Bridgestone", "sitio_web": null, "pais_origen": "Japón", "codigo_abreviado": "BDST"}	{"ip": null, "metodo": null, "endpoint": null}	INSERT INTO public.fabricantes_neumatico (id, nombre, codigo_abreviado, pais_origen, activo, creado_por) VALUES\n('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41', 'Michelin', 'MICH', 'Francia', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a42', 'Goodyear', 'GDYR', 'EEUU', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a43', 'Bridgestone', 'BDST', 'Japón', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12');
164	2025-04-20 01:42:55.552318-05	public	motivos_desecho	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin	\N	\N	c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a32	\N	{"id": "c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a32", "activo": true, "codigo": "GOLPCAS", "creado_en": "2025-04-20T01:42:55.552318-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "descripcion": "Golpe en carcasa / Rotura", "actualizado_en": null, "actualizado_por": null, "requiere_evidencia": false}	{"id": "c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a32", "activo": true, "codigo": "GOLPCAS", "descripcion": "Golpe en carcasa / Rotura", "requiere_evidencia": false}	{"ip": null, "metodo": null, "endpoint": null}	INSERT INTO public.motivos_desecho (id, codigo, descripcion, activo, creado_por) VALUES\n('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a31', 'BAJOREM', 'Bajo remanente de banda', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a32', 'GOLPCAS', 'Golpe en carcasa / Rotura', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 'DESGIRR', 'Desgaste irregular severo', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a34', 'VEJEZ', 'Envejecimiento / Cristalización', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12');
165	2025-04-20 01:42:55.552318-05	public	motivos_desecho	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin	\N	\N	c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33	\N	{"id": "c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33", "activo": true, "codigo": "DESGIRR", "creado_en": "2025-04-20T01:42:55.552318-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "descripcion": "Desgaste irregular severo", "actualizado_en": null, "actualizado_por": null, "requiere_evidencia": false}	{"id": "c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33", "activo": true, "codigo": "DESGIRR", "descripcion": "Desgaste irregular severo", "requiere_evidencia": false}	{"ip": null, "metodo": null, "endpoint": null}	INSERT INTO public.motivos_desecho (id, codigo, descripcion, activo, creado_por) VALUES\n('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a31', 'BAJOREM', 'Bajo remanente de banda', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a32', 'GOLPCAS', 'Golpe en carcasa / Rotura', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 'DESGIRR', 'Desgaste irregular severo', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a34', 'VEJEZ', 'Envejecimiento / Cristalización', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12');
166	2025-04-20 01:42:55.552318-05	public	motivos_desecho	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin	\N	\N	c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a34	\N	{"id": "c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a34", "activo": true, "codigo": "VEJEZ", "creado_en": "2025-04-20T01:42:55.552318-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "descripcion": "Envejecimiento / Cristalización", "actualizado_en": null, "actualizado_por": null, "requiere_evidencia": false}	{"id": "c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a34", "activo": true, "codigo": "VEJEZ", "descripcion": "Envejecimiento / Cristalización", "requiere_evidencia": false}	{"ip": null, "metodo": null, "endpoint": null}	INSERT INTO public.motivos_desecho (id, codigo, descripcion, activo, creado_por) VALUES\n('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a31', 'BAJOREM', 'Bajo remanente de banda', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a32', 'GOLPCAS', 'Golpe en carcasa / Rotura', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 'DESGIRR', 'Desgaste irregular severo', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a34', 'VEJEZ', 'Envejecimiento / Cristalización', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12');
167	2025-04-20 01:42:55.552318-05	public	fabricantes_neumatico	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin	\N	\N	d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41	\N	{"id": "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41", "activo": true, "nombre": "Michelin", "creado_en": "2025-04-20T01:42:55.552318-05:00", "sitio_web": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "pais_origen": "Francia", "actualizado_en": null, "actualizado_por": null, "codigo_abreviado": "MICH"}	{"id": "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41", "activo": true, "nombre": "Michelin", "sitio_web": null, "pais_origen": "Francia", "codigo_abreviado": "MICH"}	{"ip": null, "metodo": null, "endpoint": null}	INSERT INTO public.fabricantes_neumatico (id, nombre, codigo_abreviado, pais_origen, activo, creado_por) VALUES\n('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41', 'Michelin', 'MICH', 'Francia', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a42', 'Goodyear', 'GDYR', 'EEUU', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a43', 'Bridgestone', 'BDST', 'Japón', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12');
168	2025-04-20 01:42:55.552318-05	public	fabricantes_neumatico	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin	\N	\N	d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a42	\N	{"id": "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a42", "activo": true, "nombre": "Goodyear", "creado_en": "2025-04-20T01:42:55.552318-05:00", "sitio_web": null, "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "pais_origen": "EEUU", "actualizado_en": null, "actualizado_por": null, "codigo_abreviado": "GDYR"}	{"id": "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a42", "activo": true, "nombre": "Goodyear", "sitio_web": null, "pais_origen": "EEUU", "codigo_abreviado": "GDYR"}	{"ip": null, "metodo": null, "endpoint": null}	INSERT INTO public.fabricantes_neumatico (id, nombre, codigo_abreviado, pais_origen, activo, creado_por) VALUES\n('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41', 'Michelin', 'MICH', 'Francia', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a42', 'Goodyear', 'GDYR', 'EEUU', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a43', 'Bridgestone', 'BDST', 'Japón', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12');
170	2025-04-20 01:42:55.552318-05	public	modelos_neumatico	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin	\N	\N	e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a51	\N	{"id": "e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a51", "medida": "295/80R22.5", "creado_en": "2025-04-20T01:42:55.552318-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "indice_carga": "152", "fabricante_id": "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41", "nombre_modelo": "X Multi Z", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": null, "indice_velocidad": "M", "permite_reencauche": true, "reencauches_maximos": 2, "presion_recomendada_psi": 120.00, "profundidad_original_mm": 18.00}	{"id": "e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a51", "medida": "295/80R22.5", "indice_carga": "152", "fabricante_id": "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41", "nombre_modelo": "X Multi Z", "patron_dibujo": null, "tipo_servicio": null, "indice_velocidad": "M", "permite_reencauche": true, "reencauches_maximos": 2, "presion_recomendada_psi": 120.00, "profundidad_original_mm": 18.00}	{"ip": null, "metodo": null, "endpoint": null}	INSERT INTO public.modelos_neumatico (id, fabricante_id, nombre_modelo, medida, indice_carga, indice_velocidad, profundidad_original_mm, presion_recomendada_psi, permite_reencauche, reencauches_maximos, creado_por) VALUES\n('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a51', 'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41', 'X Multi Z', '295/80R22.5', '152', 'M', 18.0, 120, true, 2, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a52', 'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41', 'X Line Energy D', '11R22.5', '146', 'L', 22.0, 110, true, 2, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a53', 'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a42', 'G667', '11R22.5', '146', 'L', 21.5, 110, true, 1, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a54', 'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a43', 'R268 Ecopia', '295/80R22.5', '152', 'M', 17.0, 120, true, 1, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12');
171	2025-04-20 01:42:55.552318-05	public	modelos_neumatico	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin	\N	\N	e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a52	\N	{"id": "e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a52", "medida": "11R22.5", "creado_en": "2025-04-20T01:42:55.552318-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "indice_carga": "146", "fabricante_id": "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41", "nombre_modelo": "X Line Energy D", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": null, "indice_velocidad": "L", "permite_reencauche": true, "reencauches_maximos": 2, "presion_recomendada_psi": 110.00, "profundidad_original_mm": 22.00}	{"id": "e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a52", "medida": "11R22.5", "indice_carga": "146", "fabricante_id": "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41", "nombre_modelo": "X Line Energy D", "patron_dibujo": null, "tipo_servicio": null, "indice_velocidad": "L", "permite_reencauche": true, "reencauches_maximos": 2, "presion_recomendada_psi": 110.00, "profundidad_original_mm": 22.00}	{"ip": null, "metodo": null, "endpoint": null}	INSERT INTO public.modelos_neumatico (id, fabricante_id, nombre_modelo, medida, indice_carga, indice_velocidad, profundidad_original_mm, presion_recomendada_psi, permite_reencauche, reencauches_maximos, creado_por) VALUES\n('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a51', 'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41', 'X Multi Z', '295/80R22.5', '152', 'M', 18.0, 120, true, 2, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a52', 'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41', 'X Line Energy D', '11R22.5', '146', 'L', 22.0, 110, true, 2, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a53', 'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a42', 'G667', '11R22.5', '146', 'L', 21.5, 110, true, 1, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a54', 'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a43', 'R268 Ecopia', '295/80R22.5', '152', 'M', 17.0, 120, true, 1, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12');
172	2025-04-20 01:42:55.552318-05	public	modelos_neumatico	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin	\N	\N	e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a53	\N	{"id": "e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a53", "medida": "11R22.5", "creado_en": "2025-04-20T01:42:55.552318-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "indice_carga": "146", "fabricante_id": "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a42", "nombre_modelo": "G667", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": null, "indice_velocidad": "L", "permite_reencauche": true, "reencauches_maximos": 1, "presion_recomendada_psi": 110.00, "profundidad_original_mm": 21.50}	{"id": "e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a53", "medida": "11R22.5", "indice_carga": "146", "fabricante_id": "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a42", "nombre_modelo": "G667", "patron_dibujo": null, "tipo_servicio": null, "indice_velocidad": "L", "permite_reencauche": true, "reencauches_maximos": 1, "presion_recomendada_psi": 110.00, "profundidad_original_mm": 21.50}	{"ip": null, "metodo": null, "endpoint": null}	INSERT INTO public.modelos_neumatico (id, fabricante_id, nombre_modelo, medida, indice_carga, indice_velocidad, profundidad_original_mm, presion_recomendada_psi, permite_reencauche, reencauches_maximos, creado_por) VALUES\n('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a51', 'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41', 'X Multi Z', '295/80R22.5', '152', 'M', 18.0, 120, true, 2, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a52', 'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41', 'X Line Energy D', '11R22.5', '146', 'L', 22.0, 110, true, 2, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a53', 'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a42', 'G667', '11R22.5', '146', 'L', 21.5, 110, true, 1, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a54', 'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a43', 'R268 Ecopia', '295/80R22.5', '152', 'M', 17.0, 120, true, 1, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12');
173	2025-04-20 01:42:55.552318-05	public	modelos_neumatico	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin	\N	\N	e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a54	\N	{"id": "e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a54", "medida": "295/80R22.5", "creado_en": "2025-04-20T01:42:55.552318-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "indice_carga": "152", "fabricante_id": "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a43", "nombre_modelo": "R268 Ecopia", "patron_dibujo": null, "tipo_servicio": null, "actualizado_en": null, "actualizado_por": null, "indice_velocidad": "M", "permite_reencauche": true, "reencauches_maximos": 1, "presion_recomendada_psi": 120.00, "profundidad_original_mm": 17.00}	{"id": "e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a54", "medida": "295/80R22.5", "indice_carga": "152", "fabricante_id": "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a43", "nombre_modelo": "R268 Ecopia", "patron_dibujo": null, "tipo_servicio": null, "indice_velocidad": "M", "permite_reencauche": true, "reencauches_maximos": 1, "presion_recomendada_psi": 120.00, "profundidad_original_mm": 17.00}	{"ip": null, "metodo": null, "endpoint": null}	INSERT INTO public.modelos_neumatico (id, fabricante_id, nombre_modelo, medida, indice_carga, indice_velocidad, profundidad_original_mm, presion_recomendada_psi, permite_reencauche, reencauches_maximos, creado_por) VALUES\n('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a51', 'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41', 'X Multi Z', '295/80R22.5', '152', 'M', 18.0, 120, true, 2, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a52', 'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41', 'X Line Energy D', '11R22.5', '146', 'L', 22.0, 110, true, 2, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a53', 'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a42', 'G667', '11R22.5', '146', 'L', 21.5, 110, true, 1, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a54', 'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a43', 'R268 Ecopia', '295/80R22.5', '152', 'M', 17.0, 120, true, 1, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12');
174	2025-04-20 01:42:55.552318-05	public	tipos_vehiculo	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin	\N	\N	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a61	\N	{"id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a61", "activo": true, "nombre": "Tractocamión 6x4", "subtipo": null, "creado_en": "2025-04-20T01:42:55.552318-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "descripcion": null, "ejes_standard": 3, "actualizado_en": null, "actualizado_por": null, "categoria_principal": "Camión"}	{"id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a61", "activo": true, "nombre": "Tractocamión 6x4", "subtipo": null, "descripcion": null, "ejes_standard": 3, "categoria_principal": "Camión"}	{"ip": null, "metodo": null, "endpoint": null}	INSERT INTO public.tipos_vehiculo (id, nombre, categoria_principal, ejes_standard, activo, creado_por) VALUES\n('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a61', 'Tractocamión 6x4', 'Camión', 3, true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a62', 'Remolque Cama Baja 3 Ejes', 'Remolque', 3, true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a63', 'Bus Interprovincial 4x2', 'Autobús', 2, true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12');
175	2025-04-20 01:42:55.552318-05	public	tipos_vehiculo	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin	\N	\N	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a62	\N	{"id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a62", "activo": true, "nombre": "Remolque Cama Baja 3 Ejes", "subtipo": null, "creado_en": "2025-04-20T01:42:55.552318-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "descripcion": null, "ejes_standard": 3, "actualizado_en": null, "actualizado_por": null, "categoria_principal": "Remolque"}	{"id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a62", "activo": true, "nombre": "Remolque Cama Baja 3 Ejes", "subtipo": null, "descripcion": null, "ejes_standard": 3, "categoria_principal": "Remolque"}	{"ip": null, "metodo": null, "endpoint": null}	INSERT INTO public.tipos_vehiculo (id, nombre, categoria_principal, ejes_standard, activo, creado_por) VALUES\n('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a61', 'Tractocamión 6x4', 'Camión', 3, true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a62', 'Remolque Cama Baja 3 Ejes', 'Remolque', 3, true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a63', 'Bus Interprovincial 4x2', 'Autobús', 2, true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12');
176	2025-04-20 01:42:55.552318-05	public	tipos_vehiculo	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin	\N	\N	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a63	\N	{"id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a63", "activo": true, "nombre": "Bus Interprovincial 4x2", "subtipo": null, "creado_en": "2025-04-20T01:42:55.552318-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "descripcion": null, "ejes_standard": 2, "actualizado_en": null, "actualizado_por": null, "categoria_principal": "Autobús"}	{"id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a63", "activo": true, "nombre": "Bus Interprovincial 4x2", "subtipo": null, "descripcion": null, "ejes_standard": 2, "categoria_principal": "Autobús"}	{"ip": null, "metodo": null, "endpoint": null}	INSERT INTO public.tipos_vehiculo (id, nombre, categoria_principal, ejes_standard, activo, creado_por) VALUES\n('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a61', 'Tractocamión 6x4', 'Camión', 3, true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a62', 'Remolque Cama Baja 3 Ejes', 'Remolque', 3, true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a63', 'Bus Interprovincial 4x2', 'Autobús', 2, true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12');
177	2025-04-20 01:42:55.552318-05	public	vehiculos	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin	\N	\N	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a91	\N	{"id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a91", "vin": null, "marca": "Volvo", "notas": null, "placa": "ABC-123", "activo": true, "creado_en": "2025-04-20T01:42:55.552318-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "fecha_alta": "2025-04-20", "fecha_baja": null, "actualizado_en": null, "actualizado_por": null, "modelo_vehiculo": null, "odometro_actual": null, "anio_fabricacion": null, "numero_economico": "T-01", "tipo_vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a61", "ubicacion_actual": null, "fecha_ultimo_odometro": null}	{"id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a91", "vin": null, "marca": "Volvo", "notas": null, "placa": "ABC-123", "activo": true, "fecha_alta": "2025-04-20", "fecha_baja": null, "modelo_vehiculo": null, "odometro_actual": null, "anio_fabricacion": null, "numero_economico": "T-01", "tipo_vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a61", "ubicacion_actual": null, "fecha_ultimo_odometro": null}	{"ip": null, "metodo": null, "endpoint": null}	INSERT INTO public.vehiculos (id, tipo_vehiculo_id, placa, numero_economico, marca, activo, creado_por) VALUES\n('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a91', 'f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a61', 'ABC-123', 'T-01', 'Volvo', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a92', 'f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a61', 'DEF-456', 'T-02', 'Scania', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a93', 'f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a62', 'REM-789', 'R-05', 'Schmitz', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12')\nON CONFLICT (id) DO NOTHING;
178	2025-04-20 01:42:55.552318-05	public	vehiculos	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin	\N	\N	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a92	\N	{"id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a92", "vin": null, "marca": "Scania", "notas": null, "placa": "DEF-456", "activo": true, "creado_en": "2025-04-20T01:42:55.552318-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "fecha_alta": "2025-04-20", "fecha_baja": null, "actualizado_en": null, "actualizado_por": null, "modelo_vehiculo": null, "odometro_actual": null, "anio_fabricacion": null, "numero_economico": "T-02", "tipo_vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a61", "ubicacion_actual": null, "fecha_ultimo_odometro": null}	{"id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a92", "vin": null, "marca": "Scania", "notas": null, "placa": "DEF-456", "activo": true, "fecha_alta": "2025-04-20", "fecha_baja": null, "modelo_vehiculo": null, "odometro_actual": null, "anio_fabricacion": null, "numero_economico": "T-02", "tipo_vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a61", "ubicacion_actual": null, "fecha_ultimo_odometro": null}	{"ip": null, "metodo": null, "endpoint": null}	INSERT INTO public.vehiculos (id, tipo_vehiculo_id, placa, numero_economico, marca, activo, creado_por) VALUES\n('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a91', 'f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a61', 'ABC-123', 'T-01', 'Volvo', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a92', 'f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a61', 'DEF-456', 'T-02', 'Scania', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a93', 'f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a62', 'REM-789', 'R-05', 'Schmitz', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12')\nON CONFLICT (id) DO NOTHING;
179	2025-04-20 01:42:55.552318-05	public	vehiculos	INSERT	postgres	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin	\N	\N	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a93	\N	{"id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a93", "vin": null, "marca": "Schmitz", "notas": null, "placa": "REM-789", "activo": true, "creado_en": "2025-04-20T01:42:55.552318-05:00", "creado_por": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", "fecha_alta": "2025-04-20", "fecha_baja": null, "actualizado_en": null, "actualizado_por": null, "modelo_vehiculo": null, "odometro_actual": null, "anio_fabricacion": null, "numero_economico": "R-05", "tipo_vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a62", "ubicacion_actual": null, "fecha_ultimo_odometro": null}	{"id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a93", "vin": null, "marca": "Schmitz", "notas": null, "placa": "REM-789", "activo": true, "fecha_alta": "2025-04-20", "fecha_baja": null, "modelo_vehiculo": null, "odometro_actual": null, "anio_fabricacion": null, "numero_economico": "R-05", "tipo_vehiculo_id": "f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a62", "ubicacion_actual": null, "fecha_ultimo_odometro": null}	{"ip": null, "metodo": null, "endpoint": null}	INSERT INTO public.vehiculos (id, tipo_vehiculo_id, placa, numero_economico, marca, activo, creado_por) VALUES\n('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a91', 'f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a61', 'ABC-123', 'T-01', 'Volvo', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a92', 'f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a61', 'DEF-456', 'T-02', 'Scania', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12'),\n('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a93', 'f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a62', 'REM-789', 'R-05', 'Schmitz', true, 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12')\nON CONFLICT (id) DO NOTHING;
\.


--
-- Data for Name: configuraciones_eje; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.configuraciones_eje (id, tipo_vehiculo_id, numero_eje, nombre_eje, tipo_eje, numero_posiciones, posiciones_duales, permite_reencauchados, neumaticos_por_posicion, creado_en, actualizado_en) FROM stdin;
f1eebc99-9c0b-4ef8-bb6d-6bb9bd380a71	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a61	1	Eje Delantero Direccional	DIRECCION	2	f	t	1	2025-04-20 01:42:55.552318-05	\N
f1eebc99-9c0b-4ef8-bb6d-6bb9bd380a72	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a61	2	Eje Trasero Motriz 1	TRACCION	4	t	t	2	2025-04-20 01:42:55.552318-05	\N
f1eebc99-9c0b-4ef8-bb6d-6bb9bd380a73	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a61	3	Eje Trasero Motriz 2	TRACCION	4	t	t	2	2025-04-20 01:42:55.552318-05	\N
4439899c-3fdf-4686-8c0d-4c2310d3cb58	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a62	1	Eje Remolque 1	ARRASTRE	4	t	t	2	2025-04-20 01:42:55.552318-05	\N
9669f9c4-2598-45ed-be0a-067610ac837f	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a62	2	Eje Remolque 2	ARRASTRE	4	t	t	2	2025-04-20 01:42:55.552318-05	\N
153f5255-fb72-42f6-af30-e2f37e1f61b9	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a62	3	Eje Remolque 3	ARRASTRE	4	t	t	2	2025-04-20 01:42:55.552318-05	\N
bbcce00c-5861-45db-9531-96277ae8e5e2	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a63	1	Eje Delantero Bus Direccional	DIRECCION	2	f	t	1	2025-04-20 01:42:55.552318-05	\N
7c15a421-0841-4748-9f92-e26dd0910073	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a63	2	Eje Trasero Bus Traccion	TRACCION	4	t	t	2	2025-04-20 01:42:55.552318-05	\N
\.


--
-- Data for Name: eventos_neumaticos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.eventos_neumaticos (id, neumatico_id, tipo_evento, timestamp_evento, usuario_id, vehiculo_id, posicion_id, odometro_vehiculo_en_evento, profundidad_remanente_mm, presion_psi, costo_evento, moneda_costo, proveedor_servicio_id, notas, destino_desmontaje, motivo_desecho_id_evento, profundidad_post_reencauche_mm, datos_evento, relacion_evento_anterior, creado_en) FROM stdin;
6ca32135-adbc-4db8-bf80-f3f0b434050f	22222222-2222-2222-2222-222222222222	INSTALACION	2025-04-20 22:34:17.514742-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a92	f2eebc99-9c0b-4ef8-bb6d-6bb9bd380a81	40000	\N	\N	\N	PEN	\N	Instalacion de neumatico nuevo 222 via API	\N	\N	\N	null	\N	2025-04-20 22:34:17.535471-05
635f3b81-066e-4ddc-858e-198dee57f678	22222222-2222-2222-2222-222222222222	INSPECCION	2025-04-21 08:52:03.910273-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a92	f2eebc99-9c0b-4ef8-bb6d-6bb9bd380a81	45000	21.50	118.00	\N	PEN	\N	Primera inspeccion neumatico 222 via API	\N	\N	\N	null	\N	2025-04-21 08:52:03.933375-05
f7111ffe-04c3-4bee-bec4-f19ab7658284	22222222-2222-2222-2222-222222222222	INSTALACION	2025-04-21 10:10:48.182741-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a92	f2eebc99-9c0b-4ef8-bb6d-6bb9bd380a81	40000	\N	\N	\N	PEN	\N	Instalacion de neumatico nuevo 222 via API	\N	\N	\N	null	\N	2025-04-21 10:10:48.202982-05
7603a649-d645-46ef-a8ed-fda5548c9251	22222222-2222-2222-2222-222222222222	INSPECCION	2025-04-21 10:20:23.258147-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a92	f2eebc99-9c0b-4ef8-bb6d-6bb9bd380a81	45000	21.50	118.00	\N	PEN	\N	Primera inspeccion neumatico 222 via API	\N	\N	\N	null	\N	2025-04-21 10:20:23.261491-05
0a265063-607a-4a49-addf-d180bf56de84	22222222-2222-2222-2222-222222222222	DESMONTAJE	2025-04-21 10:29:59.183632-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a92	f2eebc99-9c0b-4ef8-bb6d-6bb9bd380a81	52000	\N	\N	\N	PEN	\N	Desmontaje via API para devolver a stock	EN_STOCK	\N	\N	null	\N	2025-04-21 10:29:59.186366-05
e6cb379a-d5f7-4b32-8c20-c3ea574e7a0d	22222222-2222-2222-2222-222222222222	INSTALACION	2025-04-22 14:18:58.685492-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a92	f2eebc99-9c0b-4ef8-bb6d-6bb9bd380a81	40000	\N	\N	\N	PEN	\N	Instalacion de neumatico nuevo 222 via API	\N	\N	\N	null	\N	2025-04-22 14:18:58.706519-05
e81ed129-6ab9-407c-ab04-a0f055561823	22222222-2222-2222-2222-222222222222	DESMONTAJE	2025-04-23 09:29:24.072018-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a92	f2eebc99-9c0b-4ef8-bb6d-6bb9bd380a81	52000	\N	\N	\N	PEN	\N	Desmontaje via API para devolver a stock (Prueba)	EN_STOCK	\N	\N	null	\N	2025-04-23 09:29:24.07778-05
\.


--
-- Data for Name: fabricantes_neumatico; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fabricantes_neumatico (id, nombre, codigo_abreviado, pais_origen, sitio_web, activo, creado_en, creado_por, actualizado_en, actualizado_por) FROM stdin;
d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41	Michelin	MICH	Francia	\N	t	2025-04-20 01:42:55.552318-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a42	Goodyear	GDYR	EEUU	\N	t	2025-04-20 01:42:55.552318-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a43	Bridgestone	BDST	Japón	\N	t	2025-04-20 01:42:55.552318-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
\.


--
-- Data for Name: modelos_neumatico; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.modelos_neumatico (id, fabricante_id, nombre_modelo, medida, indice_carga, indice_velocidad, profundidad_original_mm, presion_recomendada_psi, permite_reencauche, reencauches_maximos, patron_dibujo, tipo_servicio, creado_en, creado_por, actualizado_en, actualizado_por) FROM stdin;
e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a51	d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41	X Multi Z	295/80R22.5	152	M	18.00	120.00	t	2	\N	\N	2025-04-20 01:42:55.552318-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a52	d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41	X Line Energy D	11R22.5	146	L	22.00	110.00	t	2	\N	\N	2025-04-20 01:42:55.552318-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a53	d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a42	G667	11R22.5	146	L	21.50	110.00	t	1	\N	\N	2025-04-20 01:42:55.552318-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a54	d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a43	R268 Ecopia	295/80R22.5	152	M	17.00	120.00	t	1	\N	\N	2025-04-20 01:42:55.552318-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
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
c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a31	BAJOREM	Bajo remanente de banda	f	t	2025-04-20 01:42:55.552318-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a32	GOLPCAS	Golpe en carcasa / Rotura	f	t	2025-04-20 01:42:55.552318-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33	DESGIRR	Desgaste irregular severo	f	t	2025-04-20 01:42:55.552318-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a34	VEJEZ	Envejecimiento / Cristalización	f	t	2025-04-20 01:42:55.552318-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
\.


--
-- Data for Name: neumaticos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.neumaticos (id, numero_serie, dot, modelo_id, fecha_compra, fecha_fabricacion, costo_compra, moneda_compra, proveedor_compra_id, es_reencauchado, vida_actual, estado_actual, ubicacion_actual_vehiculo_id, ubicacion_actual_posicion_id, fecha_ultimo_evento, profundidad_inicial_mm, kilometraje_acumulado, reencauches_realizados, fecha_desecho, motivo_desecho_id, creado_en, creado_por, actualizado_en, actualizado_por, ubicacion_almacen_id, sensor_id, garantia_proveedor_id, garantia_fecha_inicio, garantia_km, garantia_meses, garantia_condiciones_url) FROM stdin;
22222222-2222-2222-2222-222222222222	SERIE456TEST	CDCD3024	e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a52	2025-04-20	\N	610.00	PEN	b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21	f	1	EN_STOCK	\N	\N	2025-04-23 09:29:24.072018-05	22.00	12000	0	\N	\N	2025-04-20 15:43:03.533994-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	2025-04-23 09:29:24.072018-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	\N	SENSOR_XYZ_123	b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21	2025-04-01	80000	24	http://example.com/garantia/llantas-sur
\.


--
-- Data for Name: parametros_inventario; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.parametros_inventario (id, parametro_tipo, modelo_id, ubicacion_almacen_id, valor_numerico, valor_texto, activo, notas, creado_en, creado_por, actualizado_en, actualizado_por) FROM stdin;
\.


--
-- Data for Name: posiciones_neumatico; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.posiciones_neumatico (id, configuracion_eje_id, codigo_posicion, etiqueta_posicion, lado, posicion_relativa, es_interna, es_direccion, es_traccion, requiere_neumatico_especifico, creado_en, actualizado_en) FROM stdin;
f2eebc99-9c0b-4ef8-bb6d-6bb9bd380a81	f1eebc99-9c0b-4ef8-bb6d-6bb9bd380a71	1LI	Delantera Izquierda	IZQUIERDO	1	f	t	f	f	2025-04-20 01:42:55.552318-05	\N
f2eebc99-9c0b-4ef8-bb6d-6bb9bd380a82	f1eebc99-9c0b-4ef8-bb6d-6bb9bd380a71	1LD	Delantera Derecha	DERECHO	1	f	t	f	f	2025-04-20 01:42:55.552318-05	\N
f2eebc99-9c0b-4ef8-bb6d-6bb9bd380a83	f1eebc99-9c0b-4ef8-bb6d-6bb9bd380a72	2LIE	Trasera 1 Izquierda Externa	IZQUIERDO	1	f	f	t	f	2025-04-20 01:42:55.552318-05	\N
f2eebc99-9c0b-4ef8-bb6d-6bb9bd380a84	f1eebc99-9c0b-4ef8-bb6d-6bb9bd380a72	2LII	Trasera 1 Izquierda Interna	IZQUIERDO	2	t	f	t	f	2025-04-20 01:42:55.552318-05	\N
f2eebc99-9c0b-4ef8-bb6d-6bb9bd380a85	f1eebc99-9c0b-4ef8-bb6d-6bb9bd380a72	2RDE	Trasera 1 Derecha Externa	DERECHO	1	f	f	t	f	2025-04-20 01:42:55.552318-05	\N
f2eebc99-9c0b-4ef8-bb6d-6bb9bd380a86	f1eebc99-9c0b-4ef8-bb6d-6bb9bd380a72	2RDI	Trasera 1 Derecha Interna	DERECHO	2	t	f	t	f	2025-04-20 01:42:55.552318-05	\N
f2eebc99-9c0b-4ef8-bb6d-6bb9bd380a87	f1eebc99-9c0b-4ef8-bb6d-6bb9bd380a73	3LIE	Trasera 2 Izquierda Externa	IZQUIERDO	1	f	f	t	f	2025-04-20 01:42:55.552318-05	\N
f2eebc99-9c0b-4ef8-bb6d-6bb9bd380a88	f1eebc99-9c0b-4ef8-bb6d-6bb9bd380a73	3LII	Trasera 2 Izquierda Interna	IZQUIERDO	2	t	f	t	f	2025-04-20 01:42:55.552318-05	\N
f2eebc99-9c0b-4ef8-bb6d-6bb9bd380a89	f1eebc99-9c0b-4ef8-bb6d-6bb9bd380a73	3RDE	Trasera 2 Derecha Externa	DERECHO	1	f	f	t	f	2025-04-20 01:42:55.552318-05	\N
f2eebc99-9c0b-4ef8-bb6d-6bb9bd380a8a	f1eebc99-9c0b-4ef8-bb6d-6bb9bd380a73	3RDI	Trasera 2 Derecha Interna	DERECHO	2	t	f	t	f	2025-04-20 01:42:55.552318-05	\N
\.


--
-- Data for Name: proveedores; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.proveedores (id, nombre, tipo, rfc, contacto_principal, telefono, email, direccion, activo, creado_en, creado_por, actualizado_en, actualizado_por) FROM stdin;
b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21	Llantas del Sur S.A.C.	DISTRIBUIDOR	20123456789	\N	\N	\N	\N	t	2025-04-20 01:42:55.552318-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22	Reencauchadora El Condor E.I.R.L.	SERVICIO_REENCAUCHE	10987654321	\N	\N	\N	\N	t	2025-04-20 01:42:55.552318-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a23	Reparaciones Viales Andinas	SERVICIO_REPARACION	20555666777	\N	\N	\N	\N	t	2025-04-20 01:42:55.552318-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
\.


--
-- Data for Name: registros_odometro; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.registros_odometro (id, vehiculo_id, odometro, fecha_medicion, fuente, creado_por, notas) FROM stdin;
\.


--
-- Data for Name: tipos_vehiculo; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tipos_vehiculo (id, nombre, descripcion, categoria_principal, subtipo, ejes_standard, activo, creado_en, creado_por, actualizado_en, actualizado_por) FROM stdin;
f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a61	Tractocamión 6x4	\N	Camión	\N	3	t	2025-04-20 01:42:55.552318-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a62	Remolque Cama Baja 3 Ejes	\N	Remolque	\N	3	t	2025-04-20 01:42:55.552318-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a63	Bus Interprovincial 4x2	\N	Autobús	\N	2	t	2025-04-20 01:42:55.552318-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuarios (id, username, nombre_completo, email, password_hash, rol, activo, creado_en, creado_por, actualizado_en, actualizado_por) FROM stdin;
a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	admin	Admin Principal	admin@tuempresa.com	$2a$06$X93kYLu1ZGz.jhaMYrg4NO86nCUGCzkU8hWKli4sFTaZE9b.zFrlW	ADMIN	t	2025-04-20 01:42:55.552318-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12
a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	operador01	Juan Perez	jperez@tuempresa.com	$2a$06$oJbb7TRwbqNT.F6WYwBUiuh5TFPYGXXt.KXso36eL3AlvQxYp0nVW	OPERADOR	t	2025-04-20 01:42:55.552318-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13	supervisor01	Maria Garcia	mgarcia@tuempresa.com	$2a$06$mYXk.CtFJ/Xo/LYtIAyVoeQQnt15zoxIIPyyXk8lYj99C7mp2v9Iy	GESTOR	t	2025-04-20 01:42:55.552318-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
\.


--
-- Data for Name: vehiculos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vehiculos (id, tipo_vehiculo_id, placa, vin, numero_economico, marca, modelo_vehiculo, anio_fabricacion, fecha_alta, fecha_baja, activo, odometro_actual, fecha_ultimo_odometro, ubicacion_actual, notas, creado_en, creado_por, actualizado_en, actualizado_por) FROM stdin;
f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a91	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a61	ABC-123	\N	T-01	Volvo	\N	\N	2025-04-20	\N	t	\N	\N	\N	\N	2025-04-20 01:42:55.552318-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a92	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a61	DEF-456	\N	T-02	Scania	\N	\N	2025-04-20	\N	t	\N	\N	\N	\N	2025-04-20 01:42:55.552318-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a93	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a62	REM-789	\N	R-05	Schmitz	\N	\N	2025-04-20	\N	t	\N	\N	\N	\N	2025-04-20 01:42:55.552318-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12	\N	\N
acd03201-8723-4718-8edb-840eadd3d13f	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a63	XYZ-789	VINBUS101XYZ	B-101	Mercedes Benz	O500	2022	2025-04-21	\N	t	\N	\N	\N	Vehículo Bus creado vía API	2025-04-21 13:36:22.658244-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	\N	\N
35b22fe3-6b2f-45ee-af5a-bbe75ed50210	f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a63	XYZ-102	VINBUS102XYZ	B-102	Freightliner	O500	2023	2025-04-22	2025-04-22	f	\N	\N	\N	Marca actualizada y nota añadida vía API PUT	2025-04-22 09:59:50.664383-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11	2025-04-22 16:00:56.755693-05	a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11
\.


--
-- Name: auditoria_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auditoria_log_id_seq', 193, true);


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
-- Name: configuraciones_eje configuraciones_eje_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.configuraciones_eje
    ADD CONSTRAINT configuraciones_eje_pkey PRIMARY KEY (id);


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
-- Name: modelos_neumatico modelos_neumatico_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modelos_neumatico
    ADD CONSTRAINT modelos_neumatico_pkey PRIMARY KEY (id);


--
-- Name: modelos_posiciones_permitidas modelos_posiciones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modelos_posiciones_permitidas
    ADD CONSTRAINT modelos_posiciones_pkey PRIMARY KEY (modelo_neumatico_id, posicion_neumatico_id);


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
-- Name: registros_odometro registros_odometro_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registros_odometro
    ADD CONSTRAINT registros_odometro_pkey PRIMARY KEY (id);


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
-- Name: posiciones_neumatico uq_posicion_neumatico; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posiciones_neumatico
    ADD CONSTRAINT uq_posicion_neumatico UNIQUE (configuracion_eje_id, codigo_posicion);


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
-- Name: idx_alertas_neumatico; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_alertas_neumatico ON public.alertas USING btree (neumatico_id) WHERE (neumatico_id IS NOT NULL);


--
-- Name: idx_alertas_tipo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_alertas_tipo ON public.alertas USING btree (tipo_alerta);


--
-- Name: idx_alertas_vehiculo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_alertas_vehiculo ON public.alertas USING btree (vehiculo_id) WHERE (vehiculo_id IS NOT NULL);


--
-- Name: idx_auditoria_entidad; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_auditoria_entidad ON public.auditoria_log USING btree (id_entidad) WHERE (id_entidad IS NOT NULL);


--
-- Name: idx_auditoria_operacion; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_auditoria_operacion ON public.auditoria_log USING btree (operacion);


--
-- Name: idx_auditoria_tabla; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_auditoria_tabla ON public.auditoria_log USING btree (esquema_tabla, nombre_tabla);


--
-- Name: idx_auditoria_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_auditoria_timestamp ON public.auditoria_log USING btree (timestamp_log DESC);


--
-- Name: idx_auditoria_usuario_app; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_auditoria_usuario_app ON public.auditoria_log USING btree (usuario_aplicacion_id) WHERE (usuario_aplicacion_id IS NOT NULL);


--
-- Name: idx_eventos_motivo_desecho; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_eventos_motivo_desecho ON public.eventos_neumaticos USING btree (motivo_desecho_id_evento);


--
-- Name: idx_eventos_neumatico; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_eventos_neumatico ON public.eventos_neumaticos USING btree (neumatico_id);


--
-- Name: idx_eventos_proveedor; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_eventos_proveedor ON public.eventos_neumaticos USING btree (proveedor_servicio_id);


--
-- Name: idx_eventos_relacion; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_eventos_relacion ON public.eventos_neumaticos USING btree (relacion_evento_anterior) WHERE (relacion_evento_anterior IS NOT NULL);


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
-- Name: idx_eventos_vehiculo_posicion; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_eventos_vehiculo_posicion ON public.eventos_neumaticos USING btree (vehiculo_id, posicion_id) WHERE (vehiculo_id IS NOT NULL);


--
-- Name: idx_fabricantes_nombre_unique; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_fabricantes_nombre_unique ON public.fabricantes_neumatico USING btree (public.f_immutable_lower_unaccent((nombre)::text)) WHERE (activo = true);


--
-- Name: idx_modelos_fabricante; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_modelos_fabricante ON public.modelos_neumatico USING btree (fabricante_id);


--
-- Name: idx_modelos_unique; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_modelos_unique ON public.modelos_neumatico USING btree (fabricante_id, public.f_immutable_lower_unaccent((nombre_modelo)::text), medida) WHERE (fabricante_id IS NOT NULL);


--
-- Name: idx_neumaticos_dot; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_neumaticos_dot ON public.neumaticos USING btree (dot) WHERE (dot IS NOT NULL);


--
-- Name: idx_neumaticos_estado; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_neumaticos_estado ON public.neumaticos USING btree (estado_actual);


--
-- Name: idx_neumaticos_garantia_proveedor; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_neumaticos_garantia_proveedor ON public.neumaticos USING btree (garantia_proveedor_id) WHERE (garantia_proveedor_id IS NOT NULL);


--
-- Name: idx_neumaticos_modelo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_neumaticos_modelo ON public.neumaticos USING btree (modelo_id);


--
-- Name: idx_neumaticos_motivo_desecho; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_neumaticos_motivo_desecho ON public.neumaticos USING btree (motivo_desecho_id);


--
-- Name: idx_neumaticos_proveedor; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_neumaticos_proveedor ON public.neumaticos USING btree (proveedor_compra_id);


--
-- Name: idx_neumaticos_serie; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_neumaticos_serie ON public.neumaticos USING btree (numero_serie) WHERE (numero_serie IS NOT NULL);


--
-- Name: idx_neumaticos_ubicacion; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_neumaticos_ubicacion ON public.neumaticos USING btree (ubicacion_actual_vehiculo_id, ubicacion_actual_posicion_id) WHERE (ubicacion_actual_vehiculo_id IS NOT NULL);


--
-- Name: idx_neumaticos_ubicacion_almacen; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_neumaticos_ubicacion_almacen ON public.neumaticos USING btree (ubicacion_almacen_id) WHERE (ubicacion_almacen_id IS NOT NULL);


--
-- Name: idx_param_inv_tipo_modelo_ubicacion; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_param_inv_tipo_modelo_ubicacion ON public.parametros_inventario USING btree (parametro_tipo, modelo_id, ubicacion_almacen_id) WHERE (activo = true);


--
-- Name: idx_proveedores_nombre_unique; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_proveedores_nombre_unique ON public.proveedores USING btree (public.f_immutable_lower_unaccent((nombre)::text)) WHERE (activo = true);


--
-- Name: idx_registros_odometro_vehiculo_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_registros_odometro_vehiculo_fecha ON public.registros_odometro USING btree (vehiculo_id, fecha_medicion DESC);


--
-- Name: idx_tipos_vehiculo_nombre; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_tipos_vehiculo_nombre ON public.tipos_vehiculo USING btree (public.f_immutable_lower_unaccent((nombre)::text)) WHERE (activo = true);


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
-- Name: INDEX uq_idx_neumatico_dot_vida; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON INDEX public.uq_idx_neumatico_dot_vida IS 'Asegura que la combinación DOT y vida sea única cuando DOT no es nulo.';


--
-- Name: eventos_neumaticos trg_actualizar_estado_neumatico; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_actualizar_estado_neumatico AFTER INSERT ON public.eventos_neumaticos FOR EACH ROW EXECUTE FUNCTION public.fn_actualizar_estado_neumatico();


--
-- Name: registros_odometro trg_actualizar_odometro; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_actualizar_odometro AFTER INSERT ON public.registros_odometro FOR EACH ROW EXECUTE FUNCTION public.fn_actualizar_odometro_vehiculo();


--
-- Name: alertas trg_auditoria_alertas; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_auditoria_alertas AFTER INSERT OR DELETE OR UPDATE ON public.alertas FOR EACH ROW EXECUTE FUNCTION public.fn_auditoria_registro();


--
-- Name: TRIGGER trg_auditoria_alertas ON alertas; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TRIGGER trg_auditoria_alertas ON public.alertas IS 'Activa el registro de auditoría para la tabla de alertas.';


--
-- Name: almacenes trg_auditoria_almacenes; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_auditoria_almacenes AFTER INSERT OR DELETE OR UPDATE ON public.almacenes FOR EACH ROW EXECUTE FUNCTION public.fn_auditoria_registro();


--
-- Name: fabricantes_neumatico trg_auditoria_fabricantes; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_auditoria_fabricantes AFTER INSERT OR DELETE OR UPDATE ON public.fabricantes_neumatico FOR EACH ROW EXECUTE FUNCTION public.fn_auditoria_registro();


--
-- Name: modelos_neumatico trg_auditoria_modelos; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_auditoria_modelos AFTER INSERT OR DELETE OR UPDATE ON public.modelos_neumatico FOR EACH ROW EXECUTE FUNCTION public.fn_auditoria_registro();


--
-- Name: motivos_desecho trg_auditoria_motivos_desecho; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_auditoria_motivos_desecho AFTER INSERT OR DELETE OR UPDATE ON public.motivos_desecho FOR EACH ROW EXECUTE FUNCTION public.fn_auditoria_registro();


--
-- Name: neumaticos trg_auditoria_neumaticos; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_auditoria_neumaticos AFTER INSERT OR DELETE OR UPDATE ON public.neumaticos FOR EACH ROW EXECUTE FUNCTION public.fn_auditoria_registro();


--
-- Name: registros_odometro trg_auditoria_odometros; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_auditoria_odometros AFTER INSERT OR DELETE OR UPDATE ON public.registros_odometro FOR EACH ROW EXECUTE FUNCTION public.fn_auditoria_registro();


--
-- Name: parametros_inventario trg_auditoria_parametros_inv; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_auditoria_parametros_inv AFTER INSERT OR DELETE OR UPDATE ON public.parametros_inventario FOR EACH ROW EXECUTE FUNCTION public.fn_auditoria_registro();


--
-- Name: proveedores trg_auditoria_proveedores; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_auditoria_proveedores AFTER INSERT OR DELETE OR UPDATE ON public.proveedores FOR EACH ROW EXECUTE FUNCTION public.fn_auditoria_registro();


--
-- Name: tipos_vehiculo trg_auditoria_tipos_vehiculo; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_auditoria_tipos_vehiculo AFTER INSERT OR DELETE OR UPDATE ON public.tipos_vehiculo FOR EACH ROW EXECUTE FUNCTION public.fn_auditoria_registro();


--
-- Name: usuarios trg_auditoria_usuarios; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_auditoria_usuarios AFTER INSERT OR DELETE OR UPDATE ON public.usuarios FOR EACH ROW EXECUTE FUNCTION public.fn_auditoria_registro();


--
-- Name: vehiculos trg_auditoria_vehiculos; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_auditoria_vehiculos AFTER INSERT OR DELETE OR UPDATE ON public.vehiculos FOR EACH ROW EXECUTE FUNCTION public.fn_auditoria_registro();


--
-- Name: modelos_posiciones_permitidas trg_validar_modelo_posicion; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_validar_modelo_posicion BEFORE INSERT OR UPDATE ON public.modelos_posiciones_permitidas FOR EACH ROW EXECUTE FUNCTION public.fn_validar_modelo_posicion();


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
-- Name: almacenes fk_almacenes_actualizado_por; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.almacenes
    ADD CONSTRAINT fk_almacenes_actualizado_por FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: almacenes fk_almacenes_creado_por; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.almacenes
    ADD CONSTRAINT fk_almacenes_creado_por FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: auditoria_log fk_auditlog_usuario_app; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auditoria_log
    ADD CONSTRAINT fk_auditlog_usuario_app FOREIGN KEY (usuario_aplicacion_id) REFERENCES public.usuarios(id) ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;


--
-- Name: CONSTRAINT fk_auditlog_usuario_app ON auditoria_log; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON CONSTRAINT fk_auditlog_usuario_app ON public.auditoria_log IS 'FK a usuarios, diferida para permitir auditar inserciones en usuarios.';


--
-- Name: configuraciones_eje fk_configuraciones_tipo_vehiculo; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.configuraciones_eje
    ADD CONSTRAINT fk_configuraciones_tipo_vehiculo FOREIGN KEY (tipo_vehiculo_id) REFERENCES public.tipos_vehiculo(id) ON DELETE RESTRICT;


--
-- Name: eventos_neumaticos fk_eventos_motivo_desecho; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eventos_neumaticos
    ADD CONSTRAINT fk_eventos_motivo_desecho FOREIGN KEY (motivo_desecho_id_evento) REFERENCES public.motivos_desecho(id) ON DELETE RESTRICT;


--
-- Name: eventos_neumaticos fk_eventos_neumatico; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eventos_neumaticos
    ADD CONSTRAINT fk_eventos_neumatico FOREIGN KEY (neumatico_id) REFERENCES public.neumaticos(id) ON DELETE RESTRICT;


--
-- Name: eventos_neumaticos fk_eventos_posicion; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eventos_neumaticos
    ADD CONSTRAINT fk_eventos_posicion FOREIGN KEY (posicion_id) REFERENCES public.posiciones_neumatico(id) ON DELETE SET NULL;


--
-- Name: eventos_neumaticos fk_eventos_proveedor_servicio; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eventos_neumaticos
    ADD CONSTRAINT fk_eventos_proveedor_servicio FOREIGN KEY (proveedor_servicio_id) REFERENCES public.proveedores(id) ON DELETE SET NULL;


--
-- Name: eventos_neumaticos fk_eventos_relacion_anterior; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eventos_neumaticos
    ADD CONSTRAINT fk_eventos_relacion_anterior FOREIGN KEY (relacion_evento_anterior) REFERENCES public.eventos_neumaticos(id) ON DELETE SET NULL;


--
-- Name: eventos_neumaticos fk_eventos_usuario; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eventos_neumaticos
    ADD CONSTRAINT fk_eventos_usuario FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE RESTRICT;


--
-- Name: eventos_neumaticos fk_eventos_vehiculo; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eventos_neumaticos
    ADD CONSTRAINT fk_eventos_vehiculo FOREIGN KEY (vehiculo_id) REFERENCES public.vehiculos(id) ON DELETE SET NULL;


--
-- Name: fabricantes_neumatico fk_fabricantes_actualizado_por; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fabricantes_neumatico
    ADD CONSTRAINT fk_fabricantes_actualizado_por FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: fabricantes_neumatico fk_fabricantes_creado_por; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fabricantes_neumatico
    ADD CONSTRAINT fk_fabricantes_creado_por FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: modelos_neumatico fk_modelos_actualizado_por; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modelos_neumatico
    ADD CONSTRAINT fk_modelos_actualizado_por FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: modelos_neumatico fk_modelos_creado_por; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modelos_neumatico
    ADD CONSTRAINT fk_modelos_creado_por FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: modelos_neumatico fk_modelos_fabricante; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modelos_neumatico
    ADD CONSTRAINT fk_modelos_fabricante FOREIGN KEY (fabricante_id) REFERENCES public.fabricantes_neumatico(id) ON DELETE RESTRICT;


--
-- Name: motivos_desecho fk_motivos_desecho_actualizado_por; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.motivos_desecho
    ADD CONSTRAINT fk_motivos_desecho_actualizado_por FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: motivos_desecho fk_motivos_desecho_creado_por; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.motivos_desecho
    ADD CONSTRAINT fk_motivos_desecho_creado_por FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: modelos_posiciones_permitidas fk_mpp_creado_por; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modelos_posiciones_permitidas
    ADD CONSTRAINT fk_mpp_creado_por FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: modelos_posiciones_permitidas fk_mpp_modelo; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modelos_posiciones_permitidas
    ADD CONSTRAINT fk_mpp_modelo FOREIGN KEY (modelo_neumatico_id) REFERENCES public.modelos_neumatico(id) ON DELETE CASCADE;


--
-- Name: modelos_posiciones_permitidas fk_mpp_posicion; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.modelos_posiciones_permitidas
    ADD CONSTRAINT fk_mpp_posicion FOREIGN KEY (posicion_neumatico_id) REFERENCES public.posiciones_neumatico(id) ON DELETE CASCADE;


--
-- Name: neumaticos fk_neumaticos_actualizado_por; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.neumaticos
    ADD CONSTRAINT fk_neumaticos_actualizado_por FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: neumaticos fk_neumaticos_creado_por; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.neumaticos
    ADD CONSTRAINT fk_neumaticos_creado_por FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: neumaticos fk_neumaticos_modelo; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.neumaticos
    ADD CONSTRAINT fk_neumaticos_modelo FOREIGN KEY (modelo_id) REFERENCES public.modelos_neumatico(id) ON DELETE RESTRICT;


--
-- Name: neumaticos fk_neumaticos_motivo_desecho; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.neumaticos
    ADD CONSTRAINT fk_neumaticos_motivo_desecho FOREIGN KEY (motivo_desecho_id) REFERENCES public.motivos_desecho(id) ON DELETE RESTRICT;


--
-- Name: neumaticos fk_neumaticos_posicion_actual; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.neumaticos
    ADD CONSTRAINT fk_neumaticos_posicion_actual FOREIGN KEY (ubicacion_actual_posicion_id) REFERENCES public.posiciones_neumatico(id) ON DELETE SET NULL;


--
-- Name: neumaticos fk_neumaticos_proveedor_compra; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.neumaticos
    ADD CONSTRAINT fk_neumaticos_proveedor_compra FOREIGN KEY (proveedor_compra_id) REFERENCES public.proveedores(id) ON DELETE SET NULL;


--
-- Name: neumaticos fk_neumaticos_ubicacion_almacen; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.neumaticos
    ADD CONSTRAINT fk_neumaticos_ubicacion_almacen FOREIGN KEY (ubicacion_almacen_id) REFERENCES public.almacenes(id) ON DELETE SET NULL;


--
-- Name: neumaticos fk_neumaticos_vehiculo_actual; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.neumaticos
    ADD CONSTRAINT fk_neumaticos_vehiculo_actual FOREIGN KEY (ubicacion_actual_vehiculo_id) REFERENCES public.vehiculos(id) ON DELETE SET NULL;


--
-- Name: registros_odometro fk_odometro_creado_por; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registros_odometro
    ADD CONSTRAINT fk_odometro_creado_por FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: registros_odometro fk_odometro_vehiculo; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registros_odometro
    ADD CONSTRAINT fk_odometro_vehiculo FOREIGN KEY (vehiculo_id) REFERENCES public.vehiculos(id) ON DELETE CASCADE;


--
-- Name: parametros_inventario fk_param_inv_actualizado_por; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parametros_inventario
    ADD CONSTRAINT fk_param_inv_actualizado_por FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: parametros_inventario fk_param_inv_creado_por; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parametros_inventario
    ADD CONSTRAINT fk_param_inv_creado_por FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: parametros_inventario fk_param_inv_modelo; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parametros_inventario
    ADD CONSTRAINT fk_param_inv_modelo FOREIGN KEY (modelo_id) REFERENCES public.modelos_neumatico(id) ON DELETE CASCADE;


--
-- Name: parametros_inventario fk_param_inv_ubicacion; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parametros_inventario
    ADD CONSTRAINT fk_param_inv_ubicacion FOREIGN KEY (ubicacion_almacen_id) REFERENCES public.almacenes(id) ON DELETE SET NULL;


--
-- Name: posiciones_neumatico fk_posiciones_configuracion_eje; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posiciones_neumatico
    ADD CONSTRAINT fk_posiciones_configuracion_eje FOREIGN KEY (configuracion_eje_id) REFERENCES public.configuraciones_eje(id) ON DELETE CASCADE;


--
-- Name: proveedores fk_proveedores_actualizado_por; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proveedores
    ADD CONSTRAINT fk_proveedores_actualizado_por FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: proveedores fk_proveedores_creado_por; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proveedores
    ADD CONSTRAINT fk_proveedores_creado_por FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: tipos_vehiculo fk_tipos_vehiculo_actualizado_por; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipos_vehiculo
    ADD CONSTRAINT fk_tipos_vehiculo_actualizado_por FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: tipos_vehiculo fk_tipos_vehiculo_creado_por; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipos_vehiculo
    ADD CONSTRAINT fk_tipos_vehiculo_creado_por FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: usuarios fk_usuarios_actualizado_por; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT fk_usuarios_actualizado_por FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: usuarios fk_usuarios_creado_por; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT fk_usuarios_creado_por FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: vehiculos fk_vehiculos_actualizado_por; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehiculos
    ADD CONSTRAINT fk_vehiculos_actualizado_por FOREIGN KEY (actualizado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: vehiculos fk_vehiculos_creado_por; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehiculos
    ADD CONSTRAINT fk_vehiculos_creado_por FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: vehiculos fk_vehiculos_tipo_vehiculo; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehiculos
    ADD CONSTRAINT fk_vehiculos_tipo_vehiculo FOREIGN KEY (tipo_vehiculo_id) REFERENCES public.tipos_vehiculo(id) ON DELETE RESTRICT;


--
-- Name: neumaticos neumaticos_garantia_proveedor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.neumaticos
    ADD CONSTRAINT neumaticos_garantia_proveedor_id_fkey FOREIGN KEY (garantia_proveedor_id) REFERENCES public.proveedores(id) ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

