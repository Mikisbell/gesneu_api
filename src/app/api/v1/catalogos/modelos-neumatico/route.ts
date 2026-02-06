
import { NextRequest } from 'next/server';
import { apiHandler } from '@/lib/utils/api-handler';
import { modeloNeumaticoService } from '@/lib/services/modelo-neumatico.service';
import { CreateModeloNeumaticoSchema } from '@/lib/validators/modelo-neumatico.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { PERMISSIONS } from '@/lib/auth/permissions';

export const GET = apiHandler({
    permission: PERMISSIONS.CATALOGOS_FABRICANTES_READ, // Use same permission family
    handler: async () => {
        const result = await modeloNeumaticoService.getAll();
        return ApiResponseHelper.fromResult(result);
    }
});

export const POST = apiHandler({
    schema: CreateModeloNeumaticoSchema,
    permission: PERMISSIONS.CATALOGOS_FABRICANTES_CREATE,
    handler: async (req: NextRequest, session, context, body) => {
        const result = await modeloNeumaticoService.create(body);
        return ApiResponseHelper.fromResult(result, 201);
    }
});
