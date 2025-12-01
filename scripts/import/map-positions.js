require('dotenv').config({ path: '.env.local' });
const { PrismaClient } = require('@prisma/client');
const { PrismaPg } = require('@prisma/adapter-pg');
const { Pool } = require('pg');

const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false },
});

const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter });

async function mapPositions() {
    console.log('📍 Mapeando posiciones de neumáticos...');

    // 1. Obtener todos los eventos de instalación para saber la posición original (P1, P2...)
    // Buscamos eventos de instalación recientes
    const instalaciones = await prisma.eventoNeumatico.findMany({
        where: { tipo_evento: 'INSTALACION' },
        include: {
            neumatico: true,
            vehiculo: {
                include: {
                    tipo_vehiculo: {
                        include: {
                            configuraciones: {
                                include: { posiciones: true }
                            }
                        }
                    }
                }
            }
        }
    });

    console.log(`Encontradas ${instalaciones.length} instalaciones para procesar`);

    let updatedCount = 0;

    for (const evento of instalaciones) {
        if (!evento.notas || !evento.vehiculo) continue;

        // Extraer P1, P2, etc. de las notas "Pos: P1"
        const match = evento.notas.match(/Pos: (P\d+|[0-9]+)/);
        if (!match) continue;

        const posCode = match[1].replace('P', ''); // "1", "2", "10"
        const posNum = parseInt(posCode);

        // Lógica de mapeo basada en el tipo de vehículo (Tracto/Volquete vs otros)
        // Asumimos lógica estándar de flotas:
        // Eje 1: 1, 2
        // Eje 2: 3, 4, 5, 6
        // Eje 3: 7, 8, 9, 10

        let targetEjeIdx = -1; // 0-based index en el array de configuraciones
        let targetPosNum = -1; // 1-4

        if (posNum <= 2) {
            targetEjeIdx = 0;
            targetPosNum = posNum;
        } else if (posNum <= 6) {
            targetEjeIdx = 1;
            targetPosNum = posNum - 2;
        } else if (posNum <= 10) {
            targetEjeIdx = 2;
            targetPosNum = posNum - 6;
        } else {
            // Eje 4?
            targetEjeIdx = 3;
            targetPosNum = posNum - 10;
        }

        const configs = evento.vehiculo.tipo_vehiculo.configuraciones.sort((a, b) => a.numero_eje - b.numero_eje);

        if (!configs[targetEjeIdx]) continue;

        const eje = configs[targetEjeIdx];
        const posicionReal = eje.posiciones.find(p => p.numero_posicion === targetPosNum);

        if (posicionReal) {
            // Actualizar Neumático
            await prisma.neumatico.update({
                where: { id: evento.neumatico_id },
                data: {
                    ubicacion_posicion_id: posicionReal.id
                }
            });

            // Actualizar Evento también (opcional pero bueno para consistencia)
            await prisma.eventoNeumatico.update({
                where: { id: evento.id },
                data: {
                    posicion_montaje_id: posicionReal.id
                }
            });

            updatedCount++;
            if (updatedCount % 50 === 0) process.stdout.write('.');
        }
    }

    console.log(`\n✅ ${updatedCount} neumáticos mapeados a posiciones físicas`);
    process.exit(0);
}

mapPositions().catch(e => {
    console.error(e);
    process.exit(1);
});
