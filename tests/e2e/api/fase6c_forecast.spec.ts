
import { test, expect } from '@playwright/test';
import prisma from '../../../src/lib/prisma';
import dotenv from 'dotenv';

dotenv.config({ path: '.env' });

test.describe('Fase 6C.4: Purchase Forecast Verification', () => {
    let apiContext: any;
    const SESSION_FILE = 'auth_6c_forecast.json';
    const ENDPOINT = '/api/v1/reportes/forecast?days=90';
    const TEST_ID = Math.floor(Math.random() * 9999);

    test.beforeAll(async ({ playwright, browser }) => {
        // 1. Auth Setup
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

        // 2. Data Seeding
        const empresa = await prisma.empresa.findFirst({ where: { ruc: '20123456789' } });
        if (!empresa) throw new Error('Empresa not found');

        // Modelo Testing
        const fab = await prisma.fabricanteNeumatico.create({ data: { nombre: `ForecastBrand ${TEST_ID}`, codigo_abreviado: `FB${TEST_ID}` } });
        const modelo = await prisma.modeloNeumatico.create({
            data: {
                fabricante_id: fab.id,
                nombre_modelo: `ForecastModel ${TEST_ID}`,
                medida: `295/80R22.5`,
                profundidad_original_mm: 20
            }
        });

        // Case 1: Critical Tire (Needs replacement soon)
        // Original: 20mm. Current: 4mm. Min: 3mm.
        // Usage: 2 years. 
        // Wear Rate = (20 - 4) / 730 days = 16/730 = ~0.02 mm/day
        // Remaining Life: (4 - 3)mm / 0.02 = 50 days.
        // Should appear in 90 day forecast.
        const twoYearsAgo = new Date();
        twoYearsAgo.setFullYear(twoYearsAgo.getFullYear() - 2);

        await prisma.neumatico.create({
            data: {
                empresa_id: empresa.id,
                modelo_id: modelo.id,
                numero_serie: `CRIT-${TEST_ID}`,
                estado_actual: 'EN_USO',
                fecha_compra: twoYearsAgo,
                profundidad_remanente_actual_mm: 4,
                costo_compra: 300
            }
        });

        // Case 2: Healthy Tire (No replacement needed)
        // Current: 15mm. 
        // Remaining: 12mm. Rate ~0.02. Days: 600.
        // Should NOT appear in 90 day forecast.
        await prisma.neumatico.create({
            data: {
                empresa_id: empresa.id,
                modelo_id: modelo.id,
                numero_serie: `GOOD-${TEST_ID}`,
                estado_actual: 'EN_USO',
                fecha_compra: twoYearsAgo,
                profundidad_remanente_actual_mm: 15,
                costo_compra: 300
            }
        });
    });

    test('6C.4: Should forecast purchasing needs correctly', async () => {
        const response = await apiContext.get(ENDPOINT);
        expect(response.ok()).toBeTruthy();

        const json = await response.json();
        expect(json.success).toBeTruthy();
        const data = json.data;

        console.log('Forecast Data:', JSON.stringify(data, null, 2));

        // Find our test model forecast
        const modelForecast = data.find((item: any) => item.medida === '295/80R22.5');

        // Assertions
        expect(modelForecast).toBeDefined();
        // Should suggest at least 1 tire (the Critical one)
        // Note: Filters usually catch specific series, verify deeply
        const criticalTire = modelForecast.detalles_neumaticos.find((t: any) => t.serie === `CRIT-${TEST_ID}`);
        const goodTire = modelForecast.detalles_neumaticos.find((t: any) => t.serie === `GOOD-${TEST_ID}`);

        expect(criticalTire).toBeDefined();
        expect(criticalTire.dias_restantes_estimados).toBeLessThan(90);

        expect(goodTire).toBeUndefined(); // Should not be in forecast
    });
});
