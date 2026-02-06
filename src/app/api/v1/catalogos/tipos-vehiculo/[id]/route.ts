
import { NextRequest } from 'next/server';
import { apiHandler } from '@/lib/utils/api-handler';
import { tipoVehiculoService } from '@/lib/services/tipo-vehiculo.service';
import { UpdateTipoVehiculoSchema } from '@/lib/validators/tipo-vehiculo.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { PERMISSIONS } from '@/lib/auth/permissions';

export const GET = apiHandler({
    permission: PERMISSIONS.VEHICULOS_READ,
    handler: async (req: NextRequest, session, context) => {
        const { id } = await context.params;
        const result = await tipoVehiculoService.getById(id);
        return ApiResponseHelper.fromResult(result);
    }
});

export const PUT = apiHandler({
    schema: UpdateTipoVehiculoSchema,
    permission: PERMISSIONS.VEHICULOS_CONFIGURAR,
    handler: async (req: NextRequest, session, context, body) => {
        const { id } = await context.params;
        const result = await tipoVehiculoService.update(id, body);
        return ApiResponseHelper.fromResult(result);
    }
});

export const DELETE = apiHandler({
    permission: PERMISSIONS.VEHICULOS_CONFIGURAR,
    handler: async (req: NextRequest, session, context) => {
        const { id } = await context.params;
        const result = await tipoVehiculoService.delete(id);
        return ApiResponseHelper.fromResult(result);
    }
});
