import { NextRequest, NextResponse } from 'next/server';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { updateUsuarioSchema } from '@/lib/validators/usuarios';
import { UsuarioService } from '@/lib/services/usuario.service';

const service = new UsuarioService();

/**
 * @swagger
 * /api/v1/usuarios/{id}:
 *   get:
 *     summary: Obtener usuario por ID
 *     tags: [Usuarios]
 *     security: [{ bearerAuth: [] }]
 */
export async function GET(
    req: NextRequest,
    context: { params: Promise<{ id: string }> }
) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.USUARIOS_READ);

        const { id } = await context.params;
        const usuario = await service.getById(id);

        return ApiResponseHelper.success(usuario);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}

/**
 * @swagger
 * /api/v1/usuarios/{id}:
 *   put:
 *     summary: Actualizar usuario
 *     tags: [Usuarios]
 */
export async function PUT(
    req: NextRequest,
    context: { params: Promise<{ id: string }> }
) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.USUARIOS_UPDATE);

        const { id } = await context.params;
        const body = await req.json();

        const validation = updateUsuarioSchema.safeParse(body);
        if (!validation.success) {
            return ApiResponseHelper.validationError(validation.error);
        }

        const updatedUser = await service.update(id, validation.data);

        return ApiResponseHelper.success(updatedUser);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}

/**
 * @swagger
 * /api/v1/usuarios/{id}:
 *   delete:
 *     summary: Eliminar (Desactivar) usuario
 *     tags: [Usuarios]
 */
export async function DELETE(
    req: NextRequest,
    context: { params: Promise<{ id: string }> }
) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.USUARIOS_DELETE);

        const { id } = await context.params;
        const result = await service.delete(id);

        return ApiResponseHelper.success(result);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
