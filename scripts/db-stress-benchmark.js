require('dotenv').config();
const { PrismaClient } = require('@prisma/client');
const { PrismaPg } = require('@prisma/adapter-pg');
const { Pool } = require('pg');

const connectionString = process.env.DATABASE_URL;
const pool = new Pool({
    connectionString,
    max: 4, // Conservative pool limit to coexist with running Next.js server
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 10000,
});
const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter });

async function runBatch(items, batchSize, fn) {
    const results = [];
    for (let i = 0; i < items.length; i += batchSize) {
        const chunk = items.slice(i, i + batchSize);
        const chunkResults = await Promise.all(chunk.map(fn));
        results.push(...chunkResults);
    }
    return results;
}

async function runDatabaseStressTest() {
    console.log('\n⚡ ===================================================');
    console.log('🚀 INICIANDO PRUEBAS DE ESTRÉS Y VELOCIDAD DE BASE DE DATOS');
    console.log('⚡ ===================================================\n');

    // 1. Fetch a valid tenant (empresa_id)
    const empresa = await prisma.empresa.findFirst({ select: { id: true, nombre: true } });
    if (!empresa) {
        console.error('❌ No se encontró empresa en la BD.');
        process.exit(1);
    }

    const empresaId = empresa.id;
    console.log(`🏢 Tenant activo: ${empresa.nombre} (${empresaId})\n`);

    // --- PRUEBA 1: Consultas Indexadas de Neumáticos por Filtros Compuestos ---
    console.log('📌 Prueba 1: Búsquedas Indexadas (100 consultas en lotes concurrentes de 4)...');
    const startP1 = performance.now();
    const tasksP1 = Array.from({ length: 100 }, (_, i) => i);
    await runBatch(tasksP1, 4, () => 
        prisma.neumatico.findMany({
            where: { empresa_id: empresaId, activo: true, estado_actual: 'EN_STOCK' },
            select: { id: true, numero_serie: true, estado_actual: true, kilometraje_acumulado: true },
            take: 20
        })
    );
    const durationP1 = performance.now() - startP1;
    const avgP1 = durationP1 / 100;
    const qpsP1 = (1000 / avgP1);
    console.log(`   ✅ 100 queries indexadas | Tiempo Total: ${durationP1.toFixed(2)}ms | Latencia Promedio por Query: ${avgP1.toFixed(2)}ms | QPS: ${qpsP1.toFixed(0)} req/s\n`);

    // --- PRUEBA 2: Carga de Estadísticas de Dashboard ---
    console.log('📌 Prueba 2: Agregaciones de Dashboard (30 ejecuciones en lotes de 4)...');
    const startP2 = performance.now();
    const tasksP2 = Array.from({ length: 30 }, (_, i) => i);
    await runBatch(tasksP2, 4, () => 
        Promise.all([
            prisma.neumatico.count({ where: { empresa_id: empresaId, activo: true } }),
            prisma.neumatico.groupBy({
                by: ['estado_actual'],
                where: { empresa_id: empresaId, activo: true },
                _count: true
            }),
            prisma.vehiculo.count({ where: { empresa_id: empresaId, activo: true } })
        ])
    );
    const durationP2 = performance.now() - startP2;
    const avgP2 = durationP2 / 30;
    const qpsP2 = (1000 / avgP2);
    console.log(`   ✅ 30 ejecuciones de Dashboard | Tiempo Total: ${durationP2.toFixed(2)}ms | Latencia Promedio: ${avgP2.toFixed(2)}ms | QPS: ${qpsP2.toFixed(0)} req/s\n`);

    // --- PRUEBA 3: Consulta Masiva de CPK por Marca con Proyección Select ---
    console.log('📌 Prueba 3: Cálculo de Comparativo de CPK con Select Optimizado (20 ejecuciones en lotes de 4)...');
    const startP3 = performance.now();
    const tasksP3 = Array.from({ length: 20 }, (_, i) => i);
    await runBatch(tasksP3, 4, () => 
        prisma.neumatico.findMany({
            where: { empresa_id: empresaId, kilometraje_acumulado: { gt: 0 } },
            select: {
                costo_compra: true,
                kilometraje_acumulado: true,
                modelo: { select: { fabricante: { select: { id: true, nombre: true } } } },
                eventos: { where: { costo_evento: { not: null } }, select: { costo_evento: true } }
            }
        })
    );
    const durationP3 = performance.now() - startP3;
    const avgP3 = durationP3 / 20;
    const qpsP3 = (1000 / avgP3);
    console.log(`   ✅ 20 reportes masivos | Tiempo Total: ${durationP3.toFixed(2)}ms | Latencia Promedio: ${avgP3.toFixed(2)}ms | QPS: ${qpsP3.toFixed(0)} req/s\n`);

    // --- METRICAS DE MEMORIA Y ESTADO ---
    const memory = process.memoryUsage();
    console.log('📊 ===================================================');
    console.log('📈 RESULTADOS DE ESTRÉS Y VELOCIDAD DE LA BASE DE DATOS');
    console.log('📊 ===================================================');
    console.log(`   • Latencia Búsqueda Indexada: ${avgP1.toFixed(2)} ms`);
    console.log(`   • Latencia Agregaciones Dashboard: ${avgP2.toFixed(2)} ms`);
    console.log(`   • Latencia Reporte CPK Marcas: ${avgP3.toFixed(2)} ms`);
    console.log(`   • Rendimiento Búsquedas (QPS): ${qpsP1.toFixed(0)} consultas/segundo`);
    console.log(`   • Memoria RAM Usada por Node.js: ${(memory.heapUsed / 1024 / 1024).toFixed(2)} MB`);
    console.log(`   • Conexiones Activas a DB: 4 (Compatibles con PgBouncer limit 15)`);
    console.log('=======================================================\n');

    await prisma.$disconnect();
    await pool.end();
}

runDatabaseStressTest().catch(async (e) => {
    console.error('❌ Error en prueba de estrés:', e);
    await prisma.$disconnect();
    await pool.end();
    process.exit(1);
});
