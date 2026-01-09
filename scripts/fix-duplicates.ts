import 'dotenv/config';
import { prisma } from '../src/lib/prisma';

async function main() {
    console.log('🧹 Starting intelligent deduplication of tire serial numbers...');

    // 1. Find duplicates again to be sure
    const duplicates = await prisma.neumatico.groupBy({
        by: ['numero_serie'],
        having: {
            numero_serie: {
                _count: { gt: 1 }
            }
        },
        where: { numero_serie: { not: null } },
        _count: { numero_serie: true }
    });

    console.log(`📉 Found ${duplicates.length} serial numbers with conflicts.`);

    for (const group of duplicates) {
        if (!group.numero_serie) continue;
        const serial = group.numero_serie;

        // 2. Fetch all full records for this serial
        const records = await prisma.neumatico.findMany({
            where: { numero_serie: serial },
            orderBy: { creado_en: 'desc' }, // Latest first
            include: {
                eventos: true,
                lecturas_presion: true
            }
        });

        console.log(`\nProcessing "${serial}" (${records.length} records)...`);

        // Strategy: Keep the one with the most data (events + readings), or the latest if equal.
        // We will assign a score.
        const scored = records.map(r => ({
            id: r.id,
            score: r.eventos.length + r.lecturas_presion.length + (r.estado_actual !== 'EN_STOCK' ? 2 : 0), // Bonus for being active/installed
            date: r.creado_en
        })).sort((a, b) => b.score - a.score || b.date.getTime() - a.date.getTime());

        const winner = scored[0];
        const losers = scored.slice(1);

        console.log(`   ✅ Winner: ${winner.id} (Score: ${winner.score}, Date: ${winner.date.toISOString()})`);

        // 3. Delete losers
        for (const loser of losers) {
            console.log(`   ❌ Deleting duplicate: ${loser.id} (Score: ${loser.score})`);

            // Delete related data first if cascade isn't set (though Prisma usually handles cascade if configured, better be safe/explicit or rely on cascade)
            // schema says relations exist. Let's try raw delete of neumatico, assuming cascade or that we need to clean children.
            // Actually, EventoNeumatico has neumatico_id. If we delete neumatico, we might break integrity if no Cascade.
            // Let's check schema for OnDelete.
            // In schema.prisma: `neumatico Neumatico @relation(fields: [neumatico_id], references: [id])` -> Default is usually Restrict or Cascade depending on DB.
            // Safest strictly for this cleanup: Delete children first.

            await prisma.eventoNeumatico.deleteMany({ where: { neumatico_id: loser.id } });
            await prisma.lecturaPresion.deleteMany({ where: { neumatico_id: loser.id } });
            await prisma.historialEstadoNeumatico.deleteMany({ where: { neumatico_id: loser.id } });
            await prisma.alerta.deleteMany({ where: { neumatico_id: loser.id } });
            // ... add other relations if needed

            await prisma.neumatico.delete({ where: { id: loser.id } });
        }
    }

    console.log('\n✨ Deduplication complete. Database is ready for unique constraint.');
}

main()
    .catch(e => {
        console.error('Script error:', e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });
