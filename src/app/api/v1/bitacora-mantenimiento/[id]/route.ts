import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { bitacoraMantenimientoService } from '@/lib/services/bitacora-mantenimiento.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { UpdateBitacoraMantenimientoSchema } from '@/lib/validators/bitacora-mantenimiento.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';

/**
 * @swagger
 * /api/v1/bitacora-mantenimiento/{id}:
 *   get:
 *     summary: Obtener registro de bitacora por ID
 *     description: Retorna los detalles completos de un registro de mantenimiento
 *     tags: [Bitacora Mantenimiento]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         description: ID del registro de bitacora
 *         schema:
 *           type: string
 *           format: uuid
 *     responses:
 *       200:
 *         description: Registro de mantenimiento encontrado
 *       404:
 *         description: Registro de mantenimiento no encontrado
 */
export const GET = apiHandler(
    async (req, session, context) => {
        const params = await context.params;
        const id = params.id;

        const result = await bitacoraMantenimientoService.getById(id);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data);
    },
    { permission: PERMISSIONS.VEHICULOS_READ }
);

/**
 * @swagger
 * /api/v1/bitacora-mantenimiento/{id}:
 *   put:
 *     summary: Actualizar registro de bitacora de mantenimiento
 *     description: Actualiza los datos de un registro de mantenimiento existente
 *     tags: [Bitacora Mantenimiento]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         description: ID del registro de bitacora
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
 *               tipo_operacion:
 *                 type: string
 *                 enum: [MANTENIMIENTO_PREVENTIVO, MANTENIMIENTO_CORRECTIVO, INSPECCION_PROGRAMADA, INSPECCION_ALEATORIA, LAVADO, ALINEACION, BALANCEO, CAMBIO_ACEITE, OTRO]
 *               fecha_programada:
 *                 type: string
 *                 format: date-time
 *               fecha_realizada:
 *                 type: string
 *                 format: date-time
 *               kilometraje:
 *                 type: number
 *               horometro:
 *                 type: number
 *               costo:
 *                 type: number
 *               proveedor_id:
 *                 type: string
 *                 format: uuid
 *               responsable:
 *                 type: string
 *                 maxLength: 200
 *               observaciones:
 *                 type: string
 *                 maxLength: 5000
 *               evidencia_url:
 *                 type: string
 *                 format: uri
 *     responses:
 *       200:
 *         description: Registro de mantenimiento actualizado exitosamente
 *       404:
 *         description: Registro de mantenimiento no encontrado
 */
export const PUT = apiHandler(
    async (req, session, context, body) => {
        const params = await context.params;
        const id = params.id;

        const result = await bitacoraMantenimientoService.update(id, body);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data, 'Registro de mantenimiento actualizado exitosamente');
    },
    {
        permission: PERMISSIONS.VEHICULOS_UPDATE,
        schema: UpdateBitacoraMantenimientoSchema
    }
);

/**
 * @swagger
 * /api/v1/bitacora-mantenimiento/{id}:
 *   delete:
 *     summary: Eliminar registro de bitacora de mantenimiento
 *     description: Elimina un registro de mantenimiento por su ID
 *     tags: [Bitacora Mantenimiento]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         description: ID del registro de bitacora
 *         schema:
 *           type: string
 *           format: uuid
 *     responses:
 *       200:
 *         description: Registro de mantenimiento eliminado exitosamente
 *       404:
 *         description: Registro de mantenimiento no encontrado
 */
export const DELETE = apiHandler(
    async (req, session, context) => {
        const params = await context.params;
        const id = params.id;

        const result = await bitacoraMantenimientoService.delete(id);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(null, 'Registro de mantenimiento eliminado exitosamente');
    },
    { permission: PERMISSIONS.VEHICULOS_DELETE }
);
