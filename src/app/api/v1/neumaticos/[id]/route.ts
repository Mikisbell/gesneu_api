import { NextRequest } from 'next/server';
import { NeumaticoService } from '@/lib/services/neumatico.service';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import {
    validateUpdateNeumatico,
    formatZodErrors
} from '@/lib/validators/neumatico.validator';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { asNeumaticoId } from '@/types/branded.types';

const service = new NeumaticoService();

/**
 * @swagger
 * /api/v1/neumaticos/{id}:
 *   get:
 *     summary: Obtener neumático
 */
export async function GET(
    request: NextRequest,
    context: { params: Promise<{ id: string }> }
) {
    try {
        await requireAuth();
        const { id } = await context.params;

        const result = await service.getById(asNeumaticoId(id));

        if (!result.success) {
            return ApiResponseHelper.handleError(result.error);
        }

        return ApiResponseHelper.success(result.data);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}

/**
 * @swagger
 * /api/v1/neumaticos/{id}:
 *   put:
 *     summary: Actualizar neumático
 */
export async function PUT(
    request: NextRequest,
    context: { params: Promise<{ id: string }> }
) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.NEUMATICOS_UPDATE);
        const { id } = await context.params;

        const json = await request.json();
        const validation = validateUpdateNeumatico(json);

        if (!validation.success) {
            return ApiResponseHelper.validationError(formatZodErrors(validation.error));
        }

        const result = await service.update(asNeumaticoId(id), validation.data);

        if (!result.success) {
            return ApiResponseHelper.handleError(result.error);
        }

        return ApiResponseHelper.success(result.data, 'Neumático actualizado exitosamente');
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}

/**
 * @swagger
 * /api/v1/neumaticos/{id}:
 *   delete:
 *     summary: Eliminar neumático
 */
export async function DELETE(
    request: NextRequest,
    context: { params: Promise<{ id: string }> }
) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.NEUMATICOS_DELETE);
        const { id } = await context.params;

        const result = await service.delete(asNeumaticoId(id));

        if (!result.success) {
            return ApiResponseHelper.handleError(result.error);
        }

        return ApiResponseHelper.success(null, 'Neumático eliminado exitosamente');
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
