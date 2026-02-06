
import { NextRequest } from 'next/server';
import { apiHandler } from '@/lib/utils/api-handler';
import { tipoVehiculoService } from '@/lib/services/tipo-vehiculo.service';
import { CreateTipoVehiculoSchema } from '@/lib/validators/tipo-vehiculo.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { PERMISSIONS } from '@/lib/auth/permissions';

export const GET = apiHandler({
    permission: PERMISSIONS.VEHICULOS_READ,
    handler: async () => {
        const result = await tipoVehiculoService.getAll();
        return ApiResponseHelper.fromResult(result);
    }
});

export const POST = apiHandler({
    schema: CreateTipoVehiculoSchema,
    permission: PERMISSIONS.VEHICULOS_CONFIGURAR,
    handler: async (req: NextRequest, session, context, body) => {
        const result = await tipoVehiculoService.create(body);
        return ApiResponseHelper.fromResult(result, 201);
    }
});
