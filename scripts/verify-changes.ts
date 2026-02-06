import 'dotenv/config';
import { PrismaClient } from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';
import { Pool } from 'pg';

// Setup Prisma Client (DB Access)
const connectionString = process.env.DATABASE_URL;
const pool = new Pool({ connectionString });
const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter });

async function verify() {
    console.log('🧪 Starting Verification: Quick Model Creation API & DB');

    // 1. Verify Manufacturer Exists (Pre-requisite)
    const michelin = await prisma.fabricanteNeumatico.findFirst({
        where: { nombre: 'Michelin' }
    });

    if (!michelin) {
        console.error('❌ Error: Michelin manufacturer not found. Seed failed?');
        process.exit(1);
    }
    console.log('✅ Pre-check: Manufacturer found:', michelin.nombre);

    // 2. Simulate API Payload for New Model
    const newModelPayload = {
        nombre_modelo: `Test Model ${Date.now()}`,
        medida: '11R22.5',
        fabricante_id: michelin.id,
        profundidad_original_mm: 22.5,
        permite_reencauche: true,
        reencauches_maximos: 3
    };

    console.log('🔄 Attempting to create model via DB (Simulating API action)...');

    // Note: Since we are running this inside the server environment, we can test the DB write directly 
    // to confirm schema validity, which underlies the API.
    // Testing the actual HTTP endpoint requires fetch against localhost:3005 which might be tricky if auth is enabled.
    // We will verify the DB layer first.

    const createdModel = await prisma.modeloNeumatico.create({
        data: newModelPayload
    });

    if (createdModel) {
        console.log('✅ DB Write Success: Created Model:', createdModel.nombre_modelo);
        console.log('   ID:', createdModel.id);
        console.log('   Medida:', createdModel.medida);
    } else {
        console.error('❌ DB Write Failed');
    }

    // 3. Verify it exists in the list (Simulating getAll)
    const allModels = await prisma.modeloNeumatico.findMany({
        where: { id: createdModel.id }
    });

    if (allModels.length > 0) {
        console.log('✅ DB Read Success: Model found in query.');
    } else {
        console.error('❌ DB Read Failed');
    }

    // Clean up
    await prisma.modeloNeumatico.delete({
        where: { id: createdModel.id }
    });
    console.log('🧹 Cleanup: Test model deleted.');
}

verify()
    .catch(e => console.error(e))
    .finally(async () => {
        await prisma.$disconnect();
    });
