import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { bitacoraMantenimientoService } from '@/lib/services/bitacora-mantenimiento.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { CreateBitacoraMantenimientoSchema } from '@/lib/validators/bitacora-mantenimiento.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';

/**
 * @swagger
 * /api/v1/bitacora-mantenimiento:
 *   get:
 *     summary: Listar registros de bitacora de mantenimiento
 *     description: Obtiene registros de mantenimiento con filtros opcionales por tipo, vehiculo, fecha y proveedor
 *     tags: [Bitacora Mantenimiento]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: tipo_operacion
 *         schema:
 *           type: string
 *         description: Filtrar por tipo de operacion
 *       - in: query
 *         name: vehiculo_id
 *         schema:
 *           type: string
 *           format: uuid
 *         description: Filtrar por ID de vehiculo
 *       - in: query
 *         name: fecha_desde
 *         schema:
 *           type: string
 *           format: date-time
 *         description: Fecha inicio del rango
 *       - in: query
 *         name: fecha_hasta
 *         schema:
 *           type: string
 *           format: date-time
 *         description: Fecha fin del rango
 *       - in: query
 *         name: proveedor_id
 *         schema:
 *           type: string
 *           format: uuid
 *         description: Filtrar por ID de proveedor
 *     responses:
 *       200:
 *         description: Lista de registros de mantenimiento
 *       401:
 *         description: No autorizado
 */
export const GET = apiHandler(
    async (req, session) => {
        const { searchParams } = new URL(req.url);

        const filters = {
            tipo_operacion: searchParams.get('tipo_operacion') || undefined,
            vehiculo_id: searchParams.get('vehiculo_id') || undefined,
            fecha_desde: searchParams.get('fecha_desde') ? new Date(searchParams.get('fecha_desde')!) : undefined,
            fecha_hasta: searchParams.get('fecha_hasta') ? new Date(searchParams.get('fecha_hasta')!) : undefined,
            proveedor_id: searchParams.get('proveedor_id') || undefined
        };

        const result = await bitacoraMantenimientoService.getAll(session.user.empresa_id, filters);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data);
    },
    { permission: PERMISSIONS.VEHICULOS_READ }
);

/**
 * @swagger
 * /api/v1/bitacora-mantenimiento:
 *   post:
 *     summary: Crear registro de bitacora de mantenimiento
 *     description: Registra una nueva entrada en la bitacora de mantenimiento
 *     tags: [Bitacora Mantenimiento]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - vehiculo_id
 *               - tipo_operacion
 *             properties:
 *               vehiculo_id:
 *                 type: string
 *                 format: uuid
 *               tipo_operacion:
 *                 type: string
 *                 enum: [MANTENIMIENTO_PREVENTIVO, MANTENIMIENTO_CORRECTIVO, INSPECCION_PROGRAMADA, INSPECCION_ALEATORIA, LAVADO, ALINEACION, BALANCEO, CAMBIO_ACEITE, OTRO]
 *               fecha_programada:
 *                 type: string
 *                 format: date-time
 *               fecha_realizada:
 *                 type: string
 *                 format: date-time
 *               kilometraje:
 *                 type: number
 *               horometro:
 *                 type: number
 *               costo:
 *                 type: number
 *               proveedor_id:
 *                 type: string
 *                 format: uuid
 *               responsable:
 *                 type: string
 *                 maxLength: 200
 *               observaciones:
 *                 type: string
 *                 maxLength: 5000
 *               evidencia_url:
 *                 type: string
 *                 format: uri
 *     responses:
 *       201:
 *         description: Registro de mantenimiento creado exitosamente
 *       400:
 *         description: Error de validacion
 */
export const POST = apiHandler(
    async (req, session, _, body) => {
        const result = await bitacoraMantenimientoService.create(
            body,
            session.user.id
        );

        if (!result.success) throw result.error;

        return ApiResponseHelper.created(result.data, 'Registro de mantenimiento creado exitosamente');
    },
    {
        permission: PERMISSIONS.VEHICULOS_UPDATE,
        schema: CreateBitacoraMantenimientoSchema
    }
);
