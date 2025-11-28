import { apiClient } from './client';
import { Proveedor } from '@prisma/client';

export interface CreateProveedorDTO {
    nombre: string;
    ruc?: string;
    email?: string;
    telefono?: string;
    direccion?: string;
    contacto?: string;
    activo?: boolean;
}

export interface UpdateProveedorDTO extends Partial<CreateProveedorDTO> { }

export const proveedoresApi = {
    getAll: () => apiClient<Proveedor[]>('/catalogos/proveedores'),
    getById: (id: string) => apiClient<Proveedor>(`/catalogos/proveedores/${id}`),
    create: (data: CreateProveedorDTO) => apiClient<Proveedor>('/catalogos/proveedores', {
        method: 'POST',
        body: JSON.stringify(data),
    }),
    update: (id: string, data: UpdateProveedorDTO) => apiClient<Proveedor>(`/catalogos/proveedores/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
    }),
    delete: (id: string) => apiClient<void>(`/catalogos/proveedores/${id}`, {
        method: 'DELETE',
    }),
};
