
import { NextRequest } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ForecastService } from '@/lib/services/forecast.service';

/**
 * @swagger
 * /api/v1/reportes/forecast:
 *   get:
 *     summary: Proyección de compras (90 días)
 *     description: Retorna lista de neumáticos que alcanzarán su límite de vida útil en el periodo especificado, agrupados por medida.
 *     tags: [Reportes, Compras]
 */
export async function GET(request: NextRequest) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.REPORTES_RENDIMIENTO);

        const { searchParams } = new URL(request.url);
        const days = Number(searchParams.get('days')) || 90;

        const data = await ForecastService.generatePurchaseForecast(session.user.empresa_id, days);

        return ApiResponseHelper.success(data);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
