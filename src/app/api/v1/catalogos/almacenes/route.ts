import { apiHandler } from '@/lib/utils/api-handler';
import { almacenService } from '@/lib/container';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { CreateAlmacenSchema } from '@/lib/validators/almacen.validator';

export const GET = apiHandler(
  async (req, session) => {
    if (!session.user.empresa_id) {
      return ApiResponseHelper.forbidden('Usuario sin empresa asignada');
    }
    const result = await almacenService.getAll(session.user.empresa_id);
    return ApiResponseHelper.fromResult(result);
  },
  { permission: PERMISSIONS.CATALOGOS_ALMACENES_READ }
);

export const POST = apiHandler(
  async (req, session, _, body) => {
    if (!session.user.empresa_id) {
      return ApiResponseHelper.forbidden('Usuario sin empresa asignada');
    }
    // body is already validated by apiHandler using the schema
    const result = await almacenService.create(session.user.empresa_id, body);
    return ApiResponseHelper.fromResult(result, 201, 'Almacén creado exitosamente');
  },
  {
    permission: PERMISSIONS.CATALOGOS_ALMACENES_CREATE,
    schema: CreateAlmacenSchema
  }
);
