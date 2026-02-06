import { apiClient } from './client';
import { NeumaticoResponse, CreateNeumaticoDTO, UpdateNeumaticoDTO } from '@/types/domain/neumatico.types';

// Re-export for compatibility if needed, but prefer usage of NeumaticoResponse
export type { NeumaticoResponse };

export const neumaticosApi = {
    getAll: () => apiClient<NeumaticoResponse[]>('/neumaticos'),
    getById: (id: string) => apiClient<NeumaticoResponse>(`/neumaticos/${id}`),
    create: (data: CreateNeumaticoDTO) => apiClient<NeumaticoResponse>('/neumaticos', {
        method: 'POST',
        body: JSON.stringify(data),
    }),
    update: (id: string, data: UpdateNeumaticoDTO) => apiClient<NeumaticoResponse>(`/neumaticos/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
    }),
    delete: (id: string) => apiClient<void>(`/neumaticos/${id}`, {
        method: 'DELETE',
    }),
};
