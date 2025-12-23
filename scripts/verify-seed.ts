import 'dotenv/config';
import { prisma } from '../src/lib/prisma';

async function main() {
    console.log('🔍 Verificando Seed Data...');

    const userCount = await prisma.usuario.count();
    const tireCount = await prisma.neumatico.count();
    const vehicleCount = await prisma.vehiculo.count();
    const posCount = await prisma.posicionNeumatico.count();
    const warehouseCount = await prisma.almacen.count();

    console.log(`\n📊 Resumen:`);
    console.log(`- Usuarios: ${userCount} (Esperado: >=3)`);
    console.log(`- Neumáticos: ${tireCount} (Esperado: >=14)`);
    console.log(`- Vehículos: ${vehicleCount} (Esperado: >=1)`);
    console.log(`- Posiciones: ${posCount} (Esperado: >=2)`);
    console.log(`- Almacenes: ${warehouseCount} (Esperado: >=2)`);

    if (userCount >= 3 && tireCount >= 14 && vehicleCount >= 1) {
        console.log('\n✅ VERIFICACION EXITOSA: La base de datos tiene la data mínima requerida.');
    } else {
        console.error('\n❌ VERIFICACION FALLIDA: Faltan datos.');
        process.exit(1);
    }
}

main()
    .catch((e) => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });
