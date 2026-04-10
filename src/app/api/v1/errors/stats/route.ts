import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { errorAplicacionService } from '@/lib/services/error-aplicacion.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ApiResponseHelper } from '@/lib/utils/api-response';

/**
 * @swagger
 * /api/v1/errors/stats:
 *   get:
 *     summary: Obtener estadisticas de errores
 *     description: Retorna estadisticas agregadas de errores de aplicacion incluyendo totales, por severidad, por modulo y errores recientes
 *     tags: [Errores de Aplicacion]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Estadisticas de errores
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                 data:
 *                   type: object
 *                   properties:
 *                     total:
 *                       type: integer
 *                     resueltos:
 *                       type: integer
 *                     noResueltos:
 *                       type: integer
 *                     porcentajeResolucion:
 *                       type: integer
 *                     porSeveridad:
 *                       type: array
 *                       items:
 *                         type: object
 *                     porModulo:
 *                       type: array
 *                       items:
 *                         type: object
 *                     recientes24h:
 *                       type: integer
 *                     criticosSinResolver:
 *                       type: integer
 *       401:
 *         description: No autorizado
 */
export const GET = apiHandler(
    async (req, session) => {
        const result = await errorAplicacionService.getStats();
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data);
    },
    { permission: PERMISSIONS.SISTEMA_AUDITORIA_READ }
);
