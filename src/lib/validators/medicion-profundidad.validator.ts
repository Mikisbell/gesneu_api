import { z } from 'zod';

export const CreateMedicionProfundidadSchema = z.object({
    neumatico_id: z.string().uuid('ID de neumático inválido'),
    profundidad_int: z.number().min(0, 'La profundidad interior no puede ser negativa').max(50, 'Profundidad fuera de rango'),
    profundidad_cen: z.number().min(0, 'La profundidad centro no puede ser negativa').max(50, 'Profundidad fuera de rango'),
    profundidad_ext: z.number().min(0, 'La profundidad exterior no puede ser negativa').max(50, 'Profundidad fuera de rango'),
    kilometraje: z.number().min(0, 'El kilometraje no puede ser negativo').optional(),
    observaciones: z.string().max(1000, 'Observaciones demasiado largas').optional(),
    evento_id: z.string().uuid('ID de evento inválido').optional(),
});

export type CreateMedicionProfundidadDTO = z.infer<typeof CreateMedicionProfundidadSchema>;

export const formatZodErrors = (error: z.ZodError): string[] => {
    return error.errors.map((err) => {
        const path = err.path.join('.');
        return `${path}: ${err.message}`;
    });
};

export const getFirstZodError = (error: z.ZodError): string => {
    return error.errors[0]?.message ?? 'Error de validación';
};
