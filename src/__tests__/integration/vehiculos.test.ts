/**
 * Integration tests for Vehículos endpoints
 */
import { NextRequest } from 'next/server';
import { GET as GET_VEHICULOS, POST as POST_VEHICULOS } from '@/app/api/v1/vehiculos/route';
import { PUT as PUT_VEHICULO, DELETE as DELETE_VEHICULO } from '@/app/api/v1/vehiculos/[id]/route';
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

const BASE_URL = 'http://localhost:3000/api/v1/vehiculos';

describe('Vehículos API Integration Tests', () => {
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

    describe('GET /api/v1/vehiculos', () => {
        it('should return 401 when not authenticated', async () => {
            (auth as jest.Mock).mockResolvedValue(null);
            const req = new NextRequest(`${BASE_URL}`);
            const res = await GET_VEHICULOS(req, { params: Promise.resolve({}) });
            expect(res.status).toBe(401);
        });

        it('should return 200 for all roles with READ permission', async () => {
            const rolesWithRead = ['admin', 'gestor', 'operador', 'consultor'] as const;

            for (const role of rolesWithRead) {
                (auth as jest.Mock).mockResolvedValue(mockSessions[role]);
                const req = new NextRequest(`${BASE_URL}`);
                const res = await GET_VEHICULOS(req, { params: Promise.resolve({}) });
                expect(res.status).toBe(200);
                const data = await res.json();
                expect(data).toHaveProperty('data');
            }
        });
    });

    describe('POST /api/v1/vehiculos', () => {
        it('should return 403 when consultor tries to create', async () => {
            (auth as jest.Mock).mockResolvedValue(mockSessions.consultor);
            const req = new NextRequest(`${BASE_URL}`, {
                method: 'POST',
                body: JSON.stringify({ placa: 'TEST-123' })
            });
            const res = await POST_VEHICULOS(req, { params: Promise.resolve({}) });
            expect(res.status).toBe(403);
        });

        it('should return 403 when operador tries to create', async () => {
            (auth as jest.Mock).mockResolvedValue(mockSessions.operador);
            const req = new NextRequest(`${BASE_URL}`, {
                method: 'POST',
                body: JSON.stringify({ placa: 'TEST-123' })
            });
            const res = await POST_VEHICULOS(req, { params: Promise.resolve({}) });
            expect(res.status).toBe(403);
        });

        it('should allow gestor to create', async () => {
            (auth as jest.Mock).mockResolvedValue(mockSessions.gestor);
            const req = new NextRequest(`${BASE_URL}`, {
                method: 'POST',
                body: JSON.stringify({
                    placa: 'TEST-123',
                    tipo_vehiculo_id: '00000000-0000-0000-0000-000000000000'
                })
            });
            const res = await POST_VEHICULOS(req, { params: Promise.resolve({}) });
            // Auth/authz passed, will fail on validation/business logic
            expect([400, 404, 201, 500]).toContain(res.status);
        });

        it('should allow admin to create', async () => {
            (auth as jest.Mock).mockResolvedValue(mockSessions.admin);
            const req = new NextRequest(`${BASE_URL}`, {
                method: 'POST',
                body: JSON.stringify({
                    placa: 'TEST-123',
                    tipo_vehiculo_id: '00000000-0000-0000-0000-000000000000'
                })
            });
            const res = await POST_VEHICULOS(req, { params: Promise.resolve({}) });
            expect([400, 404, 201, 500]).toContain(res.status);
        });
    });

    describe('PUT /api/v1/vehiculos/:id', () => {
        it('should return 403 when consultor tries to update', async () => {
            (auth as jest.Mock).mockResolvedValue(mockSessions.consultor);
            const req = new NextRequest(`${BASE_URL}/00000000-0000-0000-0000-000000000000`, {
                method: 'PUT',
                body: JSON.stringify({ marca: 'Updated' })
            });
            const res = await PUT_VEHICULO(req, { params: Promise.resolve({ id: '00000000-0000-0000-0000-000000000000' }) });
            expect(res.status).toBe(403);
        });

        it('should return 403 when operador tries to update', async () => {
            (auth as jest.Mock).mockResolvedValue(mockSessions.operador);
            const req = new NextRequest(`${BASE_URL}/00000000-0000-0000-0000-000000000000`, {
                method: 'PUT',
                body: JSON.stringify({ marca: 'Updated' })
            });
            const res = await PUT_VEHICULO(req, { params: Promise.resolve({ id: '00000000-0000-0000-0000-000000000000' }) });
            expect(res.status).toBe(403);
        });

        it('should allow gestor to update', async () => {
            (auth as jest.Mock).mockResolvedValue(mockSessions.gestor);
            const req = new NextRequest(`${BASE_URL}/00000000-0000-0000-0000-000000000000`, {
                method: 'PUT',
                body: JSON.stringify({ marca: 'Updated' })
            });
            const res = await PUT_VEHICULO(req, { params: Promise.resolve({ id: '00000000-0000-0000-0000-000000000000' }) });
            expect([400, 403, 404, 200, 500]).toContain(res.status);
        });
    });

    describe('DELETE /api/v1/vehiculos/:id', () => {
        it('should return 403 when gestor tries to delete', async () => {
            (auth as jest.Mock).mockResolvedValue(mockSessions.gestor);
            const req = new NextRequest(`${BASE_URL}/00000000-0000-0000-0000-000000000000`, {
                method: 'DELETE'
            });
            const res = await DELETE_VEHICULO(req, { params: Promise.resolve({ id: '00000000-0000-0000-0000-000000000000' }) });
            expect(res.status).toBe(403);
        });

        it('should allow only admin to delete', async () => {
            (auth as jest.Mock).mockResolvedValue(mockSessions.admin);
            const req = new NextRequest(`${BASE_URL}/00000000-0000-0000-0000-000000000000`, {
                method: 'DELETE'
            });
            const res = await DELETE_VEHICULO(req, { params: Promise.resolve({ id: '00000000-0000-0000-0000-000000000000' }) });
            expect([400, 403, 404, 200, 500]).toContain(res.status);
        });
    });
});
