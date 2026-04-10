import { apiHandler } from '@/lib/utils/api-handler';
import { almacenService } from '@/lib/container';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { UpdateAlmacenSchema } from '@/lib/validators/almacen.validator';
import { asAlmacenId } from '@/types/branded.types';

export const GET = apiHandler(
  async (req, session, { params }) => {
    if (!session.user.empresa_id) {
      return ApiResponseHelper.forbidden('Usuario sin empresa asignada');
    }
    const { id } = await params;
    const result = await almacenService.getById(session.user.empresa_id, asAlmacenId(id));
    return ApiResponseHelper.fromResult(result);
  },
  { permission: PERMISSIONS.CATALOGOS_ALMACENES_READ }
);

export const PUT = apiHandler(
  async (req, session, { params }, body) => {
    if (!session.user.empresa_id) {
      return ApiResponseHelper.forbidden('Usuario sin empresa asignada');
    }
    const { id } = await params;
    const result = await almacenService.update(session.user.empresa_id, asAlmacenId(id), body);
    return ApiResponseHelper.fromResult(result, 200, 'Almacén actualizado exitosamente');
  },
  {
    permission: PERMISSIONS.CATALOGOS_ALMACENES_UPDATE,
    schema: UpdateAlmacenSchema
  }
);

export const DELETE = apiHandler(
  async (req, session, { params }) => {
    if (!session.user.empresa_id) {
      return ApiResponseHelper.forbidden('Usuario sin empresa asignada');
    }
    const { id } = await params;
    const result = await almacenService.delete(session.user.empresa_id, asAlmacenId(id));
    return ApiResponseHelper.fromResult(result, 200, 'Almacén eliminado exitosamente');
  },
  { permission: PERMISSIONS.CATALOGOS_ALMACENES_DELETE }
);
