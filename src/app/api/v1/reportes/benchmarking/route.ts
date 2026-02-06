
import { NextRequest } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { BenchmarkingService } from '@/lib/services/benchmarking.service';

/**
 * @swagger
 * /api/v1/reportes/benchmarking:
 *   get:
 *     summary: Obtener reporte comparativo de marcas y modelos
 *     description: Retorna métricas de rendimiento (CPK, Kilometraje, Reencauchabilidad) agrupadas por Marca y Modelo, basado en neumáticos desechados/vendidos.
 *     tags: [Reportes]
 *     security:
 *       - bearerAuth: []
 */
export async function GET(request: NextRequest) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.REPORTES_RENDIMIENTO);

        const data = await BenchmarkingService.getBrandPerformance(session.user.empresa_id);

        return ApiResponseHelper.success(data);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
