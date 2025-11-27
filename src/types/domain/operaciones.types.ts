// Type definitions for tire operations


export interface MontajeNeumaticoDTO {
    neumatico_id: string;
    vehiculo_id: string;
    posicion_id: string; // ID de PosicionNeumatico (template)
    kilometraje_vehiculo: number;
    fecha_evento?: Date;
    presion_psi?: number;
    observaciones?: string;
}

export interface DesmontajeNeumaticoDTO {
    neumatico_id: string;
    motivo_id?: string; // Para desecho o reparación
    kilometraje_vehiculo: number;
    fecha_evento?: Date;
    profundidad_remanente_mm?: number;
    presion_psi?: number;
    observaciones?: string;
    destino: 'STOCK' | 'REPARACION' | 'DESECHO' | 'REENCAUCHE';
    almacen_destino_id?: string; // Si va a stock/reparación
}

export interface RotacionNeumaticoDTO {
    vehiculo_id: string;
    kilometraje_vehiculo: number;
    movimientos: {
        neumatico_id: string;
        posicion_destino_id: string;
    }[];
    observaciones?: string;
}
