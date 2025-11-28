import { GET, POST } from '@/app/api/v1/neumaticos/route';
import { GET as GET_ONE, PUT, DELETE } from '@/app/api/v1/neumaticos/[id]/route';
import { auth } from '@/lib/auth/auth';
import { prisma } from '@/lib/prisma';
import { createMockSession, mockSessions } from '../helpers/auth-helpers';
import { cleanTestData, createTestNeumatico } from '../helpers/database-helpers';
import { NextRequest } from 'next/server';

// Mock auth
jest.mock('@/lib/auth/auth', () => ({
    auth: jest.fn(),
}));

describe('Neumáticos API Integration Tests', () => {
    const BASE_URL = 'http://localhost:3000/api/v1/neumaticos';

    beforeAll(async () => {
        await cleanTestData();
    });

    afterAll(async () => {
        await cleanTestData();
        await prisma.$disconnect();
    });

    beforeEach(() => {
        jest.clearAllMocks();
    });

    // ...

    describe('GET /api/v1/neumaticos', () => {
        it('should return 401 if not authenticated', async () => {
            (auth as jest.Mock).mockResolvedValue(null);
            const req = new NextRequest(BASE_URL);
            const res = await GET(req);
            expect(res.status).toBe(401);
        });

        it('should return 200 and list of neumaticos for authenticated user', async () => {
            (auth as jest.Mock).mockResolvedValue(mockSessions.operador);
            const req = new NextRequest(BASE_URL);
            const res = await GET(req);
            expect(res.status).toBe(200);
            const data = await res.json();
            expect(Array.isArray(data.data)).toBe(true);
        });
    });

    describe('POST /api/v1/neumaticos', () => {

        it('should return 403 if user is not authorized (OPERADOR)', async () => {
            (auth as jest.Mock).mockResolvedValue(mockSessions.operador);
            const req = new NextRequest(BASE_URL, {
                method: 'POST',
                body: JSON.stringify({})
            });
            const res = await POST(req);
            expect(res.status).toBe(403);
        });

        it('should create a neumatico if user is authorized (ADMIN)', async () => {
            (auth as jest.Mock).mockResolvedValue(mockSessions.admin);

            // Create dependencies
            const timestamp = Date.now();
            let fabricante;
            try {
                fabricante = await prisma.fabricanteNeumatico.create({
                    data: { nombre: `Michelin Test ${timestamp}`, pais_origen: 'Francia' }
                });
            } catch (e) {
                console.error('Error creating fabricante:', e);
                throw e;
            }

            let modelo;
            try {
                console.log('Fabricante ID:', fabricante.id);
                modelo = await prisma.modeloNeumatico.create({
                    data: {
                        fabricante_id: fabricante.id,
                        nombre: `X Multi Z Test ${timestamp}`,
                        medida: '295/80R22.5',
                        profundidad_inicial_mm: 18.0
                    }
                });
            } catch (e) {
                const fs = require('fs');
                fs.writeFileSync('error.log', JSON.stringify(e, null, 2));
                console.log('Error creating modelo:', JSON.stringify(e, null, 2));
                throw e;
            }

            const newNeumatico = {
                numero_serie: 'TEST-NEW-123',
                modelo_id: modelo.id,
                dot: '2024',
                estado_actual: 'EN_STOCK',
                profundidad_inicial_mm: 18.0,
                profundidad_actual_mm: 18.0,
                presion_actual_psi: 110.0,
                fecha_compra: new Date().toISOString(),
                costo_compra: 450.00
            };

            const req = new NextRequest(BASE_URL, {
                method: 'POST',
                body: JSON.stringify(newNeumatico)
            });
            const res = await POST(req);

            // Debug if fails
            if (res.status !== 201) {
                const err = await res.json();
                console.error('Create failed:', err);
            }

            expect(res.status).toBe(201);
            const data = await res.json();
            expect(data.data.numero_serie).toBe(newNeumatico.numero_serie);
        });
    });
});
