import { NextRequest } from 'next/server'
import { VehiculoService } from '@/lib/services/vehiculo.service'
import { ApiResponseHelper } from '@/lib/utils/api-response'
import { requireAuth, requirePermission } from '@/lib/auth/authorization'
import { PERMISSIONS } from '@/lib/auth/permissions'
import { asVehiculoId } from '@/types/branded.types'

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
        // 3. Business logic
        const id = asVehiculoId((await params).id);

        if (!session.user.empresa_id) {
            return ApiResponseHelper.error('Usuario no tiene empresa asignada', 403);
        }

        const result = await service.getByIdWithFullConfig(session.user.empresa_id, id);

        if (!result.success) {
            return ApiResponseHelper.error(result.error.message, result.error.statusCode);
        }

        return ApiResponseHelper.success(result.data);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
