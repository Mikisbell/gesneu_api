import 'dotenv/config';
import { prisma } from '../src/lib/prisma';

async function main() {
    console.log('🌱 Seeding retreaded tire...');

    // 1. Get a tire model
    const modelo = await prisma.modeloNeumatico.findFirst();
    if (!modelo) {
        console.error('❌ No tire models found. Run the main seed first.');
        return;
    }

    // 2. Create a retreaded tire
    const serial = `R-${Math.floor(Math.random() * 10000)}`;
    const retreadedTire = await prisma.neumatico.create({
        data: {
            numero_serie: serial,
            modelo_id: modelo.id,
            dot: '2223',
            estado_actual: 'EN_STOCK',
            profundidad_inicial_mm: 15.0, // Retreads often have good depth
            profundidad_actual_mm: 15.0,
            es_reencauchado: true,
            reencauches_realizados: 1,
            vida_actual: 2,
            costo_compra: 150.00,
            fecha_compra: new Date(),
        }
    });

    console.log(`✅ Created retreaded tire: ${retreadedTire.numero_serie}`);
}

main()
    .catch((e) => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });
