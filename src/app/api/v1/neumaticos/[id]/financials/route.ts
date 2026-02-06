
import { apiHandler } from '@/lib/utils/api-handler';
import { neumaticoService } from '@/lib/services/neumatico.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ApiResponseHelper } from '@/lib/utils/api-response';

/**
 * @swagger
 * /api/v1/neumaticos/{id}/financials:
 *   get:
 *     summary: Obtener métricas financieras y proyecciones (CPK, Vida Útil)
 *     tags: [Neumáticos]
 */
export const GET = apiHandler(
    async (req, session, context) => {
        const params = await context.params;
        const id = params.id;

        const metrics = await neumaticoService.getFinancials(session.user!.empresa_id, id);

        return ApiResponseHelper.success(metrics);
    },
    { permission: PERMISSIONS.NEUMATICOS_READ }
);
