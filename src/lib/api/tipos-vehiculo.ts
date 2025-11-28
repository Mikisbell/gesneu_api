import { apiClient } from './client';
import { TipoVehiculo } from '@prisma/client';

export const tiposVehiculoApi = {
    getAll: () => apiClient<TipoVehiculo[]>('/catalogos/tipos-vehiculo'),
};
