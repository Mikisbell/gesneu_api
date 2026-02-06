import { apiClient } from './client';
import { Almacen } from '@prisma/client';

export interface CreateAlmacenDTO {
    codigo: string;
    nombre: string;
    tipo: string;
    direccion?: string;
    activo?: boolean;
}

export interface UpdateAlmacenDTO extends Partial<CreateAlmacenDTO> { }

export const almacenesApi = {
    getAll: () => apiClient<Almacen[]>('/catalogos/almacenes'),
    getById: (id: string) => apiClient<Almacen>(`/catalogos/almacenes/${id}`),
    create: (data: CreateAlmacenDTO) => apiClient<Almacen>('/catalogos/almacenes', {
        method: 'POST',
        body: JSON.stringify(data),
    }),
    update: (id: string, data: UpdateAlmacenDTO) => apiClient<Almacen>(`/catalogos/almacenes/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
    }),
    delete: (id: string) => apiClient<void>(`/catalogos/almacenes/${id}`, {
        method: 'DELETE',
    }),
};
