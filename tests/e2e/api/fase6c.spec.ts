import { test, expect } from '@playwright/test';
import prisma from '../../../src/lib/prisma';
import dotenv from 'dotenv';

// const prisma = new PrismaClient(); // Removed

test.describe('Fase 6C: Financials & TCO Verification', () => {
    let apiContext: any;
    let neumaticoId: string;
    const FINANCIALS_ENDPOINT = (id: string) => `/api/v1/neumaticos/${id}/financials`;

    test.beforeAll(async ({ playwright, browser }) => {
        // 1. Auth Setup (Login UI para obtener cookies)
        const context = await browser.newContext();
        await context.grantPermissions(['clipboard-read', 'clipboard-write']);
        const page = await context.newPage();
        await page.goto('http://localhost:3005/login');
        await page.fill('input[name="identifier"]', 'admin@gesneu.com'); // Asumimos seed existente (Fase 6B test)
        await page.fill('input[name="password"]', process.env.STRESS_PASSWORD || 'admin123'); // Fallback común
        await page.click('button[type="submit"]');
        await page.waitForURL('**/dashboard');

        await context.storageState({ path: 'auth_6c.json' });

        // 2. Crear Contexto API Autenticado
        apiContext = await playwright.request.newContext({
            baseURL: 'http://localhost:3005',
            storageState: 'auth_6c.json'
        });

        // 3. Crear Datos de Prueba (Escenario TCO)
        // Empresa y Usuario ya existen del test anterior o seed inicial.
        // Buscamos Empresa
        const empresa = await prisma.empresa.findFirst({ where: { ruc: '20123456789' } });
        const modelo = await prisma.modeloNeumatico.findFirst();

        if (!empresa || !modelo) throw new Error('Seed data missing (Empresa/Modelo)');

        // Dejar que DB genere ID o UUID válido
        const neumatico = await prisma.neumatico.create({
            data: {
                empresa_id: empresa.id,
                modelo_id: modelo.id,
                numero_serie: `TCO-TEST-${Date.now()}`,
                estado_actual: 'INSTALADO',
                costo_compra: 500.00, // Costo Base
                moneda_compra: 'USD',
                fecha_compra: new Date(),
                kilometraje_acumulado: 1000,
                vida_util_restante_km: 40000,
                profundidad_remanente_actual_mm: 12
            }
        });
        neumaticoId = neumatico.id;

        // Inyectar Evento Reparación (Costo 100)
        await prisma.eventoNeumatico.create({
            data: {
                tipo_evento: 'REPARACION_ENTRADA',
                neumatico_id: neumatico.id,
                fecha_evento: new Date(),
                costo_evento: 100.00,
                contador_vehiculo: 500,
                notas: 'Reparación parche'
            }
        });

        // Inyectar Lecturas de Presión Bajas (Para probar Impacto Combustible)
        // Presión recomendada asumimos 100 (default en servicio si no tiene modelo).
        // Inyectamos 80 PSI (20% deficit)
        await prisma.lecturaPresion.createMany({
            data: [
                { neumatico_id: neumatico.id, presion_psi: 80, fecha_lectura: new Date() },
                { neumatico_id: neumatico.id, presion_psi: 80, fecha_lectura: new Date() }
            ]
        });
    });

    test('6C.1: Validate TCO and CPK Calculation', async () => {
        const response = await apiContext.get(FINANCIALS_ENDPOINT(neumaticoId));
        expect(response.ok()).toBeTruthy();

        const json = await response.json();
        expect(json.success).toBeTruthy();
        const financials = json.data;

        console.log('Financials 6C.1:', financials);

        // Validar TCO
        // Compra (500) + Reparación (100) = 600
        expect(Number(financials.tco)).toBe(600);
        expect(Number(financials.costo_compra)).toBe(500);
        expect(Number(financials.costo_mantenimiento)).toBe(100);

        // Validar CPK
        // 600 USD / 1000 Km = 0.6 USD/Km
        expect(Number(financials.cpk)).toBeCloseTo(0.6, 2);

        // Validar CPK Proyectado
        // 600 / (1000 + 40000) = 600 / 41000 = ~0.0146
        expect(Number(financials.cpk_projected)).toBeLessThan(financials.cpk);
    });

    test('6C.2: Validate Fuel Impact Estimation', async () => {
        const response = await apiContext.get(FINANCIALS_ENDPOINT(neumaticoId));
        const financials = await response.json().then((r: any) => r.data);

        // Presión recomendada (según TcoService default) = 100
        // Presión medida = 80
        // Deficit = 20 psi.
        // Penalidad Combustible aprox > 0
        expect(Number(financials.fuel_waste_estimated_usd)).toBeGreaterThan(0);
        console.log('Estimated Fuel Waste USD:', financials.fuel_waste_estimated_usd);
    });
});
