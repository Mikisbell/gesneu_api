import { NextRequest } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { DashboardService } from '@/lib/services/dashboard.service';

const service = new DashboardService();

/**
 * @swagger
 * /api/v1/dashboard/desechos:
 *   get:
 *     summary: Reporte de desechos
 *     description: Análisis de neumáticos desechados por motivo y por mes
 *     tags:
 *       - Dashboard
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Reporte de desechos
 */
export async function GET(request: NextRequest) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.NEUMATICOS_READ);

        const reporte = await service.getReporteDesechos();
        return ApiResponseHelper.success(reporte);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
