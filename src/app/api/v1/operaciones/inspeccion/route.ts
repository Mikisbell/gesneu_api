import { NextRequest } from 'next/server';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { InspeccionNeumaticoSchema } from '@/lib/validators/inspeccion';
import { NeumaticoService } from '@/lib/services/neumatico.service';
import { TipoEventoNeumaticoEnum } from '@prisma/client';

const service = new NeumaticoService();

export async function POST(request: NextRequest) {
    try {
        // 1. Autenticación y autorización
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.NEUMATICOS_EVENTO_INSPECCION);

        // 2. Validar entrada
        const body = await request.json();
        const validatedData = InspeccionNeumaticoSchema.parse(body);

        // 3. Ejecutar servicio
        const resultado = await service.registrarEvento({
            tipo_evento: TipoEventoNeumaticoEnum.INSPECCION,
            neumatico_id: validatedData.neumatico_id,
            contador_vehiculo: validatedData.contador_vehiculo,
            presion_psi: validatedData.presion_psi,
            profundidad_remanente: validatedData.profundidad_mm,
            observaciones: validatedData.observaciones,
            fecha_evento: new Date().toISOString()
        }, session.user.id, session.user.empresa_id!);

        return ApiResponseHelper.success(resultado, 'Inspección registrada exitosamente');

    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
