import { apiClient } from './client';
import { FabricanteNeumatico } from '@prisma/client';

export interface CreateFabricanteDTO {
    nombre: string;
    codigoAbreviado?: string;
    paisOrigen?: string;
    sitioWeb?: string;
}

export interface UpdateFabricanteDTO extends Partial<CreateFabricanteDTO> {
    activo?: boolean;
}

export const fabricantesApi = {
    getAll: () => apiClient<FabricanteNeumatico[]>('/catalogos/fabricantes'),
    getById: (id: string) => apiClient<FabricanteNeumatico>(`/catalogos/fabricantes/${id}`),
    create: (data: CreateFabricanteDTO) => apiClient<FabricanteNeumatico>('/catalogos/fabricantes', {
        method: 'POST',
        body: JSON.stringify(data),
    }),
    update: (id: string, data: UpdateFabricanteDTO) => apiClient<FabricanteNeumatico>(`/catalogos/fabricantes/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
    }),
    delete: (id: string) => apiClient<void>(`/catalogos/fabricantes/${id}`, {
        method: 'DELETE',
    }),
};
