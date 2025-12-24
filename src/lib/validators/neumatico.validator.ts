import { z } from 'zod';
import { EstadoNeumaticoEnum } from '@prisma/client';

export const CreateNeumaticoSchema = z.object({
    numero_serie: z.string().min(3).max(50),
    modelo_id: z.string().uuid(),
    dot: z.string().regex(/^\d{4}$/, 'DOT debe ser 4 dígitos (SSAA)'),
    estado_actual: z.nativeEnum(EstadoNeumaticoEnum).default(EstadoNeumaticoEnum.EN_STOCK),
    ubicacion_almacen_id: z.string().uuid().optional(),
    ubicacion_vehiculo_id: z.string().uuid().optional(),
    ubicacion_posicion_id: z.string().uuid().optional(),
    profundidad_inicial_mm: z.number().min(0).max(30),
    condicion: z.enum(['NUEVO', 'USADO']).default('NUEVO'),
    precio_compra: z.number().positive().optional(),
    fecha_compra: z.string().datetime().optional()
});

export type CreateNeumaticoInput = z.infer<typeof CreateNeumaticoSchema>;
