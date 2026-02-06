
const { PrismaClient } = require('@prisma/client');
const { PrismaPg } = require('@prisma/adapter-pg');
const { Pool } = require('pg');

const connectionString = process.env.DATABASE_URL;
const pool = new Pool({ connectionString });
const adapter = new PrismaPg(pool);

// Enable logging
const prisma = new PrismaClient({
    adapter,
    log: [
        { emit: 'event', level: 'query' },
    ],
});

let queryCount = 0;
prisma.$on('query', (e) => {
    queryCount++;
    // filter out system queries if needed
});

async function measureOperation(name, fn) {
    queryCount = 0;
    const start = performance.now();
    await fn();
    const duration = performance.now() - start;
    console.log(`⚡ [${name}] Time: ${duration.toFixed(2)}ms | Queries: ${queryCount}`);
    if (queryCount > 10) console.warn(`   ⚠️ High query count! Potential N+1`);
    return { duration, queryCount };
}

async function runAudit() {
    console.log('🔍 Iniciando Auditoría de Performance (N+1 Check)...');

    try {
        // Warmup
        await measureOperation('Warmup (Connection)', async () => {
            await prisma.empresa.findFirst();
        });

        // 1. List All Tires (Common operation)
        await measureOperation('List All Tires', async () => {
            // Simulating what usually happens in a simple list
            // This assumes fetching relations too
            const tires = await prisma.neumatico.findMany({
                take: 50,
                include: {
                    modelo: { include: { fabricante: true } },
                    ubicacion_vehiculo: true,
                    ubicacion_almacen: true
                    // If we fetch events here, count might explode?
                }
            });
        });

        // 2. Dashboard Stats (Simulated)
        await measureOperation('Dashboard Statistics', async () => {
            await Promise.all([
                prisma.neumatico.count(),
                prisma.neumatico.count({ where: { estado_actual: 'INSTALADO' } }),
                prisma.vehiculo.count(),
                // Often dashboards fetch latest alerts too
                prisma.alerta.findMany({ take: 5, orderBy: { creada_en: 'desc' } })
            ]);
        });

        // 3. Vehicle Detail with Tires
        // First get a vehicle ID
        const veh = await prisma.vehiculo.findFirst();
        if (veh) {
            await measureOperation('Vehicle Detail + Tires', async () => {
                await prisma.vehiculo.findUnique({
                    where: { id: veh.id },
                    include: {
                        neumaticos_instalados: {
                            include: { modelo: true }
                        }
                    }
                });
            });
        }

    } catch (e) {
        console.error(e);
    } finally {
        await prisma.$disconnect();
        await pool.end();
    }
}

runAudit();
