import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { centroCostoService } from '@/lib/services/centro-costo.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { UpdateCentroCostoSchema } from '@/lib/validators/centro-costo.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';

/**
 * @swagger
 * /api/v1/centros-costo/{id}:
 *   get:
 *     summary: Obtener centro de costo por ID
 *     description: Retorna los detalles completos de un centro de costo, incluyendo cantidad de vehículos
 *     tags: [Centros de Costo]
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         description: ID del centro de costo
 *         schema:
 *           type: string
 *           format: uuid
 *     responses:
 *       200:
 *         description: Centro de costo encontrado
 *       404:
 *         description: Centro de costo no encontrado
 */
export const GET = apiHandler(
    async (req, session, context) => {
        const params = await context.params;
        const id = params.id;

        const result = await centroCostoService.getById(session.user.empresa_id, id);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data);
    },
    { permission: PERMISSIONS.VEHICULOS_READ }
);

/**
 * @swagger
 * /api/v1/centros-costo/{id}:
 *   put:
 *     summary: Actualizar centro de costo
 *     description: Actualiza los datos de un centro de costo existente
 *     tags: [Centros de Costo]
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         description: ID del centro de costo
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
 *               codigo:
 *                 type: string
 *                 maxLength: 20
 *               nombre:
 *                 type: string
 *                 maxLength: 100
 *               area_negocio:
 *                 type: string
 *                 maxLength: 100
 *               activo:
 *                 type: boolean
 *     responses:
 *       200:
 *         description: Centro de costo actualizado exitosamente
 *       404:
 *         description: Centro de costo no encontrado
 *       409:
 *         description: Ya existe un centro de costo con este código
 */
export const PUT = apiHandler(
    async (req, session, context, body) => {
        const params = await context.params;
        const id = params.id;

        const result = await centroCostoService.update(
            session.user.empresa_id,
            session.user.id,
            id,
            body
        );
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data, 'Centro de costo actualizado exitosamente');
    },
    {
        permission: PERMISSIONS.VEHICULOS_UPDATE,
        schema: UpdateCentroCostoSchema,
    }
);

/**
 * @swagger
 * /api/v1/centros-costo/{id}:
 *   delete:
 *     summary: Eliminar centro de costo
 *     description: Desactiva un centro de costo (solo si no tiene vehículos asociados activos)
 *     tags: [Centros de Costo]
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         description: ID del centro de costo
 *         schema:
 *           type: string
 *           format: uuid
 *     responses:
 *       200:
 *         description: Centro de costo eliminado exitosamente
 *       400:
 *         description: El centro de costo tiene vehículos asociados
 *       404:
 *         description: Centro de costo no encontrado
 */
export const DELETE = apiHandler(
    async (req, session, context) => {
        const params = await context.params;
        const id = params.id;

        const result = await centroCostoService.delete(session.user.empresa_id, id);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(null, 'Centro de costo eliminado exitosamente');
    },
    { permission: PERMISSIONS.VEHICULOS_DELETE }
);
