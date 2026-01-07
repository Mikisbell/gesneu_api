
require('dotenv').config();
const { Client } = require('pg');

async function main() {
    console.log('🚀 Creando Vistas SQL via PG Driver...');

    if (!process.env.DATABASE_URL) {
        console.error('❌ DATABASE_URL no encontrada en environment');
        process.exit(1);
    }

    const client = new Client({
        connectionString: process.env.DATABASE_URL,
        ssl: { rejectUnauthorized: false } // Supabase suele requerir SSL
    });

    try {
        await client.connect();
        console.log('✅ Conectado a Postgres.');

        // 1. Vista de Instalados
        await client.query(`
      CREATE OR REPLACE VIEW public.vw_neumaticos_instalados AS 
      WITH ultimas_inspecciones AS (
        SELECT neumatico_id, profundidad_remanente, presion_psi, fecha_evento,
               ROW_NUMBER() OVER (PARTITION BY neumatico_id ORDER BY fecha_evento DESC) as rn 
        FROM public.eventos_neumaticos 
        WHERE tipo_evento = 'INSPECCION' AND profundidad_remanente IS NOT NULL
      ) 
      SELECT 
        n.id AS neumatico_id, 
        n.numero_serie, 
        n.dot, 
        mn.nombre AS nombre_modelo, 
        mn.medida, 
        fn.nombre AS fabricante, 
        v.placa, 
        v.codigo_interno AS numero_economico, 
        tv.nombre AS tipo_vehiculo, 
        pn.numero_posicion, 
        pn.lado_vehiculo, 
        ce.tipo_eje, 
        n.actualizado_en AS fecha_instalacion, 
        ui.fecha_evento AS fecha_ultima_inspeccion, 
        ui.profundidad_remanente AS profundidad_actual_mm, 
        ui.presion_psi AS presion_actual_psi, 
        mn.profundidad_inicial_mm, 
        CASE 
          WHEN mn.profundidad_inicial_mm > 0 AND ui.profundidad_remanente IS NOT NULL 
          THEN ROUND(((ui.profundidad_remanente / mn.profundidad_inicial_mm) * 100.0), 1) 
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

        // 2. Vista Inventario
        await client.query(`
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

    } catch (err) {
        console.error('❌ Error PG:', err);
    } finally {
        await client.end();
    }
}

main();
