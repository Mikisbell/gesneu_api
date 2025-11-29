import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { updateUsuarioSchema } from '@/lib/validators/usuarios';
import { hash } from 'bcryptjs';

/**
 * @swagger
 * /api/v1/usuarios/{id}:
 *   get:
 *     summary: Obtener usuario por ID
 *     description: Retorna los detalles de un usuario específico.
 *     tags: [Usuarios]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *           format: uuid
 *         description: ID del usuario
 *     responses:
 *       200:
 *         description: Detalles del usuario recuperados exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   $ref: '#/components/schemas/Usuario'
 *       404:
 *         description: Usuario no encontrado
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere USUARIOS_READ)
 *   put:
 *     summary: Actualizar usuario
 *     description: Actualiza los datos de un usuario existente.
 *     tags: [Usuarios]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *           format: uuid
 *         description: ID del usuario
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/UpdateUsuarioDTO'
 *     responses:
 *       200:
 *         description: Usuario actualizado exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   $ref: '#/components/schemas/Usuario'
 *       400:
 *         description: Datos inválidos
 *       404:
 *         description: Usuario no encontrado
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere USUARIOS_UPDATE)
 *   delete:
 *     summary: Eliminar usuario
 *     description: Realiza un borrado lógico (soft delete) de un usuario.
 *     tags: [Usuarios]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *           format: uuid
 *         description: ID del usuario
 *     responses:
 *       200:
 *         description: Usuario eliminado exitosamente
 *       404:
 *         description: Usuario no encontrado
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere USUARIOS_DELETE)
 */
export async function GET(
    req: NextRequest,
    context: { params: Promise<{ id: string }> }
) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.USUARIOS_READ);

        const { id } = await context.params;

        const usuario = await prisma.usuario.findUnique({
            where: { id }
        });

        if (!usuario) {
            return ApiResponseHelper.notFound();
        }

        const { password_hash, ...sanitizedUser } = usuario;

        return ApiResponseHelper.success(sanitizedUser);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}

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

        const { password, ...userData } = validation.data;

        const existingUser = await prisma.usuario.findUnique({
            where: { id },
        });

        if (!existingUser) {
            return ApiResponseHelper.notFound();
        }

        let passwordHash = undefined;
        if (password) {
            passwordHash = await hash(password, 10);
        }

        const updatedUser = await prisma.usuario.update({
            where: { id },
            data: {
                ...userData,
                ...(passwordHash && { password_hash: passwordHash })
            },
        });

        if (!updatedUser) {
            throw new Error('Error al actualizar usuario');
        }

        const { password_hash: _, ...sanitizedUser } = updatedUser;

        return ApiResponseHelper.success(sanitizedUser);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}

export async function DELETE(
    req: NextRequest,
    context: { params: Promise<{ id: string }> }
) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.USUARIOS_DELETE);

        const { id } = await context.params;

        const existingUser = await prisma.usuario.findUnique({
            where: { id },
        });

        if (!existingUser) {
            return ApiResponseHelper.notFound();
        }

        // Hard delete (no soft delete in simplified schema)
        await prisma.usuario.delete({
            where: { id }
        });

        return ApiResponseHelper.success({ message: 'Usuario desactivado exitosamente' });
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
