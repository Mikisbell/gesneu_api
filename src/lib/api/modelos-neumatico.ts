import { apiClient } from './client';
import { ModeloNeumatico } from '@prisma/client';

export const modelosNeumaticoApi = {
    getAll: () => apiClient<ModeloNeumatico[]>('/catalogos/modelos-neumatico'),

    create: (data: Partial<ModeloNeumatico>) =>
        apiClient<ModeloNeumatico>('/catalogos/modelos-neumatico', {
            method: 'POST',
            body: JSON.stringify(data)
        }),

    update: (id: string, data: Partial<ModeloNeumatico>) =>
        apiClient<ModeloNeumatico>(`/catalogos/modelos-neumatico/${id}`, {
            method: 'PATCH',
            body: JSON.stringify(data)
        }),

    delete: (id: string) =>
        apiClient<void>(`/catalogos/modelos-neumatico/${id}`, {
            method: 'DELETE'
        })
};
