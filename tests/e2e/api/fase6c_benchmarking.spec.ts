
import { test, expect } from '@playwright/test';
import prisma from '../../../src/lib/prisma';
import dotenv from 'dotenv';
import { v4 as uuidv4 } from 'uuid';

dotenv.config({ path: '.env' });

test.describe('Fase 6C.2: Benchmarking Verification', () => {
    let apiContext: any;
    const ENDPOINT = '/api/v1/reportes/benchmarking';
    const SESSION_FILE = 'auth_6c_bench.json';
    const TEST_ID = Math.floor(Math.random() * 9999); // 4 digits
    const TEST_PREFIX = `BN${TEST_ID}`; // BN1234 (6 chars)

    test.beforeAll(async ({ playwright, browser }) => {
        // ... (lines 13-28 unchanged) ...
        const context = await browser.newContext();
        await context.grantPermissions(['clipboard-read', 'clipboard-write']);
        const page = await context.newPage();
        await page.goto('http://localhost:3005/login');
        await page.fill('input[name="identifier"]', 'admin@gesneu.com');
        await page.fill('input[name="password"]', process.env.STRESS_PASSWORD || 'admin123');
        await page.click('button[type="submit"]');
        await page.waitForURL('**/dashboard');

        await context.storageState({ path: SESSION_FILE });

        apiContext = await playwright.request.newContext({
            baseURL: 'http://localhost:3005',
            storageState: SESSION_FILE
        });

        // 2. Data Seeding (Brands & Models)
        const empresa = await prisma.empresa.findFirst({ where: { ruc: '20123456789' } });
        if (!empresa) throw new Error('Empresa not found');

        // Brand A: "Bridgestone Test"
        const brandA = await prisma.fabricanteNeumatico.create({
            data: { nombre: `Bridgestone ${TEST_ID}`, codigo_abreviado: `BS${TEST_ID}` } // BS1234 (6 chars) - Fits varchar(10)
        });
        const modelA1 = await prisma.modeloNeumatico.create({
            data: { fabricante_id: brandA.id, nombre_modelo: `M729 ${TEST_ID}`, medida: '295/80R22.5', profundidad_original_mm: 18 }
        });

        // Brand B: "Michelin Test"
        const brandB = await prisma.fabricanteNeumatico.create({
            data: { nombre: `Michelin ${TEST_ID}`, codigo_abreviado: `MI${TEST_ID}` } // MI1234 (6 chars)
        });
        const modelB1 = await prisma.modeloNeumatico.create({
            data: { fabricante_id: brandB.id, nombre_modelo: `XMulti ${TEST_ID}`, medida: '295/80R22.5', profundidad_original_mm: 17 }
        });

        // 3. Create Tires (Finished)
        // Tire A1 (Brand A): Great CPK (Low Cost, High Km)
        await prisma.neumatico.create({
            data: {
                empresa_id: empresa.id,
                modelo_id: modelA1.id,
                numero_serie: `A1-${TEST_PREFIX}`,
                estado_actual: 'DESECHADO',
                fecha_compra: new Date(),
                costo_compra: 400, // Cheap
                kilometraje_acumulado: 100000, // Moderate
                reencauches_realizados: 1,
                profundidad_remanente_actual_mm: 5
            }
        });

        // Tire A2 (Brand A): Good CPK
        await prisma.neumatico.create({
            data: {
                empresa_id: empresa.id,
                modelo_id: modelA1.id,
                numero_serie: `A2-${TEST_PREFIX}`,
                estado_actual: 'DESECHADO',
                fecha_compra: new Date(),
                costo_compra: 420,
                kilometraje_acumulado: 110000,
                reencauches_realizados: 0,
                profundidad_remanente_actual_mm: 4
            }
        });

        // Tire B1 (Brand B): Bad CPK (High Cost, Low Km)
        await prisma.neumatico.create({
            data: {
                empresa_id: empresa.id,
                modelo_id: modelB1.id,
                numero_serie: `B1-${TEST_PREFIX}`,
                estado_actual: 'DESECHADO',
                fecha_compra: new Date(),
                costo_compra: 600, // Expensive
                kilometraje_acumulado: 80000, // Low km
                reencauches_realizados: 0,
                profundidad_remanente_actual_mm: 6
            }
        });
    });

    test('6C.2: Should return benchmarking data grouped by brand', async () => {
        const response = await apiContext.get(ENDPOINT);
        expect(response.ok()).toBeTruthy();

        const json = await response.json();
        expect(json.success).toBeTruthy();

        const data = json.data;
        expect(Array.isArray(data)).toBeTruthy();
        console.log('Benchmarking Data:', JSON.stringify(data, null, 2));

        // Find our test brands
        const reportA = data.find((b: any) => b.marca.includes(`Bridgestone ${TEST_ID}`));
        const reportB = data.find((b: any) => b.marca.includes(`Michelin ${TEST_ID}`));

        expect(reportA).toBeDefined();
        expect(reportB).toBeDefined();

        // Validations A (Better CPK)
        // Tire A1: 400/100000 = 0.004
        // Tire A2: 420/110000 = 0.0038
        // Avg CPK approx ~0.0039
        expect(reportA.total_neumaticos).toBe(2);
        expect(reportA.km_promedio_retiro).toBeGreaterThan(100000);
        expect(reportA.cpk_promedio).toBeLessThan(0.005);
        expect(reportA.indice_reencauchabilidad).toBe(0.5); // 1 tire retreaded / 2 total

        // Validations B (Worse CPK)
        // Tire B1: 600/80000 = 0.0075
        expect(reportB.total_neumaticos).toBe(1);
        expect(reportB.cpk_promedio).toBeGreaterThan(0.007);
        expect(reportB.cpk_promedio).toBeGreaterThan(reportA.cpk_promedio); // Brand A is better
    });
});
