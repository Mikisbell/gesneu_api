
import { NextRequest } from 'next/server';
import { apiHandler } from '@/lib/utils/api-handler';
import { configuracionEjeService } from '@/lib/services/configuracion-eje.service';
import { CreateConfiguracionEjeSchema } from '@/lib/validators/configuracion-eje.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { PERMISSIONS } from '@/lib/auth/permissions';

export const GET = apiHandler({
    permission: PERMISSIONS.VEHICULOS_READ,
    handler: async (req: NextRequest) => {
        const searchParams = req.nextUrl.searchParams;
        const tipoVehiculoId = searchParams.get('tipo_vehiculo_id');

        if (!tipoVehiculoId) {
            return ApiResponseHelper.error('tipo_vehiculo_id is required', 400);
        }

        const result = await configuracionEjeService.getByTipoVehiculo(tipoVehiculoId);
        return ApiResponseHelper.fromResult(result);
    }
});

export const POST = apiHandler({
    schema: CreateConfiguracionEjeSchema,
    permission: PERMISSIONS.VEHICULOS_CONFIGURAR,
    handler: async (req: NextRequest, session, context, body) => {
        const result = await configuracionEjeService.create(body);
        return ApiResponseHelper.fromResult(result, 201);
    }
});
