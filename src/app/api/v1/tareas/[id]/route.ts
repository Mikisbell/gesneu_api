import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { tareaProgramadaService } from '@/lib/services/tarea-programada.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { UpdateTareaProgramadaSchema } from '@/lib/validators/tarea-programada.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';

/**
 * @swagger
 * /api/v1/tareas/{id}:
 *   get:
 *     summary: Obtener tarea programada por ID
 *     description: Retorna los detalles de una tarea programada incluyendo las ultimas 10 ejecuciones
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
 *         description: Tarea programada encontrada
 *       404:
 *         description: Tarea programada no encontrada
 */
export const GET = apiHandler(
    async (req, session, context) => {
        const params = await context.params;
        const id = params.id;

        const result = await tareaProgramadaService.getById(id);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data);
    },
    { permission: PERMISSIONS.SISTEMA_AJUSTES_READ }
);

/**
 * @swagger
 * /api/v1/tareas/{id}:
 *   put:
 *     summary: Actualizar tarea programada
 *     description: Actualiza la configuracion de una tarea programada existente
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
 *               tipo:
 *                 type: string
 *                 enum: [ALERTA_VENCIMIENTO, REPORTE_AUTOMATICO, BACKUP_DB, LIMPIEZA_LOGS, SINCRONIZACION, NOTIFICACION, OTRO]
 *               cron_expresion:
 *                 type: string
 *                 maxLength: 50
 *               intervalo_minutos:
 *                 type: integer
 *               proxima_ejecucion:
 *                 type: string
 *                 format: date-time
 *               parametros:
 *                 type: object
 *               max_reintentos:
 *                 type: integer
 *               activo:
 *                 type: boolean
 *     responses:
 *       200:
 *         description: Tarea programada actualizada exitosamente
 *       404:
 *         description: Tarea programada no encontrada
 */
export const PUT = apiHandler(
    async (req, session, context, body) => {
        const params = await context.params;
        const id = params.id;

        const result = await tareaProgramadaService.update(id, body);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data, 'Tarea programada actualizada exitosamente');
    },
    {
        permission: PERMISSIONS.SISTEMA_AJUSTES,
        schema: UpdateTareaProgramadaSchema
    }
);

/**
 * @swagger
 * /api/v1/tareas/{id}:
 *   delete:
 *     summary: Eliminar tarea programada
 *     description: Elimina una tarea programada del sistema
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
 *         description: Tarea programada eliminada exitosamente
 *       404:
 *         description: Tarea programada no encontrada
 */
export const DELETE = apiHandler(
    async (req, session, context) => {
        const params = await context.params;
        const id = params.id;

        const result = await tareaProgramadaService.delete(id);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(null, 'Tarea programada eliminada exitosamente');
    },
    { permission: PERMISSIONS.SISTEMA_AJUSTES }
);
