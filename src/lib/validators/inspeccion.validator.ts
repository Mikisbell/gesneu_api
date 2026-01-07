import { z } from 'zod';

export const CreateInspeccionSchema = z.object({
    neumatico_id: z.string().uuid('ID de neumático inválido'),
    presion_psi: z.number().min(0, 'La presión no puede ser negativa').max(200, 'Presión fuera de rango (máx 200 PSI)'),
    temperatura_c: z.number().optional(),
    observaciones: z.string().optional()
});

export type CreateInspeccionDTO = z.infer<typeof CreateInspeccionSchema>;
