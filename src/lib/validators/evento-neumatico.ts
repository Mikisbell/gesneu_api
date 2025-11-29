import { z } from 'zod';

// Enums based on schema.prisma
export const TipoEventoNeumaticoEnum = z.enum([
    'COMPRA',
    'INSTALACION',
    'DESMONTAJE',
    'ROTACION',
    'INSPECCION',
    'REPARACION_ENTRADA',
    'REPARACION_SALIDA',
    'REENCAUCHE_ENTRADA',
    'REENCAUCHE_SALIDA',
    'DESECHO',
    'AJUSTE_INVENTARIO',
    'TRANSFERENCIA_UBICACION',
    'ASIGNACION_A_ALMACEN',
    'VENTA',
    'MOVIMIENTO_ENTRE_ALMACENES',
    'BAJA_POR_ROBO_EXTRAVIO',
    'DESMONTE_POR_FIN_VIDA_UTIL',
    'DESMONTE_TEMPORAL'
]);

export const EstadoNeumaticoEnum = z.enum([
    'EN_STOCK',
    'INSTALADO',
    'EN_REPARACION',
    'EN_REENCAUCHE',
    'DESECHADO',
    'EN_TRANSITO'
]);

// Base schema for all events
export const EventoNeumaticoCreateSchema = z.object({
    tipo_evento: TipoEventoNeumaticoEnum,
    fecha_evento: z.string().datetime().optional().default(() => new Date().toISOString()), // ISO string
    neumatico_id: z.string().uuid().optional(), // Optional for COMPRA

    // Common fields
    kilometraje_vehiculo: z.number().nonnegative().optional(),
    profundidad_remanente: z.number().nonnegative().optional(),
    presion_psi: z.number().nonnegative().optional(),
    observaciones: z.string().optional(),
    costo_evento: z.number().nonnegative().optional(),

    // Location/Relation fields
    vehiculo_id: z.string().uuid().optional(),
    posicion_montaje_id: z.string().uuid().optional(),
    almacen_destino_id: z.string().uuid().optional(),
    proveedor_id: z.string().uuid().optional(),
    motivo_desecho_id: z.string().uuid().optional(),

    // Resulting state
    estado_neumatico_resultante: EstadoNeumaticoEnum.optional(),

    // Specific fields for COMPRA (creating a new tire)
    numero_serie: z.string().optional(),
    modelo_id: z.string().uuid().optional(),
    marca_id: z.string().uuid().optional(), // Can be inferred
    medida: z.string().optional(),
    dot: z.string().length(4).optional(),
    profundidad_inicial: z.number().nonnegative().optional(),
    fecha_compra: z.string().datetime().optional(),
    costo_compra: z.number().nonnegative().optional(),
});

export type EventoNeumaticoCreate = z.infer<typeof EventoNeumaticoCreateSchema>;
