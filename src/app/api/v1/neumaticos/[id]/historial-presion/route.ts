import { NextRequest, NextResponse } from 'next/server';
import { NeumaticoService } from '@/lib/services/neumatico.service';
import { ApiResponseHelper } from '../../../../../../lib/utils/api-response';
import { requireAuth } from '@/lib/auth/session';

export async function GET(
    request: NextRequest,
    context: { params: Promise<{ id: string }> } // Fix for Next.js 15+ async params
) {
    try {
        await requireAuth();
        const { id } = await context.params;

        const service = new NeumaticoService();
        const result = await service.getHistorialPresion(id);

        // Custom response to match frontend expectation:
        // data: Array<Lectura>
        // meta: { recomendada: number }
        return NextResponse.json({
            success: true,
            data: result.lecturas,
            meta: {
                recomendada: result.recomendada
            },
            timestamp: new Date().toISOString()
        });

    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
