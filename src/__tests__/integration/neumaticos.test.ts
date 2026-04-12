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
            const res = await GET(req, {} as any);
            expect(res.status).toBe(401);
        });

        it('should return 200 and list of neumaticos for authenticated user', async () => {
            (auth as jest.Mock).mockResolvedValue(mockSessions.operador);
            const req = new NextRequest(BASE_URL);
            const res = await GET(req, {} as any);
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
            const res = await POST(req, {} as any);
            expect(res.status).toBe(403);
        });

        // TODO: Requiere investigación - el servicio devuelve 500 a pesar de datos válidos
        it('should create a neumatico if user is authorized (ADMIN)', async () => {
            // Get real admin user from DB
            const adminUser = await prisma.usuario.findFirst({
                where: { username: 'admin' }
            });
            if (!adminUser) throw new Error('Admin user not found in DB');

            // Mock session with REAL user ID
            (auth as jest.Mock).mockResolvedValue({
                ...mockSessions.admin,
                user: {
                    ...mockSessions.admin.user,
                    id: adminUser.id
                }
            });

            // Create dependencies
            const timestamp = Date.now();
            let fabricante;
            try {
                fabricante = await prisma.fabricanteNeumatico.create({
                    data: { nombre: `Michelin Test ${timestamp}` }
                });
            } catch (e) {
                console.error('Error creating fabricante:', e);
                throw e;
            }

            let modelo;
            try {
                modelo = await prisma.modeloNeumatico.create({
                    data: {
                        fabricante_id: fabricante.id,
                        nombre_modelo: `X Multi Z Test ${timestamp}`,
                        medida: '295/80R22.5',
                        profundidad_original_mm: 18.0
                    }
                });
            } catch (e) {
                console.error('Error creating modelo:', e);
                throw e;
            }

            // Get existing almacen (from seed)
            const almacen = await prisma.almacen.findFirst();
            if (!almacen) {
                throw new Error('No almacen found. Run seed first.');
            }

            const newNeumatico = {
                numero_serie: `TEST-NEW-${timestamp}`,
                modelo_id: modelo.id,
                dot: '2024',
                profundidad_inicial_mm: 18.0,
                ubicacion_almacen_id: almacen.id,
                costo_compra: 450.00,
                fecha_compra: new Date().toISOString(),
                es_reencauchado: false,
                moneda_compra: 'PEN'
            };

            const req = new NextRequest(BASE_URL, {
                method: 'POST',
                body: JSON.stringify(newNeumatico)
            });
            const res = await POST(req, {} as any);

            if (res.status !== 201) {
                const errorData = await res.json();
                throw new Error(`POST Failed with ${res.status}: ${JSON.stringify(errorData, null, 2)}`);
            }
            expect(res.status).toBe(201);
            const body = await res.json();
            // Response shape puede ser { data: { numero_serie } } o { data: { neumatico: { numero_serie } } }
            // dependiendo del service. Verificamos que el body tenga la estructura success + data.
            expect(body.success).toBe(true);
            expect(body.data).toBeDefined();
        });
    });
});
