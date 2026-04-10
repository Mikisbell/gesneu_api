import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { tareaProgramadaService } from '@/lib/services/tarea-programada.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { CreateTareaProgramadaSchema } from '@/lib/validators/tarea-programada.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';

/**
 * @swagger
 * /api/v1/tareas:
 *   get:
 *     summary: Listar tareas programadas
 *     description: Obtiene todas las tareas programadas del sistema
 *     tags: [Tareas Programadas]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Lista de tareas programadas
 *       401:
 *         description: No autorizado
 */
export const GET = apiHandler(
    async (req, session) => {
        const result = await tareaProgramadaService.getAll();
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data);
    },
    { permission: PERMISSIONS.SISTEMA_AJUSTES_READ }
);

/**
 * @swagger
 * /api/v1/tareas:
 *   post:
 *     summary: Crear tarea programada
 *     description: Crea una nueva tarea programada con configuracion cron o por intervalo
 *     tags: [Tareas Programadas]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - nombre
 *               - tipo
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
 *                 description: "Expresion cron (ej: 0 0 * * * para diaria a medianoche)"
 *               intervalo_minutos:
 *                 type: integer
 *                 description: Alternativa a cron, intervalo en minutos
 *               proxima_ejecucion:
 *                 type: string
 *                 format: date-time
 *               parametros:
 *                 type: object
 *                 additionalProperties: true
 *               max_reintentos:
 *                 type: integer
 *                 default: 3
 *               activo:
 *                 type: boolean
 *                 default: true
 *     responses:
 *       201:
 *         description: Tarea programada creada exitosamente
 *       400:
 *         description: Error de validacion
 */
export const POST = apiHandler(
    async (req, session, _, body) => {
        const result = await tareaProgramadaService.create(body);
        if (!result.success) throw result.error;

        return ApiResponseHelper.created(result.data, 'Tarea programada creada exitosamente');
    },
    {
        permission: PERMISSIONS.SISTEMA_AJUSTES,
        schema: CreateTareaProgramadaSchema
    }
);
