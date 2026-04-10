import { z } from 'zod';

export const CreateInventarioParamSchema = z.object({
    almacen_id: z.string().uuid('ID de almacén debe ser un UUID válido'),
    modelo_id: z.string().uuid('ID de modelo debe ser un UUID válido').optional(),
    stock_minimo: z.number().int().nonnegative('El stock mínimo no puede ser negativo'),
    stock_maximo: z.number().int().positive('El stock máximo debe ser mayor a 0').optional(),
    punto_reorden: z.number().int().nonnegative('El punto de reorden no puede ser negativo').optional(),
    cantidad_reorden: z.number().int().positive('La cantidad de reorden debe ser mayor a 0').optional(),
    lead_time_dias: z.number().int().positive('El lead time debe ser mayor a 0').optional(),
    activo: z.boolean().optional().default(true),
});

export const TransferenciaStockSchema = z.object({
    neumatico_id: z.string().uuid('ID de neumático debe ser un UUID válido'),
    almacen_origen_id: z.string().uuid('ID de almacén origen debe ser un UUID válido'),
    almacen_destino_id: z.string().uuid('ID de almacén destino debe ser un UUID válido'),
    observaciones: z.string().max(1000, 'Las observaciones no pueden exceder 1000 caracteres').optional(),
    fecha_evento: z.coerce.date().optional(),
}).refine((data) => data.almacen_origen_id !== data.almacen_destino_id, {
    message: 'El almacén origen y destino deben ser diferentes',
});

export const ReorderPointSchema = z.object({
    almacen_id: z.string().uuid('ID de almacén debe ser un UUID válido').optional(),
    modelo_id: z.string().uuid('ID de modelo debe ser un UUID válido').optional(),
    stock_minimo: z.number().int().nonnegative().optional(),
    stock_maximo: z.number().int().positive().optional(),
    punto_reorden: z.number().int().nonnegative().optional(),
    cantidad_reorden: z.number().int().positive().optional(),
    lead_time_dias: z.number().int().positive().optional(),
}).refine((data) => data.almacen_id || data.modelo_id, {
    message: 'Debe especificar al menos almacen_id o modelo_id',
});

export type CreateInventarioParamInput = z.infer<typeof CreateInventarioParamSchema>;
export type TransferenciaStockInput = z.infer<typeof TransferenciaStockSchema>;
export type ReorderPointInput = z.infer<typeof ReorderPointSchema>;
