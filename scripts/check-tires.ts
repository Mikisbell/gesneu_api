import { prisma } from '@/lib/prisma';

async function main() {
    console.log('--- Verificando Neumáticos ---');
    try {
        const count = await prisma.neumatico.count();
        console.log(`Total de neumáticos: ${count}`);

        if (count > 0) {
            const sample = await prisma.neumatico.findMany({
                take: 5,
                orderBy: { creado_en: 'desc' },
                include: { modelo: true }
            });
            console.log('Últimos 5 neumáticos:');
            sample.forEach(n => {
                console.log(`- ${n.numero_serie} (${n.modelo.nombre_modelo}) - Estado: ${n.estado_actual}`);
            });
        }
    } catch (e) {
        console.error('Error consultando DB:', e);
    }
}

main();
