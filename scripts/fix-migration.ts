
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function main() {
    console.log('Attempting to delete migration history row...');
    try {
        const result = await prisma.$executeRawUnsafe(`DELETE FROM "_prisma_migrations" WHERE migration_name = '20251114051942_init';`);
        console.log('Deleted migration history row. Result:', result);
    } catch (e) {
        console.error('Error deleting migration row:', e);
    }
}

main()
    .catch((e) => {
        console.error(e)
        process.exit(1)
    })
    .finally(async () => {
        await prisma.$disconnect()
    })
