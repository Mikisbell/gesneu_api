import { apiHandler } from '@/lib/utils/api-handler';
import { motivoDesechoService } from '@/lib/services/motivo-desecho.service';
import { CreateMotivoDesechoSchema } from '@/lib/validators/motivo-desecho.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { PERMISSIONS } from '@/lib/auth/permissions';

export const GET = apiHandler(
    async () => {
        const result = await motivoDesechoService.getAll();
        return ApiResponseHelper.fromResult(result);
    },
    { permission: PERMISSIONS.NEUMATICOS_READ }
);

export const POST = apiHandler(
    async (req, session, context, body) => {
        const result = await motivoDesechoService.create(body);
        return ApiResponseHelper.fromResult(result, 201);
    },
    {
        schema: CreateMotivoDesechoSchema,
        permission: PERMISSIONS.INVENTARIO_AJUSTES
    }
);
