import { z } from 'zod';

/**
 * Schema para crear un parametro del sistema
 */
export const CreateParametroSistemaSchema = z.object({
    clave: z.string().min(1, 'La clave es requerida').max(100, 'La clave no puede exceder 100 caracteres'),
    valor: z.string().min(1, 'El valor es requerido'),
    tipo_dato: z.enum(['STRING', 'NUMBER', 'BOOLEAN', 'JSON'], {
        message: 'Tipo de dato debe ser uno de: STRING, NUMBER, BOOLEAN, JSON'
    }).default('STRING'),
    categoria: z.string().max(50, 'La categoria no puede exceder 50 caracteres').optional().or(z.literal('')),
    descripcion: z.string().max(1000, 'La descripcion no puede exceder 1000 caracteres').optional().or(z.literal('')),
    valor_default: z.string().optional().or(z.literal('')),
    editable: z.boolean().default(true),
    requiere_reinicio: z.boolean().default(false)
});

/**
 * Schema para actualizar un parametro del sistema
 */
export const UpdateParametroSistemaSchema = z.object({
    valor: z.string().min(1, 'El valor es requerido'),
    tipo_dato: z.enum(['STRING', 'NUMBER', 'BOOLEAN', 'JSON']).optional(),
    categoria: z.string().max(50).optional().or(z.literal('')),
    descripcion: z.string().max(1000).optional().or(z.literal('')),
    valor_default: z.string().optional().or(z.literal('')),
    editable: z.boolean().optional(),
    requiere_reinicio: z.boolean().optional()
});

/**
 * Schema para actualizar un parametro por clave
 */
export const SetByKeySchema = z.object({
    valor: z.string().min(1, 'El valor es requerido'),
    tipo_dato: z.enum(['STRING', 'NUMBER', 'BOOLEAN', 'JSON']).optional(),
    descripcion: z.string().max(1000).optional().or(z.literal('')),
    editable: z.boolean().optional(),
    requiere_reinicio: z.boolean().optional()
});

export type CreateParametroSistemaInput = z.infer<typeof CreateParametroSistemaSchema>;
export type UpdateParametroSistemaInput = z.infer<typeof UpdateParametroSistemaSchema>;
export type SetByKeyInput = z.infer<typeof SetByKeySchema>;
