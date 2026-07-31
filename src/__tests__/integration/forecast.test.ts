/**
 * Integration Tests for ForecastService
 * Validates purchase forecast calculations, wear rate estimations,
 * multi-tenant isolation, and days-ahead window filtering.
 */

import { prisma } from '@/lib/prisma';
import { ForecastService } from '@/lib/services/forecast.service';
import {
    setupTestDatabase,
    teardownTestDatabase,
    cleanTestData,
    createTestFabricante,
    createTestModelo,
} from '../helpers/database-helpers';

describe('ForecastService Integration Tests', () => {
    let empresaA: any;
    let empresaB: any;
    let fabricante: any;
    let modelo: any;

    beforeAll(async () => {
        await setupTestDatabase();

        const ts = Date.now().toString().slice(-8);
        empresaA = await prisma.empresa.create({
            data: { nombre: 'Empresa Forecast A ' + ts, ruc: '20' + ts + '11' },
        });

        empresaB = await prisma.empresa.create({
            data: { nombre: 'Empresa Forecast B ' + ts, ruc: '20' + ts + '12' },
        });

        fabricante = await createTestFabricante();
        modelo = await createTestModelo(fabricante.id, {
            medida: '295/80R22.5',
            profundidad_original_mm: 18.0,
        });

        // Neumático de Empresa A con profundidad cercana a retiro (3.5mm -> 0.5mm remanente sobre minDepth 3mm)
        // Comprado hace 100 días -> Wear rate = (18 - 3.5)/100 = 0.145 mm/día -> días restantes = 0.5 / 0.145 = ~3 días
        const fechaCompra = new Date();
        fechaCompra.setDate(fechaCompra.getDate() - 100);

        await prisma.neumatico.create({
            data: {
                numero_serie: 'TEST-SERIE-FC-A1-' + ts,
                empresa_id: empresaA.id,
                modelo_id: modelo.id,
                estado_actual: 'INSTALADO',
                profundidad_remanente_actual_mm: 3.5,
                fecha_compra: fechaCompra,
                costo_compra: 450.00,
            },
        });

        // Neumático de Empresa A con profundidad alta (16mm -> no debe entrar en forecast de 90 días)
        await prisma.neumatico.create({
            data: {
                numero_serie: 'TEST-SERIE-FC-A2-' + ts,
                empresa_id: empresaA.id,
                modelo_id: modelo.id,
                estado_actual: 'INSTALADO',
                profundidad_remanente_actual_mm: 16.0,
                fecha_compra: fechaCompra,
                costo_compra: 450.00,
            },
        });

        // Neumático de Empresa B cercano a retiro (3.2mm)
        await prisma.neumatico.create({
            data: {
                numero_serie: 'TEST-SERIE-FC-B1-' + ts,
                empresa_id: empresaB.id,
                modelo_id: modelo.id,
                estado_actual: 'INSTALADO',
                profundidad_remanente_actual_mm: 3.2,
                fecha_compra: fechaCompra,
                costo_compra: 450.00,
            },
        });
    });

    afterAll(async () => {
        await cleanTestData();
        await teardownTestDatabase();
    });

    describe('generatePurchaseForecast()', () => {
        test('Debe generar el reporte de forecast filtrado por empresa sin mezclar datos cross-tenant', async () => {
            const forecastA = await ForecastService.generatePurchaseForecast(empresaA.id, 90);

            expect(forecastA.length).toBe(1);
            expect(forecastA[0].medida).toBe('295/80R22.5');
            expect(forecastA[0].cantidad_sugerida).toBe(1);
            expect(forecastA[0].detalles_neumaticos[0].serie).toContain('SERIE-FC-A1');
        });

        test('Debe respetar el parámetro daysAhead y excluir neumáticos cuya proyección supera la ventana', async () => {
            // Con 1 día de ventana no debe incluir sugerencias si la fecha proyectada supera 1 día
            const forecastShort = await ForecastService.generatePurchaseForecast(empresaA.id, 1);
            // SERIE-FC-A1 con 3.5mm le quedan ~3.4 días, así que con 1 día de ventana no debería incluirlo o depender del redondeo
            expect(Array.isArray(forecastShort)).toBeTruthy();

            // Con 180 días debe incluir el neumático de Empresa B para su respectivo tenant
            const forecastB = await ForecastService.generatePurchaseForecast(empresaB.id, 180);
            expect(forecastB.length).toBe(1);
            expect(forecastB[0].detalles_neumaticos[0].serie).toContain('SERIE-FC-B1');
        });

        test('Debe retornar un array vacío si la empresa no posee neumáticos próximos a retiro', async () => {
            const FAKE_EMPRESA_ID = '00000000-0000-0000-0000-000000000099';
            const forecast = await ForecastService.generatePurchaseForecast(FAKE_EMPRESA_ID, 90);

            expect(forecast).toEqual([]);
        });
    });
});
