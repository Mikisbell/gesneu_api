/**
 * 🔧 Neumatico Validator - Backend
 * Usa schema compartido para consistencia
 */

import { z } from 'zod'
import {
    CreateNeumaticoSchema,
    UpdateNeumaticoSchema,
} from './neumatico.shared'

// ✅ Re-export schemas compartidos
export { CreateNeumaticoSchema, UpdateNeumaticoSchema }

// ✅ Type inference
export type CreateNeumaticoInput = z.infer<typeof CreateNeumaticoSchema>
export type UpdateNeumaticoInput = z.infer<typeof UpdateNeumaticoSchema>

/**
 * DEPRECATED: Use '@/lib/utils/zod.utils' instead.
 * Re-exporting here to fix stale cache build errors.
 */
export function formatZodErrors(error: z.ZodError): Record<string, string[]> {
    const errors: Record<string, string[]> = {}
    for (const issue of error.issues) {
        const path = issue.path.join('.')
        if (!errors[path]) errors[path] = []
        errors[path].push(issue.message)
    }
    return errors
}
