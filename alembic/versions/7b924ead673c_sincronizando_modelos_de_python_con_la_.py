"""Sincronizando modelos de Python con la BD existente

Revision ID: 7b924ead673c
Revises: ec4e921e44b6
Create Date: 2025-08-22 21:39:39.800202

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import VARCHAR
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '7b924ead673c'
down_revision: Union[str, Sequence[str], None] = 'ec4e921e44b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# --- Definiciones extraídas de tu base de datos ---

VISTA_SQL = """
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
  WHERE (mn.activo = true);
"""

INDICE_VISTA_SQL = """
CREATE UNIQUE INDEX idx_mv_desempeno_modelos_id ON public.mv_desempeno_modelos USING btree (modelo_id);
"""

DROP_VISTA_SQL = "DROP MATERIALIZED VIEW IF EXISTS public.mv_desempeno_modelos;"


def upgrade() -> None:
    """Upgrade schema."""
    # --- Paso 1: Eliminar la vista materializada y su índice ---
    op.execute(DROP_VISTA_SQL)

    # ### Comandos autogenerados por Alembic (ajustados) ###
    op.alter_column('fabricantes_neumatico', 'creado_en',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False,
               existing_server_default=sa.text('now()'))
    op.alter_column('fabricantes_neumatico', 'actualizado_en',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=True)
    # ... (el resto de los comandos de alteración de tablas) ...
    # ... Alembic los manejará correctamente ...

    op.alter_column('modelos_neumatico', 'medida',
               existing_type=postgresql.DOMAIN('medida_neumatico', VARCHAR()),
               type_=sqlmodel.sql.sqltypes.AutoString(length=20),
               existing_nullable=False)

    # ... (más comandos de Alembic) ...

    # --- Paso 2: Volver a crear la vista materializada y su índice ---
    op.execute(VISTA_SQL)
    op.execute(INDICE_VISTA_SQL)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # --- Paso 1 (reverso): Eliminar la vista materializada y su índice ---
    op.execute(DROP_VISTA_SQL)

    # ### Comandos autogenerados por Alembic (ajustados para el reverso) ###
    # ... (todos los comandos de downgrade generados por Alembic) ...

    op.alter_column('modelos_neumatico', 'medida',
               existing_type=sqlmodel.sql.sqltypes.AutoString(length=20),
               type_=postgresql.DOMAIN('medida_neumatico', VARCHAR()),
               existing_nullable=False)

    # ... (el resto de los comandos de downgrade) ...

    # --- Paso 2 (reverso): Volver a crear la vista y el índice como estaban antes ---
    op.execute(VISTA_SQL)
    op.execute(INDICE_VISTA_SQL)
    # ### end Alembic commands ###