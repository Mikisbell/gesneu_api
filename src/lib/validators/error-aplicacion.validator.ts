import { z } from 'zod';

/**
 * Schema para crear un registro de error de aplicacion
 */
export const CreateErrorAplicacionSchema = z.object({
    codigo: z.string().max(50, 'El codigo no puede exceder 50 caracteres').optional().or(z.literal('')),
    severidad: z.enum(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], {
        message: 'Severidad debe ser uno de: DEBUG, INFO, WARNING, ERROR, CRITICAL'
    }).default('ERROR'),
    mensaje: z.string().min(1, 'El mensaje es requerido'),
    stack_trace: z.string().optional().or(z.literal('')),
    modulo: z.string().max(50, 'El modulo no puede exceder 50 caracteres').optional().or(z.literal('')),
    endpoint: z.string().max(255, 'El endpoint no puede exceder 255 caracteres').optional().or(z.literal('')),
    metodo_http: z.string().max(10, 'El metodo HTTP no puede exceder 10 caracteres').optional().or(z.literal('')),
    usuario_id: z.string().uuid('ID de usuario debe ser un UUID valido').optional().or(z.literal('')),
    ip_direccion: z.string().max(45, 'La direccion IP no puede exceder 45 caracteres').optional().or(z.literal('')),
    user_agent: z.string().optional().or(z.literal('')),
    request_body: z.record(z.string(), z.any()).optional(),
    response_body: z.record(z.string(), z.any()).optional(),
    contexto: z.record(z.string(), z.any()).optional()
});

/**
 * Schema para resolver un error de aplicacion
 */
export const ResolveErrorSchema = z.object({
    resuelto_por: z.string().uuid('ID de usuario debe ser un UUID valido').optional(),
    notas: z.string().max(2000, 'Las notas no pueden exceder 2000 caracteres').optional()
});

export type CreateErrorAplicacionInput = z.infer<typeof CreateErrorAplicacionSchema>;
export type ResolveErrorInput = z.infer<typeof ResolveErrorSchema>;
