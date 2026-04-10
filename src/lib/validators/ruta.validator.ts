import { z } from 'zod';

export const CreateRutaSchema = z.object({
    nombre: z.string().min(1).max(100, 'El nombre no puede exceder 100 caracteres'),
    origen: z.string().max(100).optional(),
    destino: z.string().max(100).optional(),
    distancia_km: z.coerce.number().nonnegative('La distancia no puede ser negativa').default(0),
    tipo_ruta_id: z.string().uuid('ID de tipo de ruta debe ser un UUID válido'),
    activo: z.boolean().optional().default(true),
});

export const AssignRutaSchema = z.object({
    vehiculo_id: z.string().uuid('ID de vehículo debe ser un UUID válido'),
});

export const UpdateRutaSchema = CreateRutaSchema.partial();

export type CreateRutaInput = z.infer<typeof CreateRutaSchema>;
export type AssignRutaInput = z.infer<typeof AssignRutaSchema>;
export type UpdateRutaInput = z.infer<typeof UpdateRutaSchema>;
