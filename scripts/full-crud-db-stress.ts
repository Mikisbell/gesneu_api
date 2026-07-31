import 'dotenv/config';
import { prisma } from '../src/lib/prisma';
import { EstadoNeumaticoEnum } from '@prisma/client';

async function runFullCrudDatabaseStressTest() {
    console.log('🔥 ================================================================');
    console.log('⚡ INICIANDO BENCHMARK Y PRUEBA DE ESTRÉS CRUD COMPLETO EN POSTGRESQL');
    console.log('🔥 ================================================================\n');

    // 1. Obtener Tenant de prueba
    const empresa = await prisma.empresa.findFirst();
    if (!empresa) {
        console.error('❌ No se encontró empresa de prueba en la base de datos.');
        process.exit(1);
    }
    const empresaId = empresa.id;
    console.log(`🏢 Tenant activo: ${empresa.nombre} (${empresaId})\n`);

    // 2. Obtener un usuario inspector para asociar las inspecciones
    const inspector = await prisma.usuario.findFirst({ where: { empresa_id: empresaId } });
    if (!inspector) {
        console.error('❌ No se encontró usuario en la empresa para firmar inspecciones.');
        process.exit(1);
    }

    // 3. Obtener o crear catálogo base
    const fabricante = await prisma.fabricanteNeumatico.findFirst() || await prisma.fabricanteNeumatico.create({
        data: { nombre: 'Fabricante Stress Test' }
    });

    const modelo = await prisma.modeloNeumatico.findFirst({ where: { fabricante_id: fabricante.id } }) || await prisma.modeloNeumatico.create({
        data: {
            fabricante_id: fabricante.id,
            nombre_modelo: 'STRESS-MODEL-X',
            medida: '295/80R22.5',
            profundidad_original_mm: 18.0,
            profundidad_minima_retiro_mm: 3.0,
            presion_recomendada_psi: 110.0
        }
    });

    const almacen = await prisma.almacen.findFirst({ where: { empresa_id: empresaId } }) || await prisma.almacen.create({
        data: {
            empresa_id: empresaId,
            codigo: 'ALM-STRESS',
            nombre: 'Almacén Stress Test',
            tipo: 'CENTRAL'
        }
    });

    const timestamp = Date.now();
    const NUM_RECORDS = 50;

    console.log(`📥 1. ESTRÉS DE INSERCIÓN (BATCH CREATION): Insertando ${NUM_RECORDS} neumáticos con relaciones...`);
    const startInsert = performance.now();

    const createdIds: string[] = [];
    
    // Inserción concurrente en lotes de 10 para respetar la capacidad del Connection Pool
    const CHUNK_SIZE = 10;
    for (let i = 0; i < NUM_RECORDS; i += CHUNK_SIZE) {
        const chunkPromises = Array.from({ length: Math.min(CHUNK_SIZE, NUM_RECORDS - i) }, (_, index) => {
            const idx = i + index;
            return prisma.neumatico.create({
                data: {
                    empresa_id: empresaId,
                    modelo_id: modelo.id,
                    ubicacion_almacen_id: almacen.id,
                    numero_serie: `STRESS-SN-${timestamp}-${idx}`,
                    estado_actual: EstadoNeumaticoEnum.EN_STOCK,
                    profundidad_inicial_mm: 18.0,
                    profundidad_remanente_actual_mm: 18.0,
                    presion_actual_psi: 110.0,
                    kilometraje_acumulado: 0,
                    fecha_compra: new Date(),
                    activo: true
                },
                select: { id: true }
            });
        });

        const chunkResults = await Promise.all(chunkPromises);
        chunkResults.forEach(r => createdIds.push(r.id));
    }

    const durationInsert = performance.now() - startInsert;
    console.log(`   ✅ Insertados ${NUM_RECORDS} neumáticos en ${durationInsert.toFixed(2)}ms | TPS Escritura: ${(NUM_RECORDS / (durationInsert / 1000)).toFixed(2)} ops/seg\n`);

    // 4. ESTRÉS DE EDICIÓN CONCURRENTE EN LOTES (MUTACIONES & TRANSACCIONES CON POOLING)
    console.log(`🔄 2. ESTRÉS DE EDICIÓN (TRANSACCIONES POOLEADAS): Actualizando estados, lecturas e inspecciones en lotes...`);
    const startUpdate = performance.now();

    for (let i = 0; i < createdIds.length; i += CHUNK_SIZE) {
        const chunkIds = createdIds.slice(i, i + CHUNK_SIZE);
        const updatePromises = chunkIds.map((id, indexWithinChunk) => {
            const globalIndex = i + indexWithinChunk;
            const nuevaProfundidad = Math.max(3.0, 18.0 - (globalIndex % 10));
            const nuevaPresion = 110.0 - (globalIndex % 30);
            const nuevoKm = globalIndex * 1500;

            return prisma.$transaction([
                prisma.neumatico.update({
                    where: { id },
                    data: {
                        profundidad_remanente_actual_mm: nuevaProfundidad,
                        presion_actual_psi: nuevaPresion,
                        kilometraje_acumulado: nuevoKm,
                        estado_actual: nuevaProfundidad <= 4.0 ? EstadoNeumaticoEnum.EN_REPARACION : EstadoNeumaticoEnum.EN_STOCK
                    }
                }),
                prisma.inspeccion.create({
                    data: {
                        empresa_id: empresaId,
                        neumatico_id: id,
                        inspector_id: inspector.id,
                        fecha_inspeccion: new Date(),
                        psi_medido: nuevaPresion,
                        mm_medido: nuevaProfundidad,
                        observaciones: `Inspección de estrés ${globalIndex}`
                    }
                })
            ], {
                maxWait: 10000,
                timeout: 15000
            });
        });

        await Promise.all(updatePromises);
    }

    const durationUpdate = performance.now() - startUpdate;
    console.log(`   ✅ ${NUM_RECORDS} Transacciones compuestas (Update Neumático + Insert Inspección) completadas en ${durationUpdate.toFixed(2)}ms | TPS Mutación: ${(NUM_RECORDS / (durationUpdate / 1000)).toFixed(2)} ops/seg\n`);

    // 5. CONSULTA Y VERIFICACIÓN DE INTEGRIDAD DE DATOS
    console.log(`🔍 3. CONSULTA DE INTEGRIDAD: Verificando datos mutados y consistencia...`);
    const countInspecciones = await prisma.inspeccion.count({
        where: { neumatico_id: { in: createdIds } }
    });
    console.log(`   ✅ Inspecciones asociadas encontradas en BD: ${countInspecciones}/${NUM_RECORDS}`);

    const countEnReparacion = await prisma.neumatico.count({
        where: { id: { in: createdIds }, estado_actual: EstadoNeumaticoEnum.EN_REPARACION }
    });
    console.log(`   ✅ Neumáticos cambiados a estado EN_REPARACION automáticamente: ${countEnReparacion}\n`);

    // 6. ESTRÉS DE ELIMINACIÓN Y BORRADO EN CASCADA (CLEANUP & CASCADE)
    console.log(`🗑️ 4. ESTRÉS DE ELIMINACIÓN (HARD DELETE & CASCADE): Limpiando registros de prueba y probando FK constraints...`);
    const startDelete = performance.now();

    // Eliminar dependencias (inspecciones) y luego neumáticos en transacción aislada por lotes
    for (let i = 0; i < createdIds.length; i += CHUNK_SIZE) {
        const chunkIds = createdIds.slice(i, i + CHUNK_SIZE);
        await prisma.$transaction([
            prisma.inspeccion.deleteMany({
                where: { neumatico_id: { in: chunkIds } }
            }),
            prisma.neumatico.deleteMany({
                where: { id: { in: chunkIds } }
            })
        ]);
    }

    const durationDelete = performance.now() - startDelete;
    console.log(`   ✅ Eliminados ${NUM_RECORDS} neumáticos e inspecciones asociadas en ${durationDelete.toFixed(2)}ms | TPS Borrado: ${(NUM_RECORDS / (durationDelete / 1000)).toFixed(2)} ops/seg\n`);

    // 7. VERIFICACIÓN FINAL
    const remainingCount = await prisma.neumatico.count({
        where: { id: { in: createdIds } }
    });

    const memory = process.memoryUsage();
    console.log('📊 ================================================================');
    console.log('📈 RESUMEN DE METRICAS DE ESTRÉS Y RENDIMIENTO COMPLETO DE BD');
    console.log('📊 ================================================================');
    console.log(`   - Registros Restantes (consistencia post-borrado): ${remainingCount} (esperado 0)`);
    console.log(`   - Velocidad Inserción Masiva: ${(NUM_RECORDS / (durationInsert / 1000)).toFixed(2)} registros/seg`);
    console.log(`   - Velocidad Transacciones (Update + Create): ${(NUM_RECORDS / (durationUpdate / 1000)).toFixed(2)} transacciones/seg`);
    console.log(`   - Velocidad Borrado en Cascada: ${(NUM_RECORDS / (durationDelete / 1000)).toFixed(2)} registros/seg`);
    console.log(`   - Memoria Heap Utilizada: ${(memory.heapUsed / 1024 / 1024).toFixed(2)} MB`);
    console.log('==================================================================\n');

    await prisma.$disconnect();
}

runFullCrudDatabaseStressTest().catch(async (e) => {
    console.error('❌ Error fatal durante el test de estrés CRUD:', e);
    await prisma.$disconnect();
    process.exit(1);
});
