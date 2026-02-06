
import { NextRequest } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ReportesService } from '@/lib/services/reportes.service';

const service = new ReportesService();

/**
 * @swagger
 * /api/v1/reportes/historial-cambios:
 *   get:
 *     summary: Historial de cambios de neumáticos (Side-by-Side)
 *     tags: [Reportes]
 */
export async function GET(request: NextRequest) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.NEUMATICOS_READ);

        const { searchParams } = new URL(request.url);
        const vehiculoId = searchParams.get('vehiculo_id') || undefined;

        const history = await service.getChangeHistory(session.user.empresa_id!, vehiculoId);
        return ApiResponseHelper.success(history);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
