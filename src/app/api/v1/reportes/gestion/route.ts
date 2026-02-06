
import { NextRequest } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ReportesService } from '@/lib/services/reportes.service';

const service = new ReportesService();

/**
 * @swagger
 * /api/v1/reportes/gestion:
 *   get:
 *     summary: KPIs de Gestión Avanzada (Reencauchabilidad + Scrap)
 *     tags: [Reportes]
 */
export async function GET(request: NextRequest) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.NEUMATICOS_READ);

        const data = await service.getManagementKPIs(session.user.empresa_id!);
        return ApiResponseHelper.success(data);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
