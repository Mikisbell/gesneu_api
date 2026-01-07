
import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();

async function main() {
    const n = await prisma.neumatico.count();
    const v = await prisma.vehiculo.count();
    const u = await prisma.usuario.count();

    console.log('--- DB STATUS ---');
    console.log(`Usuarios: ${u}`);
    console.log(`Vehiculos: ${v}`);
    console.log(`Neumaticos: ${n}`);
    console.log('-----------------');
}

main()
    .catch(e => console.error(e))
    .finally(async () => await prisma.$disconnect());
