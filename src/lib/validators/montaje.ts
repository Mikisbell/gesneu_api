import { z } from 'zod';

/**
 * Schema para validar la operación de montaje de neumático
 */
export const MontajeNeumaticoSchema = z.object({
    neumatico_id: z.string().uuid('ID de neumático debe ser un UUID válido'),
    vehiculo_id: z.string().uuid('ID de vehículo debe ser un UUID válido'),
    posicion_neumatico_id: z.string().uuid('ID de posición debe ser un UUID válido').optional(),
    contador_vehiculo: z.number().positive('Kilometraje debe ser mayor a 0'),
    profundidad_mm: z.number().positive('Profundidad debe ser mayor a 0').max(25, 'Profundidad máxima es 25mm'),
    presion_psi: z.number().positive('Presión debe ser mayor a 0').max(150, 'Presión máxima es 150 PSI'),
    observaciones: z.string().optional(),
});

export type MontajeNeumaticoInput = z.infer<typeof MontajeNeumaticoSchema>;

/**
 * Schema para la respuesta de montaje exitoso
 */
export const MontajeNeumaticoResponseSchema = z.object({
    evento: z.object({
        id: z.string().uuid(),
        tipo_evento: z.literal('INSTALACION'),
        neumatico_id: z.string().uuid(),
        vehiculo_id: z.string().uuid(),
        fecha_evento: z.date(),
    }),
    neumatico: z.object({
        id: z.string().uuid(),
        numero_serie: z.string(),
        estado_actual: z.literal('INSTALADO'),
        ubicacion_vehiculo_id: z.string().uuid(),
    }),
});

export type MontajeNeumaticoResponse = z.infer<typeof MontajeNeumaticoResponseSchema>;
