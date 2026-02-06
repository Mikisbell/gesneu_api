import { apiClient } from './client';
import { FabricanteNeumatico } from '@prisma/client';

export const fabricantesApi = {
    getAll: () => apiClient<FabricanteNeumatico[]>('/catalogos/fabricantes'),
};
