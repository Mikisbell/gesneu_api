// Event Constants
export const InspeccionEvents = {
    PRESSURE_READ: 'INSPECCION.PRESSURE_READ',
    DEPTH_READ: 'INSPECCION.DEPTH_READ'
} as const;

// Payload Types
export interface PressureReadPayload {
    lecturaId: string;
    neumaticoId: string;
    empresaId: string;
    presionPsi: number;
    fuente: 'MANUAL' | 'SENSOR_TPMS';
    usuarioId?: string;
}

export interface DepthReadPayload {
    medicionId: string;
    neumaticoId: string;
    empresaId: string;
    profundidadPromedio: number;
    profunidades: {
        int: number;
        cen: number;
        ext: number;
    };
    kilometraje?: number;
    usuarioId?: string;
}
