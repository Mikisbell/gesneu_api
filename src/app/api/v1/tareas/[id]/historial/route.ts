import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { tareaProgramadaService } from '@/lib/services/tarea-programada.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ApiResponseHelper } from '@/lib/utils/api-response';

/**
 * @swagger
 * /api/v1/tareas/{id}/historial:
 *   get:
 *     summary: Obtener historial de ejecuciones de una tarea
 *     description: Retorna el historial de ejecuciones de una tarea programada con opcion de limitar resultados
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
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 50
 *         description: Numero maximo de ejecuciones a retornar
 *     responses:
 *       200:
 *         description: Historial de ejecuciones
 *       404:
 *         description: Tarea programada no encontrada
 */
export const GET = apiHandler(
    async (req, session, context) => {
        const params = await context.params;
        const id = params.id;

        const { searchParams } = new URL(req.url);
        const limit = searchParams.get('limit') ? parseInt(searchParams.get('limit')!) : 50;

        const result = await tareaProgramadaService.getExecutionHistory(id, limit);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data);
    },
    { permission: PERMISSIONS.SISTEMA_AJUSTES_READ }
);
