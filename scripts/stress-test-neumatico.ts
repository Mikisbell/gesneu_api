
import 'dotenv/config';
import { neumaticoService } from '../src/lib/services/neumatico.service';
import { fabricanteService } from '../src/lib/services/fabricante.service';
import { modeloNeumaticoService } from '../src/lib/services/modelo-neumatico.service';
import { prisma } from '../src/lib/prisma';
import { DEFAULT_TENANT_ID, DEFAULT_TENANT_NAME, DEFAULT_TENANT_RUC } from '../src/lib/constants';

async function main() {
    console.log('🚀 Starting STRESS TEST for Neumatico Core...\n');

    // --- SETUP ---
    console.log('📦 Setup Context...');
    await prisma.empresa.upsert({
        where: { id: DEFAULT_TENANT_ID },
        update: {},
        create: { id: DEFAULT_TENANT_ID, nombre: DEFAULT_TENANT_NAME, ruc: DEFAULT_TENANT_RUC }
    });

    const userId = '00000000-0000-0000-0000-000000000099'; // Stress User
    await prisma.usuario.upsert({
        where: { id: userId },
        update: {},
        create: {
            id: userId,
            empresa_id: DEFAULT_TENANT_ID,
            username: 'STRESS_TEST',
            nombre_completo: 'Stress Tester',
            email: 'stress@system.com',
            password_hash: 'hash',
            activo: true
        }
    });

    const fab = await fabricanteService.create({ nombre: `STRESS_FAB_${Date.now()}`, codigoAbreviado: `SF${Date.now().toString().slice(-4)}` });
    if (!fab.success) throw new Error('Fab setup failed');

    const modelo = await modeloNeumaticoService.create({
        fabricante_id: fab.data.id,
        nombre: `STRESS_MOD_${Date.now()}`,
        medida: '11R22.5',
        profundidad_original_mm: 20
    });
    if (!modelo.success) throw new Error('Model setup failed');

    const modelId = modelo.data.id;
    const createdIds: string[] = [];

    try {
        // --- TEST 1: RACE CONDITIONS (Same Serial) ---
        console.log('\n🧪 TEST 1: Race Condition (Duplicate Serial Check)...');
        const sharedSerial = `STRESS_RACE_${Date.now()}`;
        const raceAttempts = 5;
        console.log(`   Attempting to create ${raceAttempts} tires with serial ${sharedSerial} simultaneously...`);

        const promises = [];
        for (let i = 0; i < raceAttempts; i++) {
            promises.push(neumaticoService.create({
                modelo_id: modelId,
                numero_serie: sharedSerial,
                dot: '1024',
                fecha_compra: new Date().toISOString(),
                profundidad_actual_mm: 20,
                costo_compra: 1000,
                moneda_compra: 'PEN'
            }, DEFAULT_TENANT_ID, userId));
        }

        const results = await Promise.all(promises);
        const successes = results.filter(r => r.success);
        const failures = results.filter(r => !r.success);

        console.log(`   Results: ${successes.length} Success, ${failures.length} Failures.`);

        if (successes.length === 1) {
            console.log('✅ PASS: Only one creation succeeded, rest failed with Conflict.');
            createdIds.push(successes[0].data.id);
        } else if (successes.length > 1) {
            console.error('❌ FAIL: Critical! Multiple duplicates created!');
            console.error('   Duplicate IDs:', successes.map(s => s.data.id));
        } else {
            console.error('❌ FAIL: All failed? Or unexpected behavior.');
            console.error(failures.map(f => f.error));
        }


        // --- TEST 2: BULK LOAD (Performance) ---
        console.log('\n🧪 TEST 2: Bulk Load (50 Unique Tires) - Gentle Batching...');
        const bulkCount = 50;
        const batchSize = 5; // Reduced to 5 to handle transaction limits
        const createdInBulk: string[] = [];

        const start = performance.now();

        for (let i = 0; i < bulkCount; i += batchSize) {
            const batchPromises = [];
            for (let j = 0; j < batchSize && (i + j) < bulkCount; j++) {
                batchPromises.push(neumaticoService.create({
                    modelo_id: modelId,
                    numero_serie: `BULK_${Date.now()}_${i + j}`,
                    dot: '2024',
                    fecha_compra: new Date().toISOString(),
                    profundidad_actual_mm: 20
                }, DEFAULT_TENANT_ID, userId));
            }

            // Wait for batch
            const results = await Promise.all(batchPromises);
            results.forEach(r => {
                if (r.success) createdInBulk.push(r.data.id);
            });

            // Delay to prevent pool exhaustion
            await new Promise(r => setTimeout(r, 200));
        }

        const end = performance.now();
        const duration = end - start;
        createdIds.push(...createdInBulk);

        console.log(`   Processed ${bulkCount} requests in ${duration.toFixed(0)}ms.`);
        console.log(`   Average: ${(duration / bulkCount).toFixed(2)}ms/req.`);

        if (createdInBulk.length === bulkCount) {
            console.log('✅ PASS: All 50 created successfully.');
        } else {
            console.error(`❌ FAIL: Only ${createdInBulk.length}/${bulkCount} succeeded.`);
        }


        // --- TEST 3: ATOMIC UPDATES (Rapid Events) ---
        if (createdIds.length > 0) {
            const targetId = createdIds[createdIds.length - 1];
            console.log(`\n🧪 TEST 3: Atomic Updates on ID ${targetId}...`);

            const eventPromises = [];
            for (let i = 1; i <= 10; i++) {
                eventPromises.push(neumaticoService.registrarEvento({
                    tipo_evento: 'INSPECCION',
                    neumatico_id: targetId,
                    fecha_evento: new Date().toISOString(),
                    profundidad_remanente: 10 + i,
                    presion_psi: 100 + i,
                    observaciones: `Stress event ${i}`
                }, userId, DEFAULT_TENANT_ID));
            }

            await Promise.all(eventPromises);

            const finalState = await neumaticoService.getById(DEFAULT_TENANT_ID, targetId);
            if (finalState.success) {
                console.log(`   Final Depth: ${finalState.data.mediciones.profundidadActual}`);
                const evtCount = await prisma.eventoNeumatico.count({ where: { neumatico_id: targetId } });
                console.log(`   Actual Events in DB: ${evtCount}`);

                if (evtCount >= 11) console.log('✅ PASS: All events recorded.');
                else console.warn('⚠️ WARN: Some events missing?');
            }
        }

    } catch (e) {
        console.error('❌ CRITICAL ERROR:', e);
    } finally {
        console.log('\n🧹 Cleanup...');
        if (createdIds.length > 0) {
            console.log(`   Deleting ${createdIds.length} tires and relations...`);
            await prisma.alerta.deleteMany({ where: { neumatico_id: { in: createdIds } } });
            await prisma.lecturaPresion.deleteMany({ where: { neumatico_id: { in: createdIds } } });
            await prisma.historialEstadoNeumatico.deleteMany({ where: { neumatico_id: { in: createdIds } } });
            await prisma.medicionProfundidad.deleteMany({ where: { neumatico_id: { in: createdIds } } });
            await prisma.eventoNeumatico.deleteMany({ where: { neumatico_id: { in: createdIds } } });
            await prisma.neumatico.deleteMany({ where: { id: { in: createdIds } } });
        }

        await prisma.modeloNeumatico.delete({ where: { id: modelId } });
        await prisma.fabricanteNeumatico.delete({ where: { id: fab.data.id } });

        console.log('✅ Done.');
    }
}

main();
