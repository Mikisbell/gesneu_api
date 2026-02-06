
import { z } from 'zod';

export const CreateTipoVehiculoSchema = z.object({
    nombre: z.string().min(2, "El nombre debe tener al menos 2 caracteres"),
    descripcion: z.string().optional(),
    activo: z.boolean().optional().default(true),
});

export const UpdateTipoVehiculoSchema = CreateTipoVehiculoSchema.partial();
