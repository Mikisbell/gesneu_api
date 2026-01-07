
import 'dotenv/config';
import { PrismaClient, SeveridadAlertaEnum, TipoAlertaEnum } from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';
import { Pool } from 'pg';

const connectionString = process.env.DATABASE_URL;
const pool = new Pool({
    connectionString,
    ssl: connectionString?.includes('localhost') ? false : { rejectUnauthorized: false },
    max: 10
});
const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter });

const randomInt = (min: number, max: number) => Math.floor(Math.random() * (max - min) + min);
const randomFloat = (min: number, max: number) => parseFloat((Math.random() * (max - min) + min).toFixed(2));

async function main() {
    console.log('📜 GENERANDO HISTORIAL OPTIMIZADO (Secuencial)...');

    const neumaticos = await prisma.neumatico.findMany({
        where: { estado_actual: 'INSTALADO' },
        select: { id: true, kilometraje_acumulado: true },
        take: 500
    });

    console.log(`🎯 Procesando ${neumaticos.length} neumáticos en lotes secuenciales...`);

    const BATCH_SIZE = 10;
    for (let i = 0; i < neumaticos.length; i += BATCH_SIZE) {
        const batch = neumaticos.slice(i, i + BATCH_SIZE);

        await Promise.all(batch.map(async (n) => {
            await prisma.lecturaPresion.create({
                data: {
                    neumatico_id: n.id,
                    presion_psi: randomInt(95, 115),
                    fecha_lectura: new Date()
                }
            });

            await prisma.medicionProfundidad.create({
                data: {
                    neumatico_id: n.id,
                    profundidad_prom: randomFloat(8, 14),
                    profundidad_int: randomFloat(8, 14),
                    profundidad_cen: randomFloat(8, 14),
                    profundidad_ext: randomFloat(8, 14),
                    fecha_medicion: new Date(),
                    kilometraje: n.kilometraje_acumulado || 0
                }
            });

            // Alerta (Restaurada)
            if (Math.random() > 0.8) {
                await prisma.alerta.create({
                    data: {
                        neumatico_id: n.id,
                        tipo: TipoAlertaEnum.PRESION_BAJA,
                        severidad: SeveridadAlertaEnum.WARNING,
                        mensaje: 'Presión detectada fuera de rango óptimo (Simulada)',
                        leida: false
                    }
                });
            }
        }));
        process.stdout.write('.');
    }
    console.log('\n✅ Carga Histórica Completada sin saturar Pool.');
}

main()
    .finally(async () => {
        await prisma.$disconnect();
        await pool.end();
    });
