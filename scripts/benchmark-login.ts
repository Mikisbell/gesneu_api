import 'dotenv/config';
import { ReportesService } from '../src/lib/services/reportes.service';
import { DashboardService } from '../src/lib/services/dashboard.service';
import { prisma } from '../src/lib/prisma';

async function benchmarkPerformance() {
    console.log('⚡ Benchmarking Parallelized Services...');
    const reportesService = new ReportesService();
    const dashboardService = new DashboardService();

    // Get a valid empresa_id
    const empresa = await prisma.empresa.findFirst();
    if (!empresa) {
        console.log('No empresa found');
        return;
    }

    // 1. Test getFlotaStatus
    const t0 = performance.now();
    const status = await reportesService.getFlotaStatus(empresa.id);
    const t1 = performance.now();
    console.log(`🚀 getFlotaStatus (7 parallelized queries): ${(t1 - t0).toFixed(2)} ms`);

    // 2. Test getReporteInventario
    const t2 = performance.now();
    const inv = await dashboardService.getReporteInventario(empresa.id);
    const t3 = performance.now();
    console.log(`🚀 getReporteInventario (5 parallelized queries): ${(t3 - t2).toFixed(2)} ms`);
}

benchmarkPerformance().finally(() => prisma.$disconnect());
