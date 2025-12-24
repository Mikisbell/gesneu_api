import { NextRequest } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { auth } from '@/lib/auth/auth';
import { SYSTEM_ROLES } from '@/lib/auth/permissions';

/**
 * @swagger
 * /api/v1/auth/me:
 *   get:
 *     summary: Obtener usuario actual y sus permisos
 *     description: Retorna información del usuario logueado incluyendo su rol y lista de permisos
 *     tags:
 *       - Auth
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Datos del usuario y permisos
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 user:
 *                   type: object
 *                   properties:
 *                     id:
 *                       type: string
 *                     username:
 *                       type: string
 *                     email:
 *                       type: string
 *                     rol:
 *                       type: string
 *                 permissions:
 *                   type: array
 *                   items:
 *                     type: string
 *       401:
 *         description: No autenticado
 */
export async function GET(request: NextRequest) {
    try {
        const session = await auth();

        if (!session?.user) {
            return ApiResponseHelper.unauthorized('No autorizado');
        }

        const user = session.user as any;
        const rol = user.rol || 'OPERADOR';

        // Obtener permisos según rol
        const roleConfig = SYSTEM_ROLES[rol as keyof typeof SYSTEM_ROLES];
        const permissions = (roleConfig?.permisos || []) as string[];

        // Helper para verificar permiso
        const can = (perm: string) => permissions.includes(perm);

        return ApiResponseHelper.success({
            user: {
                id: user.id,
                username: user.username || user.name,
                email: user.email,
                rol: rol,
                nombre_completo: user.nombre_completo || user.name
            },
            permissions: permissions,
            // Helper flags para UI
            can: {
                // Catálogos
                createProveedores: can('catalogos:proveedores:create'),
                deleteProveedores: can('catalogos:proveedores:delete'),
                // Vehículos
                createVehiculos: can('vehiculos:create'),
                deleteVehiculos: can('vehiculos:delete'),
                configVehiculos: can('vehiculos:configurar'),
                // Neumáticos
                createNeumaticos: can('neumaticos:create'),
                deleteNeumaticos: can('neumaticos:delete'),
                // Operaciones
                montaje: can('neumaticos:evento:instalacion'),
                desmontaje: can('neumaticos:evento:desmontaje'),
                desecho: can('neumaticos:evento:desecho'),
                // Sistema
                manageUsers: can('sistema:usuarios:create'),
                viewAudit: can('sistema:auditoria:read'),
                // Reportes
                viewDashboard: can('reportes:dashboard'),
                viewReportes: can('reportes:rendimiento')
            }
        });
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
