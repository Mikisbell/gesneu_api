import { z } from 'zod';

/**
 * Schema para crear una tarea programada
 */
export const CreateTareaProgramadaSchema = z.object({
    nombre: z.string().min(1, 'El nombre es requerido').max(100, 'El nombre no puede exceder 100 caracteres'),
    tipo: z.enum([
        'ALERTA_VENCIMIENTO',
        'REPORTE_AUTOMATICO',
        'BACKUP_DB',
        'LIMPIEZA_LOGS',
        'SINCRONIZACION',
        'NOTIFICACION',
        'GENERAR_REPORTE',
        'OTRO'
    ], {
        message: 'Tipo de tarea debe ser uno de los valores permitidos'
    }),
    cron_expresion: z.string().max(50, 'La expresion cron no puede exceder 50 caracteres').optional().or(z.literal('')),
    cron_exp: z.string().max(50).optional().or(z.literal('')),
    intervalo_minutos: z.number().int('El intervalo debe ser un numero entero').positive('El intervalo debe ser mayor a 0').optional(),
    proxima_ejecucion: z.coerce.date().optional(),
    parametros: z.record(z.string(), z.any()).optional(),
    max_reintentos: z.number().int().nonnegative('Los reintentos deben ser no negativos').default(3),
    activo: z.boolean().default(true)
}).transform((data) => {
    // Normalize cron_expresion from cron_exp if provided
    if (!data.cron_expresion && data.cron_exp) {
        data.cron_expresion = data.cron_exp;
    }
    return data;
});

/**
 * Schema para actualizar una tarea programada
 */
export const UpdateTareaProgramadaSchema = z.object({
    nombre: z.string().min(1).max(100).optional(),
    tipo: z.enum([
        'ALERTA_VENCIMIENTO',
        'REPORTE_AUTOMATICO',
        'BACKUP_DB',
        'LIMPIEZA_LOGS',
        'SINCRONIZACION',
        'NOTIFICACION',
        'OTRO'
    ]).optional(),
    cron_expresion: z.string().max(50).optional().or(z.literal('')).nullable(),
    intervalo_minutos: z.number().int().positive().optional().nullable(),
    proxima_ejecucion: z.coerce.date().optional().nullable(),
    parametros: z.record(z.string(), z.any()).optional().nullable(),
    max_reintentos: z.number().int().nonnegative().optional(),
    activo: z.boolean().optional()
});

export type CreateTareaProgramadaInput = z.infer<typeof CreateTareaProgramadaSchema>;
export type UpdateTareaProgramadaInput = z.infer<typeof UpdateTareaProgramadaSchema>;
