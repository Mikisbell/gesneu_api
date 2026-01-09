import { z } from 'zod';

// Enums basados en schema.prisma - DEBE estar sincronizado con TipoEventoNeumaticoEnum en schema.prisma
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
    'AJUSTE_INVENTARIO'
]);

export const EstadoNeumaticoEnum = z.enum([
    'EN_STOCK',
    'INSTALADO',
    'EN_REPARACION',
    'EN_REENCAUCHE',
    'DESECHADO',
    'EN_TRANSITO'
]);

// Esquema Base para todos los eventos
export const EventoNeumaticoCreateSchema = z.object({
    tipo_evento: TipoEventoNeumaticoEnum,
    // Default a ahora si no se envía
    fecha_evento: z.string().datetime().optional().default(() => new Date().toISOString()),

    // El ID es opcional SOLO si es una COMPRA (porque se está creando)
    neumatico_id: z.string().uuid().optional(),

    // --- Campos Comunes de Operación ---
    contador_vehiculo: z.number().nonnegative().optional(),
    profundidad_remanente: z.number().nonnegative().optional(),
    presion_psi: z.number().nonnegative().optional(),
    observaciones: z.string().optional(),
    costo_evento: z.number().nonnegative().optional(), // 🚨 Vital para reparaciones/reencauches

    // --- Ubicaciones y Relaciones ---
    vehiculo_id: z.string().uuid().optional(),
    posicion_montaje_id: z.string().uuid().optional(),
    almacen_destino_id: z.string().uuid().optional(),
    proveedor_id: z.string().uuid().optional(), // Para compra o taller externo
    motivo_desecho_id: z.string().uuid().optional(),

    // --- Estado Resultante (Opcional) ---
    estado_neumatico_resultante: EstadoNeumaticoEnum.optional(),

    // --- Campos Específicos para COMPRA (Nacimiento del Neumático) ---
    numero_serie: z.string().optional(),
    modelo_id: z.string().uuid().optional(),
    marca_id: z.string().uuid().optional(), // Puede ser inferido del modelo, pero útil
    medida: z.string().optional(),
    dot: z.string().length(4).optional(), // Validación estricta de 4 caracteres
    profundidad_inicial: z.number().nonnegative().optional(),
    fecha_compra: z.string().datetime().optional(),
    costo_compra: z.number().nonnegative().optional(),
});

export type EventoNeumaticoCreate = z.infer<typeof EventoNeumaticoCreateSchema>;

// Alias estándar para el "Hybrid Approach"
export type CreateEventoInput = EventoNeumaticoCreate;
