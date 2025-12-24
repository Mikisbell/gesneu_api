import { NextRequest } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ReportesService } from '@/lib/services/reportes.service';

const service = new ReportesService();

/**
 * @swagger
 * /api/v1/reportes/desgaste:
 *   get:
 *     summary: Calcular Desgaste Promedio
 *     description: Calcula el desgaste promedio de un neumático en mm por cada 1000 km recorridos.
 *     tags:
 *       - Reportes
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: neumatico_id
 *         required: true
 *         schema:
 *           type: string
 *           format: uuid
 *         description: ID del neumático
 *     responses:
 *       200:
 *         description: Métricas de desgaste calculadas exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 data:
 *                   $ref: '#/components/schemas/WearRateMetricsDTO'
 *       400:
 *         description: ID de neumático faltante o inválido
 *       404:
 *         description: Neumático no encontrado
 */
export async function GET(request: NextRequest) {
    try {
        // 1. Authentication
        const session = await requireAuth();

        // 2. Authorization
        requirePermission(session, PERMISSIONS.NEUMATICOS_READ);

        // 3. Validation
        const { searchParams } = new URL(request.url);
        const neumaticoId = searchParams.get('neumatico_id');

        if (!neumaticoId) {
            return ApiResponseHelper.error('El parámetro neumatico_id es requerido', 400);
        }

        // 4. Service Call
        const metrics = await service.getDesgastePromedio(neumaticoId);

        return ApiResponseHelper.success(metrics);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
