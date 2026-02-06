
import { Neumatico, EstadoNeumaticoEnum, ModeloNeumatico, FabricanteNeumatico, Almacen, Vehiculo, PosicionNeumatico, Empresa } from '@prisma/client';

export type NeumaticoEntity = Neumatico & {
    modelo?: ModeloNeumatico & { fabricante: FabricanteNeumatico };
    ubicacion_almacen?: Almacen | null;
    ubicacion_vehiculo?: Vehiculo & { tipo_vehiculo: any } | null; // Repository includes tipo_vehiculo
    ubicacion_posicion?: PosicionNeumatico | null;
    empresa?: Empresa;
};

export interface CreateNeumaticoDTO {
    // Core Identity
    modelo_id: string;
    numero_serie?: string;
    dot?: string;
    sensor_id?: string;
    es_reencauchado?: boolean;

    // Purchase / Origin
    fecha_compra: string; // ISO Date
    fecha_fabricacion?: string; // ISO Date
    costo_compra?: number;
    moneda_compra?: string;
    proveedor_compra_id?: string;

    // Initial Condition
    profundidad_inicial_mm?: number;
    profundidad_actual_mm: number;
    profundidad_int?: number;
    profundidad_cen?: number;
    profundidad_ext?: number;
    presion_actual_psi?: number;

    // Location (Initial)
    ubicacion_almacen_id?: string;
}

export interface UpdateNeumaticoDTO {
    numero_serie?: string;
    dot?: string;
    sensor_id?: string;
    activo?: boolean;
}

export interface NeumaticoResponse {
    id: string;
    numeroSerie: string | null;
    codigo: string;
    deviceId: string | null;
    dot: string | null;
    estado: EstadoNeumaticoEnum;
    condicion: {
        esReencauchado: boolean;
        reencauchesRealizados: number;
        vidaActual: number;
    };
    modelo: {
        id: string;
        nombre: string;
        medida: string;
        fabricante: {
            id: string;
            nombre: string;
        };
    };
    mediciones: {
        profundidadActual: number;
        profundidadInicial: number | null;
        presion: number | null;
    };
    ubicacion: {
        tipo: 'ALMACEN' | 'VEHICULO' | 'DESECHO' | 'DESCONOCIDO';
        almacen?: { id: string; nombre: string };
        vehiculo?: { id: string; placa: string };
        posicion?: { id: string; codigo: string };
    };
    compra: {
        fecha: string;
        costo: number | null;
        moneda: string | null;
        proveedorId: string | null;
    };
    estadisticas: {
        kmAcumulados: number;
        horasAcumuladas: number;
        costoPorKm: number | null;
        proximaInspeccionKm: number | null;
        proximaInspeccionFecha: string | null;
    };
    createdAt: string;
    updatedAt: string | null;
}

export interface NeumaticoFilters {
    search?: string;
    numero_serie?: string;
    modelo_id?: string;
    estado_actual?: EstadoNeumaticoEnum;
    ubicacion_almacen_id?: string;
    ubicacion_vehiculo_id?: string;
    dot?: string;
    empresa_id?: string;
}

// Alias for backwards compatibility
export type INeumatico = NeumaticoResponse;
