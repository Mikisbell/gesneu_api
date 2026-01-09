import 'dotenv/config';
import { prisma } from '../src/lib/prisma';

async function main() {
    console.log('🔍 Checking for duplicate serial numbers in Neumatico table...');

    const duplicates = await prisma.neumatico.groupBy({
        by: ['numero_serie'],
        having: {
            numero_serie: {
                _count: {
                    gt: 1
                }
            }
        },
        where: {
            numero_serie: {
                not: null
            }
        },
        _count: {
            numero_serie: true
        }
    });

    if (duplicates.length > 0) {
        console.error('❌ Found duplicate serial numbers:');
        duplicates.forEach(d => {
            console.log(`  - Serial: "${d.numero_serie}" (Count: ${d._count.numero_serie})`);
        });
        console.log('\n⚠️ Cannot apply @unique constraint until duplicates are resolved.');
        process.exit(1);
    } else {
        console.log('✅ No duplicate serial numbers found. Safe to apply @unique.');
    }
}

main()
    .catch(e => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });
