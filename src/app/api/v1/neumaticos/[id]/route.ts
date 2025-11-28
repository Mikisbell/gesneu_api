import { NextRequest } from 'next/server';
import { NeumaticoService } from '@/lib/services/neumatico.service';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { UpdateNeumaticoDTO } from '@/types/domain/neumatico.types';

const service = new NeumaticoService();

/**
 * @swagger
 * /api/v1/neumaticos/{id}:
 *   get:
 *     summary: Obtener neumático por ID
 *     description: Obtiene los detalles de un neumático específico.
 *     tags: [Neumáticos]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *           format: uuid
 *         description: ID del neumático
 *     responses:
 *       200:
 *         description: Detalles del neumático
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   $ref: '#/components/schemas/Neumatico'
 *       404:
 *         description: Neumático no encontrado
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere NEUMATICOS_READ)
 */
export async function GET(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        // 1. Authentication
        const session = await requireAuth();

        // 2. Authorization
        requirePermission(session, PERMISSIONS.NEUMATICOS_READ);

        // 3. Business logic
        const neumatico = await service.getById((await params).id)
        if (!neumatico) {
            return ApiResponseHelper.notFound()
        }
        return ApiResponseHelper.success(neumatico)
    } catch (error) {
        return ApiResponseHelper.handleError(error)
    }
}

/**
 * @swagger
 * /api/v1/neumaticos/{id}:
 *   put:
 *     summary: Actualizar neumático
 *     description: Actualiza los datos de un neumático existente.
 *     tags: [Neumáticos]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *           format: uuid
 *         description: ID del neumático
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/UpdateNeumaticoDTO'
 *     responses:
 *       200:
 *         description: Neumático actualizado exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   $ref: '#/components/schemas/Neumatico'
 *                 message:
 *                   type: string
 *       400:
 *         description: Datos inválidos
 *       404:
 *         description: Neumático no encontrado
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere NEUMATICOS_UPDATE)
 */
export async function PUT(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        // 1. Authentication
        const session = await requireAuth();

        // 2. Authorization
        requirePermission(session, PERMISSIONS.NEUMATICOS_UPDATE);

        // 3. Business logic
        const body = await request.json() as UpdateNeumaticoDTO
        const neumatico = await service.update((await params).id, body)
        return ApiResponseHelper.success(neumatico, 'Neumático actualizado exitosamente')
    } catch (error) {
        return ApiResponseHelper.handleError(error)
    }
}

/**
 * @swagger
 * /api/v1/neumaticos/{id}:
 *   delete:
 *     summary: Eliminar neumático
 *     description: Elimina un neumático del sistema.
 *     tags: [Neumáticos]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *           format: uuid
 *         description: ID del neumático
 *     responses:
 *       200:
 *         description: Neumático eliminado exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   $ref: '#/components/schemas/Neumatico'
 *                 message:
 *                   type: string
 *       404:
 *         description: Neumático no encontrado
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere NEUMATICOS_DELETE)
 */
export async function DELETE(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        // 1. Authentication
        const session = await requireAuth();

        // 2. Authorization
        requirePermission(session, PERMISSIONS.NEUMATICOS_DELETE);

        // 3. Business logic
        const neumatico = await service.delete((await params).id)
        return ApiResponseHelper.success(neumatico, 'Neumático eliminado exitosamente')
    } catch (error) {
        return ApiResponseHelper.handleError(error)
    }
}
