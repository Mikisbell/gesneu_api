
import 'dotenv/config';
import { prisma } from '../src/lib/prisma';

import { seedTenants } from './seeds/seed-tenants';
import { seedCatalogs } from './seeds/seed-catalogs';
import { seedInfrastructure } from './seeds/seed-infrastructure';
import { seedFleet } from './seeds/seed-fleet';
import { seedInventory } from './seeds/seed-inventory';

async function main() {
    console.log('🌱 Starting Enhanced Database Seeding...');

    try {
        // Try to bypass RLS enforcement and set dummy context for audit triggers
        // This is safe if running as admin/postgres user
        await prisma.$executeRawUnsafe(`
            SET app.current_user_id = '00000000-0000-0000-0000-000000000000';
            SET app.current_tenant = '00000000-0000-0000-0000-000000000000';
        `);
        console.log('🔧 Session variables set.');

        // 1. Tenants & Users
        const { empresa } = await seedTenants(prisma);

        // 2. Catalogs (Brands, Models)
        const catalogs = await seedCatalogs(prisma, empresa.id);

        // 3. Infrastructure (Warehouses)
        const infrastructure = await seedInfrastructure(prisma, empresa.id);

        // 4. Fleet (Vehicles)
        const fleet = await seedFleet(prisma, empresa.id, infrastructure.cecoTransporte.id, infrastructure.cecoMinas.id);

        // 5. Inventory (Tires & History)
        await seedInventory(prisma, empresa.id, catalogs, fleet, infrastructure);

        console.log('✨ Seed Completed Successfully!');
    } catch (e) {
        console.error('❌ Seed Failed:', e);
        process.exit(1);
    } finally {
        await prisma.$disconnect();
    }
}

main();
