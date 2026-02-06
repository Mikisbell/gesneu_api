import { NextRequest } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { DashboardService } from '@/lib/services/dashboard.service';
import { EstadoNeumaticoEnum } from '@prisma/client';

const service = new DashboardService();

/**
 * @swagger
 * /api/v1/dashboard/inventario:
 *   get:
 *     summary: Reporte de inventario
 *     description: Stock agrupado por almacén, estado y modelo
 *     tags:
 *       - Dashboard
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: almacen_id
 *         schema:
 *           type: string
 *           format: uuid
 *       - in: query
 *         name: estado
 *         schema:
 *           type: string
 *           enum: [EN_STOCK, INSTALADO, EN_REPARACION, EN_REENCAUCHE, DESECHADO]
 *       - in: query
 *         name: modelo_id
 *         schema:
 *           type: string
 *           format: uuid
 *     responses:
 *       200:
 *         description: Reporte de inventario
 */
export async function GET(request: NextRequest) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.NEUMATICOS_READ);

        const { searchParams } = new URL(request.url);
        const filters: any = {};

        const almacen_id = searchParams.get('almacen_id');
        const estado = searchParams.get('estado');
        const modelo_id = searchParams.get('modelo_id');

        if (almacen_id) filters.almacen_id = almacen_id;
        if (estado) filters.estado = estado as EstadoNeumaticoEnum;
        if (modelo_id) filters.modelo_id = modelo_id;

        const report = await service.getReporteInventario(session.user.empresa_id!, {
            almacen_id: almacen_id || undefined,
            estado: estado as any,
            modelo_id: modelo_id || undefined
        });
        return ApiResponseHelper.success(report);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
