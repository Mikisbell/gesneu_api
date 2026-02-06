import { z } from 'zod';
import { TipoProveedorEnum } from '@/types/domain/proveedor.types';

export const CreateProveedorSchema = z.object({
    nombre: z.string().min(1, 'El nombre es requerido').max(100),
    ruc: z.string().max(20).optional().nullable(), // RUC optional for international/informal? Usually required for business. RF37 implies management. Let's make it optional but validated format if present.
    // RF37 doesn't specify RUC format strictly, but usually 11 digits in Peru.
    tipo: z.nativeEnum(TipoProveedorEnum, {
        message: 'Tipo de proveedor inválido'
    }),
    direccion: z.string().max(200).optional().nullable(),
    telefono: z.string().max(20).optional().nullable(),
    email: z.string().email().optional().nullable().or(z.literal('')),
    contacto_principal: z.string().max(100).optional().nullable(),
    activo: z.boolean().optional().default(true),
});

export const UpdateProveedorSchema = CreateProveedorSchema.partial();

export type CreateProveedorInput = z.infer<typeof CreateProveedorSchema>;
