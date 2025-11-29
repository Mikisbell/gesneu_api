import { Vehiculo } from '@prisma/client';

// Tipo base de Vehículo
export interface IVehiculo extends Vehiculo {
    tipo_vehiculo?: {
        nombre: string;
        cantidad_ejes?: number;
        cantidad_neumaticos?: number;
    };
    neumaticos_instalados?: {
        id: string;
        numero_serie: string;
        ubicacion_posicion?: {
            id: string;
            numero_posicion: number;
        } | null;
    }[];
}

// DTO para creación
export interface CreateVehiculoDTO {
    placa: string;
    tipo_vehiculo_id: string;
    marca: string;
    modelo: string;
    anio: number;
    tipo_medicion?: 'KILOMETRAJE' | 'HOROMETRO';
    contador_actual?: number;
    motor_serie?: string;
    chasis_serie?: string;
    activo?: boolean;
}

// DTO para actualización
export interface UpdateVehiculoDTO {
    tipo_vehiculo_id?: string;
    marca?: string;
    modelo?: string;
    anio?: number;
    tipo_medicion?: 'KILOMETRAJE' | 'HOROMETRO';
    contador_actual?: number;
    motor_serie?: string;
    chasis_serie?: string;
    activo?: boolean;
}

// Filtros de búsqueda
export interface VehiculoFilters {
    placa?: string;
    tipo_vehiculo_id?: string;
    marca?: string;
    activo?: boolean;
}
