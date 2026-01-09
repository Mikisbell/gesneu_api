/**
 * Vehiculo Validators - Validación Runtime con Zod
 * 
 * Este módulo define los schemas de validación para la entidad Vehiculo.
 * Los schemas generan automáticamente los tipos TypeScript y validan
 * los datos en runtime.
 * 
 * Compatible con Zod v5 (beta).
 * 
 * @see docs/10_TIPADO_PROFESIONAL.md
 */

import { z } from 'zod';

// ============================================
// SCHEMAS DE VALIDACIÓN
// ============================================

/**
 * Schema para creación de vehículo.
 * Incluye validaciones de formato, rangos y reglas de negocio.
 * Nota: Zod v5 usa { error: string } en lugar de { required_error: string }
 */
export const CreateVehiculoSchema = z.object({
    placa: z
        .string({ error: 'La placa es requerida' })
        .min(5, 'La placa debe tener al menos 5 caracteres')
        .max(10, 'La placa no puede exceder 10 caracteres')
        .regex(
            /^[A-Z0-9-]+$/i,
            'La placa solo puede contener letras, números y guiones'
        )
        .transform((val) => val.toUpperCase()),

    tipo_vehiculo_id: z
        .string({ error: 'El tipo de vehículo es requerido' })
        .uuid('El ID del tipo de vehículo debe ser un UUID válido'),

    marca: z
        .string({ error: 'La marca es requerida' })
        .min(2, 'La marca debe tener al menos 2 caracteres')
        .max(50, 'La marca no puede exceder 50 caracteres'),

    modelo: z
        .string({ error: 'El modelo es requerido' })
        .min(1, 'El modelo es requerido')
        .max(100, 'El modelo no puede exceder 100 caracteres'),

    anio: z
        .number({ error: 'El año es requerido' })
        .int('El año debe ser un número entero')
        .min(1990, 'El año mínimo es 1990')
        .max(new Date().getFullYear() + 1, `El año máximo es ${new Date().getFullYear() + 1}`),

    tipo_medicion: z
        .enum(['KILOMETRAJE', 'HOROMETRO'])
        .optional()
        .default('KILOMETRAJE'),

    odometro_actual: z
        .number()
        .nonnegative('El odómetro no puede ser negativo')
        .optional(),

    kilometraje_actual: z
        .number()
        .nonnegative('El kilometraje no puede ser negativo')
        .optional(),

    chasis_serie: z
        .string()
        .max(50, 'El número de chasis/VIN no puede exceder 50 caracteres')
        .optional()
        .nullable(),

    numero_economico: z
        .string()
        .max(20, 'El número económico no puede exceder 20 caracteres')
        .optional(),

    motor_serie: z
        .string()
        .max(50, 'El número de serie del motor no puede exceder 50 caracteres')
        .optional(),

    activo: z
        .boolean()
        .optional()
        .default(true),
});

/**
 * Schema para actualización de vehículo.
 * Todos los campos son opcionales (partial).
 */
export const UpdateVehiculoSchema = CreateVehiculoSchema.partial();

/**
 * Schema para filtros de búsqueda.
 */
export const VehiculoFiltersSchema = z.object({
    placa: z.string().optional(),
    tipo_vehiculo_id: z.string().uuid().optional(),
    marca: z.string().optional(),
    activo: z
        .union([z.boolean(), z.string().transform((val) => val === 'true')])
        .optional(),
    search: z.string().optional(),
});

/**
 * Schema para parámetros de paginación.
 */
export const VehiculoPaginationSchema = z.object({
    page: z
        .string()
        .optional()
        .transform((val) => (val ? parseInt(val, 10) : 1))
        .pipe(z.number().int().positive()),
    limit: z
        .string()
        .optional()
        .transform((val) => (val ? parseInt(val, 10) : 10))
        .pipe(z.number().int().min(1).max(100)),
    sortBy: z.enum(['placa', 'marca', 'anio', 'createdAt']).optional().default('placa'),
    sortOrder: z.enum(['asc', 'desc']).optional().default('asc'),
});

// ============================================
// TIPOS INFERIDOS
// ============================================

/**
 * Tipo inferido del schema de creación.
 * Usar cuando se reciben datos ya validados.
 */
export type CreateVehiculoInput = z.infer<typeof CreateVehiculoSchema>;

/**
 * Tipo inferido del schema de actualización.
 */
export type UpdateVehiculoInput = z.infer<typeof UpdateVehiculoSchema>;

/**
 * Tipo inferido del schema de filtros.
 */
export type VehiculoFiltersInput = z.infer<typeof VehiculoFiltersSchema>;

/**
 * Tipo inferido del schema de paginación.
 */
export type VehiculoPaginationInput = z.infer<typeof VehiculoPaginationSchema>;

// ============================================
// FUNCIONES DE VALIDACIÓN
// ============================================

/**
 * Valida datos de creación de vehículo.
 * Devuelve un SafeParseReturn con success/error.
 * 
 * @example
 * const result = validateCreateVehiculo(body);
 * if (!result.success) {
 *   return ApiResponse.validationError(result.error.flatten());
 * }
 * // result.data está tipado y validado
 */
export function validateCreateVehiculo(data: unknown) {
    return CreateVehiculoSchema.safeParse(data);
}

/**
 * Valida datos de actualización de vehículo.
 */
export function validateUpdateVehiculo(data: unknown) {
    return UpdateVehiculoSchema.safeParse(data);
}

/**
 * Valida filtros de búsqueda.
 */
export function validateVehiculoFilters(data: unknown) {
    return VehiculoFiltersSchema.safeParse(data);
}

/**
 * Valida parámetros de paginación.
 */
export function validateVehiculoPagination(data: unknown) {
    return VehiculoPaginationSchema.safeParse(data);
}

// ============================================
// MENSAJES DE ERROR PERSONALIZADOS
// ============================================

/**
 * Formatea los errores de Zod para respuesta de API.
 */
export function formatZodErrors(error: z.ZodError): Record<string, string[]> {
    const errors: Record<string, string[]> = {};

    for (const issue of error.issues) {
        const path = issue.path.join('.');
        if (!errors[path]) {
            errors[path] = [];
        }
        errors[path].push(issue.message);
    }

    return errors;
}

/**
 * Extrae el primer mensaje de error de un ZodError.
 */
export function getFirstZodError(error: z.ZodError): string {
    return error.issues[0]?.message ?? 'Error de validación';
}
