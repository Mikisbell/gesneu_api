import { z } from 'zod';

export const CreateRolSchema = z.object({
    nombre: z.string().min(1).max(50, 'El nombre no puede exceder 50 caracteres'),
    descripcion: z.string().max(500).optional(),
    es_sistema: z.boolean().optional().default(false),
    activo: z.boolean().optional().default(true),
});

export const AssignPermisoSchema = z.object({
    permiso_id: z.string().uuid('ID de permiso debe ser un UUID válido'),
});

export const AssignRolToUserSchema = z.object({
    rol_id: z.string().uuid('ID de rol debe ser un UUID válido'),
    es_principal: z.boolean().optional().default(false),
    valido_desde: z.coerce.date().optional(),
    valido_hasta: z.coerce.date().optional(),
});

export const UpdateRolSchema = CreateRolSchema.partial();

export type CreateRolInput = z.infer<typeof CreateRolSchema>;
export type AssignPermisoInput = z.infer<typeof AssignPermisoSchema>;
export type AssignRolToUserInput = z.infer<typeof AssignRolToUserSchema>;
export type UpdateRolInput = z.infer<typeof UpdateRolSchema>;
