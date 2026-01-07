
import 'dotenv/config';
import { PrismaClient } from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';
import { Pool } from 'pg';
import { performance } from 'perf_hooks';

// --- CONFIGURACIÓN DE CONEXIÓN ---
const connectionString = process.env.DATABASE_URL;
const pool = new Pool({
    connectionString,
    ssl: connectionString?.includes('localhost') ? false : { rejectUnauthorized: false },
    max: 20
});
const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter });

async function benchmark(label: string, fn: () => Promise<any>) {
    const start = performance.now();
    try {
        const result = await fn();
        const end = performance.now();
        const duration = (end - start).toFixed(2);

        let countInfo = '';
        if (Array.isArray(result)) countInfo = `| ${result.length} rows`;
        else if (result && typeof result === 'object' && '_count' in result) countInfo = `| Count: ${JSON.stringify(result)}`;
        else if (typeof result === 'number') countInfo = `| ${result}`;

        console.log(`✅ ${label}: ${duration}ms ${countInfo}`);
        return duration;
    } catch (e) {
        console.error(`❌ ${label} FAILED:`, e);
        return 'ERR';
    }
}

async function main() {
    console.log('🔥 INICIANDO TEST DE ESTRÉS / RENDIMIENTO (Base de Datos Poblada)...');
    console.log('---------------------------------------------------------------');

    // 0. Warmup
    await prisma.neumatico.findFirst();

    // 1. Dashboard Metrics (Aggregation Heavy)
    // Simula la carga del dashboard principal que agrupa por estado
    await benchmark('Dashboard: GroupBy Estado', async () => {
        return await prisma.neumatico.groupBy({
            by: ['estado_actual'],
            _count: true
        });
    });

    // 2. Reporte de Inventario (Data Fetching)
    // Simula un reporte de inventario con datos de modelo y fabricante
    await benchmark('Reporte: Inventario Completo (Limit 1000)', async () => {
        return await prisma.neumatico.findMany({
            where: { estado_actual: 'EN_STOCK' },
            select: {
                numero_serie: true,
                profundidad_remanente_actual_mm: true,
                modelo: {
                    select: {
                        nombre_modelo: true,
                        fabricante: { select: { nombre: true } }
                    }
                }
            },
            take: 1000
        });
    });

    // 3. Consulta Compleja de Flota (Deep Nesting)
    // Simula ver la flota con detalle de neumáticos montados
    await benchmark('Flota: Vehículos con Neumáticos Montados', async () => {
        return await prisma.vehiculo.findMany({
            include: {
                tipo_vehiculo: true,
                neumaticos_instalados: {
                    include: {
                        modelo: true
                    }
                }
            },
            take: 50 // Página 1
        });
    });

    // 4. Test de Concurrencia (Simulación de Tráfico)
    console.log('\n⚡ Test de Concurrencia (50 usuarios simultáneos en Dashboard)...');

    const startConcurrent = performance.now();
    const requests = [];
    for (let i = 0; i < 50; i++) {
        requests.push(prisma.neumatico.count()); // Query ligera pero frecuente
    }

    await Promise.all(requests);
    const endConcurrent = performance.now();
    const durationConcurrent = (endConcurrent - startConcurrent).toFixed(2);

    console.log(`✅ 50 Concurrent Requests terminados en ${durationConcurrent}ms`);
    console.log(`   Promedio por request: ${(Number(durationConcurrent) / 50).toFixed(2)}ms`);

    console.log('\n🏁 Stress Test Finalizado.');
}

main()
    .catch(console.error)
    .finally(async () => {
        await prisma.$disconnect();
        await pool.end();
    });
