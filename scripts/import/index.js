#!/usr/bin/env node

const Logger = require('./utils/logger');
const prisma = require('./utils/prismaClient');
const MasterDataImporter = require('./importers/importMasterData');
const VehiculosImporter = require('./importers/importVehiculos');
const NeumaticosImporter = require('./importers/importNeumaticos');
const config = require('./config');

async function main() {
    const logger = new Logger();

    console.log('\n' + '='.repeat(80));
    console.log('🚀 SISTEMA PROFESIONAL DE IMPORTACIÓN DE DATOS');
    console.log('='.repeat(80));
    console.log(`Modo: ${config.DRY_RUN ? 'DRY RUN (Preview)' : 'PRODUCCIÓN'}`);
    console.log(`Archivo: ${config.FILES.CONTROL_MANTENIMIENTO}`);
    console.log('='.repeat(80) + '\n');

    try {
        // Verificar conexión a BD
        logger.info('Verificando conexión a base de datos...');
        await prisma.$queryRaw`SELECT 1`;
        logger.success('✓ Conexión a base de datos exitosa');

        // FASE 1: Datos Maestros
        logger.info('\n🔧 Iniciando FASE 1: Datos Maestros');
        const masterDataImporter = new MasterDataImporter(logger);
        await prisma.$transaction(async (tx) => {
            // Temporarily override prisma with transaction client
            const originalPrisma = global.prisma;
            global.prisma = tx;

            await masterDataImporter.import();

            global.prisma = originalPrisma;
        }, {
            maxWait: 30000,
            timeout: 120000
        });

        // FASE 2: Vehículos
        logger.info('\n🚗 Iniciando FASE 2: Vehículos');
        const vehiculosImporter = new VehiculosImporter(logger);
        await vehiculosImporter.import();

        // FASE 4: Histórico de Neumáticos
        logger.info('\n🍩 Iniciando FASE 4: Histórico de Neumáticos');
        const neumaticosImporter = new NeumaticosImporter(logger);
        await neumaticosImporter.import();

        // Resumen final
        logger.printSummary();

        // Verificación final
        logger.info('\n📊 Verificando datos importados...');
        const [vehiculos, centrosCosto, fabricantes, modelos, almacenes] = await Promise.all([
            prisma.vehiculo.count(),
            prisma.centroCosto.count(),
            prisma.fabricanteNeumatico.count(),
            prisma.modeloNeumatico.count(),
            prisma.almacen.count()
        ]);

        console.log('\n' + '='.repeat(80));
        console.log('✅ IMPORTACIÓN COMPLETADA EXITOSAMENTE');
        console.log('='.repeat(80));
        console.log(`Vehículos: ${vehiculos}`);
        console.log(`Centros de Costo: ${centrosCosto}`);
        console.log(`Fabricantes: ${fabricantes}`);
        console.log(`Modelos de Neumáticos: ${modelos}`);
        console.log(`Almacenes: ${almacenes}`);
        console.log('='.repeat(80) + '\n');

        process.exit(0);
    } catch (error) {
        logger.error('Error crítico en importación', error);
        logger.printSummary();
        process.exit(1);
    } finally {
        await prisma.$disconnect();
    }
}

// Manejo de señales
process.on('SIGINT', async () => {
    console.log('\n\n⚠️  Importación interrumpida por el usuario');
    await prisma.$disconnect();
    process.exit(130);
});

process.on('unhandledRejection', (error) => {
    console.error('❌ Unhandled rejection:', error);
    process.exit(1);
});

main();
