import { NextRequest, NextResponse } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { createUsuarioSchema } from '@/lib/validators/usuarios';
import { UsuarioService } from '@/lib/services/usuario.service';

const service = new UsuarioService();

/**
 * @swagger
 * /api/v1/usuarios:
 *   get:
 *     summary: Listar usuarios
 *     tags: [Usuarios]
 */
export async function GET(req: NextRequest) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.USUARIOS_READ);

        const { searchParams } = new URL(req.url);
        const page = parseInt(searchParams.get('page') || '1');
        const limit = parseInt(searchParams.get('limit') || '10');
        const search = searchParams.get('search') || '';

        const result = await service.getPaginated({ page, limit, search });

        return ApiResponseHelper.paginated(result.data, {
            ...result.meta,
            hasNext: result.meta.page < result.meta.totalPages,
            hasPrev: result.meta.page > 1,
        });
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}

/**
 * @swagger
 * /api/v1/usuarios:
 *   post:
 *     summary: Crear usuario
 *     tags: [Usuarios]
 */
export async function POST(req: NextRequest) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.USUARIOS_CREATE);

        const body = await req.json();
        const validation = createUsuarioSchema.safeParse(body);

        if (!validation.success) {
            return ApiResponseHelper.validationError(validation.error);
        }

        const newUser = await service.create(validation.data);

        return ApiResponseHelper.created(newUser);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
