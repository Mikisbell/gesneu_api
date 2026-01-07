
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
    console.log('🚀 Creando Vistas SQL de Alto Rendimiento...');

    try {
        // 1. Vista de Neumáticos Instalados (Optimizada)
        await prisma.$executeRawUnsafe(`
      CREATE OR REPLACE VIEW public.vw_neumaticos_instalados AS 
      WITH ultimas_inspecciones AS (
        SELECT neumatico_id, profundidad_remanente_mm, presion_psi, timestamp_evento,
               ROW_NUMBER() OVER (PARTITION BY neumatico_id ORDER BY timestamp_evento DESC) as rn 
        FROM public.eventos_neumaticos 
        WHERE tipo_evento = 'INSPECCION' AND profundidad_remanente_mm IS NOT NULL
      ) 
      SELECT 
        n.id AS neumatico_id, 
        n.numero_serie, 
        n.dot, 
        mn.nombre AS nombre_modelo, 
        mn.medida, 
        fn.nombre AS fabricante, 
        v.placa, 
        v.codigo_interno AS numero_economico, -- Mapeo de nombre
        tv.nombre AS tipo_vehiculo, 
        pn.numero_posicion, 
        pn.lado_vehiculo, 
        ce.tipo_eje, 
        n.actualizado_en AS fecha_instalacion, -- Aproximación si no hay campo explícito
        ui.timestamp_evento AS fecha_ultima_inspeccion, 
        ui.profundidad_remanente_mm AS profundidad_actual_mm, 
        ui.presion_psi AS presion_actual_psi, 
        mn.profundidad_inicial_mm, 
        CASE 
          WHEN mn.profundidad_inicial_mm > 0 AND ui.profundidad_remanente_mm IS NOT NULL 
          THEN ROUND(((ui.profundidad_remanente_mm / mn.profundidad_inicial_mm) * 100.0), 1) 
          ELSE NULL 
        END as porcentaje_vida_util_remanente, 
        v.contador_actual AS odometro_vehiculo_actual, 
        n.kilometraje_acumulado AS kilometraje_neumatico_acumulado, 
        n.vida_actual, 
        n.reencauches_realizados 
      FROM public.neumaticos n 
      JOIN public.modelos_neumatico mn ON n.modelo_id = mn.id 
      JOIN public.fabricantes_neumatico fn ON mn.fabricante_id = fn.id 
      LEFT JOIN public.vehiculos v ON n.ubicacion_vehiculo_id = v.id 
      LEFT JOIN public.tipos_vehiculo tv ON v.tipo_vehiculo_id = tv.id 
      LEFT JOIN public.posiciones_neumatico pn ON n.ubicacion_posicion_id = pn.id 
      LEFT JOIN public.configuraciones_eje ce ON pn.configuracion_eje_id = ce.id 
      LEFT JOIN ultimas_inspecciones ui ON n.id = ui.neumatico_id AND ui.rn = 1
      WHERE n.estado_actual = 'INSTALADO';
    `);
        console.log('✅ Vista vw_neumaticos_instalados creada.');

        // 2. Vista de Resumen de Inventario (KPIs)
        await prisma.$executeRawUnsafe(`
      CREATE OR REPLACE VIEW public.vw_inventario_resumen AS 
      SELECT 
        mn.id as modelo_id, 
        mn.nombre as nombre_modelo, 
        mn.medida, 
        fn.nombre as fabricante, 
        n.estado_actual, 
        n.es_reencauchado, 
        n.vida_actual, 
        COUNT(*) as cantidad, 
        AVG(n.kilometraje_acumulado) FILTER (WHERE n.estado_actual != 'EN_STOCK' AND n.kilometraje_acumulado > 0) as km_promedio_por_vida, 
        MIN(n.fecha_compra) as fecha_compra_mas_antigua, 
        MAX(n.fecha_compra) as fecha_compra_mas_reciente 
      FROM public.neumaticos n 
      JOIN public.modelos_neumatico mn ON n.modelo_id = mn.id 
      JOIN public.fabricantes_neumatico fn ON mn.fabricante_id = fn.id 
      WHERE n.estado_actual != 'DESECHADO' 
      GROUP BY mn.id, mn.nombre, mn.medida, fn.nombre, n.estado_actual, n.es_reencauchado, n.vida_actual 
      ORDER BY fabricante, nombre_modelo, medida, estado_actual;
    `);
        console.log('✅ Vista vw_inventario_resumen creada.');

    } catch (error) {
        console.error('❌ Error creando vistas:', error);
    } finally {
        await prisma.$disconnect();
    }
}

main();
