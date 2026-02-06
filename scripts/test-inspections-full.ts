import 'dotenv/config';
import { prisma } from '../src/lib/prisma';
import { InspeccionService } from '../src/lib/services/inspeccion.service';
import { registerObservers } from '../src/lib/events/registry';

/**
 * COMPREHENSIVE TEST SUITE: Inspections Module
 * Tests: Backend Logic, DB Persistence, Event Flow, Alert Generation
 */

// Initialize Observers
registerObservers();

const service = new InspeccionService();

interface TestResult {
    name: string;
    passed: boolean;
    details: string;
}

const results: TestResult[] = [];

async function test(name: string, fn: () => Promise<boolean>, details: string = '') {
    try {
        const passed = await fn();
        results.push({ name, passed, details: passed ? '✅' : details || '❌' });
    } catch (error: any) {
        results.push({ name, passed: false, details: `Error: ${error.message}` });
    }
}

async function main() {
    console.log("🧪 COMPREHENSIVE TEST SUITE: INSPECTIONS MODULE\n");
    console.log("=".repeat(60));

    // === SETUP ===
    const tire = await prisma.neumatico.findFirst({
        include: { modelo: true }
    });

    if (!tire) {
        console.error("❌ No tires in DB. Cannot run tests.");
        process.exit(1);
    }

    console.log(`🎯 Target Tire: ${tire.numero_serie} (ID: ${tire.id})`);
    console.log(`📊 Model: ${tire.modelo.nombre_modelo}`);

    // Ensure model has recommended pressure for alert testing
    if (!tire.modelo.presion_recomendada_psi) {
        await prisma.modeloNeumatico.update({
            where: { id: tire.modelo_id },
            data: { presion_recomendada_psi: 100 }
        });
        console.log("🔧 Set Model Recommended Pressure to 100 PSI");
    }

    const initialAlertCount = await prisma.alerta.count({ where: { neumatico_id: tire.id } });
    const initialPressureReadings = await prisma.lecturaPresion.count({ where: { neumatico_id: tire.id } });
    const initialDepthReadings = await prisma.medicionProfundidad.count({ where: { neumatico_id: tire.id } });

    console.log(`📈 Initial State: ${initialAlertCount} alerts, ${initialPressureReadings} pressure readings, ${initialDepthReadings} depth readings`);
    console.log("\n" + "=".repeat(60) + "\n");

    // === TEST 1: Pressure Reading Persistence ===
    await test("1. Pressure Reading - DB Persistence", async () => {
        const lectura = await service.registrarPresion({
            neumaticoId: tire.id,
            presionPsi: 95,
            empresaId: tire.empresa_id,
            fuente: 'MANUAL'
        });
        return !!lectura.id;
    });

    // === TEST 2: Low Pressure Alert Generation ===
    await test("2. Low Pressure Alert - Auto Generation", async () => {
        await service.registrarPresion({
            neumaticoId: tire.id,
            presionPsi: 50, // Below 90% of 100 = 90
            empresaId: tire.empresa_id,
            fuente: 'MANUAL'
        });

        // Check if alert was created
        const alerts = await prisma.alerta.findMany({
            where: {
                neumatico_id: tire.id,
                tipo: 'PRESION_BAJA'
            },
            orderBy: { creada_en: 'desc' },
            take: 1
        });

        return alerts.length > 0 && alerts[0].mensaje.includes('50');
    });

    // === TEST 3: Depth Reading Persistence ===
    await test("3. Depth Reading - DB Persistence", async () => {
        const medicion = await service.registrarProfundidad({
            neumaticoId: tire.id,
            profundidades: { int: 8, cen: 8.5, ext: 7.5 },
            empresaId: tire.empresa_id
        });
        return !!medicion.id && Number(medicion.profundidad_prom) === 8;
    });

    // === TEST 4: Critical Depth Alert Generation ===
    await test("4. Critical Depth Alert - Auto Generation", async () => {
        await service.registrarProfundidad({
            neumaticoId: tire.id,
            profundidades: { int: 2, cen: 2.5, ext: 2 },
            empresaId: tire.empresa_id
        });

        const alerts = await prisma.alerta.findMany({
            where: {
                neumatico_id: tire.id,
                tipo: 'PROFUNDIDAD_MINIMA'
            },
            orderBy: { creada_en: 'desc' },
            take: 1
        });

        return alerts.length > 0 && alerts[0].severidad === 'CRITICAL';
    });

    // === TEST 5: Neumatico Snapshot Update (Pressure) ===
    await test("5. Tire Snapshot Update - Pressure", async () => {
        await service.registrarPresion({
            neumaticoId: tire.id,
            presionPsi: 105,
            empresaId: tire.empresa_id
        });

        const updated = await prisma.neumatico.findUnique({ where: { id: tire.id } });
        return Number(updated?.presion_actual_psi) === 105;
    });

    // === TEST 6: Neumatico Snapshot Update (Depth) ===
    await test("6. Tire Snapshot Update - Depth", async () => {
        await service.registrarProfundidad({
            neumaticoId: tire.id,
            profundidades: { int: 10, cen: 10, ext: 10 },
            empresaId: tire.empresa_id
        });

        const updated = await prisma.neumatico.findUnique({ where: { id: tire.id } });
        return Number(updated?.profundidad_remanente_actual_mm) === 10;
    });

    // === TEST 7: Multiple Readings Performance ===
    await test("7. Bulk Readings - Performance (10 readings)", async () => {
        const start = Date.now();
        for (let i = 0; i < 10; i++) {
            await service.registrarPresion({
                neumaticoId: tire.id,
                presionPsi: 100 + i,
                empresaId: tire.empresa_id
            });
        }
        const duration = Date.now() - start;
        return duration < 5000; // Should complete in < 5s
    }, `Took too long`);

    // === TEST 8: Readings Count After Tests ===
    await test("8. DB Integrity - Reading Counts", async () => {
        const finalPressure = await prisma.lecturaPresion.count({ where: { neumatico_id: tire.id } });
        const finalDepth = await prisma.medicionProfundidad.count({ where: { neumatico_id: tire.id } });

        // We created: 1 (T1) + 1 (T2) + 1 (T5) + 10 (T7) = 13 pressure
        // We created: 1 (T3) + 1 (T4) + 1 (T6) = 3 depth
        const expectedPressure = initialPressureReadings + 13;
        const expectedDepth = initialDepthReadings + 3;

        return finalPressure === expectedPressure && finalDepth === expectedDepth;
    }, `Counts mismatch`);

    // === RESULTS ===
    console.log("\n" + "=".repeat(60));
    console.log("📊 TEST RESULTS:");
    console.log("=".repeat(60));

    let passed = 0;
    let failed = 0;

    for (const r of results) {
        const status = r.passed ? '✅ PASS' : '❌ FAIL';
        console.log(`${status} | ${r.name}`);
        if (!r.passed) console.log(`   └─ ${r.details}`);
        r.passed ? passed++ : failed++;
    }

    console.log("\n" + "=".repeat(60));
    console.log(`🏁 SUMMARY: ${passed}/${results.length} tests passed`);

    if (failed === 0) {
        console.log("🎉 ALL TESTS PASSED!");
    } else {
        console.log(`⚠️ ${failed} tests failed. Review issues above.`);
    }

    await prisma.$disconnect();
}

main().catch(console.error);
