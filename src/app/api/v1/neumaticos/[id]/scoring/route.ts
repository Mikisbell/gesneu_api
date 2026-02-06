
import { NextRequest } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ScoringService } from '@/lib/services/scoring.service';

/**
 * @swagger
 * /api/v1/neumaticos/[id]/scoring:
 *   get:
 *     summary: Evaluar carcasa para reencauche
 *     description: Retorna puntaje y recomendación (Apto/Desecho) basado en marca, edad y vidas previas.
 *     tags: [Neumáticos, Premium]
 */
export async function GET(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.REPORTES_RENDIMIENTO);

        const { id } = await params;
        const result = await ScoringService.calculateScasingScore(id);

        return ApiResponseHelper.success(result);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
