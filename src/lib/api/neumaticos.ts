import { apiClient } from './client';
import { Neumatico, ModeloNeumatico, Almacen, Vehiculo, PosicionNeumatico } from '@prisma/client';

export interface NeumaticoWithRelations extends Neumatico {
    modelo: ModeloNeumatico;
    ubicacion_almacen?: Almacen;
    ubicacion_vehiculo?: Vehiculo;
    ubicacion_posicion?: PosicionNeumatico;
}

export interface CreateNeumaticoDTO {
    numero_serie: string;
    modelo_id: string;
    dot: string;
    profundidad_inicial_mm: number;
    costo_compra?: number;
    fecha_compra?: string;
    ubicacion_almacen_id?: string;
}

export interface UpdateNeumaticoDTO extends Partial<CreateNeumaticoDTO> { }

export const neumaticosApi = {
    getAll: () => apiClient<NeumaticoWithRelations[]>('/neumaticos'),
    getById: (id: string) => apiClient<NeumaticoWithRelations>(`/neumaticos/${id}`),
    create: (data: CreateNeumaticoDTO) => apiClient<Neumatico>('/neumaticos', {
        method: 'POST',
        body: JSON.stringify(data),
    }),
    update: (id: string, data: UpdateNeumaticoDTO) => apiClient<Neumatico>(`/neumaticos/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
    }),
    delete: (id: string) => apiClient<void>(`/neumaticos/${id}`, {
        method: 'DELETE',
    }),
};
