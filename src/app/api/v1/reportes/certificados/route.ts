import { NextRequest } from 'next/server';
import { apiHandler } from '@/lib/utils/api-handler';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { listarCertificadosFlota } from '@/lib/services/certificado.service';
import { EstadoOperatividadEnum } from '@prisma/client';

/**
 * @swagger
 * /api/v1/reportes/certificados:
 *   get:
 *     summary: Listar certificados de operatividad emitidos históricamente para la flota
 *     tags: [Reportes]
 *     parameters:
 *       - in: query
 *         name: page
 *         schema:
 *           type: integer
 *           default: 1
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 20
 *       - in: query
 *         name: q
 *         schema:
 *           type: string
 *           description: Búsqueda por folio numérico o placa del vehículo
 *       - in: query
 *         name: estado
 *         schema:
 *           type: string
 *           enum: [APTO, CONDICIONAL, NO_APTO]
 *       - in: query
 *         name: fecha_desde
 *         schema:
 *           type: string
 *           format: date
 *       - in: query
 *         name: fecha_hasta
 *         schema:
 *           type: string
 *           format: date
 *     responses:
 *       200:
 *         description: Lista paginada de certificados emitidos
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Sin permiso REPORTES_DASHBOARD
 */
export const GET = apiHandler(
    async (req: NextRequest, session) => {
        const { searchParams } = new URL(req.url);

        const page = parseInt(searchParams.get('page') || '1', 10);
        const limit = parseInt(searchParams.get('limit') || '20', 10);
        const search = searchParams.get('q') || undefined;
        const estadoParam = searchParams.get('estado');
        const fechaDesdeParam = searchParams.get('fecha_desde');
        const fechaHastaParam = searchParams.get('fecha_hasta');

        let estado: EstadoOperatividadEnum | undefined;
        if (
            estadoParam &&
            Object.values(EstadoOperatividadEnum).includes(estadoParam as EstadoOperatividadEnum)
        ) {
            estado = estadoParam as EstadoOperatividadEnum;
        }

        const result = await listarCertificadosFlota(session.user.empresa_id, {
            page,
            limit,
            search,
            estado,
            fechaDesde: fechaDesdeParam ? new Date(fechaDesdeParam) : undefined,
            fechaHasta: fechaHastaParam ? new Date(fechaHastaParam) : undefined,
        });

        const pagination = {
            ...result.pagination,
            hasNext: result.pagination.page < result.pagination.totalPages,
            hasPrev: result.pagination.page > 1
        };

        return ApiResponseHelper.paginated(result.data, pagination);
    },
    { permission: PERMISSIONS.REPORTES_DASHBOARD }
);
