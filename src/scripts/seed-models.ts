import 'dotenv/config'
import { PrismaClient } from '@prisma/client'
import { PrismaPg } from '@prisma/adapter-pg'
import { Pool } from 'pg'

const connectionString = process.env.DATABASE_URL
const pool = new Pool({
    connectionString,
    ssl: false,
})
const adapter = new PrismaPg(pool)
const prisma = new PrismaClient({ adapter })

async function seedModels() {
    console.log('🌱 Populating standard commercial tire models catalog...')

    const fabricantesData = [
        { nombre: 'MICHELIN', codigo_abreviado: 'MI', pais_origen: 'Francia', sitio_web: 'https://www.michelin.com' },
        { nombre: 'GOODYEAR', codigo_abreviado: 'GY', pais_origen: 'EE.UU.', sitio_web: 'https://www.goodyear.com' },
        { nombre: 'BRIDGESTONE', codigo_abreviado: 'BS', pais_origen: 'Japón', sitio_web: 'https://www.bridgestone.com' },
        { nombre: 'CONTINENTAL', codigo_abreviado: 'CON', pais_origen: 'Alemania', sitio_web: 'https://www.continental-tires.com' },
        { nombre: 'PIRELLI', codigo_abreviado: 'PIR', pais_origen: 'Italia', sitio_web: 'https://www.pirelli.com' },
        { nombre: 'HANKOOK', codigo_abreviado: 'HK', pais_origen: 'Corea del Sur', sitio_web: 'https://www.hankooktire.com' },
        { nombre: 'YOKOHAMA', codigo_abreviado: 'YOK', pais_origen: 'Japón', sitio_web: 'https://www.yokohamatire.com' },
        { nombre: 'KUMHO', codigo_abreviado: 'KH', pais_origen: 'Corea del Sur', sitio_web: 'https://www.kumhotire.com' },
        { nombre: 'TOYO', codigo_abreviado: 'TY', pais_origen: 'Japón', sitio_web: 'https://www.toyotires.com' },
        { nombre: 'DUNLOP', codigo_abreviado: 'DUN', pais_origen: 'Reino Unido', sitio_web: 'https://www.dunlop.com' },
        { nombre: 'FIRESTONE', codigo_abreviado: 'FS', pais_origen: 'EE.UU.', sitio_web: 'https://www.firestonetire.com' },
        { nombre: 'DOUBLE COIN', codigo_abreviado: 'DC', pais_origen: 'China', sitio_web: 'https://www.doublecointires.com' },
        { nombre: 'LINGLONG', codigo_abreviado: 'LL', pais_origen: 'China', sitio_web: 'https://www.linglongtire.com' },
        { nombre: 'SAILUN', codigo_abreviado: 'SL', pais_origen: 'China', sitio_web: 'https://www.sailuntire.com' },
        { nombre: 'TRIANGLE', codigo_abreviado: 'TR', pais_origen: 'China', sitio_web: 'https://www.triangletire.com' },
        { nombre: 'GITI', codigo_abreviado: 'GT', pais_origen: 'Singapur', sitio_web: 'https://www.giti.com' },
        { nombre: 'BKT', codigo_abreviado: 'BKT', pais_origen: 'India', sitio_web: 'https://www.bkt-tires.com' },
        { nombre: 'AEOLUS', codigo_abreviado: 'AEO', pais_origen: 'China', sitio_web: 'https://www.aeolustire.com' },
        { nombre: 'MAXXIS', codigo_abreviado: 'MX', pais_origen: 'Taiwán', sitio_web: 'https://www.maxxis.com' },
        { nombre: 'WESTLAKE', codigo_abreviado: 'WL', pais_origen: 'China', sitio_web: 'https://www.westlaketire.com' },
    ];

    const fabMap = new Map();
    for (const f of fabricantesData) {
        const fab = await prisma.fabricanteNeumatico.upsert({
            where: { codigo_abreviado: f.codigo_abreviado },
            update: {
                nombre: f.nombre,
                pais_origen: f.pais_origen,
                sitio_web: f.sitio_web
            },
            create: {
                nombre: f.nombre,
                codigo_abreviado: f.codigo_abreviado,
                pais_origen: f.pais_origen,
                sitio_web: f.sitio_web
            }
        });
        fabMap.set(f.codigo_abreviado, fab);
    }

    const modelosData = [
        // Goodyear
        { fabCode: 'GY', nombre: 'KMAX S', medida: '295/80R22.5', profOrig: 15.8, profRetiro: 3.0, psi: 110, reencauches: 2, permiteReencauche: true, patron: 'DIRECCIONAL', tipoServicio: 'REGIONAL', carga: '152', vel: 'M' },
        { fabCode: 'GY', nombre: 'KMAX D', medida: '295/80R22.5', profOrig: 21.0, profRetiro: 3.0, psi: 115, reencauches: 3, permiteReencauche: true, patron: 'TRACCION', tipoServicio: 'REGIONAL', carga: '154', vel: 'L' },
        { fabCode: 'GY', nombre: 'OMNITRAC MSD II', medida: '295/80R22.5', profOrig: 23.5, profRetiro: 4.0, psi: 120, reencauches: 2, permiteReencauche: true, patron: 'TRACCION', tipoServicio: 'MIXTO/OFF-ROAD', carga: '154', vel: 'K' },
        { fabCode: 'GY', nombre: 'MARATHON LHT', medida: '295/80R22.5', profOrig: 14.0, profRetiro: 2.0, psi: 105, reencauches: 2, permiteReencauche: true, patron: 'REMOLQUE', tipoServicio: 'LARGA DISTANCIA', carga: '150', vel: 'M' },

        // Michelin
        { fabCode: 'MI', nombre: 'X MULTI Z', medida: '295/80R22.5', profOrig: 16.0, profRetiro: 3.0, psi: 110, reencauches: 3, permiteReencauche: true, patron: 'TODA POSICION', tipoServicio: 'REGIONAL', carga: '152', vel: 'M' },
        { fabCode: 'MI', nombre: 'X WORKS XDY', medida: '295/80R22.5', profOrig: 22.0, profRetiro: 4.0, psi: 120, reencauches: 2, permiteReencauche: true, patron: 'TRACCION', tipoServicio: 'MIXTO/OFF-ROAD', carga: '154', vel: 'K' },
        { fabCode: 'MI', nombre: 'X LINE ENERGY T', medida: '295/80R22.5', profOrig: 14.5, profRetiro: 2.0, psi: 105, reencauches: 2, permiteReencauche: true, patron: 'REMOLQUE', tipoServicio: 'LARGA DISTANCIA', carga: '150', vel: 'M' },
        { fabCode: 'MI', nombre: 'X MULTI D', medida: '295/80R22.5', profOrig: 20.0, profRetiro: 3.0, psi: 115, reencauches: 3, permiteReencauche: true, patron: 'TRACCION', tipoServicio: 'REGIONAL', carga: '152', vel: 'L' },

        // Bridgestone
        { fabCode: 'BS', nombre: 'R268 ECOPIA', medida: '295/80R22.5', profOrig: 16.5, profRetiro: 3.0, psi: 110, reencauches: 3, permiteReencauche: true, patron: 'TODA POSICION', tipoServicio: 'REGIONAL', carga: '152', vel: 'M' },
        { fabCode: 'BS', nombre: 'M726 ELA', medida: '295/80R22.5', profOrig: 24.0, profRetiro: 3.5, psi: 120, reencauches: 3, permiteReencauche: true, patron: 'TRACCION', tipoServicio: 'LARGA DISTANCIA', carga: '154', vel: 'L' },
        { fabCode: 'BS', nombre: 'R197 ECOPIA', medida: '295/80R22.5', profOrig: 13.5, profRetiro: 2.0, psi: 105, reencauches: 2, permiteReencauche: true, patron: 'REMOLQUE', tipoServicio: 'LARGA DISTANCIA', carga: '150', vel: 'M' },
        { fabCode: 'BS', nombre: 'M840', medida: '295/80R22.5', profOrig: 21.5, profRetiro: 4.0, psi: 115, reencauches: 2, permiteReencauche: true, patron: 'TODA POSICION', tipoServicio: 'MIXTO/OFF-ROAD', carga: '154', vel: 'K' },

        // Continental
        { fabCode: 'CON', nombre: 'HSR2', medida: '295/80R22.5', profOrig: 16.0, profRetiro: 3.0, psi: 110, reencauches: 3, permiteReencauche: true, patron: 'DIRECCIONAL', tipoServicio: 'REGIONAL', carga: '152', vel: 'M' },
        { fabCode: 'CON', nombre: 'HDR2', medida: '295/80R22.5', profOrig: 21.0, profRetiro: 3.0, psi: 115, reencauches: 3, permiteReencauche: true, patron: 'TRACCION', tipoServicio: 'REGIONAL', carga: '152', vel: 'L' },
        { fabCode: 'CON', nombre: 'HSC1', medida: '295/80R22.5', profOrig: 22.5, profRetiro: 4.0, psi: 120, reencauches: 2, permiteReencauche: true, patron: 'TRACCION', tipoServicio: 'MIXTO/OFF-ROAD', carga: '154', vel: 'K' },

        // Pirelli
        { fabCode: 'PIR', nombre: 'FH:01 ENERGY', medida: '295/80R22.5', profOrig: 15.5, profRetiro: 3.0, psi: 110, reencauches: 3, permiteReencauche: true, patron: 'DIRECCIONAL', tipoServicio: 'LARGA DISTANCIA', carga: '152', vel: 'M' },
        { fabCode: 'PIR', nombre: 'TH:01 ENERGY', medida: '295/80R22.5', profOrig: 20.5, profRetiro: 3.0, psi: 115, reencauches: 3, permiteReencauche: true, patron: 'TRACCION', tipoServicio: 'LARGA DISTANCIA', carga: '152', vel: 'L' },
        { fabCode: 'PIR', nombre: 'ST:01 BASE', medida: '295/80R22.5', profOrig: 14.0, profRetiro: 2.0, psi: 105, reencauches: 2, permiteReencauche: true, patron: 'REMOLQUE', tipoServicio: 'REGIONAL', carga: '150', vel: 'M' },

        // Hankook
        { fabCode: 'HK', nombre: 'AH31', medida: '295/80R22.5', profOrig: 16.0, profRetiro: 3.0, psi: 110, reencauches: 2, permiteReencauche: true, patron: 'TODA POSICION', tipoServicio: 'REGIONAL', carga: '152', vel: 'M' },
        { fabCode: 'HK', nombre: 'DH31', medida: '295/80R22.5', profOrig: 21.0, profRetiro: 3.0, psi: 115, reencauches: 2, permiteReencauche: true, patron: 'TRACCION', tipoServicio: 'REGIONAL', carga: '152', vel: 'L' },

        // Double Coin
        { fabCode: 'DC', nombre: 'RR680', medida: '295/80R22.5', profOrig: 15.5, profRetiro: 3.0, psi: 110, reencauches: 2, permiteReencauche: true, patron: 'TODA POSICION', tipoServicio: 'REGIONAL', carga: '152', vel: 'M' },
        { fabCode: 'DC', nombre: 'RLB400', medida: '295/80R22.5', profOrig: 23.0, profRetiro: 3.5, psi: 120, reencauches: 2, permiteReencauche: true, patron: 'TRACCION', tipoServicio: 'REGIONAL', carga: '154', vel: 'K' },

        // Firestone
        { fabCode: 'FS', nombre: 'FS561', medida: '295/80R22.5', profOrig: 15.5, profRetiro: 3.0, psi: 110, reencauches: 2, permiteReencauche: true, patron: 'DIRECCIONAL', tipoServicio: 'REGIONAL', carga: '152', vel: 'M' },
        { fabCode: 'FS', nombre: 'FD691', medida: '295/80R22.5', profOrig: 22.0, profRetiro: 3.5, psi: 115, reencauches: 2, permiteReencauche: true, patron: 'TRACCION', tipoServicio: 'LARGA DISTANCIA', carga: '154', vel: 'L' },
    ];

    let count = 0
    for (const m of modelosData) {
        const fab = fabMap.get(m.fabCode);
        if (fab) {
            await prisma.modeloNeumatico.upsert({
                where: { fabricante_id_nombre_modelo_medida: { fabricante_id: fab.id, nombre_modelo: m.nombre, medida: m.medida } },
                update: {
                    profundidad_original_mm: m.profOrig,
                    profundidad_minima_retiro_mm: m.profRetiro,
                    presion_recomendada_psi: m.psi,
                    reencauches_maximos: m.reencauches,
                    permite_reencauche: m.permiteReencauche,
                    patron_dibujo: m.patron,
                    tipo_servicio: m.tipoServicio,
                    indice_carga: m.carga,
                    indice_velocidad: m.vel
                },
                create: {
                    nombre_modelo: m.nombre,
                    medida: m.medida,
                    profundidad_original_mm: m.profOrig,
                    profundidad_minima_retiro_mm: m.profRetiro,
                    presion_recomendada_psi: m.psi,
                    fabricante_id: fab.id,
                    reencauches_maximos: m.reencauches,
                    permite_reencauche: m.permiteReencauche,
                    patron_dibujo: m.patron,
                    tipo_servicio: m.tipoServicio,
                    indice_carga: m.carga,
                    indice_velocidad: m.vel
                }
            });
            count++;
        }
    }

    console.log(`✅ Successfully seeded ${count} commercial tire models into database!`)
}

seedModels()
    .then(() => process.exit(0))
    .catch((err) => {
        console.error('❌ Error seeding models:', err)
        process.exit(1)
    })
