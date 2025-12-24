import { NextRequest } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { DashboardService } from '@/lib/services/dashboard.service';

const service = new DashboardService();

/**
 * @swagger
 * /api/v1/dashboard/rendimiento:
 *   get:
 *     summary: Reporte de rendimiento
 *     description: Top mejores y peores neumáticos por CPK
 *     tags:
 *       - Dashboard
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 10
 *         description: Cantidad de neumáticos a mostrar en cada lista
 *     responses:
 *       200:
 *         description: Reporte de rendimiento con top mejores/peores
 */
export async function GET(request: NextRequest) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.NEUMATICOS_READ);

        const { searchParams } = new URL(request.url);
        const limit = parseInt(searchParams.get('limit') || '10');

        const reporte = await service.getReporteRendimiento(limit);
        return ApiResponseHelper.success(reporte);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
