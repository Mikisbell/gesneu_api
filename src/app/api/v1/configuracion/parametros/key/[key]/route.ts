import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { parametroSistemaService } from '@/lib/services/parametro-sistema.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { SetByKeySchema } from '@/lib/validators/parametro-sistema.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';

/**
 * @swagger
 * /api/v1/configuracion/parametros/key/{key}:
 *   get:
 *     summary: Obtener parametro del sistema por clave
 *     description: Retorna un parametro del sistema buscando por su clave unica
 *     tags: [Configuracion - Parametros del Sistema]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - name: key
 *         in: path
 *         required: true
 *         description: Clave unica del parametro (ej: EMPRESA_NOMBRE)
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Parametro del sistema encontrado
 *       404:
 *         description: Parametro del sistema no encontrado
 */
export const GET = apiHandler(
    async (req, session, context) => {
        const params = await context.params;
        const key = decodeURIComponent(params.key);

        const result = await parametroSistemaService.getByKey(key);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data);
    },
    { permission: PERMISSIONS.SISTEMA_AJUSTES_READ }
);

/**
 * @swagger
 * /api/v1/configuracion/parametros/key/{key}:
 *   put:
 *     summary: Actualizar parametro del sistema por clave
 *     description: Actualiza el valor de un parametro del sistema buscando por su clave unica
 *     tags: [Configuracion - Parametros del Sistema]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - name: key
 *         in: path
 *         required: true
 *         description: Clave unica del parametro (ej: EMPRESA_NOMBRE)
 *         schema:
 *           type: string
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
 *               descripcion:
 *                 type: string
 *                 maxLength: 1000
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
        const key = decodeURIComponent(params.key);

        const result = await parametroSistemaService.setByKey(key, body, session.user.id);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data, 'Parametro del sistema actualizado exitosamente');
    },
    {
        permission: PERMISSIONS.SISTEMA_AJUSTES_READ,
        schema: SetByKeySchema
    }
);
