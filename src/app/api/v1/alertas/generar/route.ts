import { NextRequest } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { AlertasService } from '@/lib/services/alertas.service';

const service = new AlertasService();

/**
 * @swagger
 * /api/v1/alertas/generar:
 *   post:
 *     summary: Generar alertas
 *     description: Escanea todos los neumáticos y genera alertas para condiciones críticas
 *     tags:
 *       - Alertas
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Alertas generadas exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                 data:
 *                   type: object
 *                   properties:
 *                     profundidad:
 *                       type: integer
 *                     reencauche:
 *                       type: integer
 *                     total:
 *                       type: integer
 */
export async function POST(request: NextRequest) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.NEUMATICOS_UPDATE); // Solo admin/gestor

        const result = await service.generarTodasLasAlertas();

        return ApiResponseHelper.success(result, `Se generaron ${result.total} alertas`);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
