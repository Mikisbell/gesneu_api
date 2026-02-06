
import { NextRequest } from 'next/server';
import { apiHandler } from '@/lib/utils/api-handler';
import { modeloNeumaticoService } from '@/lib/services/modelo-neumatico.service';
import { UpdateModeloNeumaticoSchema } from '@/lib/validators/modelo-neumatico.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { PERMISSIONS } from '@/lib/auth/permissions';

export const GET = apiHandler({
    permission: PERMISSIONS.CATALOGOS_FABRICANTES_READ,
    handler: async (req: NextRequest, session, context) => {
        const { id } = await context.params;
        const result = await modeloNeumaticoService.getById(id);
        return ApiResponseHelper.fromResult(result);
    }
});

export const PUT = apiHandler({
    schema: UpdateModeloNeumaticoSchema,
    permission: PERMISSIONS.CATALOGOS_FABRICANTES_UPDATE,
    handler: async (req: NextRequest, session, context, body) => {
        const { id } = await context.params;
        const result = await modeloNeumaticoService.update(id, body);
        return ApiResponseHelper.fromResult(result);
    }
});

export const DELETE = apiHandler({
    permission: PERMISSIONS.CATALOGOS_FABRICANTES_DELETE,
    handler: async (req: NextRequest, session, context) => {
        const { id } = await context.params;
        const result = await modeloNeumaticoService.delete(id);
        return ApiResponseHelper.fromResult(result);
    }
});
