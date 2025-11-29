/**
 * Custom error class for business logic errors.
 * Allows proper HTTP status codes (400, 404, 409) instead of generic 500.
 */
export class BusinessError extends Error {
    constructor(
        public message: string,
        public statusCode: number = 400,
        public code: string = 'BUSINESS_ERROR'
    ) {
        super(message);
        this.name = 'BusinessError';
        // Maintains proper stack trace for where our error was thrown
        Error.captureStackTrace(this, this.constructor);
    }

    /**
     * Factory methods for common business errors
     */
    static notFound(resource: string, identifier?: string): BusinessError {
        const msg = identifier
            ? `${resource} con identificador '${identifier}' no encontrado`
            : `${resource} no encontrado`;
        return new BusinessError(msg, 404, 'NOT_FOUND');
    }

    static conflict(message: string): BusinessError {
        return new BusinessError(message, 409, 'CONFLICT');
    }

    static badRequest(message: string): BusinessError {
        return new BusinessError(message, 400, 'BAD_REQUEST');
    }

    static forbidden(message: string): BusinessError {
        return new BusinessError(message, 403, 'FORBIDDEN');
    }
}
