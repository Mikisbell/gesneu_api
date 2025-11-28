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
        userId: 'admin-user-id',
        username: 'admin',
        email: 'admin@example.com',
        roles: ['ADMINISTRADOR'],
        permissions: ['*'] // All permissions
    }),

    gestor: createMockSession({
        userId: 'gestor-user-id',
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
        userId: 'operador-user-id',
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

    consultor: createMockSession({
        userId: 'consultor-user-id',
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
