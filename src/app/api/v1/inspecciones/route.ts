import { NextRequest } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { InspeccionService } from '@/lib/services/inspeccion.service';
import { CreateInspeccionSchema } from '@/lib/validators/inspeccion.validator';
import { requireAuth } from '@/lib/auth/authorization';

const service = new InspeccionService();

export async function POST(request: NextRequest) {
    try {
        const session = await requireAuth();

        const json = await request.json();

        // Validation (Zod)
        const body = CreateInspeccionSchema.parse(json);

        const lectura = await service.registrarManual(body, session.user.id);

        return ApiResponseHelper.created(lectura, 'Inspección registrada correctamente');
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
