import { NextRequest } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ReencaucheSalidaSchema } from '@/lib/validators/operaciones';
import { NeumaticoService } from '@/lib/services/neumatico.service';
import { TipoEventoNeumaticoEnum } from '@prisma/client';

const service = new NeumaticoService();

export async function POST(req: NextRequest) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.NEUMATICOS_EVENTO_REENCAUCHE);

        const body = await req.json();
        const validation = ReencaucheSalidaSchema.safeParse(body);

        if (!validation.success) {
            return ApiResponseHelper.validationError(validation.error);
        }

        const {
            neumatico_id,
            almacen_destino_id,
            costo_real,
            profundidad_nueva_mm,
            observaciones,
            fecha_evento
        } = validation.data;

        await service.registrarEvento({
            tipo_evento: TipoEventoNeumaticoEnum.REENCAUCHE_SALIDA,
            neumatico_id,
            almacen_destino_id,
            costo_evento: costo_real,
            profundidad_remanente: profundidad_nueva_mm,
            observaciones,
            fecha_evento: fecha_evento?.toISOString() ?? new Date().toISOString()
        }, session.user.id, session.user.empresa_id!);

        return ApiResponseHelper.success({ message: 'Neumático retornado de reencauche exitosamente' });
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
