import 'dotenv/config';
import { prisma } from '../src/lib/prisma';

/**
 * DATABASE VERIFICATION: Inspections Module
 * Directly queries DB to verify data was persisted correctly.
 */

async function main() {
    console.log("🗄️ DATABASE VERIFICATION: INSPECTIONS MODULE\n");
    console.log("=".repeat(60));

    // 1. Count Pressure Readings
    const pressureCount = await prisma.lecturaPresion.count();
    console.log(`📊 Total Pressure Readings: ${pressureCount}`);

    // 2. Count Depth Measurements
    const depthCount = await prisma.medicionProfundidad.count();
    console.log(`📊 Total Depth Measurements: ${depthCount}`);

    // 3. Count Alerts
    const alertCount = await prisma.alerta.count();
    console.log(`📊 Total Alerts: ${alertCount}`);

    // 4. Recent Pressure Readings (Last 5)
    console.log("\n📈 Last 5 Pressure Readings:");
    const recentPressure = await prisma.lecturaPresion.findMany({
        take: 5,
        orderBy: { fecha_lectura: 'desc' },
        include: { neumatico: { select: { numero_serie: true } } }
    });
    recentPressure.forEach((r, i) => {
        console.log(`   ${i + 1}. ${r.neumatico.numero_serie}: ${r.presion_psi} PSI (${r.fuente}) @ ${r.fecha_lectura.toISOString()}`);
    });

    // 5. Recent Depth Measurements (Last 5)
    console.log("\n📏 Last 5 Depth Measurements:");
    const recentDepth = await prisma.medicionProfundidad.findMany({
        take: 5,
        orderBy: { fecha_medicion: 'desc' },
        include: { neumatico: { select: { numero_serie: true } } }
    });
    recentDepth.forEach((r, i) => {
        console.log(`   ${i + 1}. ${r.neumatico.numero_serie}: ${r.profundidad_prom}mm (Int:${r.profundidad_int}/Cen:${r.profundidad_cen}/Ext:${r.profundidad_ext}) @ ${r.fecha_medicion.toISOString()}`);
    });

    // 6. Recent Alerts (Last 5)
    console.log("\n🚨 Last 5 Alerts:");
    const recentAlerts = await prisma.alerta.findMany({
        take: 5,
        orderBy: { creada_en: 'desc' },
        include: { neumatico: { select: { numero_serie: true } } }
    });
    recentAlerts.forEach((a, i) => {
        const tire = a.neumatico?.numero_serie || 'N/A';
        console.log(`   ${i + 1}. [${a.severidad}] ${a.tipo} - ${tire}: ${a.mensaje.substring(0, 50)}...`);
    });

    // 7. Verify Tire Snapshot Updated
    console.log("\n🔍 Tire Snapshot Check (Last Updated Tires):");
    const updatedTires = await prisma.neumatico.findMany({
        where: {
            OR: [
                { presion_actual_psi: { not: null } },
                { profundidad_remanente_actual_mm: { not: null } }
            ]
        },
        take: 3,
        orderBy: { actualizado_en: 'desc' },
        select: {
            numero_serie: true,
            presion_actual_psi: true,
            profundidad_remanente_actual_mm: true,
            actualizado_en: true
        }
    });
    updatedTires.forEach((t, i) => {
        console.log(`   ${i + 1}. ${t.numero_serie}: PSI=${t.presion_actual_psi}, Depth=${t.profundidad_remanente_actual_mm}mm (Updated: ${t.actualizado_en?.toISOString()})`);
    });

    console.log("\n" + "=".repeat(60));
    console.log("✅ DATABASE VERIFICATION COMPLETE");

    await prisma.$disconnect();
}

main().catch(console.error);
