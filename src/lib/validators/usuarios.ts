import { z } from 'zod';

// Definimos los roles permitidos según el Schema
const RolesEnum = z.enum(['ADMIN', 'GESTOR', 'OPERADOR']);

export const createUsuarioSchema = z.object({
    username: z.string().min(3, 'El nombre de usuario debe tener al menos 3 caracteres').max(50),
    nombre_completo: z.string().min(3, 'El nombre completo debe tener al menos 3 caracteres').max(200),
    email: z.string().email('Email inválido').max(100),
    password: z.string().min(6, 'La contraseña debe tener al menos 6 caracteres'),
    // Ahora es un solo Enum, no un array de UUIDs
    rol: RolesEnum.default('OPERADOR'),
});

export const updateUsuarioSchema = z.object({
    nombre_completo: z.string().min(3).max(200).optional(),
    email: z.string().email().max(100).optional(),
    password: z.string().min(6).optional(),
    rol: RolesEnum.optional(),
    activo: z.boolean().optional(),
});

export type CreateUsuarioDTO = z.infer<typeof createUsuarioSchema>;
export type UpdateUsuarioDTO = z.infer<typeof updateUsuarioSchema>;
