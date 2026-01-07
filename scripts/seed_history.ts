
import 'dotenv/config';
import { PrismaClient, TipoMedicionEnum, TipoEventoNeumaticoEnum, TipoAlertaEnum, SeveridadAlertaEnum } from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';
import { Pool } from 'pg';

// --- CONFIGURACIÓN DE CONEXIÓN ---
const connectionString = process.env.DATABASE_URL;
const pool = new Pool({
    connectionString,
    ssl: connectionString?.includes('localhost') ? false : { rejectUnauthorized: false },
    max: 20
});
const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter });

const randomInt = (min: number, max: number) => Math.floor(Math.random() * (max - min + 1)) + min;
const randomFloat = (min: number, max: number) => parseFloat((Math.random() * (max - min) + min).toFixed(2));

async function main() {
    console.log('📜 GENERANDO HISTORIAL MASIVO (Mediciones, Eventos, Alertas)...');

    // Obtener neumáticos instalados
    const neumaticos = await prisma.neumatico.findMany({
        where: { estado_actual: 'INSTALADO' },
        select: { id: true, kilometraje_acumulado: true }
    });

    console.log(`🎯 Procesando historial para ${neumaticos.length} neumáticos instalados...`);

    // Batch processing to avoid memory issues
    const BATCH_SIZE = 50;
    for (let i = 0; i < neumaticos.length; i += BATCH_SIZE) {
        const batch = neumaticos.slice(i, i + BATCH_SIZE);
        const promises = batch.map(async (n) => {
            // 1. Mediciones de Presión (5 por neumático)
            for (let j = 0; j < 5; j++) {
                await prisma.lecturaPresion.create({
                    data: {
                        neumatico_id: n.id,
                        presion_psi: randomInt(90, 120),
                        fecha_lectura: new Date(Date.now() - j * 7 * 24 * 60 * 60 * 1000), // Semanal
                    }
                });
            }

            // 2. Mediciones de Profundidad (3 por neumático)
            for (let k = 0; k < 3; k++) {
                await prisma.medicionProfundidad.create({
                    data: {
                        neumatico_id: n.id,
                        profundidad_prom: randomFloat(5, 15),
                        profundidad_int: randomFloat(5, 15),
                        profundidad_cen: randomFloat(5, 15),
                        profundidad_ext: randomFloat(5, 15),
                        fecha_medicion: new Date(Date.now() - k * 30 * 24 * 60 * 60 * 1000), // Mensual
                        kilometraje: Math.max(0, (n.kilometraje_acumulado || 0) - (k * 4000))
                    }
                });
            }

            // 3. Evento de Inspección
            await prisma.eventoNeumatico.create({
                data: {
                    neumatico_id: n.id,
                    tipo_evento: TipoEventoNeumaticoEnum.INSPECCION,
                    fecha_evento: new Date(),
                    contador_vehiculo: n.kilometraje_acumulado || 0,
                    notas: 'Inspección de rutina OK'
                }
            });
        });

        await Promise.all(promises);
        process.stdout.write('.');
    }

    // 4. Generar Alertas (Simuladas)
    console.log('\n🚨 Generando Alertas...');
    const alertasTipo = [TipoAlertaEnum.PRESION_BAJA, TipoAlertaEnum.DESGASTE_IRREGULAR];

    for (let i = 0; i < 50; i++) {
        const n = neumaticos[randomInt(0, neumaticos.length - 1)];
        if (!n) continue;

        await prisma.alerta.create({
            data: {
                tipo: alertasTipo[randomInt(0, alertasTipo.length - 1)],
                severidad: SeveridadAlertaEnum.MEDIA, // Asumiendo Enum válido
                mensaje: 'Valor fuera de rango detectado en auditoría',
                neumatico_id: n.id,
                estado: 'PENDIENTE',
                fecha_detectada: new Date()
            }
        });
    }

    console.log('\n✅ HISTORIAL GENERADO CORRECTAMENTE.');
}

main()
    .catch(console.error)
    .finally(async () => {
        await prisma.$disconnect();
        await pool.end();
    });
