
import { z } from 'zod';

export const AdminPaginationSchema = z.object({
    limit: z.coerce.number().min(1).max(100).default(50),
    offset: z.coerce.number().min(0).default(0),
});

export const AdminUserSearchSchema = AdminPaginationSchema.extend({
    search: z.string().optional(),
    empresa_id: z.string().uuid().optional(),
    rol: z.enum(['SUPERADMIN', 'ADMIN', 'ADMINISTRADOR', 'GESTOR', 'OPERADOR', 'CONSULTOR']).optional(),
    activo: z.enum(['true', 'false']).transform(val => val === 'true').optional(),
});

export const AdminAuditSearchSchema = AdminPaginationSchema.extend({
    search: z.string().optional(),
    operacion: z.enum(['INSERT', 'UPDATE', 'DELETE']).optional(),
    tabla: z.string().optional(),
    usuario_id: z.string().uuid().optional(),
    empresa_id: z.string().uuid().optional(),
    fecha_desde: z.string().datetime().optional(),
    fecha_hasta: z.string().datetime().optional(),
});

export const AdminWebhookSearchSchema = AdminPaginationSchema.extend({
    empresa_id: z.string().uuid().optional(),
    exitoso: z.enum(['true', 'false']).transform(val => val === 'true').optional(),
});
