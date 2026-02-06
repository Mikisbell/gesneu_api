import { z } from 'zod';

/**
 * Formats Zod errors into a structured object for API responses.
 * Returns a record where keys are field paths and values are arrays of error messages.
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
 * Extracts the first error message from a ZodError.
 */
export function getFirstZodError(error: z.ZodError): string {
    return error.issues[0]?.message ?? 'Error de validación';
}
