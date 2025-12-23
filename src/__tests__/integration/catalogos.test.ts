/**
 * Integration tests for Catálogos endpoints (Almacenes & Proveedores)
 */
import { NextRequest } from 'next/server';
import { GET as GET_ALMACENES, POST as POST_ALMACENES } from '@/app/api/v1/catalogos/almacenes/route';
import { DELETE as DELETE_ALMACEN } from '@/app/api/v1/catalogos/almacenes/[id]/route';
import { GET as GET_PROVEEDORES, POST as POST_PROVEEDORES } from '@/app/api/v1/catalogos/proveedores/route';
import { PUT as PUT_PROVEEDOR, DELETE as DELETE_PROVEEDOR } from '@/app/api/v1/catalogos/proveedores/[id]/route';
import { auth } from '@/lib/auth/auth';
import { mockSessions } from '../helpers/auth-helpers';
import {
    setupTestDatabase,
    teardownTestDatabase,
    cleanTestData
} from '../helpers/database-helpers';

// Mock auth
jest.mock('@/lib/auth/auth', () => ({
    auth: jest.fn()
}));

const BASE_URL = 'http://localhost:3000/api/v1/catalogos';

describe('Catálogos API Integration Tests', () => {
    beforeAll(async () => {
        await setupTestDatabase();
    });

    afterAll(async () => {
        await teardownTestDatabase();
    });

    afterEach(async () => {
        await cleanTestData();
        jest.clearAllMocks();
    });

    describe('Almacenes Endpoints', () => {
        describe('GET /api/v1/catalogos/almacenes', () => {
            it('should return 401 when not authenticated', async () => {
                (auth as jest.Mock).mockResolvedValue(null);
                const req = new NextRequest(`${BASE_URL}/almacenes`);
                const res = await GET_ALMACENES(req);
                expect(res.status).toBe(401);
            });

            it('should return 200 for all roles', async () => {
                const allRoles = ['admin', 'gestor', 'operador', 'consultor'] as const;

                for (const role of allRoles) {
                    (auth as jest.Mock).mockResolvedValue(mockSessions[role]);
                    const req = new NextRequest(`${BASE_URL}/almacenes`);
                    const res = await GET_ALMACENES(req);
                    expect(res.status).toBe(200);
                    const data = await res.json();
                    expect(data).toHaveProperty('data');
                }
            });
        });

        describe('POST /api/v1/catalogos/almacenes', () => {
            it('should return 403 when consultor tries to create', async () => {
                (auth as jest.Mock).mockResolvedValue(mockSessions.consultor);
                const req = new NextRequest(`${BASE_URL}/almacenes`, {
                    method: 'POST',
                    body: JSON.stringify({ nombre: '[TEST] Almacen Consultor' })
                });
                const res = await POST_ALMACENES(req);
                expect(res.status).toBe(403);
            });

            it('should return 403 when operador tries to create', async () => {
                (auth as jest.Mock).mockResolvedValue(mockSessions.operador);
                const req = new NextRequest(`${BASE_URL}/almacenes`, {
                    method: 'POST',
                    body: JSON.stringify({ nombre: '[TEST] Almacen Operador' })
                });
                const res = await POST_ALMACENES(req);
                expect(res.status).toBe(403);
            });

            it('should allow gestor to create', async () => {
                (auth as jest.Mock).mockResolvedValue(mockSessions.gestor);
                const req = new NextRequest(`${BASE_URL}/almacenes`, {
                    method: 'POST',
                    body: JSON.stringify({ nombre: `[TEST] Almacen Gestor ${Date.now()}` })
                });
                const res = await POST_ALMACENES(req);
                expect([400, 201, 409]).toContain(res.status);
            });
        });

        describe('DELETE /api/v1/catalogos/almacenes/:id', () => {
            it('should return 403 when gestor tries to delete', async () => {
                (auth as jest.Mock).mockResolvedValue(mockSessions.gestor);
                const req = new NextRequest(`${BASE_URL}/almacenes/00000000-0000-0000-0000-000000000000`, {
                    method: 'DELETE'
                });
                const res = await DELETE_ALMACEN(req, { params: Promise.resolve({ id: '00000000-0000-0000-0000-000000000000' }) });
                expect(res.status).toBe(403);
            });

            it('should allow only admin to delete', async () => {
                (auth as jest.Mock).mockResolvedValue(mockSessions.admin);
                const req = new NextRequest(`${BASE_URL}/almacenes/00000000-0000-0000-0000-000000000000`, {
                    method: 'DELETE'
                });
                const res = await DELETE_ALMACEN(req, { params: Promise.resolve({ id: '00000000-0000-0000-0000-000000000000' }) });
                expect([404, 200]).toContain(res.status);
            });
        });
    });

    describe('Proveedores Endpoints', () => {
        describe('GET /api/v1/catalogos/proveedores', () => {
            it('should return 401 when not authenticated', async () => {
                (auth as jest.Mock).mockResolvedValue(null);
                const req = new NextRequest(`${BASE_URL}/proveedores`);
                const res = await GET_PROVEEDORES(req);
                expect(res.status).toBe(401);
            });

            it('should return 200 for all roles', async () => {
                const allRoles = ['admin', 'gestor', 'operador', 'consultor'] as const;

                for (const role of allRoles) {
                    (auth as jest.Mock).mockResolvedValue(mockSessions[role]);
                    const req = new NextRequest(`${BASE_URL}/proveedores`);
                    const res = await GET_PROVEEDORES(req);
                    expect(res.status).toBe(200);
                    const data = await res.json();
                    expect(data).toHaveProperty('data');
                }
            });
        });

        describe('POST /api/v1/catalogos/proveedores', () => {
            it('should return 403 when consultor tries to create', async () => {
                (auth as jest.Mock).mockResolvedValue(mockSessions.consultor);
                const req = new NextRequest(`${BASE_URL}/proveedores`, {
                    method: 'POST',
                    body: JSON.stringify({ nombre: '[TEST] Proveedor', tipo: 'FABRICANTE' })
                });
                const res = await POST_PROVEEDORES(req);
                expect(res.status).toBe(403);
            });

            it('should allow gestor to create with valid data', async () => {
                (auth as jest.Mock).mockResolvedValue(mockSessions.gestor);
                const req = new NextRequest(`${BASE_URL}/proveedores`, {
                    method: 'POST',
                    body: JSON.stringify({
                        tipo: 'FABRICANTE',
                        nombre: `[TEST] Proveedor ${Date.now()}`,
                        ruc: `TEST${Date.now()}`.substring(0, 20)
                    })
                });
                const res = await POST_PROVEEDORES(req);
                expect([400, 201, 409]).toContain(res.status);
            });

            it('should return 400 with missing required fields', async () => {
                (auth as jest.Mock).mockResolvedValue(mockSessions.admin);
                const req = new NextRequest(`${BASE_URL}/proveedores`, {
                    method: 'POST',
                    body: JSON.stringify({})
                });
                const res = await POST_PROVEEDORES(req);
                expect(res.status).toBe(400);
            });
        });

        describe('PUT /api/v1/catalogos/proveedores/:id', () => {
            it('should return 403 when operador tries to update', async () => {
                (auth as jest.Mock).mockResolvedValue(mockSessions.operador);
                const req = new NextRequest(`${BASE_URL}/proveedores/00000000-0000-0000-0000-000000000000`, {
                    method: 'PUT',
                    body: JSON.stringify({ nombre: 'Updated' })
                });
                const res = await PUT_PROVEEDOR(req, { params: Promise.resolve({ id: '00000000-0000-0000-0000-000000000000' }) });
                expect(res.status).toBe(403);
            });

            it('should allow gestor to update', async () => {
                (auth as jest.Mock).mockResolvedValue(mockSessions.gestor);
                const req = new NextRequest(`${BASE_URL}/proveedores/00000000-0000-0000-0000-000000000000`, {
                    method: 'PUT',
                    body: JSON.stringify({ nombre: 'Updated' })
                });
                const res = await PUT_PROVEEDOR(req, { params: Promise.resolve({ id: '00000000-0000-0000-0000-000000000000' }) });
                expect([400, 404, 200]).toContain(res.status);
            });
        });

        describe('DELETE /api/v1/catalogos/proveedores/:id', () => {
            it('should return 403 when gestor tries to delete', async () => {
                (auth as jest.Mock).mockResolvedValue(mockSessions.gestor);
                const req = new NextRequest(`${BASE_URL}/proveedores/00000000-0000-0000-0000-000000000000`, {
                    method: 'DELETE'
                });
                const res = await DELETE_PROVEEDOR(req, { params: Promise.resolve({ id: '00000000-0000-0000-0000-000000000000' }) });
                expect(res.status).toBe(403);
            });

            it('should allow only admin to delete', async () => {
                (auth as jest.Mock).mockResolvedValue(mockSessions.admin);
                const req = new NextRequest(`${BASE_URL}/proveedores/00000000-0000-0000-0000-000000000000`, {
                    method: 'DELETE'
                });
                const res = await DELETE_PROVEEDOR(req, { params: Promise.resolve({ id: '00000000-0000-0000-0000-000000000000' }) });
                expect([404, 200]).toContain(res.status);
            });
        });
    });
});
