import { apiClient } from './client';
import { EstadoOperatividadEnum } from '@prisma/client';

export interface CertificadoVehiculo {
    id: string;
    placa: string;
    numero_economico: string | null;
    marca: string | null;
    modelo_vehiculo: string | null;
}

export interface CertificadoEmisor {
    id: string;
    nombre_completo: string;
    email: string;
}

export interface CertificadoListado {
    id: string;
    folio_numero: number;
    fecha_emision: string;
    estado_operatividad: EstadoOperatividadEnum;
    vehiculo: CertificadoVehiculo;
    emisor: CertificadoEmisor;
}

export interface PaginatedResponse<T> {
    data: T[];
    pagination: {
        total: number;
        page: number;
        limit: number;
        totalPages: number;
    };
}

export interface ListarCertificadosParams {
    page?: number;
    limit?: number;
    q?: string;
    estado?: EstadoOperatividadEnum;
    fecha_desde?: string;
    fecha_hasta?: string;
}

export const certificadosApi = {
    getAll: (params?: ListarCertificadosParams) => {
        // Remove undefined values
        const cleanParams = Object.fromEntries(
            Object.entries(params || {}).filter(([_, v]) => v !== undefined)
        ) as Record<string, string>;
        
        return apiClient<PaginatedResponse<CertificadoListado>>('/reportes/certificados', {
            params: cleanParams
        });
    },
};
