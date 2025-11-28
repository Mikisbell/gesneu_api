/**
 * Unit tests for authorization helper functions
 * Note: These tests focus on the pure functions that don't require auth context
 */
import {
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    requirePermission,
    requireAnyPermission,
    requireAllPermissions,
    hasRole,
    isAdmin,
    type ExtendedSession
} from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';

// Mock the auth import to avoid next-auth dependency
jest.mock('@/lib/auth/auth', () => ({
    auth: jest.fn()
}));

// Mock session data
const createMockSession = (permissions: string[], roles: string[] = ['OPERADOR']): ExtendedSession => ({
    user: {
        id: 'test-user-id',
        name: 'Test User',
        email: 'test@example.com',
        username: 'testuser',
        roles,
        permissions
    }
});

describe('Authorization Helper Functions', () => {
    describe('hasPermission', () => {
        it('should return true when user has the permission', () => {
            const session = createMockSession([PERMISSIONS.NEUMATICOS_READ, PERMISSIONS.NEUMATICOS_CREATE]);

            expect(hasPermission(session, PERMISSIONS.NEUMATICOS_READ)).toBe(true);
        });

        it('should return false when user does not have the permission', () => {
            const session = createMockSession([PERMISSIONS.NEUMATICOS_READ]);

            expect(hasPermission(session, PERMISSIONS.NEUMATICOS_DELETE)).toBe(false);
        });

        it('should return false for empty permissions array', () => {
            const session = createMockSession([]);

            expect(hasPermission(session, PERMISSIONS.NEUMATICOS_READ)).toBe(false);
        });
    });

    describe('hasAnyPermission', () => {
        it('should return true when user has at least one permission', () => {
            const session = createMockSession([PERMISSIONS.NEUMATICOS_READ]);

            expect(hasAnyPermission(session, [
                PERMISSIONS.NEUMATICOS_READ,
                PERMISSIONS.NEUMATICOS_CREATE
            ])).toBe(true);
        });

        it('should return false when user has none of the permissions', () => {
            const session = createMockSession([PERMISSIONS.VEHICULOS_READ]);

            expect(hasAnyPermission(session, [
                PERMISSIONS.NEUMATICOS_READ,
                PERMISSIONS.NEUMATICOS_CREATE
            ])).toBe(false);
        });

        it('should return true when user has all permissions', () => {
            const session = createMockSession([
                PERMISSIONS.NEUMATICOS_READ,
                PERMISSIONS.NEUMATICOS_CREATE
            ]);

            expect(hasAnyPermission(session, [
                PERMISSIONS.NEUMATICOS_READ,
                PERMISSIONS.NEUMATICOS_CREATE
            ])).toBe(true);
        });
    });

    describe('hasAllPermissions', () => {
        it('should return true when user has all permissions', () => {
            const session = createMockSession([
                PERMISSIONS.NEUMATICOS_READ,
                PERMISSIONS.NEUMATICOS_CREATE,
                PERMISSIONS.NEUMATICOS_UPDATE
            ]);

            expect(hasAllPermissions(session, [
                PERMISSIONS.NEUMATICOS_READ,
                PERMISSIONS.NEUMATICOS_CREATE
            ])).toBe(true);
        });

        it('should return false when user is missing one permission', () => {
            const session = createMockSession([PERMISSIONS.NEUMATICOS_READ]);

            expect(hasAllPermissions(session, [
                PERMISSIONS.NEUMATICOS_READ,
                PERMISSIONS.NEUMATICOS_CREATE
            ])).toBe(false);
        });

        it('should return false when user has none of the permissions', () => {
            const session = createMockSession([PERMISSIONS.VEHICULOS_READ]);

            expect(hasAllPermissions(session, [
                PERMISSIONS.NEUMATICOS_READ,
                PERMISSIONS.NEUMATICOS_CREATE
            ])).toBe(false);
        });
    });

    describe('requirePermission', () => {
        it('should not throw when user has the permission', () => {
            const session = createMockSession([PERMISSIONS.NEUMATICOS_READ]);

            expect(() => {
                requirePermission(session, PERMISSIONS.NEUMATICOS_READ);
            }).not.toThrow();
        });

        it('should throw FORBIDDEN when user does not have the permission', () => {
            const session = createMockSession([PERMISSIONS.NEUMATICOS_READ]);

            expect(() => {
                requirePermission(session, PERMISSIONS.NEUMATICOS_DELETE);
            }).toThrow('FORBIDDEN');
        });
    });

    describe('requireAnyPermission', () => {
        it('should not throw when user has at least one permission', () => {
            const session = createMockSession([PERMISSIONS.NEUMATICOS_READ]);

            expect(() => {
                requireAnyPermission(session, [
                    PERMISSIONS.NEUMATICOS_READ,
                    PERMISSIONS.NEUMATICOS_CREATE
                ]);
            }).not.toThrow();
        });

        it('should throw FORBIDDEN when user has none of the permissions', () => {
            const session = createMockSession([PERMISSIONS.VEHICULOS_READ]);

            expect(() => {
                requireAnyPermission(session, [
                    PERMISSIONS.NEUMATICOS_READ,
                    PERMISSIONS.NEUMATICOS_CREATE
                ]);
            }).toThrow('FORBIDDEN');
        });
    });

    describe('requireAllPermissions', () => {
        it('should not throw when user has all permissions', () => {
            const session = createMockSession([
                PERMISSIONS.NEUMATICOS_READ,
                PERMISSIONS.NEUMATICOS_CREATE
            ]);

            expect(() => {
                requireAllPermissions(session, [
                    PERMISSIONS.NEUMATICOS_READ,
                    PERMISSIONS.NEUMATICOS_CREATE
                ]);
            }).not.toThrow();
        });

        it('should throw FORBIDDEN when user is missing one permission', () => {
            const session = createMockSession([PERMISSIONS.NEUMATICOS_READ]);

            expect(() => {
                requireAllPermissions(session, [
                    PERMISSIONS.NEUMATICOS_READ,
                    PERMISSIONS.NEUMATICOS_CREATE
                ]);
            }).toThrow('FORBIDDEN');
        });
    });

    describe('hasRole', () => {
        it('should return true when user has the role', () => {
            const session = createMockSession([], ['ADMIN', 'GESTOR']);

            expect(hasRole(session, 'ADMIN')).toBe(true);
            expect(hasRole(session, 'GESTOR')).toBe(true);
        });

        it('should return false when user does not have the role', () => {
            const session = createMockSession([], ['OPERADOR']);

            expect(hasRole(session, 'ADMIN')).toBe(false);
        });
    });

    describe('isAdmin', () => {
        it('should return true when user has ADMINISTRADOR role', () => {
            const session = createMockSession([], ['ADMINISTRADOR']);

            expect(isAdmin(session)).toBe(true);
        });

        it('should return false when user does not have ADMINISTRADOR role', () => {
            const session = createMockSession([], ['OPERADOR', 'GESTOR']);

            expect(isAdmin(session)).toBe(false);
        });
    });
});
