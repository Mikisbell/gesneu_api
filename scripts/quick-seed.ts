import 'dotenv/config';
import { PrismaClient } from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';
import { Pool } from 'pg';

const connectionString = process.env.DATABASE_URL;

const pool = new Pool({ connectionString });
const adapter = new PrismaPg(pool);

const prisma = new PrismaClient({
    adapter,
    log: ['info', 'warn', 'error'],
});

async function main() {
    console.log('🌱 Starting Quick Seed...');

    try {
        // 1. Create Default Content (Empresa) if needed
        const empresaId = "00000000-0000-0000-0000-000000000000";
        // Assuming empresa exists or we bypass for now. 
        // Actually, let's create manufacturers without relation to empresa if schema allows, 
        // or fetch the first found empresa.

        // 2. Manufacturers
        const manufacturers = [
            { nombre: 'Michelin', codigo_abreviado: 'MICH' },
            { nombre: 'Bridgestone', codigo_abreviado: 'BRID' },
            { nombre: 'Goodyear', codigo_abreviado: 'GOOD' }
        ];

        for (const man of manufacturers) {
            const exists = await prisma.fabricanteNeumatico.findFirst({
                where: { nombre: man.nombre }
            });

            if (!exists) {
                await prisma.fabricanteNeumatico.create({
                    data: {
                        nombre: man.nombre,
                        codigo_abreviado: man.codigo_abreviado,
                        activo: true
                    }
                });
                console.log(`✅ Created Manufacturer: ${man.nombre}`);
            } else {
                console.log(`ℹ️ Manufacturer already exists: ${man.nombre}`);
            }
        }

        // 3. Models
        // Fetch a manufacturer to link
        const michelin = await prisma.fabricanteNeumatico.findFirst({ where: { nombre: 'Michelin' } });

        if (michelin) {
            const models = [
                { nombre: 'X Multi Z', medida: '295/80R22.5', fabricante_id: michelin.id },
                { nombre: 'X Works', medida: '11R22.5', fabricante_id: michelin.id }
            ];

            for (const mod of models) {
                const exists = await prisma.modeloNeumatico.findFirst({
                    where: { nombre_modelo: mod.nombre }
                });

                if (!exists) {
                    await prisma.modeloNeumatico.create({
                        data: {
                            nombre_modelo: mod.nombre,
                            medida: mod.medida,
                            fabricante_id: mod.fabricante_id,
                            profundidad_original_mm: 20,
                            permite_reencauche: true,
                            reencauches_maximos: 3
                        }
                    });
                    console.log(`✅ Created Model: ${mod.nombre}`);
                } else {
                    console.log(`ℹ️ Model already exists: ${mod.nombre}`);
                }
            }
        }

        console.log('✨ Quick Seed Completed!');
    } catch (e) {
        console.error('❌ Quick Seed Failed:', e);
    } finally {
        await prisma.$disconnect();
    }
}

main();
