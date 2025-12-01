#!/usr/bin/env node

require('dotenv').config({ path: '.env.local' });
const prisma = require('./utils/prismaClient');
const config = require('./config');

async function createAlmacenes() {
    console.log('🏢 Creando almacenes por defecto...\n');

    try {
        for (const almacen of config.DEFAULT_ALMACENES) {
            const existing = await prisma.almacen.findFirst({
                where: { nombre: almacen.nombre }
            });

            if (existing) {
                console.log(`⏭️  Almacén "${almacen.nombre}" ya existe`);
            } else {
                await prisma.almacen.create({ data: almacen });
                console.log(`✅ Almacén "${almacen.nombre}" creado`);
            }
        }

        console.log('\n✅ Almacenes creados exitosamente\n');
        process.exit(0);
    } catch (error) {
        console.error('❌ Error:', error.message);
        process.exit(1);
    } finally {
        await prisma.$disconnect();
    }
}

createAlmacenes();
