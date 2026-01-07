
const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
    console.log('--- DB CONNECTION START ---');
    try {
        const n = await prisma.neumatico.count();
        const v = await prisma.vehiculo.count();
        const u = await prisma.usuario.count();

        console.log(`✅ SUCCESS`);
        console.log(`Usuarios: ${u}`);
        console.log(`Vehiculos: ${v}`);
        console.log(`Neumaticos: ${n}`);
    } catch (e: any) {
        console.error('❌ DB ERROR:', e?.message || e);
    }
    console.log('--- END QUERY ---');
}

main()
    .catch((e: any) => console.error(e))
    .finally(async () => await prisma.$disconnect());
