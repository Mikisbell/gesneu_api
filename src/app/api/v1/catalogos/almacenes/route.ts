import { apiHandler } from '@/lib/utils/api-handler';
import { almacenService } from '@/lib/container';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { CreateAlmacenSchema } from '@/lib/validators/almacen.validator';

export const GET = apiHandler(
  async () => {
    const result = await almacenService.getAll();
    return ApiResponseHelper.fromResult(result);
  },
  { permission: PERMISSIONS.CATALOGOS_ALMACENES_READ }
);

export const POST = apiHandler(
  async (req, session, _, body) => {
    // body is already validated by apiHandler using the schema
    const result = await almacenService.create(body);
    return ApiResponseHelper.fromResult(result, 201, 'Almacén creado exitosamente');
  },
  {
    permission: PERMISSIONS.CATALOGOS_ALMACENES_CREATE,
    schema: CreateAlmacenSchema
  }
);
