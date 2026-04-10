import { z } from 'zod';

export const CreateGarantiaSchema = z.object({
    neumatico_id: z.string().uuid('ID de neumático debe ser un UUID válido'),
    proveedor_id: z.string().uuid('ID de proveedor debe ser un UUID válido').optional(),
    numero_garantia: z.string().max(50).optional(),
    fecha_inicio: z.coerce.date(),
    fecha_fin: z.coerce.date(),
    kilometraje_max: z.number().positive('El kilometraje máximo debe ser mayor a 0').optional(),
    profundidad_min: z.number().positive('La profundidad mínima debe ser mayor a 0').optional(),
    condiciones: z.string().max(5000, 'Las condiciones no pueden exceder 5000 caracteres').optional(),
}).refine((data) => data.fecha_fin > data.fecha_inicio, {
    message: 'La fecha de fin debe ser posterior a la fecha de inicio',
    path: ['fecha_fin'],
});

export const ClaimGarantiaSchema = z.object({
    motivo_reclamo: z.string().min(10, 'El motivo del reclamo debe tener al menos 10 caracteres').max(5000),
    fecha_reclamo: z.coerce.date().optional(),
});

export const ResolveGarantiaSchema = z.object({
    resolucion: z.string().min(10, 'La resolución debe tener al menos 10 caracteres').max(5000),
    monto_reembolso: z.number().nonnegative('El monto de reembolso no puede ser negativo').optional(),
});

export const UpdateGarantiaSchema = z.object({
    neumatico_id: z.string().uuid().optional(),
    proveedor_id: z.string().uuid().optional(),
    numero_garantia: z.string().max(50).optional(),
    fecha_inicio: z.coerce.date().optional(),
    fecha_fin: z.coerce.date().optional(),
    kilometraje_max: z.number().positive().optional(),
    profundidad_min: z.number().positive().optional(),
    condiciones: z.string().max(5000).optional(),
}).refine((data) => {
    if (data.fecha_inicio && data.fecha_fin) {
        return data.fecha_fin > data.fecha_inicio;
    }
    return true;
}, {
    message: 'La fecha de fin debe ser posterior a la fecha de inicio',
    path: ['fecha_fin'],
});

export type CreateGarantiaInput = z.infer<typeof CreateGarantiaSchema>;
export type ClaimGarantiaInput = z.infer<typeof ClaimGarantiaSchema>;
export type ResolveGarantiaInput = z.infer<typeof ResolveGarantiaSchema>;
export type UpdateGarantiaInput = z.infer<typeof UpdateGarantiaSchema>;
