import { NextRequest } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ReportesService } from '@/lib/services/reportes.service';

const service = new ReportesService();

/**
 * @swagger
 * /api/v1/reportes/comparativo-marcas:
 *   get:
 *     summary: Comparativo de CPK por Marca/Fabricante
 *     description: |
 *       Calcula y compara el CPK promedio de cada fabricante/marca.
 *       Solo incluye neumáticos con kilometraje > 0.
 *       Ordenado de menor a mayor CPK (mejor a peor).
 *     tags:
 *       - Reportes
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Comparativo de marcas calculado exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 data:
 *                   $ref: '#/components/schemas/BrandComparisonResultDTO'
 */
export async function GET(request: NextRequest) {
    try {
        // 1. Authentication
        const session = await requireAuth();

        // 2. Authorization
        requirePermission(session, PERMISSIONS.NEUMATICOS_READ);

        // 3. Service Call
        const data = await service.getComparativoMarcas(session.user.empresa_id || '');

        return ApiResponseHelper.success(data);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}

