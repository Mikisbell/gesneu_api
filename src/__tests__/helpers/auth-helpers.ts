/**
 * Authentication test helpers
 * Provides utilities for mocking NextAuth sessions in integration tests
 */
import { Session } from 'next-auth';

export interface MockSessionOptions {
    userId?: string;
    username?: string;
    email?: string;
    roles?: string[];
    permissions?: string[];
}

/**
 * Create a mock session for testing
 */
export function createMockSession(options: MockSessionOptions = {}): Session {
    const {
        userId = 'test-user-id',
        username = 'testuser',
        email = 'test@example.com',
        roles = ['OPERADOR'],
        permissions = []
    } = options;

    return {
        user: {
            id: userId,
            name: username,
            email,
            username,
            roles,
            permissions
        },
        expires: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString() // 30 days
    } as any;
}

/**
 * Create mock sessions for different roles
 */
export const mockSessions = {
    admin: createMockSession({
        userId: '00000000-0000-0000-0000-000000000001',
        username: 'admin',
        email: 'admin@example.com',
        roles: ['ADMIN'],
        permissions: ['*'] // All permissions
    }),

    gestor: createMockSession({
        userId: '00000000-0000-0000-0000-000000000002',
        username: 'gestor',
        email: 'gestor@example.com',
        roles: ['GESTOR'],
        permissions: [
            'neumaticos:read',
            'neumaticos:create',
            'neumaticos:update',
            'vehiculos:read',
            'vehiculos:create',
            'vehiculos:update',
            'neumaticos:evento:instalacion',
            'neumaticos:evento:desmontaje',
            'neumaticos:evento:rotacion',
            // Catalogos
            'catalogos:proveedores:read',
            'catalogos:proveedores:create',
            'catalogos:proveedores:update',
            'catalogos:almacenes:read',
            'catalogos:almacenes:create',
            'catalogos:almacenes:update',
            'catalogos:fabricantes:read',
            'catalogos:fabricantes:create',
            'catalogos:fabricantes:update'
        ]
    }),

    operador: createMockSession({
        userId: '00000000-0000-0000-0000-000000000003',
        username: 'operador',
        email: 'operador@example.com',
        roles: ['OPERADOR'],
        permissions: [
            'neumaticos:read',
            'vehiculos:read',
            'neumaticos:evento:instalacion',
            'neumaticos:evento:desmontaje',
            'neumaticos:evento:rotacion',
            // Catalogos Read
            'catalogos:proveedores:read',
            'catalogos:almacenes:read',
            'catalogos:fabricantes:read'
        ]
    }),

    // @deprecated — El rol CONSULTOR fue eliminado del sistema productivo (enum Prisma, SYSTEM_ROLES, validators).
    // Este mock se preserva únicamente para tests legacy que validan el comportamiento "usuario sin permisos → 403".
    // En tests nuevos, usar mockSessions.operador o crear un mock específico read-only.
    consultor: createMockSession({
        userId: '00000000-0000-0000-0000-000000000004',
        username: 'consultor',
        email: 'consultor@example.com',
        roles: ['CONSULTOR'],
        permissions: [
            'neumaticos:read',
            'vehiculos:read',
            'catalogos:almacenes:read',
            'catalogos:proveedores:read',
            'catalogos:fabricantes:read'
        ]
    })
};

/**
 * Mock the auth function for testing
 * Usage in tests:
 * 
 * jest.mock('@/lib/auth/auth', () => ({
 *   auth: jest.fn()
 * }));
 * 
 * const { auth } = require('@/lib/auth/auth');
 * auth.mockResolvedValue(mockSessions.admin);
 */
export function mockAuth(session: Session | null) {
    const { auth } = require('@/lib/auth/auth');
    if (auth && typeof auth.mockResolvedValue === 'function') {
        auth.mockResolvedValue(session);
    }
    return auth;
}
import { prisma } from '@/lib/prisma'; // Ensure this import exists or add it

// ... existing code ...

/**
 * DB Helpers
 */
export async function clearDatabase() {
    await prisma.eventoNeumatico.deleteMany();
    await prisma.neumatico.deleteMany();
    await prisma.modeloNeumatico.deleteMany();
    await prisma.fabricanteNeumatico.deleteMany();
    await prisma.usuario.deleteMany();
}

export async function createTestUser(overrides = {}) {
    return await prisma.usuario.create({
        data: {
            username: 'testuser_' + Date.now(),
            email: 'test_' + Date.now() + '@example.com',
            password_hash: 'hashed_password',
            nombre_completo: 'Test User',
            rol: 'ADMIN',
            ...overrides
        }
    });
}

export async function createTestNeumatico(overrides: any = {}) {
    const fabricante = await prisma.fabricanteNeumatico.create({
        data: { nombre: 'Michelin ' + Date.now() }
    });

    const modelo = await prisma.modeloNeumatico.create({
        data: {
            nombre_modelo: 'X Multi Z ' + Date.now(),
            medida: '295/80R22.5',
            profundidad_original_mm: 18.5,
            fabricante_id: fabricante.id,
            reencauches_maximos: 2
        }
    });

    return await prisma.neumatico.create({
        data: {
            numero_serie: 'NEU-' + Date.now(),
            modelo_id: modelo.id,
            profundidad_remanente_actual_mm: 18.5,
            estado_actual: 'EN_STOCK',
            fecha_compra: new Date(),
            empresa_id: '00000000-0000-0000-0000-000000000000',
            kilometraje_acumulado: 0,
            ...overrides
        }
    });
}
