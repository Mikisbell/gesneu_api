import { NextRequest } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { neumaticoService } from '@/lib/container';
import { CreateInspeccionSchema } from '@/lib/validators/inspeccion.validator';
import { requireAuth } from '@/lib/auth/authorization';
import { TipoEventoNeumaticoEnum } from '@prisma/client';

export async function POST(request: NextRequest) {
    try {
        const session = await requireAuth();
        const json = await request.json();
        const body = CreateInspeccionSchema.parse(json);

        // Map Inspeccion DTO to Event Interface
        const resultado = await neumaticoService.registrarEvento({
            tipo_evento: TipoEventoNeumaticoEnum.INSPECCION,
            neumatico_id: body.neumatico_id,
            presion_psi: body.presion_psi,
            // profundidad_remanente: not capturing depth in manual pressure check
            observaciones: body.observaciones,
            fecha_evento: new Date().toISOString()
        }, session.user.id, session.user.empresa_id!);

        return ApiResponseHelper.created(resultado, 'Inspección registrada correctamente');
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
