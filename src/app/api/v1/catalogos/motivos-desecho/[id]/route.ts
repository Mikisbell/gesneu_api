import { apiHandler } from '@/lib/utils/api-handler';
import { motivoDesechoService } from '@/lib/services/motivo-desecho.service';
import { UpdateMotivoDesechoSchema } from '@/lib/validators/motivo-desecho.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { PERMISSIONS } from '@/lib/auth/permissions';

export const GET = apiHandler(
    async (req, session, context) => {
        const params = await context.params;
        const result = await motivoDesechoService.getById(params.id);
        return ApiResponseHelper.fromResult(result);
    },
    { permission: PERMISSIONS.NEUMATICOS_READ }
);

export const PUT = apiHandler(
    async (req, session, context, body) => {
        const params = await context.params;
        const result = await motivoDesechoService.update(params.id, body);
        return ApiResponseHelper.fromResult(result);
    },
    {
        schema: UpdateMotivoDesechoSchema,
        permission: PERMISSIONS.INVENTARIO_AJUSTES
    }
);

export const DELETE = apiHandler(
    async (req, session, context) => {
        const params = await context.params;
        const result = await motivoDesechoService.delete(params.id);
        return ApiResponseHelper.fromResult(result);
    },
    { permission: PERMISSIONS.INVENTARIO_AJUSTES }
);
