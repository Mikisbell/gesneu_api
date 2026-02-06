import 'dotenv/config'; // Load env vars
import { PrismaClient } from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';
import { Pool } from 'pg';
import { DEFAULT_TENANT_ID, DEFAULT_TENANT_NAME, DEFAULT_TENANT_RUC } from '../src/lib/constants';

// Copying instantiation logic from src/lib/prisma.ts to ensure compatibility
const connectionString = process.env.DATABASE_URL;
const isLocalhost = connectionString?.includes('localhost') || connectionString?.includes('127.0.0.1');
const isCI = process.env.CI === 'true';
// Force SSL for Supabase unless localhost explicitly
const useSSL = !isLocalhost && !isCI;

const pool = new Pool({
    connectionString,
    ssl: useSSL ? { rejectUnauthorized: false } : false,
    max: 5,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 10000,
});

const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter, log: ['error', 'warn', 'info'] });

async function main() {
    console.log('🚀 Iniciando migración a Single-Tenant...');
    console.log(`Tenant ID Objetivo: ${DEFAULT_TENANT_ID}`);

    try {
        // 1. Asegurar que existe la Empresa Default
        const existingCompany = await prisma.empresa.findUnique({
            where: { id: DEFAULT_TENANT_ID }
        });

        if (!existingCompany) {
            console.log('📦 Creando Empresa Principal por defecto...');
            const rucConflict = await prisma.empresa.findUnique({ where: { ruc: DEFAULT_TENANT_RUC } });
            if (rucConflict) {
                console.log(`⚠️ RUC ${DEFAULT_TENANT_RUC} ya existe en otra empresa. Eliminando conflicto...`);
                // WARNING: Deleting existing conflict. In Dev this is fine.
                await prisma.empresa.delete({ where: { ruc: DEFAULT_TENANT_RUC } });
            }

            await prisma.empresa.create({
                data: {
                    id: DEFAULT_TENANT_ID,
                    nombre: DEFAULT_TENANT_NAME,
                    ruc: DEFAULT_TENANT_RUC,
                    activo: true
                }
            });
            console.log('✅ Empresa Principal creada.');
        } else {
            console.log('✅ Empresa Principal ya existe.');
        }

        // 2. Mover TODOS los datos existentes a esta empresa
        const tables = [
            'usuario',
            'vehiculo',
            'neumatico',
            'almacen',
            'proveedor',
            'webhookConfig'
        ];

        for (const table of tables) {
            // @ts-ignore
            const model = prisma[table];
            if (model) {
                console.log(`🔄 Migrando ${table}...`);
                const result = await model.updateMany({
                    where: {
                        empresa_id: { not: DEFAULT_TENANT_ID }
                    },
                    data: {
                        empresa_id: DEFAULT_TENANT_ID
                    }
                });
                console.log(`   - ${result.count} registros actualizados en ${table}.`);
            }
        }

        console.log('🏁 Migración Single-Tenant completada exitosamente.');
    } catch (error) {
        console.error("Error crítico durante la migración:", error);
        throw error;
    }
}

main()
    .catch((e) => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
        await pool.end();
    });
