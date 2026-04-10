import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { parametroSistemaService } from '@/lib/services/parametro-sistema.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { UpdateParametroSistemaSchema } from '@/lib/validators/parametro-sistema.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';

/**
 * @swagger
 * /api/v1/configuracion/parametros/{id}:
 *   get:
 *     summary: Obtener parametro del sistema por ID
 *     description: Retorna los detalles de un parametro del sistema
 *     tags: [Configuracion - Parametros del Sistema]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         description: ID del parametro del sistema
 *         schema:
 *           type: string
 *           format: uuid
 *     responses:
 *       200:
 *         description: Parametro del sistema encontrado
 *       404:
 *         description: Parametro del sistema no encontrado
 */
export const GET = apiHandler(
    async (req, session, context) => {
        const params = await context.params;
        const id = params.id;

        const result = await parametroSistemaService.getById(id);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data);
    },
    { permission: PERMISSIONS.SISTEMA_AJUSTES_READ }
);

/**
 * @swagger
 * /api/v1/configuracion/parametros/{id}:
 *   put:
 *     summary: Actualizar parametro del sistema
 *     description: Actualiza los datos de un parametro del sistema existente
 *     tags: [Configuracion - Parametros del Sistema]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         description: ID del parametro del sistema
 *         schema:
 *           type: string
 *           format: uuid
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - valor
 *             properties:
 *               valor:
 *                 type: string
 *               tipo_dato:
 *                 type: string
 *                 enum: [STRING, NUMBER, BOOLEAN, JSON]
 *               categoria:
 *                 type: string
 *                 maxLength: 50
 *               descripcion:
 *                 type: string
 *                 maxLength: 1000
 *               valor_default:
 *                 type: string
 *               editable:
 *                 type: boolean
 *               requiere_reinicio:
 *                 type: boolean
 *     responses:
 *       200:
 *         description: Parametro del sistema actualizado exitosamente
 *       404:
 *         description: Parametro del sistema no encontrado
 *       403:
 *         description: Parametro del sistema no editable
 */
export const PUT = apiHandler(
    async (req, session, context, body) => {
        const params = await context.params;
        const id = params.id;

        const result = await parametroSistemaService.update(id, body);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data, 'Parametro del sistema actualizado exitosamente');
    },
    {
        permission: PERMISSIONS.SISTEMA_AJUSTES_READ,
        schema: UpdateParametroSistemaSchema
    }
);

/**
 * @swagger
 * /api/v1/configuracion/parametros/{id}:
 *   delete:
 *     summary: Eliminar parametro del sistema
 *     description: Elimina un parametro del sistema (solo si no es un parametro de sistema)
 *     tags: [Configuracion - Parametros del Sistema]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         description: ID del parametro del sistema
 *         schema:
 *           type: string
 *           format: uuid
 *     responses:
 *       200:
 *         description: Parametro del sistema eliminado exitosamente
 *       404:
 *         description: Parametro del sistema no encontrado
 *       403:
 *         description: No se puede eliminar un parametro del sistema
 */
export const DELETE = apiHandler(
    async (req, session, context) => {
        const params = await context.params;
        const id = params.id;

        const result = await parametroSistemaService.delete(id);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(null, 'Parametro del sistema eliminado exitosamente');
    },
    { permission: PERMISSIONS.SISTEMA_AJUSTES_READ }
);
