
import { NextRequest } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ReportesService } from '@/lib/services/reportes.service';

const service = new ReportesService();

/**
 * @swagger
 * /api/v1/reportes/rendimiento:
 *   get:
 *     summary: Reporte detallado de rendimiento de flota (DET_REND)
 *     tags: [Reportes]
 */
export async function GET(request: NextRequest) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.NEUMATICOS_READ); // O REPORTES_READ

        const metrics = await service.getFleetPerformance(session.user.empresa_id!);
        return ApiResponseHelper.success(metrics);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
