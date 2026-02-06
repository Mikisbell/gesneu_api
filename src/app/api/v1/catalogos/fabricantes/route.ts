
import { NextRequest } from 'next/server';
import { apiHandler } from '@/lib/utils/api-handler';
import { fabricanteService } from '@/lib/services/fabricante.service';
import { CreateFabricanteSchema } from '@/lib/validators/fabricante.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { PERMISSIONS } from '@/lib/auth/permissions';

export const GET = apiHandler({
    permission: PERMISSIONS.CATALOGOS_FABRICANTES_READ,
    handler: async () => {
        const result = await fabricanteService.getAll();
        return ApiResponseHelper.fromResult(result);
    }
});

export const POST = apiHandler({
    schema: CreateFabricanteSchema,
    permission: PERMISSIONS.CATALOGOS_FABRICANTES_CREATE,
    handler: async (req: NextRequest, session, context, body) => {
        const result = await fabricanteService.create(body);
        return ApiResponseHelper.fromResult(result, 201);
    }
});
