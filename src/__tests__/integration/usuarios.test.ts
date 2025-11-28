import { NextRequest } from 'next/server';
import { prisma } from '@/lib/prisma';
import { cleanDatabase } from '../helpers/database-helpers';
import { mockSessions } from '../helpers/auth-helpers';
import { GET as getUsersGET, POST as createUser } from '@/app/api/v1/usuarios/route';
import { GET as getUserGET, PUT as updateUser, DELETE as deleteUser } from '@/app/api/v1/usuarios/[id]/route';

jest.mock('@/lib/auth/auth');

describe('Usuarios Integration Tests', () => {
    let adminRoleId: string;
    let gestorRoleId: string;

    beforeAll(async () => {
        await cleanDatabase();

        // Create roles for testing
        const adminRole = await prisma.rol.create({
            data: { nombre: 'ADMIN', descripcion: 'Administrador' },
        });
        adminRoleId = adminRole.id;

        const gestorRole = await prisma.rol.create({
            data: { nombre: 'GESTOR', descripcion: 'Gestor' },
        });
        gestorRoleId = gestorRole.id;
    });

    afterAll(async () => {
        await prisma.rol.deleteMany({});
        await prisma.usuarioRol.deleteMany({});
        await prisma.usuario.deleteMany({});
    });

    describe('POST /api/v1/usuarios', () => {
        it('debe crear un usuario con roles asignados', async () => {
            const payload = {
                username: 'testuser',
                nombre_completo: 'Test User',
                email: 'test@example.com',
                password: 'password123',
                roles: [adminRoleId],
            };

            const req = new NextRequest('http://localhost:3000/api/v1/usuarios', {
                method: 'POST',
                body: JSON.stringify(payload),
            });

            (req as any).headers = new Map([['authorization', 'Bearer mock-token']]);
            const mockGetServerSession = require('@/lib/auth/auth').getServerSession;
            mockGetServerSession.mockResolvedValueOnce(mockSessions.admin);

            const response = await createUser(req);
            const data = await response.json();

            expect(response.status).toBe(201);
            expect(data.data.username).toBe('testuser');
            expect(data.data.roles).toHaveLength(1);
            expect(data.data.password_hash).toBeUndefined();
        });

        it('debe rechazar usuarios duplicados', async () => {
            const payload = {
                username: 'testuser',
                nombre_completo: 'Duplicate User',
                email: 'test@example.com',
                password: 'password123',
                roles: [adminRoleId],
            };

            const req = new NextRequest('http://localhost:3000/api/v1/usuarios', {
                method: 'POST',
                body: JSON.stringify(payload),
            });

            (req as any).headers = new Map([['authorization', 'Bearer mock-token']]);
            const mockGetServerSession = require('@/lib/auth/auth').getServerSession;
            mockGetServerSession.mockResolvedValueOnce(mockSessions.admin);

            const response = await createUser(req);
            expect(response.status).toBe(409);
        });
    });

    describe('GET /api/v1/usuarios', () => {
        it('debe listar usuarios activos', async () => {
            const req = new NextRequest('http://localhost:3000/api/v1/usuarios?page=1&limit=10');

            (req as any).headers = new Map([['authorization', 'Bearer mock-token']]);
            const mockGetServerSession = require('@/lib/auth/auth').getServerSession;
            mockGetServerSession.mockResolvedValueOnce(mockSessions.admin);

            const response = await getUsersGET(req);
            const data = await response.json();

            expect(response.status).toBe(200);
            expect(Array.isArray(data.data)).toBe(true);
            expect(data.meta).toBeDefined();
        });
    });

    describe('PUT /api/v1/usuarios/{id}', () => {
        it('debe actualizar un usuario', async () => {
            const usuario = await prisma.usuario.findFirst({ where: { username: 'testuser' } });

            const payload = {
                nombre_completo: 'Updated Name',
            };

            const req = new NextRequest(`http://localhost:3000/api/v1/usuarios/${usuario!.id}`, {
                method: 'PUT',
                body: JSON.stringify(payload),
            });

            (req as any).headers = new Map([['authorization', 'Bearer mock-token']]);
            const mockGetServerSession = require('@/lib/auth/auth').getServerSession;
            mockGetServerSession.mockResolvedValueOnce(mockSessions.admin);

            const response = await updateUser(req, { params: { id: usuario!.id } });
            const data = await response.json();

            expect(response.status).toBe(200);
            expect(data.data.nombre_completo).toBe('Updated Name');
        });
    });

    describe('DELETE /api/v1/usuarios/{id}', () => {
        it('debe desactivar un usuario (soft delete)', async () => {
            const usuario = await prisma.usuario.findFirst({ where: { username: 'testuser' } });

            const req = new NextRequest(`http://localhost:3000/api/v1/usuarios/${usuario!.id}`, {
                method: 'DELETE',
            });

            (req as any).headers = new Map([['authorization', 'Bearer mock-token']]);
            const mockGetServerSession = require('@/lib/auth/auth').getServerSession;
            mockGetServerSession.mockResolvedValueOnce(mockSessions.admin);

            const response = await deleteUser(req, { params: { id: usuario!.id } });

            expect(response.status).toBe(200);

            const deletedUser = await prisma.usuario.findUnique({ where: { id: usuario!.id } });
            expect(deletedUser?.activo).toBe(false);
        });
    });
});
