import { auth } from './auth';
import { Permission } from './permissions';

/**
 * Extended session with roles and permissions
 */
export interface ExtendedSession {
    user: {
        id: string;
        name?: string | null;
        email?: string | null;
        username: string;
        roles: string[];
        permissions: string[];
        empresa_id?: string;  // Multi-tenancy - empresa del usuario
    };
}

/**
 * Get the current user session with authentication check
 * @returns Extended session or null if not authenticated
 */
export async function getCurrentUser(): Promise<ExtendedSession | null> {
    const session = await auth();

    if (!session || !session.user) {
        return null;
    }

    return session as unknown as ExtendedSession;
}

/**
 * Require authentication - throws error if not authenticated
 * @returns Extended session
 * @throws Error if not authenticated
 */
export async function requireAuth(): Promise<ExtendedSession> {
    const session = await getCurrentUser();

    if (!session) {
        throw new Error('UNAUTHORIZED');
    }

    return session;
}

/**
 * Check if user has a specific permission
 * @param session - User session
 * @param permission - Permission to check
 * @returns true if user has permission
 */
export function hasPermission(session: ExtendedSession, permission: Permission): boolean {
    return session.user.permissions.includes('*') || session.user.permissions.includes(permission);
}

/**
 * Check if user has any of the specified permissions
 * @param session - User session
 * @param permissions - Array of permissions to check
 * @returns true if user has at least one permission
 */
export function hasAnyPermission(session: ExtendedSession, permissions: Permission[]): boolean {
    return permissions.some(permission => session.user.permissions.includes(permission));
}

/**
 * Check if user has all specified permissions
 * @param session - User session
 * @param permissions - Array of permissions to check
 * @returns true if user has all permissions
 */
export function hasAllPermissions(session: ExtendedSession, permissions: Permission[]): boolean {
    return permissions.every(permission => session.user.permissions.includes(permission));
}

/**
 * Require specific permission - throws error if user doesn't have it
 * @param session - User session
 * @param permission - Required permission
 * @throws Error if user doesn't have permission
 */
export function requirePermission(session: ExtendedSession, permission: Permission): void {
    if (!hasPermission(session, permission)) {
        throw new Error('FORBIDDEN');
    }
}

/**
 * Require any of the specified permissions - throws error if user has none
 * @param session - User session
 * @param permissions - Array of permissions
 * @throws Error if user doesn't have any permission
 */
export function requireAnyPermission(session: ExtendedSession, permissions: Permission[]): void {
    if (!hasAnyPermission(session, permissions)) {
        throw new Error('FORBIDDEN');
    }
}

/**
 * Require all specified permissions - throws error if user is missing any
 * @param session - User session
 * @param permissions - Array of permissions
 * @throws Error if user doesn't have all permissions
 */
export function requireAllPermissions(session: ExtendedSession, permissions: Permission[]): void {
    if (!hasAllPermissions(session, permissions)) {
        throw new Error('FORBIDDEN');
    }
}

/**
 * Check if user has a specific role
 * @param session - User session
 * @param role - Role to check
 * @returns true if user has role
 */
export function hasRole(session: ExtendedSession, role: string): boolean {
    return session.user.roles.includes(role);
}

/**
 * Check if user is admin
 * @param session - User session
 * @returns true if user is admin
 */
export function isAdmin(session: ExtendedSession): boolean {
    return hasRole(session, 'ADMINISTRADOR');
}
