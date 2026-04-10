import { z } from 'zod';

export const CreateCentroCostoSchema = z.object({
    codigo: z.string().min(1).max(20, 'El código no puede exceder 20 caracteres'),
    nombre: z.string().min(1).max(100, 'El nombre no puede exceder 100 caracteres'),
    area_negocio: z.string().max(100).optional(),
    activo: z.boolean().optional().default(true),
});

export const UpdateCentroCostoSchema = CreateCentroCostoSchema.partial();

export type CreateCentroCostoInput = z.infer<typeof CreateCentroCostoSchema>;
export type UpdateCentroCostoInput = z.infer<typeof UpdateCentroCostoSchema>;
