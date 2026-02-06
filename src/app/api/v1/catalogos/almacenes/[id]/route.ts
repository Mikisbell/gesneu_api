import { apiHandler } from '@/lib/utils/api-handler';
import { almacenService } from '@/lib/container';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { UpdateAlmacenSchema } from '@/lib/validators/almacen.validator';
import { asAlmacenId } from '@/types/branded.types';

export const GET = apiHandler(
  async (req, session, { params }) => {
    const { id } = await params;
    const result = await almacenService.getById(asAlmacenId(id));
    return ApiResponseHelper.fromResult(result);
  },
  { permission: PERMISSIONS.CATALOGOS_ALMACENES_READ }
);

export const PUT = apiHandler(
  async (req, session, { params }, body) => {
    const { id } = await params;
    const result = await almacenService.update(asAlmacenId(id), body);
    return ApiResponseHelper.fromResult(result, 200, 'Almacén actualizado exitosamente');
  },
  {
    permission: PERMISSIONS.CATALOGOS_ALMACENES_UPDATE,
    schema: UpdateAlmacenSchema
  }
);

export const DELETE = apiHandler(
  async (req, session, { params }) => {
    const { id } = await params;
    const result = await almacenService.delete(asAlmacenId(id));
    return ApiResponseHelper.fromResult(result, 200, 'Almacén eliminado exitosamente');
  },
  { permission: PERMISSIONS.CATALOGOS_ALMACENES_DELETE }
);
