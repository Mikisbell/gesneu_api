import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { errorAplicacionService } from '@/lib/services/error-aplicacion.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { CreateErrorAplicacionSchema } from '@/lib/validators/error-aplicacion.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';

/**
 * @swagger
 * /api/v1/errors:
 *   get:
 *     summary: Listar errores de aplicacion
 *     description: Obtiene errores de aplicacion con filtros opcionales por severidad, modulo, estado y fecha
 *     tags: [Errores de Aplicacion]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: severidad
 *         schema:
 *           type: string
 *           enum: [DEBUG, INFO, WARNING, ERROR, CRITICAL]
 *       - in: query
 *         name: modulo
 *         schema:
 *           type: string
 *       - in: query
 *         name: resuelto
 *         schema:
 *           type: boolean
 *       - in: query
 *         name: fecha_desde
 *         schema:
 *           type: string
 *           format: date-time
 *       - in: query
 *         name: fecha_hasta
 *         schema:
 *           type: string
 *           format: date-time
 *       - in: query
 *         name: codigo
 *         schema:
 *           type: string
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 100
 *     responses:
 *       200:
 *         description: Lista de errores de aplicacion
 *       401:
 *         description: No autorizado
 */
export const GET = apiHandler(
    async (req, session) => {
        const { searchParams } = new URL(req.url);

        const filters = {
            severidad: searchParams.get('severidad') || undefined,
            modulo: searchParams.get('modulo') || undefined,
            resuelto: searchParams.get('resuelto') !== null ? searchParams.get('resuelto') === 'true' : undefined,
            fecha_desde: searchParams.get('fecha_desde') ? new Date(searchParams.get('fecha_desde')!) : undefined,
            fecha_hasta: searchParams.get('fecha_hasta') ? new Date(searchParams.get('fecha_hasta')!) : undefined,
            codigo: searchParams.get('codigo') || undefined
        };

        const limit = searchParams.get('limit') ? parseInt(searchParams.get('limit')!) : 100;

        const result = await errorAplicacionService.getAll(filters, limit);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data);
    },
    { permission: PERMISSIONS.SISTEMA_AUDITORIA_READ }
);

/**
 * @swagger
 * /api/v1/errors:
 *   post:
 *     summary: Crear registro de error de aplicacion
 *     description: Registra un nuevo error de aplicacion para monitoreo y debugging
 *     tags: [Errores de Aplicacion]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - mensaje
 *             properties:
 *               codigo:
 *                 type: string
 *                 maxLength: 50
 *               severidad:
 *                 type: string
 *                 enum: [DEBUG, INFO, WARNING, ERROR, CRITICAL]
 *                 default: ERROR
 *               mensaje:
 *                 type: string
 *               stack_trace:
 *                 type: string
 *               modulo:
 *                 type: string
 *                 maxLength: 50
 *               endpoint:
 *                 type: string
 *                 maxLength: 255
 *               metodo_http:
 *                 type: string
 *                 maxLength: 10
 *               usuario_id:
 *                 type: string
 *                 format: uuid
 *               ip_direccion:
 *                 type: string
 *                 maxLength: 45
 *               user_agent:
 *                 type: string
 *               request_body:
 *                 type: object
 *               response_body:
 *                 type: object
 *               contexto:
 *                 type: object
 *     responses:
 *       201:
 *         description: Error de aplicacion registrado exitosamente
 *       400:
 *         description: Error de validacion
 */
export const POST = apiHandler(
    async (req, session, _, body) => {
        const result = await errorAplicacionService.create(body);
        if (!result.success) throw result.error;

        return ApiResponseHelper.created(result.data, 'Error de aplicacion registrado exitosamente');
    },
    {
        permission: PERMISSIONS.SISTEMA_AUDITORIA,
        schema: CreateErrorAplicacionSchema
    }
);
