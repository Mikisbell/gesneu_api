import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
    const vehiculo = await prisma.vehiculo.findFirst();
    if (vehiculo) {
        console.log(`Vehicle ID: ${vehiculo.id}`);
        console.log(`Placa: ${vehiculo.placa}`);
    } else {
        console.log('No vehicles found');
    }
}

main()
    .catch(e => console.error(e))
    .finally(async () => await prisma.$disconnect());
