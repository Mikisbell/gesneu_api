/**
 * Almacen Validators
 */
import { z } from 'zod';

export const CreateAlmacenSchema = z.object({
    codigo: z.string().min(1).max(20),
    nombre: z.string().min(1).max(150),
    tipo: z.string().max(50).optional().default('PRINCIPAL'),
    direccion: z.string().max(200).optional(),
    activo: z.boolean().optional().default(true),
});

export const UpdateAlmacenSchema = CreateAlmacenSchema.partial();

export type CreateAlmacenInput = z.infer<typeof CreateAlmacenSchema>;
export type UpdateAlmacenInput = z.infer<typeof UpdateAlmacenSchema>;

export function validateCreateAlmacen(data: unknown) {
    return CreateAlmacenSchema.safeParse(data);
}
