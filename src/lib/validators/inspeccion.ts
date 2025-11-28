import { z } from 'zod';

/**
 * Schema para validar la operación de inspección de neumático
 */
export const InspeccionNeumaticoSchema = z.object({
    neumatico_id: z.string().uuid('ID de neumático debe ser un UUID válido'),
    profundidad_mm: z.number().positive('Profundidad debe ser mayor a 0').max(30, 'Profundidad máxima es 30mm'),
    presion_psi: z.number().positive('Presión debe ser mayor a 0').max(150, 'Presión máxima es 150 PSI'),
    kilometraje_vehiculo: z.number().positive('Kilometraje debe ser mayor a 0').optional(),
    observaciones: z.string().optional(),
});

export type InspeccionNeumaticoInput = z.infer<typeof InspeccionNeumaticoSchema>;

/**
 * Schema para la respuesta de inspección exitosa
 */
export const InspeccionNeumaticoResponseSchema = z.object({
    medicion: z.object({
        id: z.string().uuid(),
        neumatico_id: z.string().uuid(),
        profundidad_mm: z.number(),
        fecha_medicion: z.date(),
    }),
    neumatico: z.object({
        id: z.string().uuid(),
        numero_serie: z.string(),
        estado_actual: z.string(),
        profundidad_actual_mm: z.number(),
        presion_actual_psi: z.number(),
    }),
    alerta: z.object({
        generada: z.boolean(),
        tipo: z.enum(['CRITICA', 'ADVERTENCIA']).optional(),
        mensaje: z.string().optional(),
    }).optional(),
});

export type InspeccionNeumaticoResponse = z.infer<typeof InspeccionNeumaticoResponseSchema>;
