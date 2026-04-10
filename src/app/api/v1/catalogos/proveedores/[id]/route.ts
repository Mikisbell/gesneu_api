import { apiHandler } from '@/lib/utils/api-handler';
import { proveedorService } from '@/lib/container';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { UpdateProveedorSchema } from '@/lib/validators/proveedor.validator';
import { asProveedorId } from '@/types/branded.types';

export const GET = apiHandler(
  async (req, session, { params }) => {
    if (!session.user.empresa_id) {
      return ApiResponseHelper.forbidden('Usuario sin empresa asignada');
    }
    const { id } = await params;
    const result = await proveedorService.getById(session.user.empresa_id, asProveedorId(id));
    return ApiResponseHelper.fromResult(result);
  },
  { permission: PERMISSIONS.CATALOGOS_PROVEEDORES_READ }
);

export const PUT = apiHandler(
  async (req, session, { params }, body) => {
    if (!session.user.empresa_id) {
      return ApiResponseHelper.forbidden('Usuario sin empresa asignada');
    }
    const { id } = await params;
    const result = await proveedorService.update(session.user.empresa_id, asProveedorId(id), body);
    return ApiResponseHelper.fromResult(result, 200, 'Proveedor actualizado exitosamente');
  },
  {
    permission: PERMISSIONS.CATALOGOS_PROVEEDORES_UPDATE,
    schema: UpdateProveedorSchema
  }
);

export const DELETE = apiHandler(
  async (req, session, { params }) => {
    if (!session.user.empresa_id) {
      return ApiResponseHelper.forbidden('Usuario sin empresa asignada');
    }
    const { id } = await params;
    const result = await proveedorService.delete(session.user.empresa_id, asProveedorId(id));
    return ApiResponseHelper.fromResult(result, 200, 'Proveedor eliminado exitosamente');
  },
  { permission: PERMISSIONS.CATALOGOS_PROVEEDORES_DELETE }
);
