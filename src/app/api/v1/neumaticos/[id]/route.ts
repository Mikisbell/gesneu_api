import { neumaticoService } from '@/lib/services/neumatico.service';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { UpdateNeumaticoSchema } from '@/lib/validators/neumatico.validator';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { apiHandler } from '@/lib/utils/api-handler';

/**
 * @swagger
 * /api/v1/neumaticos/{id}:
 *   get:
 *     summary: Obtener neumático
 */
export const GET = apiHandler(
    async (req, session, context) => {
        const params = await context.params;
        const id = params.id;
        const result = await neumaticoService.getById(session.user!.empresa_id, id);

        if (!result.success) throw result.error;
        return ApiResponseHelper.success(result.data);
    },
    { permission: PERMISSIONS.NEUMATICOS_READ }
);

/**
 * @swagger
 * /api/v1/neumaticos/{id}:
 *   put:
 *     summary: Actualizar neumático
 */
export const PUT = apiHandler(
    async (req, session, context, body) => {
        const params = await context.params;
        const id = params.id;
        const result = await neumaticoService.update(
            session.user!.empresa_id,
            id,
            body,
            session.user!.id
        );

        if (!result.success) throw result.error;
        return ApiResponseHelper.success(result.data, 'Neumático actualizado exitosamente');
    },
    {
        permission: PERMISSIONS.NEUMATICOS_UPDATE,
        schema: UpdateNeumaticoSchema
    }
);

/**
 * @swagger
 * /api/v1/neumaticos/{id}:
 *   delete:
 *     summary: Eliminar neumático
 */
export const DELETE = apiHandler(
    async (req, session, context) => {
        const params = await context.params;
        const id = params.id;
        const result = await neumaticoService.delete(session.user!.empresa_id, id);

        if (!result.success) throw result.error;
        return ApiResponseHelper.success(null, 'Neumático eliminado exitosamente');
    },
    { permission: PERMISSIONS.NEUMATICOS_DELETE }
);
