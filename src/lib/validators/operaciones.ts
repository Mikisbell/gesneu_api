import { z } from 'zod';

/**
 * Schema de validación para operación de montaje de neumático
 */
export const MontajeNeumaticoSchema = z.object({
    neumatico_id: z.string().uuid('ID de neumático debe ser un UUID válido'),
    vehiculo_id: z.string().uuid('ID de vehículo debe ser un UUID válido'),
    posicion_id: z.string().uuid('ID de posición debe ser un UUID válido'),
    kilometraje_vehiculo: z.number()
        .nonnegative('El kilometraje debe ser un número positivo')
        .int('El kilometraje debe ser un número entero'),
    presion_psi: z.number()
        .positive('La presión debe ser mayor a 0')
        .max(150, 'La presión no puede exceder 150 PSI')
        .optional(),
    observaciones: z.string().max(1000, 'Las observaciones no pueden exceder 1000 caracteres').optional(),
    fecha_evento: z.coerce.date().optional()
});

/**
 * Schema de validación para operación de desmontaje de neumático
 */
export const DesmontajeNeumaticoSchema = z.object({
    neumatico_id: z.string().uuid('ID de neumático debe ser un UUID válido'),
    destino: z.enum(['STOCK', 'REPARACION', 'REENCAUCHE', 'DESECHO'], {
        message: 'Destino debe ser uno de: STOCK, REPARACION, REENCAUCHE, DESECHO'
    }),
    kilometraje_vehiculo: z.number()
        .nonnegative('El kilometraje debe ser un número positivo')
        .int('El kilometraje debe ser un número entero'),
    almacen_destino_id: z.string().uuid('ID de almacén debe ser un UUID válido').optional(),
    motivo_id: z.string().uuid('ID de motivo debe ser un UUID válido').optional(),
    profundidad_remanente_mm: z.number()
        .positive('La profundidad debe ser mayor a 0')
        .max(25, 'La profundidad no puede exceder 25mm')
        .optional(),
    presion_psi: z.number()
        .positive('La presión debe ser mayor a 0')
        .max(150, 'La presión no puede exceder 150 PSI')
        .optional(),
    observaciones: z.string().max(1000, 'Las observaciones no pueden exceder 1000 caracteres').optional(),
    fecha_evento: z.coerce.date().optional()
}).refine((data) => {
    // Si el destino es STOCK, debe especificar almacen_destino_id
    if (data.destino === 'STOCK' && !data.almacen_destino_id) {
        return false;
    }
    // Si el destino es DESECHO, debe especificar motivo_id
    if (data.destino === 'DESECHO' && !data.motivo_id) {
        return false;
    }
    return true;
}, {
    message: 'Cuando el destino es STOCK debe especificar almacen_destino_id; cuando es DESECHO debe especificar motivo_id'
});

/**
 * Schema de validación para movimiento individual en rotación
 */
const MovimientoRotacionSchema = z.object({
    neumatico_id: z.string().uuid('ID de neumático debe ser un UUID válido'),
    posicion_destino_id: z.string().uuid('ID de posición destino debe ser un UUID válido')
});

/**
 * Schema de validación para operación de rotación de neumáticos
 */
export const RotacionNeumaticoSchema = z.object({
    vehiculo_id: z.string().uuid('ID de vehículo debe ser un UUID válido'),
    kilometraje_vehiculo: z.number()
        .nonnegative('El kilometraje debe ser un número positivo')
        .int('El kilometraje debe ser un número entero'),
    movimientos: z.array(MovimientoRotacionSchema)
        .min(2, 'Debe especificar al menos 2 movimientos para una rotación')
        .max(20, 'No se pueden rotar más de 20 neumáticos en una operación'),
    observaciones: z.string().max(1000, 'Las observaciones no pueden exceder 1000 caracteres').optional()
}).refine((data) => {
    // Validar que no haya IDs de neumáticos duplicados
    const neumaticosIds = data.movimientos.map(m => m.neumatico_id);
    const uniqueIds = new Set(neumaticosIds);
    return uniqueIds.size === neumaticosIds.length;
}, {
    message: 'No puede haber neumáticos duplicados en los movimientos de rotación'
}).refine((data) => {
    // Validar que no haya posiciones destino duplicadas
    const posicionesIds = data.movimientos.map(m => m.posicion_destino_id);
    const uniqueIds = new Set(posicionesIds);
    return uniqueIds.size === posicionesIds.length;
}, {
    message: 'No puede haber posiciones destino duplicadas en los movimientos de rotación'
});

// Export tipos inferidos
export type MontajeNeumaticoInput = z.infer<typeof MontajeNeumaticoSchema>;
export type DesmontajeNeumaticoInput = z.infer<typeof DesmontajeNeumaticoSchema>;
export type RotacionNeumaticoInput = z.infer<typeof RotacionNeumaticoSchema>;
