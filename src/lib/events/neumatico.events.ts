// Event Constants for Tire Operations
export const NeumaticoEvents = {
    // Lifecycle Events
    PURCHASED: 'NEUMATICO.PURCHASED',
    MOUNTED: 'NEUMATICO.MOUNTED',
    DISMOUNTED: 'NEUMATICO.DISMOUNTED',
    ROTATED: 'NEUMATICO.ROTATED',
    SCRAPPED: 'NEUMATICO.SCRAPPED',

    // Repair Cycle
    REPAIR_STARTED: 'NEUMATICO.REPAIR_STARTED',
    REPAIR_COMPLETED: 'NEUMATICO.REPAIR_COMPLETED',

    // Retread Cycle
    RETREAD_SENT: 'NEUMATICO.RETREAD_SENT',
    RETREAD_RETURNED: 'NEUMATICO.RETREAD_RETURNED',

    // State Changes
    STATUS_CHANGED: 'NEUMATICO.STATUS_CHANGED',
    LOCATION_CHANGED: 'NEUMATICO.LOCATION_CHANGED'
} as const;

// Base payload interface
interface BaseNeumaticoPayload {
    neumaticoId: string;
    empresaId: string;
    usuarioId: string;
    timestamp?: Date;
}

// Tire Purchase Event
export interface TirePurchasedPayload extends BaseNeumaticoPayload {
    numeroSerie?: string;
    modeloId: string;
    marcaId: string;
    costoCompra: number;
    proveedorId?: string;
    metadata: {
        medida: string;
        dot?: string;
        profundidadInicial: number;
    };
}

// Tire Mounted Event
export interface TireMountedPayload extends BaseNeumaticoPayload {
    vehiculoId: string;
    posicionId: string;
    kilometrajeVehiculo?: number;
    metadata: {
        numeroSerie: string | null;
        modeloNombre: string;
        estadoAnterior: string;
        profundidadActual?: number;
    };
}

// Tire Dismounted Event
export interface TireDismountedPayload extends BaseNeumaticoPayload {
    vehiculoId: string;
    posicionId: string;
    almacenDestinoId?: string;
    razon?: string;
    profundidadRemanente?: number;
    metadata: {
        numeroSerie: string | null;
        kilometrajeVidaActual: number;
        estadoResultante: string;
    };
}

// Tire Rotated Event
export interface TireRotatedPayload extends BaseNeumaticoPayload {
    vehiculoId: string;
    posicionOrigenId: string;
    posicionDestinoId: string;
    kilometrajeVehiculo: number;
    metadata: {
        numeroSerie: string | null;
        profundidadActual?: number;
    };
}

// Tire Scrapped Event
export interface TireScrappedPayload extends BaseNeumaticoPayload {
    motivoDesechoId?: string;
    motivoTexto: string;
    profundidadFinal?: number;
    metadata: {
        numeroSerie: string | null;
        costoTotal: number;
        kmTotales: number;
        vidaActual: number;
        reencauchesRealizados: number;
        modeloNombre: string;
    };
}

// Repair Started Event
export interface RepairStartedPayload extends BaseNeumaticoPayload {
    proveedorId?: string;
    costoEstimado?: number;
    observaciones?: string;
    metadata: {
        numeroSerie: string | null;
        estadoAnterior: string;
        profundidadPreReparacion?: number;
    };
}

// Repair Completed Event
export interface RepairCompletedPayload extends BaseNeumaticoPayload {
    proveedorId?: string;
    costoReal: number;
    observaciones?: string;
    metadata: {
        numeroSerie: string | null;
        estadoResultante: string;
        profundidadPostReparacion?: number;
        diasEnTaller: number;
    };
}

// Retread Sent Event (unified with existing)
export interface RetreadSentPayload extends BaseNeumaticoPayload {
    proveedorId: string;
    metadata: {
        numeroSerie: string | null;
        vidaActual: number;
        profundidadPreRetread?: number;
    };
}

// Retread Returned Event (unified with existing)
export interface RetreadReturnedPayload extends BaseNeumaticoPayload {
    proveedorId: string;
    costoReencauche: number;
    nuevaProfundidad: number;
    metadata: {
        numeroSerie: string | null;
        nuevoReencaucheCount: number;
        nuevaVida: number;
    };
}

// Status Changed Event (generic state transition)
export interface StatusChangedPayload extends BaseNeumaticoPayload {
    estadoAnterior: string;
    estadoNuevo: string;
    tipoEvento: string;
    metadata: {
        numeroSerie: string | null;
        razon?: string;
    };
}

// Location Changed Event
export interface LocationChangedPayload extends BaseNeumaticoPayload {
    ubicacionAnterior: {
        tipo: 'VEHICULO' | 'ALMACEN' | 'PROVEEDOR';
        id?: string;
    };
    ubicacionNueva: {
        tipo: 'VEHICULO' | 'ALMACEN' | 'PROVEEDOR';
        id?: string;
    };
    metadata: {
        numeroSerie: string | null;
    };
}
