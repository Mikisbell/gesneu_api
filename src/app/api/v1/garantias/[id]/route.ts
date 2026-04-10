import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { garantiaService } from '@/lib/services/garantia.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { UpdateGarantiaSchema } from '@/lib/validators/garantia.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';

/**
 * @swagger
 * /api/v1/garantias/{id}:
 *   get:
 *     summary: Obtener garantía por ID
 *     description: Retorna los detalles completos de una garantía específica
 *     tags: [Garantías]
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         description: ID de la garantía
 *         schema:
 *           type: string
 *           format: uuid
 *     responses:
 *       200:
 *         description: Garantía encontrada
 *       404:
 *         description: Garantía no encontrada
 */
export const GET = apiHandler(
    async (req, session, context) => {
        const params = await context.params;
        const id = params.id;

        const result = await garantiaService.getById(session.user.empresa_id, id);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data);
    },
    { permission: PERMISSIONS.NEUMATICOS_READ }
);

/**
 * @swagger
 * /api/v1/garantias/{id}:
 *   put:
 *     summary: Actualizar garantía
 *     description: Actualiza los datos de una garantía existente
 *     tags: [Garantías]
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         description: ID de la garantía
 *         schema:
 *           type: string
 *           format: uuid
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               fecha_inicio:
 *                 type: string
 *                 format: date
 *               fecha_fin:
 *                 type: string
 *                 format: date
 *               kilometraje_max:
 *                 type: number
 *               profundidad_min:
 *                 type: number
 *               condiciones:
 *                 type: string
 *     responses:
 *       200:
 *         description: Garantía actualizada exitosamente
 *       404:
 *         description: Garantía no encontrada
 */
export const PUT = apiHandler(
    async (req, session, context, body) => {
        const params = await context.params;
        const id = params.id;

        const result = await garantiaService.update(
            session.user.empresa_id,
            session.user.id,
            id,
            body
        );
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data, 'Garantía actualizada exitosamente');
    },
    {
        permission: PERMISSIONS.NEUMATICOS_UPDATE,
        schema: UpdateGarantiaSchema,
    }
);

/**
 * @swagger
 * /api/v1/garantias/{id}:
 *   delete:
 *     summary: Eliminar garantía
 *     description: Elimina una garantía (solo si está en estado VIGENTE)
 *     tags: [Garantías]
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         description: ID de la garantía
 *         schema:
 *           type: string
 *           format: uuid
 *     responses:
 *       200:
 *         description: Garantía eliminada exitosamente
 *       404:
 *         description: Garantía no encontrada
 *       400:
 *         description: No se puede eliminar una garantía que no está en estado VIGENTE
 */
export const DELETE = apiHandler(
    async (req, session, context) => {
        const params = await context.params;
        const id = params.id;

        const result = await garantiaService.delete(session.user.empresa_id, id);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(null, 'Garantía eliminada exitosamente');
    },
    { permission: PERMISSIONS.NEUMATICOS_DELETE }
);
