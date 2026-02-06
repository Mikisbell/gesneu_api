
import { test, expect } from '@playwright/test';
import prisma from '../../../src/lib/prisma';
import dotenv from 'dotenv';

dotenv.config({ path: '.env' });

test.describe('Fase 6C.3: Casing Scoring Verification', () => {
    let apiContext: any;
    const SESSION_FILE = 'auth_6c_scoring.json';
    const SCORING_ENDPOINT = (id: string) => `/api/v1/neumaticos/${id}/scoring`;
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

        // Brand Premium (Michelin)
        const premiumBrand = await prisma.fabricanteNeumatico.create({
            data: { nombre: `Michelin Scoring ${TEST_ID}`, codigo_abreviado: `MI${TEST_ID}` }
        });
        const premiumModel = await prisma.modeloNeumatico.create({
            data: { fabricante_id: premiumBrand.id, nombre_modelo: `XZE ${TEST_ID}`, medida: '295/80', profundidad_original_mm: 18 }
        });

        // Brand Budget (Generic)
        const budgetBrand = await prisma.fabricanteNeumatico.create({
            data: { nombre: `Budget Scoring ${TEST_ID}`, codigo_abreviado: `BU${TEST_ID}` }
        });
        const budgetModel = await prisma.modeloNeumatico.create({
            data: { fabricante_id: budgetBrand.id, nombre_modelo: `Cheap ${TEST_ID}`, medida: '295/80', profundidad_original_mm: 15 }
        });

        // Case 1: Premium Tire, Newish, 0 Retreads -> APTO
        const tirePremiumNew = await prisma.neumatico.create({
            data: {
                empresa_id: empresa.id,
                modelo_id: premiumModel.id,
                numero_serie: `PREM-NEW-${TEST_ID}`,
                estado_actual: 'EN_USO',
                fecha_compra: new Date(), // New
                reencauches_realizados: 0,
                costo_compra: 500,
                profundidad_remanente_actual_mm: 5
            }
        });
        process.env.TIRE_PREM_NEW_ID = tirePremiumNew.id;

        // Case 2: Premium Tire, Max Retreads (3) -> DESECHO
        const tirePremiumOld = await prisma.neumatico.create({
            data: {
                empresa_id: empresa.id,
                modelo_id: premiumModel.id,
                numero_serie: `PREM-OLD-${TEST_ID}`,
                estado_actual: 'EN_USO',
                fecha_compra: new Date('2020-01-01'), // 6 years old (Penalty)
                reencauches_realizados: 3, // Max limit
                costo_compra: 500,
                profundidad_remanente_actual_mm: 2
            }
        });
        process.env.TIRE_PREM_OLD_ID = tirePremiumOld.id;

        // Case 3: Budget Tire, 1 Retread (Limit 1) -> EVALUAR/DESECHO (likely low score)
        const tireBudget = await prisma.neumatico.create({
            data: {
                empresa_id: empresa.id,
                modelo_id: budgetModel.id,
                numero_serie: `BUDGET-${TEST_ID}`,
                estado_actual: 'EN_USO',
                fecha_compra: new Date(),
                reencauches_realizados: 1, // Limit for budget
                costo_compra: 200,
                profundidad_remanente_actual_mm: 3
            }
        });
        process.env.TIRE_BUDGET_ID = tireBudget.id;
    });

    test('6C.3: Validar Scoring Premium Nuevo (Apto)', async () => {
        const response = await apiContext.get(SCORING_ENDPOINT(process.env.TIRE_PREM_NEW_ID!));
        expect(response.ok()).toBeTruthy();
        const json = await response.json();
        const data = json.data;

        console.log('Premium New:', data);
        expect(data.factors.brand_tier).toBe('PREMIUM');
        expect(data.recommendation).toBe('APTO_REENCAUCHE');
        expect(data.score).toBeGreaterThan(80);
    });

    test('6C.3: Validar Scoring Premium Viejo/Max Vidas (Desecho)', async () => {
        const response = await apiContext.get(SCORING_ENDPOINT(process.env.TIRE_PREM_OLD_ID!));
        expect(response.ok()).toBeTruthy();
        const json = await response.json();
        const data = json.data;

        console.log('Premium Old:', data);
        expect(data.factors.brand_tier).toBe('PREMIUM');
        expect(data.recommendation).toBe('DESECHO');
        // Penalty for max retreads should kill score
        expect(data.factors.retread_penalty).toBeGreaterThanOrEqual(60);
    });

    test('6C.3: Validar Scoring Budget (Limite Vidas)', async () => {
        const response = await apiContext.get(SCORING_ENDPOINT(process.env.TIRE_BUDGET_ID!));
        expect(response.ok()).toBeTruthy();
        const json = await response.json();
        const data = json.data;

        console.log('Budget used:', data);
        expect(data.factors.brand_tier).toBe('STANDARD');
        // 1 retread for standard logic causes penalty
        // Might be EVALUAR_MANUAL or DESECHO depending on strictness
        expect(['DESECHO', 'EVALUAR_MANUAL']).toContain(data.recommendation);
        expect(data.max_retreads_allowed).toBe(1);
    });
});
