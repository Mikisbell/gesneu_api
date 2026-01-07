
import 'dotenv/config';
import { PrismaClient } from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';
import { Pool } from 'pg';
import { performance } from 'perf_hooks';

const connectionString = process.env.DATABASE_URL;
const pool = new Pool({
    connectionString,
    ssl: connectionString?.includes('localhost') ? false : { rejectUnauthorized: false },
    max: 20
});
const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter });

async function benchmark(modelName: string, operation: string, fn: () => Promise<any>) {
    const start = performance.now();
    try {
        const res = await fn();
        const end = performance.now();
        const duration = (end - start).toFixed(2);

        // Count result items
        let count = 'N/A';
        if (typeof res === 'number') count = res.toString();
        if (Array.isArray(res)) count = res.length.toString();
        if (res && typeof res === 'object' && '_count' in res) count = JSON.stringify(res._count);

        console.log(`| ${modelName.padEnd(20)} | ${operation.padEnd(30)} | ${duration.padStart(8)} ms | ${count.padStart(10)} rows |`);
    } catch (e: any) {
        console.log(`| ${modelName.padEnd(20)} | ${operation.padEnd(30)} |    ERROR | ${e.message.substring(0, 20)}... |`);
    }
}

async function main() {
    console.log('\n📊 FULL SYSTEM STRESS TEST REPORT');
    console.log('================================================================================');
    console.log(`| ${'Model'.padEnd(20)} | ${'Operation'.padEnd(30)} | ${'Latency'.padEnd(11)} | ${'Rows'.padEnd(10)} |`);
    console.log('|----------------------|--------------------------------|-------------|------------|');

    // 0. Warmup
    await prisma.usuario.findFirst();

    // 1. Usuarios & Auth
    await benchmark('Usuario', 'FindAll', () => prisma.usuario.findMany());

    // 2. Organización
    await benchmark('CentroCosto', 'FindAll', () => prisma.centroCosto.findMany());
    await benchmark('Almacen', 'FindAll + Count Neumáticos', () => prisma.almacen.findMany({ include: { _count: { select: { neumaticos: true } } } }));

    // 3. Catálogos
    await benchmark('Proveedor', 'FindAll', () => prisma.proveedor.findMany());
    await benchmark('FabricanteNeumatico', 'FindAll + Count Modelos', () => prisma.fabricanteNeumatico.findMany({ include: { _count: { select: { modelos: true } } } }));
    await benchmark('ModeloNeumatico', 'FindMany (Limit 1000)', () => prisma.modeloNeumatico.findMany({ take: 1000 }));

    // 4. Activos (Vehículos)
    await benchmark('Vehiculo', 'Count Total', () => prisma.vehiculo.count());
    await benchmark('Vehiculo', 'FindAll (Simple)', () => prisma.vehiculo.findMany());
    await benchmark('Vehiculo', 'Deep Load (Typo+Conf+Neum)', () => prisma.vehiculo.findMany({
        take: 100,
        include: {
            tipo_vehiculo: { include: { configuraciones: true } },
            neumaticos_instalados: { include: { modelo: true } }
        }
    }));

    // 5. Inventario (Neumáticos)
    await benchmark('Neumatico', 'Count Total', () => prisma.neumatico.count());
    await benchmark('Neumatico', 'GroupBy Estado', () => prisma.neumatico.groupBy({ by: ['estado_actual'], _count: true }));
    await benchmark('Neumatico', 'Filter Stock + Relaciones', () => prisma.neumatico.findMany({
        where: { estado_actual: 'EN_STOCK' },
        take: 500,
        include: { modelo: { include: { fabricante: true } } }
    }));

    // 6. Operaciones (Historial)
    await benchmark('EventoNeumatico', 'Count', () => prisma.eventoNeumatico.count());
    await benchmark('EventoNeumatico', 'Sort by Date Desc (Limit)', () => prisma.eventoNeumatico.findMany({ orderBy: { fecha_evento: 'desc' }, take: 500 }));

    // 7. Mediciones (Heavy Data)
    await benchmark('LecturaPresion', 'Count', () => prisma.lecturaPresion.count());
    await benchmark('LecturaPresion', 'Avg Pressure (Aggr)', () => prisma.lecturaPresion.aggregate({ _avg: { presion_psi: true } }));
    await benchmark('MedicionProfundidad', 'Count', () => prisma.medicionProfundidad.count());

    // 8. Alertas
    await benchmark('Alerta', 'Count Pending', () => prisma.alerta.count({ where: { estado: 'PENDIENTE' } }));

    console.log('================================================================================');
    console.log('🏁 End of Report');
}

main()
    .finally(async () => {
        await prisma.$disconnect();
        await pool.end();
    });
