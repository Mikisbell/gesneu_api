import { apiHandler } from '@/lib/utils/api-handler';
import { proveedorService } from '@/lib/container';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { CreateProveedorSchema } from '@/lib/validators/proveedor.validator';

export const GET = apiHandler(
  async (req, session) => {
    if (!session.user.empresa_id) {
      return ApiResponseHelper.forbidden('Usuario sin empresa asignada');
    }
    const result = await proveedorService.getAll(session.user.empresa_id);
    return ApiResponseHelper.fromResult(result);
  },
  { permission: PERMISSIONS.CATALOGOS_PROVEEDORES_READ }
);

export const POST = apiHandler(
  async (req, session, _, body) => {
    if (!session.user.empresa_id) {
      return ApiResponseHelper.forbidden('Usuario sin empresa asignada');
    }
    const result = await proveedorService.create(session.user.empresa_id, body);
    return ApiResponseHelper.fromResult(result, 201, 'Proveedor creado exitosamente');
  },
  {
    permission: PERMISSIONS.CATALOGOS_PROVEEDORES_CREATE,
    schema: CreateProveedorSchema
  }
);
