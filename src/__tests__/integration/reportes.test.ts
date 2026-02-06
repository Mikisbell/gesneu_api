import { prisma } from '@/lib/prisma';

// Helper simple para limpieza y creación de datos de prueba
async function clearTestData() {
    await prisma.eventoNeumatico.deleteMany();
    await prisma.neumatico.deleteMany();
    await prisma.modeloNeumatico.deleteMany();
    await prisma.fabricanteNeumatico.deleteMany();
}

async function createTestNeumatico(overrides: any = {}) {
    const fabricante = await prisma.fabricanteNeumatico.create({
        data: { nombre: 'TestFab_' + Date.now() }
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

    return await prisma.neumatico.create({
        data: {
            numero_serie: 'TEST-' + Date.now(),
            modelo_id: modelo.id,
            profundidad_original_mm: 18,
            estado_actual: 'EN_STOCK',
            costo_compra: 0,
            kilometraje_acumulado: 0,
            ...overrides
        }
    });
}

// Import del servicio DESPUÉS de helpers para evitar problemas de orden
import { ReportesService } from '@/lib/services/reportes.service';

describe('ReportesService: CPK', () => {
    const service = new ReportesService();

    beforeAll(async () => {
        await clearTestData();
    });

    afterAll(async () => {
        await clearTestData();
        await prisma.$disconnect();
    });

    it('debería calcular CPK correctamente: (Compra + Eventos) / Km', async () => {
        // 1. Crear neumático con costo y kilometraje conocidos
        const neumatico = await createTestNeumatico({
            costo_compra: 500,
            kilometraje_acumulado: 1000
        });

        // 2. Agregar evento con costo
        await prisma.eventoNeumatico.create({
            data: {
                tipo_evento: 'REPARACION_SALIDA',
                neumatico_id: neumatico.id,
                fecha_evento: new Date(),
                costo_evento: 100
            }
        });

        // 3. Llamar al servicio (usando empresaId de prueba)
        const testEmpresaId = '00000000-0000-0000-0000-000000000001';
        const metrics = await service.getCPK(testEmpresaId, neumatico.id);

        // 4. Verificar
        expect(metrics.cpk).toBe(0.6); // (500 + 100) / 1000 = 0.6
        expect(metrics.costo_total).toBe(600);
        expect(metrics.desglose.compra).toBe(500);
        expect(metrics.desglose.reparaciones).toBe(100);
    });

    it('debería retornar CPK = 0 cuando kilometraje es 0', async () => {
        const neumatico = await createTestNeumatico({
            costo_compra: 500,
            kilometraje_acumulado: 0
        });

        const testEmpresaId = '00000000-0000-0000-0000-000000000001';
        const metrics = await service.getCPK(testEmpresaId, neumatico.id);

        expect(metrics.cpk).toBe(0);
        expect(metrics.kilometraje_total).toBe(0);
    });

    it('debería lanzar error si neumático no existe', async () => {
        const testEmpresaId = '00000000-0000-0000-0000-000000000001';
        await expect(service.getCPK(testEmpresaId, '00000000-0000-0000-0000-000000000000')).rejects.toThrow('Neumático no encontrado');
    });
});

describe('ReportesService: Desgaste Promedio', () => {
    const service = new ReportesService();

    beforeAll(async () => {
        await clearTestData();
    });

    afterAll(async () => {
        await clearTestData();
        await prisma.$disconnect();
    });

    it('debería calcular desgaste en mm/1000km correctamente', async () => {
        // Neumático con 18mm inicial, 14mm actual, 10000 km
        // Desgaste = (18 - 14) / 10000 * 1000 = 0.4 mm/1000km
        const neumatico = await createTestNeumatico({
            profundidad_original_mm: 18,
            profundidad_remanente_actual_mm: 14,
            kilometraje_acumulado: 10000
        });

        const testEmpresaId = '00000000-0000-0000-0000-000000000001';
        const metrics = await service.getDesgastePromedio(testEmpresaId, neumatico.id);

        expect(metrics.desgaste_mm_por_1000km).toBe(0.4);
        expect(metrics.desgaste_total_mm).toBe(4);
        expect(metrics.estado).toBe('OPTIMO'); // 14mm > 70% de 18mm (12.6mm)
    });

    it('debería detectar estado CRITICO cuando profundidad <= 4mm', async () => {
        const neumatico = await createTestNeumatico({
            profundidad_original_mm: 18,
            profundidad_remanente_actual_mm: 3.5,
            kilometraje_acumulado: 50000
        });

        const testEmpresaId = '00000000-0000-0000-0000-000000000001';
        const metrics = await service.getDesgastePromedio(testEmpresaId, neumatico.id);

        expect(metrics.estado).toBe('CRITICO');
    });

    it('debería estimar vida restante en km', async () => {
        // 18mm inicial, 14mm actual, 10000 km = 0.4mm/1000km
        // Restante: 14 - 4 = 10mm
        // Vida restante: 10 / 0.4 * 1000 = 25000 km
        const neumatico = await createTestNeumatico({
            profundidad_original_mm: 18,
            profundidad_remanente_actual_mm: 14,
            kilometraje_acumulado: 10000
        });

        const testEmpresaId = '00000000-0000-0000-0000-000000000001';
        const metrics = await service.getDesgastePromedio(testEmpresaId, neumatico.id);

        expect(metrics.vida_restante_estimada_km).toBe(25000);
    });
});

describe('ReportesService: Comparativo Marcas', () => {
    const service = new ReportesService();

    beforeAll(async () => {
        await clearTestData();
    });

    afterAll(async () => {
        await clearTestData();
        await prisma.$disconnect();
    });

    it('debería agrupar CPKs por fabricante correctamente', async () => {
        // Crear neumáticos de diferentes fabricantes
        const n1 = await createTestNeumatico({
            costo_compra: 500,
            kilometraje_acumulado: 1000
        });
        const n2 = await createTestNeumatico({
            costo_compra: 600,
            kilometraje_acumulado: 1200
        });

        const testEmpresaId = '00000000-0000-0000-0000-000000000001';
        const result = await service.getComparativoMarcas(testEmpresaId);

        expect(result.marcas.length).toBeGreaterThanOrEqual(1);
        expect(result.fecha_calculo).toBeDefined();
    });

    it('debería retornar lista vacía si no hay neumáticos con km > 0', async () => {
        await clearTestData();

        const testEmpresaId = '00000000-0000-0000-0000-000000000001';
        const result = await service.getComparativoMarcas(testEmpresaId);

        expect(result.marcas).toEqual([]);
        expect(result.mejor_marca).toBeNull();
        expect(result.peor_marca).toBeNull();
    });
});
