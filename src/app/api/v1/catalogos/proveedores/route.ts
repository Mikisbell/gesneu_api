import { apiHandler } from '@/lib/utils/api-handler';
import { proveedorService } from '@/lib/container';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { CreateProveedorSchema } from '@/lib/validators/proveedor.validator';

export const GET = apiHandler(
  async () => {
    const result = await proveedorService.getAll();
    return ApiResponseHelper.fromResult(result);
  },
  { permission: PERMISSIONS.CATALOGOS_PROVEEDORES_READ }
);

export const POST = apiHandler(
  async (req, session, _, body) => {
    const result = await proveedorService.create(body);
    return ApiResponseHelper.fromResult(result, 201, 'Proveedor creado exitosamente');
  },
  {
    permission: PERMISSIONS.CATALOGOS_PROVEEDORES_CREATE,
    schema: CreateProveedorSchema
  }
);
