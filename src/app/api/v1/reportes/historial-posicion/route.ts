import { NextRequest } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ReportesService } from '@/lib/services/reportes.service';

const service = new ReportesService();

/**
 * @swagger
 * /api/v1/reportes/historial-posicion:
 *   get:
 *     summary: Historial de últimas N instalaciones en una posición
 *     tags: [Reportes]
 *     parameters:
 *       - in: query
 *         name: vehiculo_id
 *         required: true
 *         schema:
 *           type: string
 *       - in: query
 *         name: posicion_codigo
 *         required: true
 *         schema:
 *           type: string
 *       - in: query
 *         name: limit
 *         description: Número de instalaciones a retornar (default 4)
 *         schema:
 *           type: integer
 *           default: 4
 */
export async function GET(request: NextRequest) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.NEUMATICOS_READ);

        const { searchParams } = new URL(request.url);
        const vehiculoId = searchParams.get('vehiculo_id');
        const posicionCodigo = searchParams.get('posicion_codigo');
        const limit = parseInt(searchParams.get('limit') || '4', 10);

        if (!vehiculoId || !posicionCodigo) {
            return ApiResponseHelper.error('vehiculo_id y posicion_codigo son requeridos', 400);
        }

        const data = await service.getHistorialPosicion(
            session.user.empresa_id!,
            vehiculoId,
            posicionCodigo,
            limit
        );
        return ApiResponseHelper.success(data);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
