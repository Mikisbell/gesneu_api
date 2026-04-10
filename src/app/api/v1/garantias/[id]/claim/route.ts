import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { garantiaService } from '@/lib/services/garantia.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ClaimGarantiaSchema, ResolveGarantiaSchema } from '@/lib/validators/garantia.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';

/**
 * @swagger
 * /api/v1/garantias/{id}/claim:
 *   post:
 *     summary: Presentar un reclamo de garantía
 *     description: Inicia el proceso de reclamo para una garantía vigente
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
 *             required: [motivo_reclamo]
 *             properties:
 *               motivo_reclamo:
 *                 type: string
 *                 minLength: 10
 *                 maxLength: 5000
 *               fecha_reclamo:
 *                 type: string
 *                 format: date-time
 *     responses:
 *       201:
 *         description: Reclamo presentado exitosamente
 *       400:
 *         description: La garantía no está en estado VIGENTE
 */
export const POST = apiHandler(
    async (req, session, context, body) => {
        const params = await context.params;
        const id = params.id;

        const result = await garantiaService.fileClaim(
            session.user.empresa_id,
            session.user.id,
            id,
            body
        );
        if (!result.success) throw result.error;

        return ApiResponseHelper.created(result.data, 'Reclamo presentado exitosamente');
    },
    {
        permission: PERMISSIONS.NEUMATICOS_UPDATE,
        schema: ClaimGarantiaSchema,
    }
);

/**
 * @swagger
 * /api/v1/garantias/{id}/claim:
 *   patch:
 *     summary: Resolver un reclamo de garantía
 *     description: Resuelve un reclamo existente, marcándolo como APROBADA o RECHAZADA según el monto de reembolso
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
 *             required: [resolucion]
 *             properties:
 *               resolucion:
 *                 type: string
 *                 minLength: 10
 *                 maxLength: 5000
 *               monto_reembolso:
 *                 type: number
 *                 minimum: 0
 *     responses:
 *       200:
 *         description: Reclamo resuelto exitosamente
 *       400:
 *         description: La garantía no está en estado RECLAMADA
 */
export const PATCH = apiHandler(
    async (req, session, context, body) => {
        const params = await context.params;
        const id = params.id;

        const result = await garantiaService.resolveClaim(
            session.user.empresa_id,
            session.user.id,
            id,
            body
        );
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data, 'Reclamo resuelto exitosamente');
    },
    {
        permission: PERMISSIONS.NEUMATICOS_UPDATE,
        schema: ResolveGarantiaSchema,
    }
);
