import { prisma } from '@/lib/prisma';

// Helper simple para limpieza y creación de datos de prueba
async function clearTestData() {
    await prisma.alerta.deleteMany();
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
            profundidad_remanente_actual_mm: 18,
            estado_actual: 'EN_STOCK',
            costo_compra: 0,
            kilometraje_acumulado: 0,
            ...overrides
        }
    });
}

import { AlertasService } from '@/lib/services/alertas.service';

describe('AlertasService', () => {
    const service = new AlertasService();

    beforeAll(async () => {
        await clearTestData();
    });

    afterAll(async () => {
        await clearTestData();
        await prisma.$disconnect();
    });

    describe('generarAlertasProfundidad', () => {
        it('debería generar alerta CRITICAL cuando profundidad < 4mm', async () => {
            // Crear neumático con profundidad crítica
            await createTestNeumatico({
                profundidad_remanente_actual_mm: 3.5,
                activo: true
            });

            const count = await service.generarAlertasProfundidad();

            expect(count).toBeGreaterThanOrEqual(1);

            // Verificar que se creó la alerta
            const alertas = await service.getAlertas({ tipo: 'PROFUNDIDAD_MINIMA' });
            expect(alertas.length).toBeGreaterThanOrEqual(1);
            expect(alertas[0].severidad).toBe('CRITICAL');
        });

        it('no debería generar duplicados si ya existe alerta no resuelta', async () => {
            // Ejecutar generador de nuevo
            const count1 = await service.generarAlertasProfundidad();
            const count2 = await service.generarAlertasProfundidad();

            // La segunda ejecución no debería crear duplicados
            expect(count2).toBe(0);
        });
    });

    describe('getAlertas', () => {
        it('debería filtrar por severidad', async () => {
            const alertas = await service.getAlertas({ severidad: 'CRITICAL' });

            alertas.forEach(a => {
                expect(a.severidad).toBe('CRITICAL');
            });
        });
    });

    describe('marcarComoLeida', () => {
        it('debería marcar alerta como leída', async () => {
            const alertas = await service.getAlertas({ leida: false });
            if (alertas.length > 0) {
                const alerta = await service.marcarComoLeida(alertas[0].id);
                expect(alerta.leida).toBe(true);
            }
        });
    });
});
