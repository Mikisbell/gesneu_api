'use client';

import { createContext, useContext, useEffect, useState } from 'react';

interface UserPermissions {
    user: {
        id: string;
        username: string;
        email: string;
        rol: string;
        nombre_completo?: string;
    } | null;
    permissions: string[];
    can: {
        createProveedores: boolean;
        deleteProveedores: boolean;
        createVehiculos: boolean;
        deleteVehiculos: boolean;
        configVehiculos: boolean;
        createNeumaticos: boolean;
        deleteNeumaticos: boolean;
        montaje: boolean;
        desmontaje: boolean;
        desecho: boolean;
        manageUsers: boolean;
        viewAudit: boolean;
        viewDashboard: boolean;
        viewReportes: boolean;
    };
    loading: boolean;
    error: string | null;
}

const defaultPermissions: UserPermissions = {
    user: null,
    permissions: [],
    can: {
        createProveedores: false,
        deleteProveedores: false,
        createVehiculos: false,
        deleteVehiculos: false,
        configVehiculos: false,
        createNeumaticos: false,
        deleteNeumaticos: false,
        montaje: false,
        desmontaje: false,
        desecho: false,
        manageUsers: false,
        viewAudit: false,
        viewDashboard: false,
        viewReportes: false
    },
    loading: true,
    error: null
};

const PermissionsContext = createContext<UserPermissions>(defaultPermissions);

export function PermissionsProvider({ children }: { children: React.ReactNode }) {
    const [state, setState] = useState<UserPermissions>(defaultPermissions);

    useEffect(() => {
        fetchPermissions();
    }, []);

    async function fetchPermissions() {
        try {
            const res = await fetch('/api/v1/auth/me');
            if (res.ok) {
                const data = await res.json();
                setState({
                    user: data.data.user,
                    permissions: data.data.permissions,
                    can: data.data.can,
                    loading: false,
                    error: null
                });
            } else {
                setState(prev => ({ ...prev, loading: false, error: 'No autenticado' }));
            }
        } catch (e) {
            setState(prev => ({ ...prev, loading: false, error: 'Error de conexión' }));
        }
    }

    return (
        <PermissionsContext.Provider value={state}>
            {children}
        </PermissionsContext.Provider>
    );
}

/**
 * Hook para acceder a los permisos del usuario actual
 * @example
 * const { can, user } = usePermissions();
 * if (can.deleteNeumaticos) { ... }
 */
export function usePermissions() {
    return useContext(PermissionsContext);
}

/**
 * Hook para verificar un permiso específico
 * @example
 * const canDelete = useHasPermission('neumaticos:delete');
 */
export function useHasPermission(permission: string): boolean {
    const { permissions } = useContext(PermissionsContext);
    return permissions.includes(permission);
}
