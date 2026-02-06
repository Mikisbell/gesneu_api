import { apiHandler } from '@/lib/utils/api-handler';
import { usuarioService } from '@/lib/container';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { createUsuarioSchema } from '@/lib/validators/usuarios';
import { ApiResponseHelper } from '@/lib/utils/api-response';

export const GET = apiHandler(
    async (req, session) => {
        const { searchParams } = new URL(req.url);
        const page = parseInt(searchParams.get('page') || '1');
        const limit = parseInt(searchParams.get('limit') || '10');
        const search = searchParams.get('search') || '';

        const result = await usuarioService.getPaginated(session.user.empresa_id!, { page, limit, search });

        // apiHandler usually expects data or Response. 
        // We return paginated response helper directly.
        return ApiResponseHelper.paginated(result.data, {
            ...result.meta,
            hasNext: result.meta.page < result.meta.totalPages,
            hasPrev: result.meta.page > 1,
        });
    },
    { permission: PERMISSIONS.USUARIOS_READ }
);

export const POST = apiHandler(
    async (req, session, _, body) => {
        const newUser = await usuarioService.create(session.user.empresa_id!, body);
        return ApiResponseHelper.created(newUser);
    },
    {
        permission: PERMISSIONS.USUARIOS_CREATE,
        schema: createUsuarioSchema
    }
);
