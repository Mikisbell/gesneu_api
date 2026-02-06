/**
 * 🔧 Schema Compartido: Neumático
 * Validación unificada entre Frontend y Backend
 */

import { z } from 'zod'

/**
 * Validación de DOT (Date of Tire manufacture)
 * Formato: WWYY (Week 01-53, Year 00-99)
 * Ejemplo: 2423 = Semana 24 del año 2023
 */
export const DOTSchema = z
    .string()
    .regex(
        /^([0-4][0-9]|5[0-3])(0[0-9]|[1-9][0-9])$/,
        'DOT inválido. Formato: WWYY (Ej: 2423 = Semana 24 del 2023)'
    )
    .optional()
    .or(z.literal(''))

/**
 * Validación de número de serie
 * Industria real: Requerido, alfanumérico + guiones
 */
export const NumeroSerieSchema = z
    .string()
    .min(4, 'Número de serie debe tener mínimo 4 caracteres')
    .max(100, 'Número de serie debe tener máximo 100 caracteres')
    .regex(/^[A-Z0-9-]+$/i, 'Solo se permiten letras, números y guiones')
    .optional() // Mantener optional por compatibilidad, pero recomendado required

/**
 * Base Schema compartido entre Frontend y Backend
 * ✅ Usa z.coerce para convertir strings a numbers automáticamente
 */
export const BaseNeumaticoSchema = z.object({
    numero_serie: NumeroSerieSchema,
    modelo_id: z.string().uuid('ID de modelo inválido'),
    dot: DOTSchema,
    sensor_id: z
        .string()
        .max(100, 'ID de sensor muy largo')
        .optional()
        .or(z.literal('')),

    // ✅ z.coerce.number convierte string → number automáticamente
    profundidad_inicial_mm: z.coerce
        .number({ invalid_type_error: 'Debe ser un número' })
        .min(0, 'Profundidad no puede ser negativa')
        .max(50, 'Profundidad máxima: 50mm'),

    profundidad_actual_mm: z.coerce
        .number()
        .min(0, 'Profundidad no puede ser negativa')
        .max(50, 'Profundidad máxima: 50mm'),

    costo_compra: z.coerce
        .number()
        .min(0, 'Costo no puede ser negativo')
        .optional()
        .or(z.literal('')),

    ubicacion_almacen_id: z
        .string()
        .uuid('ID de almacén inválido')
        .optional()
        .or(z.literal('')),
})

/**
 * Frontend Form Schema
 * Para uso en react-hook-form
 * Omite profundidad_actual_mm porque se calcula al enviar
 */
export const NeumaticoFormSchema = BaseNeumaticoSchema.omit({ profundidad_actual_mm: true })

/**
 * Backend Create Schema
 * Extiende base con campos server-only
 */
export const CreateNeumaticoSchema = BaseNeumaticoSchema.extend({
    es_reencauchado: z.boolean().optional().default(false),

    // Validación de fecha con rangos
    fecha_compra: z
        .string()
        .datetime({ offset: true })
        .or(z.string().regex(/^\d{4}-\d{2}-\d{2}/, 'Formato fecha inválido'))
        .refine(
            (date) => new Date(date) <= new Date(),
            'Fecha de compra no puede ser futura'
        )
        .refine(
            (date) => new Date(date) >= new Date('2000-01-01'),
            'Fecha de compra inválida (anterior al año 2000)'
        ),

    fecha_fabricacion: z.string().optional(),
    moneda_compra: z.string().length(3).optional().default('PEN'),
    proveedor_compra_id: z.string().uuid().optional(),

    // Profundidades adicionales
    profundidad_int: z.coerce.number().min(0).optional(),
    profundidad_cen: z.coerce.number().min(0).optional(),
    profundidad_ext: z.coerce.number().min(0).optional(),
    presion_actual_psi: z.coerce.number().min(0).optional(),
})

/**
 * Backend Update Schema
 */
export const UpdateNeumaticoSchema = z.object({
    numero_serie: NumeroSerieSchema,
    dot: DOTSchema,
    sensor_id: z.string().max(100).optional().or(z.literal('')),
    activo: z.boolean().optional(),
})

/**
 * Type inference para TypeScript
 */
export type NeumaticoFormValues = z.infer<typeof NeumaticoFormSchema>
export type CreateNeumaticoInput = z.infer<typeof CreateNeumaticoSchema>
export type UpdateNeumaticoInput = z.infer<typeof UpdateNeumaticoSchema>
