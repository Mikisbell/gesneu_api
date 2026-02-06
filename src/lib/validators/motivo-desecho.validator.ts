
import { z } from 'zod';

export const CreateMotivoDesechoSchema = z.object({
    codigo: z.string().min(1, "El código es requerido").max(20),
    nombre: z.string().min(2, "El nombre debe tener al menos 2 caracteres"),
    descripcion: z.string().optional(),
    requiere_evidencia: z.boolean().optional().default(false),
});

export const UpdateMotivoDesechoSchema = CreateMotivoDesechoSchema.partial().extend({
    activo: z.boolean().optional(),
});
