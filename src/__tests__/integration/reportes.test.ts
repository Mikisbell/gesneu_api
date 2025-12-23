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
            nombre: 'TestModel_' + Date.now(),
            medida: '295/80R22.5',
            profundidad_inicial_mm: 18,
            fabricante_id: fabricante.id,
            reencauches_maximos: 2
        }
    });

    return await prisma.neumatico.create({
        data: {
            numero_serie: 'TEST-' + Date.now(),
            modelo_id: modelo.id,
            profundidad_inicial_mm: 18,
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

        // 3. Llamar al servicio
        const metrics = await service.getCPK(neumatico.id);

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

        const metrics = await service.getCPK(neumatico.id);

        expect(metrics.cpk).toBe(0);
        expect(metrics.kilometraje_total).toBe(0);
    });

    it('debería lanzar error si neumático no existe', async () => {
        await expect(service.getCPK('00000000-0000-0000-0000-000000000000')).rejects.toThrow('Neumático no encontrado');
    });
});
