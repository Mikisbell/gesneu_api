import { z } from 'zod';

/**
 * Schema para crear un registro en la bitacora de mantenimiento
 */
export const CreateBitacoraMantenimientoSchema = z.object({
    vehiculo_id: z.string().uuid('ID de vehiculo debe ser un UUID valido'),
    tipo_operacion: z.enum([
        'MANTENIMIENTO_PREVENTIVO',
        'MANTENIMIENTO_CORRECTIVO',
        'INSPECCION_PROGRAMADA',
        'INSPECCION_ALEATORIA',
        'LAVADO',
        'ALINEACION',
        'BALANCEO',
        'CAMBIO_ACEITE',
        'OTRO'
    ], {
        message: 'Tipo de operacion debe ser uno de los valores permitidos'
    }).optional(),
    // Accept 'tipo' as alias for tipo_operacion with shorthand mapping
    tipo: z.enum([
        'PREVENTIVO',
        'CORRECTIVO',
        'INSPECCION',
        'OTRO'
    ]).optional(),
    fecha_programada: z.coerce.date().optional(),
    fecha_realizada: z.coerce.date().optional(),
    fecha_mantenimiento: z.coerce.date().optional(),
    kilometraje: z.number().positive('El kilometraje debe ser mayor a 0').optional(),
    horometro: z.number().positive('El horometro debe ser mayor a 0').optional(),
    costo: z.number().nonnegative('El costo debe ser un numero no negativo').optional(),
    proveedor_id: z.string().uuid('ID de proveedor debe ser un UUID valido').optional(),
    proveedor: z.string().optional(),
    responsable: z.string().max(200, 'El responsable no puede exceder 200 caracteres').optional(),
    observaciones: z.string().max(5000, 'Las observaciones no pueden exceder 5000 caracteres').optional(),
    descripcion: z.string().max(5000).optional(),
    evidencia_url: z.string().url('La evidencia URL debe ser una URL valida').optional()
}).transform((data) => {
    // Map tipo shorthand to tipo_operacion
    const tipoMap: Record<string, string> = {
        'PREVENTIVO': 'MANTENIMIENTO_PREVENTIVO',
        'CORRECTIVO': 'MANTENIMIENTO_CORRECTIVO',
        'INSPECCION': 'INSPECCION_PROGRAMADA',
    };
    if (!data.tipo_operacion && data.tipo && tipoMap[data.tipo]) {
        data.tipo_operacion = tipoMap[data.tipo] as any;
    }
    // Map fecha_mantenimiento to fecha_realizada
    if (!data.fecha_realizada && data.fecha_mantenimiento) {
        data.fecha_realizada = data.fecha_mantenimiento;
    }
    // Map descripcion to observaciones if observaciones not provided
    if (!data.observaciones && data.descripcion) {
        data.observaciones = data.descripcion;
    }
    return data;
});

/**
 * Schema para actualizar un registro en la bitacora de mantenimiento
 */
export const UpdateBitacoraMantenimientoSchema = z.object({
    tipo_operacion: z.enum([
        'MANTENIMIENTO_PREVENTIVO',
        'MANTENIMIENTO_CORRECTIVO',
        'INSPECCION_PROGRAMADA',
        'INSPECCION_ALEATORIA',
        'LAVADO',
        'ALINEACION',
        'BALANCEO',
        'CAMBIO_ACEITE',
        'OTRO'
    ]).optional(),
    fecha_programada: z.coerce.date().optional(),
    fecha_realizada: z.coerce.date().optional(),
    kilometraje: z.number().positive().optional(),
    horometro: z.number().positive().optional(),
    costo: z.number().nonnegative().optional(),
    proveedor_id: z.string().uuid().optional(),
    responsable: z.string().max(200).optional(),
    observaciones: z.string().max(5000).optional(),
    evidencia_url: z.string().url().optional()
});

export type CreateBitacoraMantenimientoInput = z.infer<typeof CreateBitacoraMantenimientoSchema>;
export type UpdateBitacoraMantenimientoInput = z.infer<typeof UpdateBitacoraMantenimientoSchema>;
