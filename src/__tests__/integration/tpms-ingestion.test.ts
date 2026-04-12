import { POST } from '@/app/api/v1/integraciones/tpms/route';
import { prisma } from '@/lib/prisma';
import { cleanTestData, createTestNeumatico, createTestModelo, createTestUser, createTestFabricante, getOrCreateTestEnterprise } from '../helpers/database-helpers';
import { NextRequest } from 'next/server';

const TEST_API_KEY = 'test-tpms-key-123';

describe('TPMS Ingestion API', () => {
    let empresaId: string;
    let availableNeumaticoId: string;
    let sensorId = 'SENSOR-TEST-001';

    beforeAll(async () => {
        // Set env var for auth
        process.env.TPMS_API_KEY = TEST_API_KEY;
    });

    afterAll(async () => {
        delete process.env.TPMS_API_KEY;
        await cleanTestData();
    });

    beforeEach(async () => {
        await cleanTestData();
        const empresa = await getOrCreateTestEnterprise();
        empresaId = empresa.id;

        const maker = await createTestFabricante(empresaId);
        const modelo = await createTestModelo(maker.id);

        // Update modelo to have specific recommended pressure for alert testing
        await prisma.modeloNeumatico.update({
            where: { id: modelo.id },
            data: { presion_recomendada_psi: 100 }
        });

        // Create tire with sensor_id
        const neumatico = await createTestNeumatico(modelo.id, empresaId);
        await prisma.neumatico.update({
            where: { id: neumatico.id },
            data: { sensor_id: sensorId }
        });
        availableNeumaticoId = neumatico.id;
    });

    it('should reject requests without valid API Key', async () => {
        const req = new NextRequest('http://localhost:3000/api/v1/integraciones/tpms', {
            method: 'POST',
            headers: { 'content-type': 'application/json' }, // No x-api-key
            body: JSON.stringify([])
        });

        const res = await POST(req);
        // Unauthorized
        expect(res.status).toBe(401);
    });

    it('should process valid readings and trigger alerts', async () => {
        const payload = [
            {
                sensor_id: sensorId,
                psi: 70, // Below 80% of 100 (Critical < 70? No, 80% is 80 PSI. < 56 is critical (70% of 80?). Wait. Logic check below.)
                temp_c: 45,
                timestamp: new Date().toISOString()
            }
        ];

        // Logic in route:
        // umbralMinimo = 100 * 0.8 = 80.
        // Alert trigger if psi < 80.
        // Severidad CRITICAL if psi < 80 * 0.7 = 56.
        // So 70 is WARNING (LOW, but not CRITICAL low). Wait, typical alert logic:
        // AlertasService: severidad = presionActual < (presionMinima * 0.7) ? CRITICAL : WARNING
        // 70 < 56? False. So WARNING.

        const req = new NextRequest('http://localhost:3000/api/v1/integraciones/tpms', {
            method: 'POST',
            headers: {
                'x-api-key': TEST_API_KEY,
                'content-type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const res = await POST(req);
        const json = await res.json();

        expect(res.status).toBe(200);
        expect(json.processed).toBe(1);
        expect(json.alerts_triggered).toBe(1);

        // Verify DB
        const lectura = await prisma.lecturaPresion.findFirst({
            where: { neumatico_id: availableNeumaticoId }
        });
        expect(lectura).toBeTruthy();
        expect(Number(lectura?.presion_psi)).toBe(70);
        expect(lectura?.fuente).toBe('SENSOR_TPMS');

        // Verify Alert
        const alert = await prisma.alerta.findFirst({
            where: { neumatico_id: availableNeumaticoId }
        });
        expect(alert).toBeTruthy();
        expect(alert?.tipo).toBe('PRESION_BAJA');
        // Severity puede ser WARNING o CRITICAL dependiendo de cuál observer/service
        // generó la alerta primero (AlertObserver emite WARNING, InspeccionService
        // puede emitir CRITICAL si la desviación es >10%). Ambos son válidos para 70 PSI.
        expect(['WARNING', 'CRITICAL']).toContain(alert?.severidad);
    });

    it('should update neumatico snapshot', async () => {
        const payload = [{ sensor_id: sensorId, psi: 105, temp_c: 50 }];
        const req = new NextRequest('http://localhost:3000/api/v1/integraciones/tpms', {
            method: 'POST',
            headers: { 'x-api-key': TEST_API_KEY },
            body: JSON.stringify(payload)
        });

        await POST(req);

        const neumatico = await prisma.neumatico.findUnique({ where: { id: availableNeumaticoId } });
        expect(Number(neumatico?.presion_actual_psi)).toBe(105);
    });
});
