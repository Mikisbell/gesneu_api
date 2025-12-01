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

const CONFIGS = {
    'TRACTO': [ // 6x4
        { numero: 1, tipo: 'DIRECCION', llantas: 2, reencauche: false },
        { numero: 2, tipo: 'TRACCION', llantas: 4, reencauche: true },
        { numero: 3, tipo: 'TRACCION', llantas: 4, reencauche: true }
    ],
    'VOLQUETE': [ // 6x4
        { numero: 1, tipo: 'DIRECCION', llantas: 2, reencauche: false },
        { numero: 2, tipo: 'TRACCION', llantas: 4, reencauche: true },
        { numero: 3, tipo: 'TRACCION', llantas: 4, reencauche: true }
    ],
    'CAMIONETA': [ // 4x2 o 4x4
        { numero: 1, tipo: 'DIRECCION', llantas: 2, reencauche: false },
        { numero: 2, tipo: 'TRACCION', llantas: 2, reencauche: false }
    ],
    'BUS': [ // 4x2
        { numero: 1, tipo: 'DIRECCION', llantas: 2, reencauche: false },
        { numero: 2, tipo: 'TRACCION', llantas: 4, reencauche: true }
    ],
    'SEMIRREMOLQUE': [ // 3 ejes arrastre
        { numero: 1, tipo: 'ARRASTRE', llantas: 4, reencauche: true },
        { numero: 2, tipo: 'ARRASTRE', llantas: 4, reencauche: true },
        { numero: 3, tipo: 'ARRASTRE', llantas: 4, reencauche: true }
    ],
    'LINEA_AMARILLA': [ // Genérico 2 ejes
        { numero: 1, tipo: 'TRACCION', llantas: 2, reencauche: true },
        { numero: 2, tipo: 'TRACCION', llantas: 2, reencauche: true }
    ]
};

// Mapeo de nombres de BD a templates
const TYPE_MAPPING = {
    'TRACTO': 'TRACTO',
    'TRACTO 6X4': 'TRACTO',
    'TRACTO SEMITRAILER': 'TRACTO',
    'VOLQUETE': 'VOLQUETE',
    'CAMIONETA ': 'CAMIONETA',
    'BUS': 'BUS',
    'MICROBUS': 'BUS',
    'MINIBUS': 'BUS',
    'OMNIBUS ': 'BUS',
    'SEMIRREMOLQUE': 'SEMIRREMOLQUE',
    'CISTERNA COMBUSTIBLE': 'SEMIRREMOLQUE', // Asumimos configuración de carreta
    'CISTERNA AGUA': 'VOLQUETE', // Cisternas sobre chasis rígido suelen ser como volquetes
    'CARGADOR FRONTAL': 'LINEA_AMARILLA',
    'RETROEXCAVADORA': 'LINEA_AMARILLA',
    'MOTONIVELADORA': 'LINEA_AMARILLA', // Simplificación (moto tiene 3 ejes)
    'RODILLO': 'LINEA_AMARILLA'
};

async function createConfigs() {
    console.log('🔧 Creando configuraciones de ejes...');

    const tipos = await prisma.tipoVehiculo.findMany({
        include: { configuraciones: true }
    });

    for (const tipo of tipos) {
        if (tipo.configuraciones.length > 0) {
            console.log(`⏭️  ${tipo.nombre} ya tiene configuración`);
            continue;
        }

        // Buscar template
        let templateName = 'LINEA_AMARILLA'; // Default
        for (const [key, value] of Object.entries(TYPE_MAPPING)) {
            if (tipo.nombre.includes(key)) {
                templateName = value;
                break;
            }
        }

        const configTemplate = CONFIGS[templateName];
        if (!configTemplate) continue;

        console.log(`🔨 Configurando ${tipo.nombre} como ${templateName}...`);

        for (const ejeConfig of configTemplate) {
            // Crear Eje
            const eje = await prisma.configuracionEje.create({
                data: {
                    tipo_vehiculo_id: tipo.id,
                    numero_eje: ejeConfig.numero,
                    tipo_eje: ejeConfig.tipo,
                    posiciones_neumatico: ejeConfig.llantas,
                    permite_reencauchados: ejeConfig.reencauche
                }
            });

            // Crear Posiciones
            const posiciones = [];
            if (ejeConfig.llantas === 2) {
                posiciones.push({ num: 1, lado: 'IZQUIERDO' });
                posiciones.push({ num: 2, lado: 'DERECHO' });
            } else if (ejeConfig.llantas === 4) {
                posiciones.push({ num: 1, lado: 'IZQUIERDO' }); // Ext
                posiciones.push({ num: 2, lado: 'IZQUIERDO' }); // Int
                posiciones.push({ num: 3, lado: 'DERECHO' });   // Int
                posiciones.push({ num: 4, lado: 'DERECHO' });   // Ext
            }

            for (const pos of posiciones) {
                await prisma.posicionNeumatico.create({
                    data: {
                        configuracion_eje_id: eje.id,
                        numero_posicion: pos.num,
                        lado_vehiculo: pos.lado
                    }
                });
            }
        }
    }

    console.log('✅ Configuraciones creadas exitosamente');
    process.exit(0);
}

createConfigs().catch(e => {
    console.error(e);
    process.exit(1);
});
