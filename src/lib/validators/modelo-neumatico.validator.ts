import { z } from 'zod';

export const CreateModeloNeumaticoSchema = z.object({
    fabricante_id: z.string().uuid("ID de fabricante inválido"),
    nombre: z.string().min(2, "El nombre debe tener al menos 2 caracteres"),
    medida: z.string().min(3, "Medida requerida (ej: 295/80R22.5)"),
    profundidad_original_mm: z.number().min(1, "Profundidad debe ser mayor a 1mm"),
    profundidad_minima_retiro_mm: z.number().min(0.5, "Profundidad de retiro inválida").optional().default(3.0),
    presion_recomendada_psi: z.number().min(0).optional(),
    patron_dibujo: z.string().optional(),
    tipo_servicio: z.string().optional(),
    indice_carga: z.string().max(10).optional(),
    indice_velocidad: z.string().max(5).optional(),
    permite_reencauche: z.boolean().optional().default(true),
    reencauches_maximos: z.number().min(0).optional().default(3),
});

export const UpdateModeloNeumaticoSchema = CreateModeloNeumaticoSchema.partial().extend({
    activo: z.boolean().optional(),
});
