import { NextRequest } from 'next/server'
import { prisma } from '@/lib/prisma'
import { ApiResponseHelper } from '@/lib/utils/api-response'
import { requireAuth, requirePermission } from '@/lib/auth/authorization'
import { PERMISSIONS } from '@/lib/auth/permissions'

/**
 * @swagger
 * /api/v1/catalogos/tipos-vehiculo:
 *   get:
 *     summary: Listar tipos de vehículo
 *     description: Obtiene una lista de todos los tipos de vehículo activos.
 *     tags: [Catálogos]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Lista de tipos recuperada exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   type: array
 *                   items:
 *                     $ref: '#/components/schemas/TipoVehiculo'
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes
 */
export async function GET(request: NextRequest) {
    try {
        // 1. Authentication
        const session = await requireAuth();

        // 2. Authorization (Usamos VEHICULOS_READ ya que es intrínseco)
        requirePermission(session, PERMISSIONS.VEHICULOS_READ);

        // 3. Business logic
        const tipos = await prisma.tipoVehiculo.findMany({
            where: {
                activo: true
            },
            orderBy: {
                nombre: 'asc'
            }
        })

        return ApiResponseHelper.success(tipos)
    } catch (error) {
        return ApiResponseHelper.handleError(error)
    }
}
