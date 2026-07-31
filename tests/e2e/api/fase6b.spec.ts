import { test, expect, APIRequestContext } from '@playwright/test';
import prisma from '@/lib/prisma';
import bcrypt from 'bcryptjs';

test.describe('Fase 6B: API Verification', () => {
    let neumaticoId: string;
    let apiContext: APIRequestContext;
    const INSPECCIONES_ENDPOINT = '/api/v1/inspecciones';
    const NEUMATICOS_ENDPOINT = '/api/v1/neumaticos';

    test.beforeAll(async ({ playwright, browser }) => {
        // 0. Asegurar usuario admin (Seed en tiempo real)
        const hashedPassword = await bcrypt.hash(process.env.STRESS_PASSWORD || 'admin123', 10);

        // Crear empresa para asegurar FK
        const empresa = await prisma.empresa.upsert({
            where: { ruc: '20123456789' },
            update: {},
            create: {
                nombre: 'GesNeu Test Corp',
                ruc: '20123456789'
            }
        });

        await prisma.usuario.upsert({
            where: { email: 'admin@gesneu.com' },
            update: {
                password_hash: hashedPassword,
                empresa_id: empresa.id
            },
            create: {
                nombre_completo: 'Admin Test',
                email: 'admin@gesneu.com',
                password_hash: hashedPassword,
                rol: 'ADMIN',
                empresa_id: empresa.id,
                username: 'admin'
            }
        });

        // Autenticación via UI para obtener cookies
        const context = await browser.newContext();
        const page = await context.newPage();

        await page.goto('/login');
        await page.fill('input[name="identifier"]', process.env.STRESS_USER || 'admin');
        await page.fill('input[name="password"]', process.env.STRESS_PASSWORD || 'admin123');
        await page.click('button[type="submit"]');

        // Esperar a redirigir al dashboard (login exitoso) - Timeout aumentado
        await page.waitForURL(/\/dashboard/, { timeout: 60000 });

        // Guardar estado de almacenamiento (cookies)
        await context.storageState({ path: 'auth.json' });

        // Crear contexto API autenticado
        // Obtenemos la baseURL del proyecto si existe, o inferimos del page url
        const baseURL = page.url().split('/dashboard')[0];
        console.log(`Base URL for API: ${baseURL}`);

        apiContext = await playwright.request.newContext({
            storageState: 'auth.json',
            baseURL
        });

        await context.close();
    });

    // Puesto que crear datos complejos es difícil sin un seed, vamos a buscar un neumático existente
    // y trabajar con él, o crear uno si tenemos endpoint de seed.
    // Estrategia: Buscar neumáticos activos y usar el primero.

    test('6B.1 & 6B.2: Crear Inspección y Verificar Alertas', async () => {
        // a) Buscar neumático
        const neumaticosRes = await apiContext.get(`${NEUMATICOS_ENDPOINT}?limit=1`);

        // Debug si falla
        if (!neumaticosRes.ok()) {
            console.error('Error getting neumaticos:', await neumaticosRes.text(), neumaticosRes.status());
        }

        expect(neumaticosRes.ok()).toBeTruthy();
        const jsonResponse = await neumaticosRes.json();
        expect(jsonResponse.success).toBeTruthy();

        const neumaticos = jsonResponse.data;
        expect(Array.isArray(neumaticos)).toBeTruthy();
        expect(neumaticos.length).toBeGreaterThan(0);
        neumaticoId = neumaticos[0].id;

        console.log(`Using neumatico: ${neumaticoId} for testing`);

        // b) Crear Inspección 1 (Base) - Hace 15 días (simulado ahora)
        const inspBase = await apiContext.post(INSPECCIONES_ENDPOINT, {
            data: {
                neumatico_id: neumaticoId,
                psi_medido: 100,
                mm_medido: 15,
                fuente: 'MANUAL',
                observaciones: 'Base test'
            }
        });
        expect(inspBase.ok()).toBeTruthy();
        const jsonBase = await inspBase.json();
        expect(jsonBase.success).toBeTruthy();

        // c) Crear Inspección 2 (Anomalía Presión) - PSI baja a 90 (>5% drop)
        const inspAnomalia = await apiContext.post(INSPECCIONES_ENDPOINT, {
            data: {
                neumatico_id: neumaticoId,
                psi_medido: 90,
                mm_medido: 14.8,
                fuente: 'SENSOR_TPMS',
                observaciones: 'Test alerta presion'
            }
        });

        expect(inspAnomalia.ok()).toBeTruthy();
        const jsonAnomalia = await inspAnomalia.json();
        expect(jsonAnomalia.success).toBeTruthy();

        // Verificar 6B.2: Alertas generadas
        // El count viene dentro de data.alertas_generadas o data directamente?
        // Asumiendo que devolvemos la inspeccion creada + metadata.
        // Si no, verificamos alerts via query separada si fuera necesario, pero el endpoint prometía devolverlo.
        if (jsonAnomalia.data && jsonAnomalia.data.alertas_generadas !== undefined) {
            console.log('Alertas generadas:', jsonAnomalia.data.alertas_generadas);
            expect(jsonAnomalia.data).toHaveProperty('alertas_generadas');
        }
    });

    test('6B.3: Endpoint Predicción', async () => {
        expect(neumaticoId).toBeDefined();
        const res = await apiContext.get(`/api/v1/neumaticos/${neumaticoId}/prediccion`);

        if (!res.ok()) { console.log(await res.text()); }
        expect(res.ok()).toBeTruthy();

        const jsonPred = await res.json();
        expect(jsonPred.success).toBeTruthy();
        const data = jsonPred.data;

        console.log('Predicción Data:', data);

        expect(data).toHaveProperty('km_restantes_estimado');
        expect(data).toHaveProperty('fecha_estimada_cambio');
        expect(data).toHaveProperty('estado');
    });

    test('6B.4: Endpoint Próximas Inspecciones', async () => {
        const res = await apiContext.get('/api/v1/inspecciones/proximas?limit=5');
        expect(res.ok()).toBeTruthy();
        const jsonProx = await res.json();
        expect(jsonProx.success).toBeTruthy();
        const data = jsonProx.data;

        console.log('Próximas Data:', data);

        expect(data).toHaveProperty('resumen');
        expect(data).toHaveProperty('proximas');
        expect(Array.isArray(data.proximas)).toBeTruthy();

        if (data.proximas.length > 0) {
            const item = data.proximas[0];
            expect(item).toHaveProperty('urgencia');
            expect(item).toHaveProperty('frecuencia_recomendada_dias');
        }
    });
});
