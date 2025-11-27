import { Neumatico, Almacen, Vehiculo, PosicionNeumatico } from '@prisma/client';

// Tipo base de Neumático (refleja el modelo de BD pero puede extenderse)
export interface INeumatico extends Neumatico {
    // Propiedades calculadas o relaciones opcionales pueden ir aquí
    modelo?: {
        nombre: string;
        medida: string;
        fabricante?: {
            nombre: string;
        };
    };
    ubicacion_almacen?: Almacen | null;
    ubicacion_vehiculo?: Vehiculo | null;
    ubicacion_posicion?: PosicionNeumatico | null;
}

// DTO para creación
export interface CreateNeumaticoDTO {
    numero_serie: string;
    modelo_id: string;
    dot: string;
    estado_actual?: string;
    profundidad_inicial_mm: number;
    profundidad_actual_mm?: number;
    presion_actual_psi?: number;
    ubicacion_almacen_id?: string;
    costo_compra?: number;
    fecha_compra?: Date;
}

// DTO para actualización
export interface UpdateNeumaticoDTO {
    estado_actual?: string;
    profundidad_actual_mm?: number;
    presion_actual_psi?: number;
    kilometraje_acumulado?: number;
    vida_actual?: number;
    reencauches_realizados?: number;
    es_reencauchado?: boolean;
    ubicacion_almacen_id?: string | null;
    ubicacion_vehiculo_id?: string | null;
    ubicacion_posicion_id?: string | null;
    activo?: boolean;
}

// Filtros de búsqueda
export interface NeumaticoFilters {
    numero_serie?: string;
    modelo_id?: string;
    estado_actual?: string;
    ubicacion_almacen_id?: string;
    ubicacion_vehiculo_id?: string;
    dot?: string;
    activo?: boolean;
}
