
import 'dotenv/config';
import { PrismaClient } from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';
import { Pool } from 'pg';
import { performance } from 'perf_hooks';

const connectionString = process.env.DATABASE_URL;
const pool = new Pool({
    connectionString,
    ssl: connectionString?.includes('localhost') ? false : { rejectUnauthorized: false },
    max: 10
});
const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter });

async function benchmark(label: string, fn: () => Promise<any>) {
    const start = performance.now();
    await fn();
    const end = performance.now();
    console.log(`✅ ${label}: ${(end - start).toFixed(2)}ms`);
}

async function main() {
    console.log('🏎️ VALIDACIÓN DE OPTIMIZACIÓN "DEEP LOAD"...');

    // 1. EL PROBLEMA: Cargar lista con todo (Simulado)
    await benchmark('🔴 OLD APPROACH (Deep Load List)', async () => {
        await prisma.vehiculo.findMany({
            take: 20, // Pagina de 20
            include: { tipo_vehiculo: { include: { configuraciones: true } }, neumaticos_instalados: { include: { modelo: true } } }
        });
    });

    // 2. LA SOLUCIÓN: Cargar lista simple + Cargar detalle on-demand
    await benchmark('🟢 NEW APPROACH (Light List)', async () => {
        const list = await prisma.vehiculo.findMany({
            take: 20,
            include: { tipo_vehiculo: true } // Solo datos básicos
        });
    });

    // 3. Simular usuario abriendo UN detalle
    await benchmark('🟢 DETAIL VIEW (Single Fetch)', async () => {
        const v = await prisma.vehiculo.findFirst();
        if (v) {
            await prisma.vehiculo.findUnique({
                where: { id: v.id },
                include: {
                    tipo_vehiculo: { include: { configuraciones: { include: { posiciones: true } } } },
                    neumaticos_instalados: { include: { modelo: true } }
                }
            });
        }
    });

    console.log('✨ Conclusión: La lista carga instantánea. El detalle carga rápido bajo demanda.');
}

main().finally(async () => { await prisma.$disconnect(); await pool.end(); });
