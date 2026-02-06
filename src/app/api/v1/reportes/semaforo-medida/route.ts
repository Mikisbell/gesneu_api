import { NextRequest } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ReportesService } from '@/lib/services/reportes.service';

const service = new ReportesService();

/**
 * @swagger
 * /api/v1/reportes/semaforo-medida:
 *   get:
 *     summary: Matriz Semáforo por Medida con distribución por eje
 *     tags: [Reportes]
 *     parameters:
 *       - in: query
 *         name: medida
 *         description: Filtrar por medida de neumático (ej: 295/80R22.5)
 *         schema:
 *           type: string
 */
export async function GET(request: NextRequest) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.NEUMATICOS_READ);

        const { searchParams } = new URL(request.url);
        const medida = searchParams.get('medida') || undefined;

        const data = await service.getSemaforoByMedida(session.user.empresa_id!, medida);
        return ApiResponseHelper.success(data);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
