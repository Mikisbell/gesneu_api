/**
 * Vehiculos API Routes - Detalle, Actualización y Eliminación
 * 
 * Implementa los endpoints GET, PUT y DELETE para un vehículo específico.
 * Usa el patrón Result para manejo explícito de errores y branded IDs.
 * 
 * @see docs/10_TIPADO_PROFESIONAL.md
 */

import { NextRequest } from 'next/server';
import { VehiculoService } from '@/lib/services/vehiculo.service';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { asVehiculoId, VehiculoId } from '@/types/branded.types';
import { isBusinessError } from '@/types/result.types';
import {
    validateUpdateVehiculo,
    formatZodErrors,
    getFirstZodError,
} from '@/lib/validators/vehiculo.validator';

const service = new VehiculoService();

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

        // 3. Parse ID with branded type
        const id = asVehiculoId((await params).id);

        // 4. Business logic with Result handling
        if (!session.user.empresa_id) {
            return ApiResponseHelper.error('Usuario no tiene empresa asignada', 403);
        }
        const result = await service.getById(session.user.empresa_id, id);

        if (!result.success) {
            return ApiResponseHelper.error(
                result.error.message,
                result.error.statusCode
            );
        }

        return ApiResponseHelper.success(result.data);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
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
 *       409:
 *         description: Conflicto (placa duplicada)
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

        // 3. Parse ID with branded type
        const id = asVehiculoId((await params).id);

        // 4. Parse and validate body
        const body = await request.json();
        const validation = validateUpdateVehiculo(body);

        if (!validation.success) {
            return ApiResponseHelper.validationError(
                formatZodErrors(validation.error),
                getFirstZodError(validation.error)
            );
        }

        // 5. Business logic with Result handling
        if (!session.user.empresa_id) {
            return ApiResponseHelper.error('Usuario no tiene empresa asignada', 403);
        }
        const result = await service.update(session.user.empresa_id, id, validation.data);

        if (!result.success) {
            if (isBusinessError(result.error)) {
                return ApiResponseHelper.error(
                    result.error.message,
                    result.error.statusCode
                );
            }
            return ApiResponseHelper.error((result.error as Error).message || 'Error desconocido', 500);
        }

        return ApiResponseHelper.success(result.data, 'Vehículo actualizado exitosamente');
    } catch (error) {
        return ApiResponseHelper.handleError(error);
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

        // 3. Parse ID with branded type
        const id = asVehiculoId((await params).id);

        // 4. Business logic with Result handling
        if (!session.user.empresa_id) {
            return ApiResponseHelper.error('Usuario no tiene empresa asignada', 403);
        }
        const result = await service.delete(session.user.empresa_id, id);

        if (!result.success) {
            if (isBusinessError(result.error)) {
                return ApiResponseHelper.error(
                    result.error.message,
                    result.error.statusCode
                );
            }
            return ApiResponseHelper.error((result.error as Error).message || 'Error desconocido', 500);
        }

        return ApiResponseHelper.success(result.data, 'Vehículo eliminado exitosamente');
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
