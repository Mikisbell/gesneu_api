import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { rutaService } from '@/lib/services/ruta.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { UpdateRutaSchema } from '@/lib/validators/ruta.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';

/**
 * @swagger
 * /api/v1/rutas/{id}:
 *   get:
 *     summary: Obtener ruta por ID
 *     description: Retorna los detalles completos de una ruta, incluyendo vehículos asignados
 *     tags: [Rutas]
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         description: ID de la ruta
 *         schema:
 *           type: string
 *           format: uuid
 *     responses:
 *       200:
 *         description: Ruta encontrada
 *       404:
 *         description: Ruta no encontrada
 */
export const GET = apiHandler(
    async (req, session, context) => {
        const params = await context.params;
        const id = params.id;

        const result = await rutaService.getById(session.user.empresa_id, id);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data);
    },
    { permission: PERMISSIONS.VEHICULOS_READ }
);

/**
 * @swagger
 * /api/v1/rutas/{id}:
 *   put:
 *     summary: Actualizar ruta
 *     description: Actualiza los datos de una ruta existente
 *     tags: [Rutas]
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         description: ID de la ruta
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
 *               nombre:
 *                 type: string
 *                 maxLength: 100
 *               origen:
 *                 type: string
 *                 maxLength: 100
 *               destino:
 *                 type: string
 *                 maxLength: 100
 *               distancia_km:
 *                 type: number
 *               tipo_ruta_id:
 *                 type: string
 *                 format: uuid
 *               activo:
 *                 type: boolean
 *     responses:
 *       200:
 *         description: Ruta actualizada exitosamente
 *       404:
 *         description: Ruta no encontrada
 */
export const PUT = apiHandler(
    async (req, session, context, body) => {
        const params = await context.params;
        const id = params.id;

        const result = await rutaService.update(
            session.user.empresa_id,
            session.user.id,
            id,
            body
        );
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data, 'Ruta actualizada exitosamente');
    },
    {
        permission: PERMISSIONS.VEHICULOS_UPDATE,
        schema: UpdateRutaSchema,
    }
);

/**
 * @swagger
 * /api/v1/rutas/{id}:
 *   delete:
 *     summary: Eliminar ruta
 *     description: Desactiva una ruta (solo si no tiene vehículos asignados activos)
 *     tags: [Rutas]
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         description: ID de la ruta
 *         schema:
 *           type: string
 *           format: uuid
 *     responses:
 *       200:
 *         description: Ruta eliminada exitosamente
 *       400:
 *         description: La ruta tiene vehículos asignados
 *       404:
 *         description: Ruta no encontrada
 */
export const DELETE = apiHandler(
    async (req, session, context) => {
        const params = await context.params;
        const id = params.id;

        const result = await rutaService.delete(session.user.empresa_id, id);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(null, 'Ruta eliminada exitosamente');
    },
    { permission: PERMISSIONS.VEHICULOS_DELETE }
);
