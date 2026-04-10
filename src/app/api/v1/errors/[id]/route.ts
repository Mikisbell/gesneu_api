import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { errorAplicacionService } from '@/lib/services/error-aplicacion.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ResolveErrorSchema } from '@/lib/validators/error-aplicacion.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';

/**
 * @swagger
 * /api/v1/errors/{id}:
 *   get:
 *     summary: Obtener error de aplicacion por ID
 *     description: Retorna los detalles completos de un error de aplicacion registrado
 *     tags: [Errores de Aplicacion]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         description: ID del error de aplicacion
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Error de aplicacion encontrado
 *       404:
 *         description: Error de aplicacion no encontrado
 */
export const GET = apiHandler(
    async (req, session, context) => {
        const params = await context.params;
        const id = params.id;

        const result = await errorAplicacionService.getById(id);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data);
    },
    { permission: PERMISSIONS.SISTEMA_AUDITORIA_READ }
);

/**
 * @swagger
 * /api/v1/errors/{id}:
 *   patch:
 *     summary: Reconocer error de aplicacion
 *     description: Marca un error como revisado/reconocido sin resolverlo
 *     tags: [Errores de Aplicacion]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         description: ID del error de aplicacion
 *         schema:
 *           type: string
 *     requestBody:
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               accion:
 *                 type: string
 *                 enum: [acknowledge, resolve]
 *                 description: "Accion a realizar: acknowledge para reconocer, resolve para resolver"
 *               notas:
 *                 type: string
 *                 maxLength: 2000
 *     responses:
 *       200:
 *         description: Error actualizado exitosamente
 *       404:
 *         description: Error de aplicacion no encontrado
 */
export const PATCH = apiHandler(
    async (req, session, context, body) => {
        const params = await context.params;
        const id = params.id;

        const accion = body?.accion || 'acknowledge';

        if (accion === 'acknowledge') {
            const result = await errorAplicacionService.acknowledge(id, session.user.id);
            if (!result.success) throw result.error;

            return ApiResponseHelper.success(result.data, 'Error reconocido exitosamente');
        }

        if (accion === 'resolve') {
            const validation = ResolveErrorSchema.safeParse(body);
            if (!validation.success) {
                return ApiResponseHelper.validationError(validation.error);
            }

            const result = await errorAplicacionService.resolve(
                id,
                session.user.id,
                validation.data.notas
            );
            if (!result.success) throw result.error;

            return ApiResponseHelper.success(result.data, 'Error resuelto exitosamente');
        }

        return ApiResponseHelper.badRequest('Accion invalida. Use acknowledge o resolve');
    },
    { permission: PERMISSIONS.SISTEMA_AUDITORIA_READ }
);
