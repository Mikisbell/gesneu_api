import 'dotenv/config';
import { prisma } from '../src/lib/prisma';
import { InspeccionService } from '../src/lib/services/inspeccion.service';
import { registerObservers } from '../src/lib/events/registry';

// Initialize Observers MANUALLY for script
registerObservers();

const service = new InspeccionService();
const TENANT_ID = 'd9c3b8f0-1111-4444-8888-999999999999'; // Mock or fetch real

async function main() {
    console.log("🔍 TESTING INSPECTION EVENTS...");

    // 1. Get a test Tire
    const tire = await prisma.neumatico.findFirst({
        include: { modelo: true }
    });
    if (!tire) throw new Error("No tires found");
    console.log(`target: ${tire.numero_serie} (ID: ${tire.id})`);

    // SELF-HEALING: Ensure Model has recommended pressure
    if (!tire.modelo.presion_recomendada_psi) {
        console.log("🔧 [Setup] Setting Recommended Pressure to 100 PSI...");
        await prisma.modeloNeumatico.update({
            where: { id: tire.modelo_id },
            data: { presion_recomendada_psi: 100 }
        });
    }

    // 2. Simulate Low Pressure Reading
    console.log("👉 Sending Low Pressure Reading (50 PSI)...");
    await service.registrarPresion({
        neumaticoId: tire.id,
        presionPsi: 50,
        empresaId: TENANT_ID,
        usuarioId: undefined, // System
        fuente: 'MANUAL'
    });

    // 3. Simulate Critical Depth Reading
    console.log("👉 Sending Critical Depth Reading (2mm)...");
    await service.registrarProfundidad({
        neumaticoId: tire.id,
        profundidades: { int: 2, cen: 2, ext: 2 },
        empresaId: TENANT_ID
    });

    console.log("✅ Events Dispatched. Waiting for Side Effects (2-3s)...");
    // Observers are async awaited in publish, so theoretically done, but let's pause
    await new Promise(r => setTimeout(r, 2000));

    // 4. Verify Side Effects
    const updatedTire = await prisma.neumatico.findUnique({ where: { id: tire.id } });
    const alerts = await prisma.alerta.findMany({
        where: { neumatico_id: tire.id },
        orderBy: { creada_en: 'desc' },
        take: 2
    });

    console.log("📊 VERIFICATION:");
    console.log(`   - Tire Pressure Updated: ${updatedTire?.presion_actual_psi} (Expected 50)`);
    console.log(`   - Tire Depth Updated: ${updatedTire?.profundidad_remanente_actual_mm} (Expected 2.00)`);
    console.log(`   - Alerts Created: ${alerts.length}`);
    alerts.forEach(a => console.log(`     ⚠️ [${a.severidad}] ${a.mensaje}`));
}

main().catch(console.error);
