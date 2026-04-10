import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { rbacService } from '@/lib/services/rbac.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { AssignPermisoSchema } from '@/lib/validators/rbac.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';

/**
 * @swagger
 * /api/v1/admin/roles/{id}/permisos:
 *   post:
 *     summary: Asignar permiso a un rol
 *     description: Agrega un permiso existente a un rol específico
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
 *             required: [permiso_id]
 *             properties:
 *               permiso_id:
 *                 type: string
 *                 format: uuid
 *     responses:
 *       201:
 *         description: Permiso asignado al rol exitosamente
 *       404:
 *         description: Rol o permiso no encontrado
 *       409:
 *         description: El permiso ya está asignado a este rol
 */
export const POST = apiHandler(
    async (req, session, context, body) => {
        const params = await context.params;
        const id = params.id;

        const result = await rbacService.addPermisoToRol(
            session.user.empresa_id,
            session.user.id,
            id,
            body
        );
        if (!result.success) throw result.error;

        return ApiResponseHelper.created(result.data, 'Permiso asignado al rol exitosamente');
    },
    {
        permission: PERMISSIONS.SISTEMA_PERMISOS_MANAGE,
        schema: AssignPermisoSchema,
    }
);

/**
 * @swagger
 * /api/v1/admin/roles/{id}/permisos:
 *   delete:
 *     summary: Remover permiso de un rol
 *     description: Elimina la asignación de un permiso a un rol
 *     tags: [Admin - RBAC]
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         description: ID del rol
 *         schema:
 *           type: string
 *           format: uuid
 *       - name: permiso_id
 *         in: query
 *         required: true
 *         description: ID del permiso a remover
 *         schema:
 *           type: string
 *           format: uuid
 *     responses:
 *       200:
 *         description: Permiso removido del rol exitosamente
 *       404:
 *         description: Rol o asignación de permiso no encontrada
 */
export const DELETE = apiHandler(
    async (req, session, context) => {
        const params = await context.params;
        const id = params.id;
        const { searchParams } = new URL(req.url);
        const permisoId = searchParams.get('permiso_id');

        if (!permisoId) {
            return ApiResponseHelper.badRequest('El parámetro permiso_id es requerido');
        }

        const result = await rbacService.removePermisoFromRol(
            session.user.empresa_id,
            id,
            permisoId
        );
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(null, 'Permiso removido del rol exitosamente');
    },
    { permission: PERMISSIONS.SISTEMA_PERMISOS_MANAGE }
);
