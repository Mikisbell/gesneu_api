#!/usr/bin/env node

const Logger = require('./scripts/import/utils/logger');
const prisma = require('./scripts/import/utils/prismaClient');
const NeumaticosImporter = require('./scripts/import/importers/importNeumaticos');
const config = require('./scripts/import/config');

async function main() {
    const logger = new Logger();

    console.log('\n' + '='.repeat(80));
    console.log('🍩 EJECUTANDO SOLO FASE 4: HISTÓRICO DE NEUMÁTICOS');
    console.log('='.repeat(80));

    try {
        const neumaticosImporter = new NeumaticosImporter(logger);
        await neumaticosImporter.import();

        logger.printSummary();
        process.exit(0);
    } catch (error) {
        logger.error('Error crítico', error);
        process.exit(1);
    } finally {
        await prisma.$disconnect();
    }
}

main();
