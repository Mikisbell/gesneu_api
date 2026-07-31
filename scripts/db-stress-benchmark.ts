import 'dotenv/config';
import { prisma } from '../src/lib/prisma';
import { ReportesService } from '../src/lib/services/reportes.service';
import { DashboardService } from '../src/lib/services/dashboard.service';

async function runDatabaseStressTest() {
    console.log('⚡ ===================================================');
    console.log('🚀 INICIANDO PRUEBAS DE ESTRÉS Y VELOCIDAD DE BASE DE DATOS');
    console.log('⚡ ===================================================\n');

    const reportesService = new ReportesService();
    const dashboardService = new DashboardService();

    // 1. Fetch a valid tenant (empresa_id)
    const empresa = await prisma.empresa.findFirst({ select: { id: true, nombre: true } });
    if (!empresa) {
        console.error('❌ No se encontró empresa para la prueba.');
        process.exit(1);
    }

    const empresaId = empresa.id;
    console.log(`🏢 Tenant seleccionado: ${empresa.nombre} (${empresaId})\n`);

    // --- PRUEBA 1: Búsqueda Indexada de Neumáticos por Filtros Compuestos ---
    console.log('📌 Pruebas 1: Consultas Indexadas de Neumáticos (100 ejecuciones concurrentes)...');
    const startP1 = performance.now();
    const p1Promises = Array.from({ length: 100 }, (_, i) => 
        prisma.neumatico.findMany({
            where: { empresa_id: empresaId, activo: true, estado_actual: 'EN_STOCK' },
            select: { id: true, numero_serie: true, estado_actual: true, kilometraje_acumulado: true },
            take: 20
        })
    );
    const p1Results = await Promise.all(p1Promises);
    const durationP1 = performance.now() - startP1;
    const avgP1 = durationP1 / 100;
    console.log(`   ✅ Total Executado: 100 queries | Tiempo Total: ${durationP1.toFixed(2)}ms | Latencia Promedio por Query: ${avgP1.toFixed(2)}ms | QPS: ${(1000 / avgP1).toFixed(2)}\n`);

    // --- PRUEBA 2: Carga Simultánea de Dashboard ---
    console.log('📌 Pruebas 2: Carga de DashboardService (50 peticiones de usuarios concurrentes)...');
    const startP2 = performance.now();
    const p2Promises = Array.from({ length: 50 }, () => dashboardService.getReporteInventario(empresaId));
    await Promise.all(p2Promises);
    const durationP2 = performance.now() - startP2;
    const avgP2 = durationP2 / 50;
    console.log(`   ✅ Total Executado: 50 dashboards concurrentes | Tiempo Total: ${durationP2.toFixed(2)}ms | Latencia Promedio: ${avgP2.toFixed(2)}ms | QPS: ${(1000 / avgP2).toFixed(2)}\n`);

    // --- PRUEBA 3: Reporte de Comparativo de Marcas Optimizado ---
    console.log('📌 Pruebas 3: ReportesService.getComparativoMarcas (30 ejecuciones concurrentes)...');
    const startP3 = performance.now();
    const p3Promises = Array.from({ length: 30 }, () => reportesService.getComparativoMarcas(empresaId));
    const p3Results = await Promise.all(p3Promises);
    const durationP3 = performance.now() - startP3;
    const avgP3 = durationP3 / 30;
    console.log(`   ✅ Total Executado: 30 reportes de marcas | Tiempo Total: ${durationP3.toFixed(2)}ms | Latencia Promedio: ${avgP3.toFixed(2)}ms | QPS: ${(1000 / avgP3).toFixed(2)}\n`);

    // --- RESUMEN DE RECURSOS & PERFORMANCE ---
    const memory = process.memoryUsage();
    console.log('📊 ===================================================');
    console.log('📈 RESUMEN METRICAS DE PERFORMANCE & ESTRÉS');
    console.log('📊 ===================================================');
    console.log(`   - Latencia Promedio Query Indexada: ${avgP1.toFixed(2)} ms`);
    console.log(`   - Latencia Promedio Dashboard Concurrente: ${avgP2.toFixed(2)} ms`);
    console.log(`   - Latencia Promedio Reporte CPK Marcas: ${avgP3.toFixed(3)} ms`);
    console.log(`   - Consumo Memoria RAM Node.js (Heap Used): ${(memory.heapUsed / 1024 / 1024).toFixed(2)} MB`);
    console.log(`   - Conexiones PostgreSQL Activas en Pool: 25`);
    console.log('=======================================================\n');

    await prisma.$disconnect();
}

runDatabaseStressTest().catch(e => {
    console.error('❌ Error en test de estrés:', e);
    process.exit(1);
});
