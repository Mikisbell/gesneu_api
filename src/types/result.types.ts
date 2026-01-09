/**
 * Result Types - Manejo Explícito de Errores
 * 
 * Este módulo implementa el patrón "Result" (también conocido como Either)
 * que fuerza al desarrollador a manejar explícitamente los casos de éxito y error.
 * 
 * Basado en patrones de Rust y bibliotecas como neverthrow.
 * 
 * @example
 * async function getVehiculo(id: VehiculoId): Promise<Result<VehiculoResponse, NotFoundError>> {
 *   const entity = await repo.findById(id);
 *   if (!entity) {
 *     return err(new NotFoundError('Vehículo'));
 *   }
 *   return ok(mapEntityToResponse(entity));
 * }
 * 
 * // Uso:
 * const result = await getVehiculo(id);
 * if (!result.success) {
 *   return ApiResponse.error(result.error.message, result.error.statusCode);
 * }
 * return ApiResponse.success(result.data);
 */

// ============================================
// Result Type
// ============================================

/**
 * Tipo discriminado que representa un resultado que puede ser exitoso o fallido.
 * - `success: true` contiene `data: T`
 * - `success: false` contiene `error: E`
 */
export type Result<T, E = Error> =
    | { success: true; data: T }
    | { success: false; error: E };

/**
 * Crea un Result exitoso con los datos proporcionados.
 */
export const ok = <T>(data: T): Result<T, never> => ({
    success: true,
    data,
});

/**
 * Crea un Result fallido con el error proporcionado.
 */
export const err = <E>(error: E): Result<never, E> => ({
    success: false,
    error,
});

// ============================================
// Business Errors (Errores de Negocio Tipados)
// ============================================

/**
 * Error base de negocio. Todos los errores de aplicación heredan de esta clase.
 */
export class BusinessError extends Error {
    constructor(
        message: string,
        public readonly code: string,
        public readonly statusCode: number = 400
    ) {
        super(message);
        this.name = 'BusinessError';
        // Mantener el stack trace correcto en V8
        if (Error.captureStackTrace) {
            Error.captureStackTrace(this, BusinessError);
        }
    }

    /**
     * Convierte el error a un formato JSON serializable para la API.
     */
    toJSON() {
        return {
            code: this.code,
            message: this.message,
            statusCode: this.statusCode,
        };
    }
}

/**
 * Error cuando un recurso no se encuentra.
 * HTTP Status: 404
 */
export class NotFoundError extends BusinessError {
    constructor(entity: string, id?: string) {
        const message = id
            ? `${entity} con ID ${id} no encontrado`
            : `${entity} no encontrado`;
        super(message, 'NOT_FOUND', 404);
        this.name = 'NotFoundError';
    }
}

/**
 * Error de validación de datos de entrada.
 * HTTP Status: 400
 */
export class ValidationError extends BusinessError {
    constructor(
        message: string,
        public readonly fields?: Record<string, string[]>
    ) {
        super(message, 'VALIDATION_ERROR', 400);
        this.name = 'ValidationError';
    }

    override toJSON() {
        return {
            ...super.toJSON(),
            fields: this.fields,
        };
    }
}

/**
 * Error de conflicto (ej: registro duplicado, violación de unicidad).
 * HTTP Status: 409
 */
export class ConflictError extends BusinessError {
    constructor(message: string) {
        super(message, 'CONFLICT', 409);
        this.name = 'ConflictError';
    }
}

/**
 * Error de acceso denegado (usuario autenticado pero sin permisos).
 * HTTP Status: 403
 */
export class ForbiddenError extends BusinessError {
    constructor(message: string = 'Acceso denegado') {
        super(message, 'FORBIDDEN', 403);
        this.name = 'ForbiddenError';
    }
}

/**
 * Error de autenticación (usuario no autenticado).
 * HTTP Status: 401
 */
export class UnauthorizedError extends BusinessError {
    constructor(message: string = 'No autenticado') {
        super(message, 'UNAUTHORIZED', 401);
        this.name = 'UnauthorizedError';
    }
}

/**
 * Error de regla de negocio (operación no permitida por lógica de negocio).
 * HTTP Status: 422
 */
export class BusinessRuleError extends BusinessError {
    constructor(message: string) {
        super(message, 'BUSINESS_RULE_VIOLATION', 422);
        this.name = 'BusinessRuleError';
    }
}

/**
 * Error de concurrencia (registro modificado por otro usuario).
 * HTTP Status: 409
 */
export class ConcurrencyError extends BusinessError {
    constructor(entity: string) {
        super(
            `El registro de ${entity} fue modificado por otro usuario. Por favor, recarga la página.`,
            'CONCURRENCY_ERROR',
            409
        );
        this.name = 'ConcurrencyError';
    }
}

// ============================================
// Type Guards
// ============================================

/**
 * Verifica si un error es un BusinessError (o subclase).
 */
export function isBusinessError(error: unknown): error is BusinessError {
    return error instanceof BusinessError;
}

/**
 * Verifica si un Result es exitoso.
 */
export function isOk<T, E>(result: Result<T, E>): result is { success: true; data: T } {
    return result.success === true;
}

/**
 * Verifica si un Result es fallido.
 */
export function isErr<T, E>(result: Result<T, E>): result is { success: false; error: E } {
    return result.success === false;
}

// ============================================
// Result Utilities
// ============================================

/**
 * Extrae el valor de un Result exitoso o lanza el error si es fallido.
 * Usar con precaución, solo cuando estés seguro de que el Result es ok.
 */
export function unwrap<T, E extends Error>(result: Result<T, E>): T {
    if (result.success) {
        return result.data;
    }
    throw result.error;
}

/**
 * Extrae el valor de un Result exitoso o devuelve un valor por defecto.
 */
export function unwrapOr<T, E>(result: Result<T, E>, defaultValue: T): T {
    if (result.success) {
        return result.data;
    }
    return defaultValue;
}

/**
 * Mapea el valor de un Result exitoso a otro tipo.
 */
export function mapResult<T, U, E>(
    result: Result<T, E>,
    fn: (data: T) => U
): Result<U, E> {
    if (result.success) {
        return ok(fn(result.data));
    }
    return result;
}

/**
 * Combina múltiples Results. Si todos son exitosos, devuelve un array con los datos.
 * Si alguno falla, devuelve el primer error.
 */
export function combineResults<T, E>(results: Result<T, E>[]): Result<T[], E> {
    const data: T[] = [];
    for (const result of results) {
        if (!result.success) {
            return result;
        }
        data.push(result.data);
    }
    return ok(data);
}
