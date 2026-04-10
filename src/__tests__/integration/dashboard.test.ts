import { prisma } from '@/lib/prisma';

// Helper simple para limpieza y creación de datos de prueba
async function clearTestData() {
    // 1. Dependencias de Neumático (Tablas hijas)
    await prisma.medicionProfundidad.deleteMany();
    await prisma.lecturaPresion.deleteMany();
    await prisma.alerta.deleteMany();
    await prisma.historialEstadoNeumatico.deleteMany();
    await prisma.eventoNeumatico.deleteMany();
    await prisma.garantiaNeumatico.deleteMany();

    // 2. Tablas principales
    await prisma.neumatico.deleteMany();
    await prisma.modeloNeumatico.deleteMany();
    await prisma.fabricanteNeumatico.deleteMany();
}

async function createTestNeumatico(overrides: any = {}) {
    const fabricante = await prisma.fabricanteNeumatico.create({
        data: { nombre: 'TestFab_' + Date.now() + Math.random() }
    });

    const modelo = await prisma.modeloNeumatico.create({
        data: {
            nombre_modelo: 'TestModel_' + Date.now(),
            medida: '295/80R22.5',
            profundidad_original_mm: 18,
            fabricante_id: fabricante.id,
            reencauches_maximos: 2
        }
    });

    const empresa = await prisma.empresa.create({
        data: { nombre: `Test Dash ${Date.now()}`, ruc: `TEST-DSH-${Date.now()}`.substring(0, 20) }
    });

    return await prisma.neumatico.create({
        data: {
            numero_serie: 'TEST-' + Date.now() + Math.random(),
            modelo_id: modelo.id,
            empresa_id: empresa.id,
            fecha_compra: new Date(),
            profundidad_inicial_mm: 18,
            profundidad_remanente_actual_mm: 18,
            estado_actual: 'EN_STOCK',
            costo_compra: 500,
            kilometraje_acumulado: 1000,
            activo: true,
            ...overrides
        }
    });
}

import { DashboardService } from '@/lib/services/dashboard.service';

describe('DashboardService', () => {
    const service = new DashboardService();

    beforeAll(async () => {
        await clearTestData();
        // Crear algunos neumáticos de prueba
        await createTestNeumatico({ estado_actual: 'EN_STOCK' });
        await createTestNeumatico({ estado_actual: 'INSTALADO', kilometraje_acumulado: 5000 });
        await createTestNeumatico({ estado_actual: 'DESECHADO' });
    });

    afterAll(async () => {
        await clearTestData();
        await prisma.$disconnect();
    });

    describe('getReporteInventario', () => {
        it('debería retornar totales por estado', async () => {
            const reporte = await service.getReporteInventario();

            expect(reporte.total_neumaticos).toBeGreaterThanOrEqual(1);
            expect(reporte.por_estado).toBeDefined();
            expect(Array.isArray(reporte.por_estado)).toBe(true);
        });
    });

    describe('getReporteRendimiento', () => {
        it('debería retornar top mejores y peores por CPK', async () => {
            const reporte = await service.getReporteRendimiento(5);

            expect(reporte.top_mejores).toBeDefined();
            expect(reporte.top_peores).toBeDefined();
            expect(typeof reporte.promedio_cpk).toBe('number');
        });
    });

    describe('getReporteDesechos', () => {
        it('debería retornar análisis de desechos', async () => {
            const reporte = await service.getReporteDesechos();

            expect(typeof reporte.total_desechados).toBe('number');
            expect(Array.isArray(reporte.por_motivo)).toBe(true);
            expect(Array.isArray(reporte.por_mes)).toBe(true);
        });
    });
});
