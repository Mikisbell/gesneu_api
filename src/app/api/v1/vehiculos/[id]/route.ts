import { NextRequest } from 'next/server'
import { VehiculoService } from '@/lib/services/vehiculo.service'
import { ApiResponseHelper } from '@/lib/utils/api-response'
import { UpdateVehiculoDTO } from '@/types/domain/vehiculo.types'
import { requireAuth, requirePermission } from '@/lib/auth/authorization'
import { PERMISSIONS } from '@/lib/auth/permissions'

const service = new VehiculoService()

/**
 * @swagger
 * /api/v1/vehiculos/{id}:
 *   get:
 *     summary: Obtener vehículo por ID
 *     description: Obtiene los detalles de un vehículo específico.
 *     tags: [Vehículos]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *           format: uuid
 *         description: ID del vehículo
 *     responses:
 *       200:
 *         description: Detalles del vehículo
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   $ref: '#/components/schemas/Vehiculo'
 *       404:
 *         description: Vehículo no encontrado
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere VEHICULOS_READ)
 */
export async function GET(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        // 1. Authentication
        const session = await requireAuth();

        // 2. Authorization
        requirePermission(session, PERMISSIONS.VEHICULOS_READ);

        // 3. Business logic
        const vehiculo = await service.getById((await params).id)
        if (!vehiculo) {
            return ApiResponseHelper.notFound()
        }
        return ApiResponseHelper.success(vehiculo)
    } catch (error) {
        return ApiResponseHelper.handleError(error)
    }
}

/**
 * @swagger
 * /api/v1/vehiculos/{id}:
 *   put:
 *     summary: Actualizar vehículo
 *     description: Actualiza los datos de un vehículo existente.
 *     tags: [Vehículos]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *           format: uuid
 *         description: ID del vehículo
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/UpdateVehiculoDTO'
 *     responses:
 *       200:
 *         description: Vehículo actualizado exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   $ref: '#/components/schemas/Vehiculo'
 *                 message:
 *                   type: string
 *       400:
 *         description: Datos inválidos
 *       404:
 *         description: Vehículo no encontrado
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere VEHICULOS_UPDATE)
 */
export async function PUT(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        // 1. Authentication
        const session = await requireAuth();

        // 2. Authorization
        requirePermission(session, PERMISSIONS.VEHICULOS_UPDATE);

        // 3. Business logic
        const body = await request.json() as UpdateVehiculoDTO
        const vehiculo = await service.update((await params).id, body)
        return ApiResponseHelper.success(vehiculo, 'Vehículo actualizado exitosamente')
    } catch (error) {
        return ApiResponseHelper.handleError(error)
    }
}

/**
 * @swagger
 * /api/v1/vehiculos/{id}:
 *   delete:
 *     summary: Eliminar vehículo
 *     description: Elimina un vehículo del sistema.
 *     tags: [Vehículos]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *           format: uuid
 *         description: ID del vehículo
 *     responses:
 *       200:
 *         description: Vehículo eliminado exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   $ref: '#/components/schemas/Vehiculo'
 *                 message:
 *                   type: string
 *       404:
 *         description: Vehículo no encontrado
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere VEHICULOS_DELETE)
 */
export async function DELETE(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        // 1. Authentication
        const session = await requireAuth();

        // 2. Authorization
        requirePermission(session, PERMISSIONS.VEHICULOS_DELETE);

        // 3. Business logic
        const vehiculo = await service.delete((await params).id)
        return ApiResponseHelper.success(vehiculo, 'Vehículo eliminado exitosamente')
    } catch (error) {
        return ApiResponseHelper.handleError(error)
    }
}
