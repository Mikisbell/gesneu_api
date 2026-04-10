import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { rbacService } from '@/lib/services/rbac.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { UpdateRolSchema } from '@/lib/validators/rbac.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { DYNAMIC_RBAC_ENABLED, featureDisabledResponse } from '@/lib/features';

/**
 * @swagger
 * /api/v1/admin/roles/{id}:
 *   get:
 *     summary: Obtener rol por ID
 *     description: Retorna los detalles completos de un rol, incluyendo permisos asignados y conteo de usuarios
 *     tags: [Admin - RBAC]
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         description: ID del rol
 *         schema:
 *           type: string
 *           format: uuid
 *     responses:
 *       200:
 *         description: Rol encontrado
 *       404:
 *         description: Rol no encontrado
 */
const _GET = apiHandler(
    async (req, session, context) => {
        const params = await context.params;
        const id = params.id;

        const result = await rbacService.getRolById(session.user.empresa_id, id);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data);
    },
    { permission: PERMISSIONS.SISTEMA_ROLES_MANAGE }
);

/**
 * @swagger
 * /api/v1/admin/roles/{id}:
 *   put:
 *     summary: Actualizar rol
 *     description: Actualiza los datos de un rol existente (no se puede modificar nombre de roles del sistema)
 *     tags: [Admin - RBAC]
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         description: ID del rol
 *         schema:
 *           type: string
 *           format: uuid
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               nombre:
 *                 type: string
 *                 maxLength: 50
 *               descripcion:
 *                 type: string
 *                 maxLength: 500
 *               activo:
 *                 type: boolean
 *     responses:
 *       200:
 *         description: Rol actualizado exitosamente
 *       400:
 *         description: No se puede modificar el nombre de un rol del sistema
 *       404:
 *         description: Rol no encontrado
 *       409:
 *         description: Ya existe un rol con este nombre
 */
const _PUT = apiHandler(
    async (req, session, context, body) => {
        const params = await context.params;
        const id = params.id;

        const result = await rbacService.updateRol(
            session.user.empresa_id,
            session.user.id,
            id,
            body
        );
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data, 'Rol actualizado exitosamente');
    },
    {
        permission: PERMISSIONS.SISTEMA_ROLES_MANAGE,
        schema: UpdateRolSchema,
    }
);

/**
 * @swagger
 * /api/v1/admin/roles/{id}:
 *   delete:
 *     summary: Eliminar rol
 *     description: Desactiva un rol (solo si no es del sistema y no tiene usuarios asignados)
 *     tags: [Admin - RBAC]
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         description: ID del rol
 *         schema:
 *           type: string
 *           format: uuid
 *     responses:
 *       200:
 *         description: Rol eliminado exitosamente
 *       400:
 *         description: No se pueden eliminar roles del sistema o tiene usuarios asignados
 *       404:
 *         description: Rol no encontrado
 */
const _DELETE = apiHandler(
    async (req, session, context) => {
        const params = await context.params;
        const id = params.id;

        const result = await rbacService.deleteRol(session.user.empresa_id, id);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(null, 'Rol eliminado exitosamente');
    },
    { permission: PERMISSIONS.SISTEMA_ROLES_MANAGE }
);

function rbacGuard(handler: typeof _GET) {
    return async (...args: Parameters<typeof _GET>) => {
        if (!DYNAMIC_RBAC_ENABLED) {
            return featureDisabledResponse(
                'RBAC dinámico',
                'Las tablas dinámicas Rol/Permiso no afectan la autenticación real en single-tenant. Feature disponible cuando se active multi-tenant.'
            );
        }
        return handler(...args);
    };
}

export const GET = rbacGuard(_GET);
export const PUT = rbacGuard(_PUT);
export const DELETE = rbacGuard(_DELETE);
