import { NextRequest } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { AlertasService } from '@/lib/services/alertas.service';

const service = new AlertasService();

/**
 * @swagger
 * /api/v1/alertas/{id}:
 *   patch:
 *     summary: Actualizar estado de alerta
 *     description: Marca una alerta como leída o resuelta
 *     tags:
 *       - Alertas
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *           format: uuid
 *     requestBody:
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               leida:
 *                 type: boolean
 *               resuelta:
 *                 type: boolean
 *     responses:
 *       200:
 *         description: Alerta actualizada
 */
export async function PATCH(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.NEUMATICOS_UPDATE);

        const { id } = await params;
        const body = await request.json();

        let alerta;
        if (body.resuelta === true) {
            alerta = await service.resolver(id);
        } else if (body.leida === true) {
            alerta = await service.marcarComoLeida(id);
        } else {
            return ApiResponseHelper.error('Debe especificar leida o resuelta', 400);
        }

        return ApiResponseHelper.success(alerta);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
