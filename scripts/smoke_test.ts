import 'dotenv/config';
import { PrismaClient } from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';
import { Pool } from 'pg';

// Setup Driver Adapter (Required for Prisma 7 with this config)
const connectionString = process.env.DATABASE_URL;
const pool = new Pool({
    connectionString,
    ssl: connectionString?.includes('localhost') ? false : { rejectUnauthorized: false }
});
const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter });

async function main() {
    console.log('🚀 Iniciando Smoke Test Post-Migración (Adapter Mode)...');

    try {
        // 1. Verificar conexión y Counts
        const neumaticos = await prisma.neumatico.count();
        const vehiculos = await prisma.vehiculo.count();
        const almacenes = await prisma.almacen.count();

        console.log(`✅ Conexión OK. Estadísticas actuales:
      - Neumáticos: ${neumaticos}
      - Vehículos: ${vehiculos}
      - Almacenes: ${almacenes}
    `);

        // 2. Verificar datos enriquecidos en Vehículo
        const vehiculo = await prisma.vehiculo.findFirst({
            orderBy: { creado_en: 'desc' }
        });

        if (vehiculo) {
            console.log(`🚗 Vehículo muestra:
          - Placa: ${vehiculo.placa}
          - Económico: ${vehiculo.numero_economico} (Nuevo!)
          - Odómetro: ${vehiculo.odometro_actual} km
        `);
        } else {
            console.warn('⚠️ No hay vehículos para validar.');
        }

        // 3. Verificar Neumático y sus nuevas relaciones (Modelo -> Fabricante)
        const neumatico = await prisma.neumatico.findFirst({
            include: {
                modelo: {
                    include: { fabricante: true }
                },
                proveedor_compra: true
            }
        });

        if (neumatico) {
            console.log(`🍩 Neumático muestra:
          - ID: ${neumatico.id}
          - Serie: ${neumatico.numero_serie || 'N/A'}
          - Estado: ${neumatico.estado_actual}
          - Profundidad Remanente: ${neumatico.profundidad_remanente_actual_mm} mm
          - Modelo: ${neumatico.modelo?.nombre_modelo}
          - Fabricante: ${neumatico.modelo?.fabricante?.nombre}
        `);
        } else {
            console.warn('⚠️ No hay neumáticos para validar.');
        }

        console.log('✨ Smoke Test completado exitosamente. La API debería fluir.');
    } catch (error) {
        console.error('❌ Error en Smoke Test:', error);
        process.exit(1);
    }
}

main()
    .catch(e => {
        console.error('❌ Error fatal:', e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
        await pool.end();
    });
