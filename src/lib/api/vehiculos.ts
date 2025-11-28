import { apiClient } from './client';
import { Vehiculo, TipoVehiculo } from '@prisma/client';

export interface VehiculoWithRelations extends Vehiculo {
    tipo_vehiculo: TipoVehiculo;
}

export interface CreateVehiculoDTO {
    placa: string;
    tipo_vehiculo_id: string;
    marca?: string;
    modelo?: string;
    anio?: number;
    kilometraje_actual?: number;
    activo?: boolean;
}

export interface UpdateVehiculoDTO extends Partial<CreateVehiculoDTO> { }

export const vehiculosApi = {
    getAll: () => apiClient<VehiculoWithRelations[]>('/vehiculos'),
    getById: (id: string) => apiClient<VehiculoWithRelations>(`/vehiculos/${id}`),
    create: (data: CreateVehiculoDTO) => apiClient<Vehiculo>('/vehiculos', {
        method: 'POST',
        body: JSON.stringify(data),
    }),
    update: (id: string, data: UpdateVehiculoDTO) => apiClient<Vehiculo>(`/vehiculos/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
    }),
    delete: (id: string) => apiClient<void>(`/vehiculos/${id}`, {
        method: 'DELETE',
    }),
};
