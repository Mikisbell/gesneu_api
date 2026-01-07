import 'dotenv/config';
import { PrismaClient } from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';
import { Pool } from 'pg';

const connectionString = process.env.DATABASE_URL;
const pool = new Pool({
    connectionString,
    ssl: connectionString?.includes('localhost') ? false : { rejectUnauthorized: false },
});
const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter });

async function main() {
    console.log('🔓 Intentando liberar Advisory Lock de Prisma (72707369)...');
    try {
        // Usamos queryRaw para ver el resultado boolean
        const result = await prisma.$queryRaw`SELECT pg_advisory_unlock(72707369)`;
        console.log('✅ Lock liberado:', result);
    } catch (e) {
        console.error('❌ Error liberando lock:', e);
    } finally {
        await prisma.$disconnect();
    }
}

main();
