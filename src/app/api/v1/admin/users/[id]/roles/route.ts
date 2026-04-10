import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { rbacService } from '@/lib/services/rbac.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { AssignRolToUserSchema } from '@/lib/validators/rbac.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';

/**
 * @swagger
 * /api/v1/admin/users/{id}/roles:
 *   post:
 *     summary: Asignar rol a un usuario
 *     description: Asigna un rol existente a un usuario específico, con opcional fecha de expiración
 *     tags: [Admin - RBAC]
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         description: ID del usuario
 *         schema:
 *           type: string
 *           format: uuid
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [rol_id]
 *             properties:
 *               rol_id:
 *                 type: string
 *                 format: uuid
 *               es_principal:
 *                 type: boolean
 *                 description: Si este es el rol principal del usuario
 *               valido_desde:
 *                 type: string
 *                 format: date-time
 *               valido_hasta:
 *                 type: string
 *                 format: date-time
 *                 description: Fecha de expiración del rol (null = sin expiración)
 *     responses:
 *       201:
 *         description: Rol asignado al usuario exitosamente
 *       404:
 *         description: Rol o usuario no encontrado
 *       409:
 *         description: El usuario ya tiene este rol asignado
 */
export const POST = apiHandler(
    async (req, session, context, body) => {
        const params = await context.params;
        const id = params.id;

        const result = await rbacService.assignRolToUser(
            session.user.empresa_id,
            session.user.id,
            id,
            body
        );
        if (!result.success) throw result.error;

        return ApiResponseHelper.created(result.data, 'Rol asignado al usuario exitosamente');
    },
    {
        permission: PERMISSIONS.SISTEMA_ROLES_MANAGE,
        schema: AssignRolToUserSchema,
    }
);

/**
 * @swagger
 * /api/v1/admin/users/{id}/roles:
 *   delete:
 *     summary: Remover rol de un usuario
 *     description: Elimina la asignación de un rol a un usuario
 *     tags: [Admin - RBAC]
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         description: ID del usuario
 *         schema:
 *           type: string
 *           format: uuid
 *       - name: rol_id
 *         in: query
 *         required: true
 *         description: ID del rol a remover
 *         schema:
 *           type: string
 *           format: uuid
 *     responses:
 *       200:
 *         description: Rol removido del usuario exitosamente
 *       404:
 *         description: Usuario o asignación de rol no encontrada
 */
export const DELETE = apiHandler(
    async (req, session, context) => {
        const params = await context.params;
        const id = params.id;
        const { searchParams } = new URL(req.url);
        const rolId = searchParams.get('rol_id');

        if (!rolId) {
            return ApiResponseHelper.badRequest('El parámetro rol_id es requerido');
        }

        const result = await rbacService.removeRolFromUser(
            session.user.empresa_id,
            id,
            rolId
        );
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(null, 'Rol removido del usuario exitosamente');
    },
    { permission: PERMISSIONS.SISTEMA_ROLES_MANAGE }
);
