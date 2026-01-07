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
    console.log('🔪 Matando conexiones zombies...');
    try {
        // Matamos todas las conexiones excepto la nuestra
        const result = await prisma.$queryRaw`
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE pid <> pg_backend_pid()
            AND datname = current_database()
        `;
        console.log('✅ Conexiones terminadas:', result);
    } catch (e) {
        console.error('❌ Error matando conexiones:', e);
    } finally {
        await prisma.$disconnect();
    }
}
main();
