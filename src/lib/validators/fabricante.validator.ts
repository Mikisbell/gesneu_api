
import { z } from 'zod';

export const CreateFabricanteSchema = z.object({
    nombre: z.string().min(2, "El nombre debe tener al menos 2 caracteres"),
    codigoAbreviado: z.string().max(10).optional(),
    paisOrigen: z.string().max(50).optional(),
    sitioWeb: z.string().url("URL inválida").optional().or(z.literal('')),
});

export const UpdateFabricanteSchema = CreateFabricanteSchema.partial().extend({
    activo: z.boolean().optional(),
});
