
import { NextRequest } from 'next/server';
import { apiHandler } from '@/lib/utils/api-handler';
import { configuracionEjeService } from '@/lib/services/configuracion-eje.service';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { PERMISSIONS } from '@/lib/auth/permissions';

export const DELETE = apiHandler(
    async (req: NextRequest, session, { params }) => {
        const { id } = await params;
        const result = await configuracionEjeService.delete(id);
        return ApiResponseHelper.fromResult(result);
    },
    { permission: PERMISSIONS.VEHICULOS_CONFIGURAR }
);
