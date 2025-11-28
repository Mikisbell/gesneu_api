import 'dotenv/config';
import { PrismaClient } from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';
import pkg from 'pg';
const { Pool } = pkg;

const pool = new Pool({ connectionString: process.env.DATABASE_URL });
const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter });

async function main() {
    try {
        console.log('🔌 Conectando a Prisma...');
        const userCount = await prisma.usuario.count();
        console.log(`✅ Prisma está funcionando correctamente.`);
        console.log(`📊 Total de usuarios en BD: ${userCount}`);

        // Check one more thing to be sure
        const providerCount = await prisma.proveedor.count();
        console.log(`🏭 Total de proveedores: ${providerCount}`);

    } catch (error) {
        console.error('❌ Error conectando con Prisma:', error);
        process.exit(1);
    } finally {
        await prisma.$disconnect();
    }
}

main();
