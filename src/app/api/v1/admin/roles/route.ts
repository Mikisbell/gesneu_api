import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { rbacService } from '@/lib/services/rbac.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { CreateRolSchema } from '@/lib/validators/rbac.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { DYNAMIC_RBAC_ENABLED, featureDisabledResponse } from '@/lib/features';

/**
 * @swagger
 * /api/v1/admin/roles:
 *   get:
 *     summary: Listar roles del sistema
 *     description: Retorna todos los roles, con conteo de usuarios y permisos asignados
 *     tags: [Admin - RBAC]
 *     parameters:
 *       - name: activo
 *         in: query
 *         description: Filtrar por estado activo
 *         schema:
 *           type: boolean
 *       - name: includePermisos
 *         in: query
 *         description: Incluir lista detallada de permisos
 *         schema:
 *           type: boolean
 *     responses:
 *       200:
 *         description: Lista de roles obtenida exitosamente
 */
const _GET = apiHandler(
    async (req, session) => {
        const { searchParams } = new URL(req.url);

        const filters = {
            activo: searchParams.has('activo') ? searchParams.get('activo') === 'true' : undefined,
            includePermisos: searchParams.has('includePermisos') ? searchParams.get('includePermisos') === 'true' : false,
        };

        const result = await rbacService.getRoles(session.user.empresa_id, filters);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data);
    },
    { permission: PERMISSIONS.SISTEMA_ROLES_MANAGE }
);

/**
 * @swagger
 * /api/v1/admin/roles:
 *   post:
 *     summary: Crear un nuevo rol
 *     description: Crea un rol personalizado con nombre, descripción y estado
 *     tags: [Admin - RBAC]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [nombre]
 *             properties:
 *               nombre:
 *                 type: string
 *                 maxLength: 50
 *               descripcion:
 *                 type: string
 *                 maxLength: 500
 *               es_sistema:
 *                 type: boolean
 *               activo:
 *                 type: boolean
 *     responses:
 *       201:
 *         description: Rol creado exitosamente
 *       409:
 *         description: Ya existe un rol con este nombre
 */
const _POST = apiHandler(
    async (req, session, _, body) => {
        const result = await rbacService.createRol(
            session.user.empresa_id,
            session.user.id,
            body
        );
        if (!result.success) throw result.error;

        return ApiResponseHelper.created(result.data, 'Rol creado exitosamente');
    },
    {
        permission: PERMISSIONS.SISTEMA_ROLES_MANAGE,
        schema: CreateRolSchema,
    }
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
export const POST = rbacGuard(_POST);
