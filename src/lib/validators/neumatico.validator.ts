/**
 * Neumatico Validators - Validación Runtime con Zod
 * 
 * Este módulo define los schemas de validación para la entidad Neumatico.
 * Compatible con Zod v5 (beta).
 * 
 * @see docs/10_TIPADO_PROFESIONAL.md
 */

import { z } from 'zod';

// ============================================
// SCHEMAS DE VALIDACIÓN
// ============================================

/**
 * Schema para creación de neumático.
 */
export const CreateNeumaticoSchema = z.object({
    modelo_id: z
        .string({ error: 'El modelo de neumático es requerido' })
        .uuid('ID de modelo inválido'),

    numero_serie: z
        .string()
        .min(3, 'El número de serie debe tener al menos 3 caracteres')
        .max(50, 'El número de serie no puede exceder 50 caracteres')
        .optional(),

    dot: z
        .string()
        .max(20, 'El DOT no puede exceder 20 caracteres')
        .optional(),

    estado: z
        .enum(['NUEVO', 'USADO', 'REENCAUCHADO'], { error: 'Estado inválido' })
        .optional()
        .default('NUEVO'),

    costo_compra: z
        .number()
        .nonnegative('El costo no puede ser negativo')
        .optional(),

    moneda_compra: z
        .string()
        .length(3, 'El código de moneda debe tener 3 caracteres')
        .optional()
        .default('PEN'),

    proveedor_id: z
        .string()
        .uuid('ID de proveedor inválido')
        .optional(),

    fecha_compra: z
        .string()
        .datetime('Fecha de compra inválida (formato ISO)')
        .optional(),

    fecha_fabricacion: z
        .string()
        .datetime('Fecha de fabricación inválida (formato ISO)')
        .optional(),

    profundidad_inicial: z
        .number()
        .min(0, 'La profundidad no puede ser negativa')
        .max(30, 'La profundidad parece excesiva (>30mm)')
        .optional(),

    kilometraje_acumulado: z
        .number()
        .nonnegative()
        .optional(),

    // Ubicación inicial (opcional)
    ubicacion_almacen_id: z.string().uuid().optional(),
    ubicacion_vehiculo_id: z.string().uuid().optional(),
    ubicacion_posicion_id: z.string().uuid().optional(),
});

/**
 * Schema para actualización de neumático.
 */
export const UpdateNeumaticoSchema = z.object({
    numero_serie: z.string().min(3).max(50).optional(),
    dot: z.string().max(20).optional(),
    proveedor_id: z.string().uuid().optional(),
    costo_compra: z.number().nonnegative().optional(),
    fecha_compra: z.string().datetime().optional(),
    fecha_fabricacion: z.string().datetime().optional(),
    sensor_id: z.string().max(100).optional(),
    notas: z.string().max(1000).optional(),
    activo: z.boolean().optional(),
});

/**
 * Schema para filtros de búsqueda.
 */
export const NeumaticoFiltersSchema = z.object({
    serie: z.string().optional(),
    marca: z.string().optional(),
    estado: z.string().optional(), // EN_STOCK, MONTADO, etc.
    ubicacion: z.enum(['ALMACEN', 'MONTADO']).optional(),
    vehiculo_id: z.string().uuid().optional(),
    search: z.string().optional(),
});

// ============================================
// TIPOS INFERIDOS
// ============================================

export type CreateNeumaticoInput = z.infer<typeof CreateNeumaticoSchema>;
export type UpdateNeumaticoInput = z.infer<typeof UpdateNeumaticoSchema>;
export type NeumaticoFiltersInput = z.infer<typeof NeumaticoFiltersSchema>;

// ============================================
// FUNCIONES DE VALIDACIÓN
// ============================================

export function validateCreateNeumatico(data: unknown) {
    return CreateNeumaticoSchema.safeParse(data);
}

export function validateUpdateNeumatico(data: unknown) {
    return UpdateNeumaticoSchema.safeParse(data);
}

export function validateNeumaticoFilters(data: unknown) {
    return NeumaticoFiltersSchema.safeParse(data);
}

/**
 * Extrae el primer mensaje de error de un ZodError.
 */
export function getFirstZodError(error: z.ZodError): string {
    return error.issues[0]?.message ?? 'Error de validación';
}

/**
 * Formatea errores de Zod para respuesta de API.
 */
export function formatZodErrors(error: z.ZodError): Record<string, string[]> {
    return error.flatten().fieldErrors as Record<string, string[]>;
}
