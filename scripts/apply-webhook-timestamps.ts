import 'dotenv/config';
// Import the configured instance
import { prisma } from '../src/lib/prisma';

// Remove manual init
// const dbUrl = ...
// const prisma = ...

async function main() {
    console.log('Applying manual migration for WebhookConfig timestamps...');

    try {
        // 1. Add creado_en
        await prisma.$executeRawUnsafe(`
      ALTER TABLE "webhook_configs" 
      ADD COLUMN IF NOT EXISTS "creado_en" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP;
    `);
        console.log('✅ Added creado_en column');

        // 2. Add actualizado_en
        await prisma.$executeRawUnsafe(`
      ALTER TABLE "webhook_configs" 
      ADD COLUMN IF NOT EXISTS "actualizado_en" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP;
    `);
        console.log('✅ Added actualizado_en column');

    } catch (e) {
        console.error('Error applying migration:', e);
    } finally {
        await prisma.$disconnect();
    }
}

main();
