import { NextRequest } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { AlertasService } from '@/lib/services/alertas.service';
import { TipoAlertaEnum, SeveridadAlertaEnum } from '@prisma/client';

const service = new AlertasService();

/**
 * @swagger
 * /api/v1/alertas:
 *   get:
 *     summary: Listar alertas
 *     description: Obtiene lista de alertas con filtros opcionales
 *     tags:
 *       - Alertas
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: tipo
 *         schema:
 *           type: string
 *           enum: [PROFUNDIDAD_MINIMA, REENCAUCHE_MAXIMO, DESGASTE_IRREGULAR, VENCIMIENTO_DOT]
 *       - in: query
 *         name: severidad
 *         schema:
 *           type: string
 *           enum: [INFO, WARNING, CRITICAL]
 *       - in: query
 *         name: leida
 *         schema:
 *           type: boolean
 *       - in: query
 *         name: resuelta
 *         schema:
 *           type: boolean
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 50
 *     responses:
 *       200:
 *         description: Lista de alertas
 */
export async function GET(request: NextRequest) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.NEUMATICOS_READ);

        const { searchParams } = new URL(request.url);

        const filters: any = {};
        const tipo = searchParams.get('tipo');
        const severidad = searchParams.get('severidad');
        const leida = searchParams.get('leida');
        const resuelta = searchParams.get('resuelta');
        const limit = searchParams.get('limit');

        if (tipo) filters.tipo = tipo as TipoAlertaEnum;
        if (severidad) filters.severidad = severidad as SeveridadAlertaEnum;
        if (leida !== null) filters.leida = leida === 'true';
        if (resuelta !== null) filters.resuelta = resuelta === 'true';
        if (limit) filters.limit = parseInt(limit);

        const alertas = await service.getAlertas(filters);

        return ApiResponseHelper.success(alertas);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}

/**
 * @swagger
 * /api/v1/alertas:
 *   patch:
 *     summary: Actualizar estado de alertas (leída/resuelta)
 */
export async function PATCH(request: NextRequest) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.REPORTES_DASHBOARD);

        const json = await request.json();
        const { id, accion } = json; // accion: 'MARCAR_LEIDA' | 'RESOLVER'

        if (!id) return ApiResponseHelper.error('ID requerido', 400);

        if (accion === 'MARCAR_LEIDA') {
            await service.marcarComoLeida(id);
        } else if (accion === 'RESOLVER') {
            await service.resolver(id);
        } else {
            return ApiResponseHelper.error('Acción inválida', 400);
        }

        return ApiResponseHelper.success({ success: true });
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
