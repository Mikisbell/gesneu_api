import { apiClient } from './client';
import { ModeloNeumatico } from '@prisma/client';

export const modelosNeumaticoApi = {
    getAll: () => apiClient<ModeloNeumatico[]>('/catalogos/modelos-neumatico'),
};
