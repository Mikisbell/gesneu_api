import { auth } from '@/lib/auth/auth';

export async function getSession() {
    return await auth();
}

export async function getCurrentUser() {
    const session = await getSession();
    return session?.user;
}

export async function requireAuth() {
    const session = await getSession();
    if (!session) {
        throw new Error('No autenticado');
    }
    return session;
}

export function hasPermission(session: any, permission: string): boolean {
    if (!session?.user?.permissions) return false;
    return session.user.permissions.includes(permission);
}

export function hasRole(session: any, role: string): boolean {
    if (!session?.user?.roles) return false;
    return session.user.roles.includes(role);
}
