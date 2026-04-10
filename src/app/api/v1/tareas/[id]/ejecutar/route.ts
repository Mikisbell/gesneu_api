import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { tareaProgramadaService } from '@/lib/services/tarea-programada.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ApiResponseHelper } from '@/lib/utils/api-response';

/**
 * @swagger
 * /api/v1/tareas/{id}/ejecutar:
 *   post:
 *     summary: Ejecutar tarea programada ahora
 *     description: Ejecuta inmediatamente una tarea programada, creando un registro de ejecucion
 *     tags: [Tareas Programadas]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         description: ID de la tarea programada
 *         schema:
 *           type: string
 *           format: uuid
 *     responses:
 *       200:
 *         description: Tarea ejecutada exitosamente
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
 *                     tarea:
 *                       type: object
 *                     ejecucion:
 *                       type: object
 *       400:
 *         description: La tarea no esta activa
 *       404:
 *         description: Tarea programada no encontrada
 */
export const POST = apiHandler(
    async (req, session, context) => {
        const params = await context.params;
        const id = params.id;

        const result = await tareaProgramadaService.executeNow(id);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data, 'Tarea ejecutada exitosamente');
    },
    { permission: PERMISSIONS.SISTEMA_AJUSTES_READ }
);
