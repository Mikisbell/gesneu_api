'use client';

import { usePermissions, useHasPermission } from '@/hooks/usePermissions';
import { ReactNode } from 'react';

interface PermissionGateProps {
    /** Permiso requerido (ej: 'neumaticos:delete') */
    permission?: string;
    /** O usar el helper de can (ej: 'deleteNeumaticos') */
    can?: keyof ReturnType<typeof usePermissions>['can'];
    /** Contenido a mostrar si tiene permiso */
    children: ReactNode;
    /** Contenido alternativo si NO tiene permiso (opcional) */
    fallback?: ReactNode;
    /** Si true, oculta completamente. Si false, muestra deshabilitado */
    hideIfDenied?: boolean;
}

/**
 * Componente que oculta/muestra contenido según permisos del usuario
 * 
 * @example
 * // Usando permiso directo
 * <PermissionGate permission="neumaticos:delete">
 *   <Button>Eliminar</Button>
 * </PermissionGate>
 * 
 * @example
 * // Usando helper can
 * <PermissionGate can="deleteNeumaticos">
 *   <Button>Eliminar</Button>
 * </PermissionGate>
 * 
 * @example
 * // Con fallback
 * <PermissionGate can="manageUsers" fallback={<span>Sin acceso</span>}>
 *   <AdminPanel />
 * </PermissionGate>
 */
export function PermissionGate({
    permission,
    can: canKey,
    children,
    fallback = null,
    hideIfDenied = true
}: PermissionGateProps) {
    const { can, permissions, loading } = usePermissions();

    if (loading) {
        return null; // O un skeleton
    }

    let hasPermission = false;

    if (canKey && can) {
        hasPermission = can[canKey] || false;
    } else if (permission) {
        hasPermission = permissions.includes(permission);
    }

    if (hasPermission) {
        return <>{children}</>;
    }

    if (hideIfDenied) {
        return <>{fallback}</>;
    }

    // Si no hideIfDenied, mostrar children pero deshabilitados
    return (
        <div style={{ opacity: 0.5, pointerEvents: 'none' }} title="Sin permisos">
            {children}
        </div>
    );
}

/**
 * Componente para mostrar contenido SOLO a roles específicos
 * 
 * @example
 * <RoleGate roles={['ADMIN', 'GESTOR']}>
 *   <AdminSettings />
 * </RoleGate>
 */
export function RoleGate({
    roles,
    children,
    fallback = null
}: {
    roles: string[];
    children: ReactNode;
    fallback?: ReactNode;
}) {
    const { user, loading } = usePermissions();

    if (loading) return null;

    if (user && roles.includes(user.rol)) {
        return <>{children}</>;
    }

    return <>{fallback}</>;
}
