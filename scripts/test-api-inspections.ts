import 'dotenv/config';
import { prisma } from '../src/lib/prisma';
import { InspeccionService } from '../src/lib/services/inspeccion.service';
import { registerObservers } from '../src/lib/events/registry';

/**
 * API-LEVEL TEST: Simulates what the API routes do
 * Tests the full flow as if called via HTTP (but bypasses auth)
 */

registerObservers();
const service = new InspeccionService();

async function main() {
    console.log("🌐 API-LEVEL TEST: Inspections Endpoints\n");
    console.log("=".repeat(60));

    // Get a test tire
    const tire = await prisma.neumatico.findFirst({ include: { modelo: true } });
    if (!tire) throw new Error("No tires found");

    const MOCK_USER_ID = '00000000-0000-0000-0000-000000000001';
    const MOCK_EMPRESA_ID = tire.empresa_id;

    console.log(`🎯 Target: ${tire.numero_serie}`);

    // ========================================
    // TEST: POST /api/v1/inspecciones/presion
    // ========================================
    console.log("\n📡 TEST: POST /api/v1/inspecciones/presion");
    const mockPressureBody = {
        neumatico_id: tire.id,
        presion_psi: 98,
        fuente: 'MANUAL'
    };
    console.log(`   Request: ${JSON.stringify(mockPressureBody)}`);

    try {
        const result = await service.registrarPresion({
            neumaticoId: mockPressureBody.neumatico_id,
            presionPsi: mockPressureBody.presion_psi,
            empresaId: MOCK_EMPRESA_ID,
            usuarioId: MOCK_USER_ID,
            fuente: mockPressureBody.fuente as any
        });
        console.log(`   ✅ Response: { success: true, data: { id: "${result.id}" } }`);
    } catch (e: any) {
        console.log(`   ❌ Error: ${e.message}`);
    }

    // ========================================
    // TEST: POST /api/v1/inspecciones/profundidad
    // ========================================
    console.log("\n📡 TEST: POST /api/v1/inspecciones/profundidad");
    const mockDepthBody = {
        neumatico_id: tire.id,
        profundidad_int: 7.5,
        profundidad_cen: 8.0,
        profundidad_ext: 7.2
    };
    console.log(`   Request: ${JSON.stringify(mockDepthBody)}`);

    try {
        const result = await service.registrarProfundidad({
            neumaticoId: mockDepthBody.neumatico_id,
            profundidades: {
                int: mockDepthBody.profundidad_int,
                cen: mockDepthBody.profundidad_cen,
                ext: mockDepthBody.profundidad_ext
            },
            empresaId: MOCK_EMPRESA_ID,
            usuarioId: MOCK_USER_ID
        });
        console.log(`   ✅ Response: { success: true, data: { id: "${result.id}", profundidad_prom: ${result.profundidad_prom} } }`);
    } catch (e: any) {
        console.log(`   ❌ Error: ${e.message}`);
    }

    // ========================================
    // VERIFY SIDE EFFECTS
    // ========================================
    console.log("\n🔍 VERIFICATION: Side Effects");

    const updatedTire = await prisma.neumatico.findUnique({
        where: { id: tire.id },
        select: { presion_actual_psi: true, profundidad_remanente_actual_mm: true }
    });

    console.log(`   Tire Snapshot Updated:`);
    console.log(`     - presion_actual_psi: ${updatedTire?.presion_actual_psi} (Expected: 98)`);
    console.log(`     - profundidad_remanente_actual_mm: ${updatedTire?.profundidad_remanente_actual_mm} (Expected: ~7.57)`);

    // Count new records
    const recentPressure = await prisma.lecturaPresion.findFirst({
        where: { neumatico_id: tire.id },
        orderBy: { fecha_lectura: 'desc' }
    });
    const recentDepth = await prisma.medicionProfundidad.findFirst({
        where: { neumatico_id: tire.id },
        orderBy: { fecha_medicion: 'desc' }
    });

    console.log(`\n   Last Records Created:`);
    console.log(`     - Pressure: ${recentPressure?.presion_psi} PSI @ ${recentPressure?.fecha_lectura}`);
    console.log(`     - Depth: ${recentDepth?.profundidad_prom}mm @ ${recentDepth?.fecha_medicion}`);

    console.log("\n" + "=".repeat(60));
    console.log("✅ API-LEVEL TEST COMPLETE");

    await prisma.$disconnect();
}

main().catch(console.error);
