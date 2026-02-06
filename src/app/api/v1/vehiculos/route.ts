import { apiHandler } from '@/lib/utils/api-handler';
import { vehiculoService } from '@/lib/container';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { CreateVehiculoSchema } from '@/lib/validators/vehiculo.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';

export const GET = apiHandler(
    async (req, session) => {
        const { searchParams } = new URL(req.url);
        const filters = {
            placa: searchParams.get('placa') || undefined,
            marca: searchParams.get('marca') || undefined,
            tipo_vehiculo_id: searchParams.get('tipo_vehiculo_id') || undefined,
            activo: searchParams.has('activo') ? searchParams.get('activo') === 'true' : undefined,
        };

        const empresaId = session.user.empresa_id!;

        // Using safe legacy method to ensure partial frontend compatibility while migrating Architecture
        const vehiculos = await vehiculoService.getAllLegacy(empresaId, filters);
        return vehiculos;
    },
    { permission: PERMISSIONS.VEHICULOS_READ }
);

export const POST = apiHandler(
    async (req, session, _, body) => {
        // Body is validated by apiHandler using schema
        const empresaId = session.user.empresa_id!;
        const result = await vehiculoService.create(body, empresaId);

        if (!result.success) throw result.error;
        return ApiResponseHelper.created(result.data, 'Vehículo creado exitosamente');
    },
    {
        permission: PERMISSIONS.VEHICULOS_CREATE,
        schema: CreateVehiculoSchema
    }
);
