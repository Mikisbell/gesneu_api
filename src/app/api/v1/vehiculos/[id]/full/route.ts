import { NextRequest } from 'next/server'
import { VehiculoService } from '@/lib/services/vehiculo.service'
import { ApiResponseHelper } from '@/lib/utils/api-response'
import { requireAuth, requirePermission } from '@/lib/auth/authorization'
import { PERMISSIONS } from '@/lib/auth/permissions'

const service = new VehiculoService()

/**
 * @swagger
 * /api/v1/vehiculos/{id}/full:
 *   get:
 *     summary: Obtener vehículo con configuración completa
 *     description: Obtiene los detalles de un vehículo incluyendo configuración de ejes y neumáticos instalados.
 *     tags: [Vehículos]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *           format: uuid
 *         description: ID del vehículo
 *     responses:
 *       200:
 *         description: Detalles completos del vehículo
 *       404:
 *         description: Vehículo no encontrado
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes
 */
export async function GET(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        // 1. Authentication
        const session = await requireAuth();

        // 2. Authorization
        requirePermission(session, PERMISSIONS.VEHICULOS_READ);

        // 3. Business logic
        const vehiculo = await service.getByIdWithFullConfig((await params).id)
        if (!vehiculo) {
            return ApiResponseHelper.notFound()
        }
        return ApiResponseHelper.success(vehiculo)
    } catch (error) {
        return ApiResponseHelper.handleError(error)
    }
}
