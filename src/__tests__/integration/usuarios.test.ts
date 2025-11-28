import { NextRequest } from 'next/server';
import { auth } from '@/lib/auth/auth';
import { GET as getUsersGET, POST as createUser } from '@/app/api/v1/usuarios/route';
import { GET as getUserGET, PUT as updateUser, DELETE as deleteUser } from '@/app/api/v1/usuarios/[id]/route';
import { mockSessions } from '../helpers/auth-helpers';

// Mock auth
jest.mock('@/lib/auth/auth', () => ({
    auth: jest.fn(),
}));

describe('Usuarios API Integration Tests', () => {
    const BASE_URL = 'http://localhost:3000/api/v1/usuarios';

    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe('GET /api/v1/usuarios', () => {
        it('should return 401 when not authenticated', async () => {
            (auth as jest.Mock).mockResolvedValue(null);

            const req = new NextRequest(BASE_URL);
            const response = await getUsersGET(req);

            expect(response.status).toBe(401);
        });

        it('should return 403 when consultor tries to access (no permission)', async () => {
            (auth as jest.Mock).mockResolvedValue(mockSessions.consultor);

            const req = new NextRequest(BASE_URL);
            const response = await getUsersGET(req);

            expect(response.status).toBe(403);
        });
    });

    describe('POST /api/v1/usuarios', () => {
        it('should return 401 when not authenticated', async () => {
            (auth as jest.Mock).mockResolvedValue(null);

            const payload = {
                username: 'testuser',
                nombre_completo: 'Test User',
                email: 'test@example.com',
                password: 'password123',
                roles: ['some-uuid'],
            };

            const req = new NextRequest(BASE_URL, {
                method: 'POST',
                body: JSON.stringify(payload),
            });

            const response = await createUser(req);
            expect(response.status).toBe(401);
        });

        it('should return 403 when gestor tries to create (no permission)', async () => {
            (auth as jest.Mock).mockResolvedValue(mockSessions.gestor);

            const payload = {
                username: 'testuser',
                nombre_completo: 'Test User',
                email: 'test@example.com',
                password: 'password123',
                roles: ['some-uuid'],
            };

            const req = new NextRequest(BASE_URL, {
                method: 'POST',
                body: JSON.stringify(payload),
            });

            const response = await createUser(req);
            expect(response.status).toBe(403);
        });
    });

    describe('PUT /api/v1/usuarios/:id', () => {
        it('should return 401 when not authenticated', async () => {
            (auth as jest.Mock).mockResolvedValue(null);

            const req = new NextRequest(`${BASE_URL}/some-uuid`, {
                method: 'PUT',
                body: JSON.stringify({ nombre_completo: 'Updated' }),
            });

            const response = await updateUser(req, { params: Promise.resolve({ id: 'some-uuid' }) });
            expect(response.status).toBe(401);
        });
    });

    describe('DELETE /api/v1/usuarios/:id', () => {
        it('should return 401 when not authenticated', async () => {
            (auth as jest.Mock).mockResolvedValue(null);

            const req = new NextRequest(`${BASE_URL}/some-uuid`, {
                method: 'DELETE',
            });

            const response = await deleteUser(req, { params: Promise.resolve({ id: 'some-uuid' }) });
            expect(response.status).toBe(401);
        });

        it('should return 403 when gestor tries to delete (no permission)', async () => {
            (auth as jest.Mock).mockResolvedValue(mockSessions.gestor);

            const req = new NextRequest(`${BASE_URL}/some-uuid`, {
                method: 'DELETE',
            });

            const response = await deleteUser(req, { params: Promise.resolve({ id: 'some-uuid' }) });
            expect(response.status).toBe(403);
        });
    });
});
