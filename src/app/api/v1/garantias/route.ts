import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { garantiaService } from '@/lib/services/garantia.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { CreateGarantiaSchema } from '@/lib/validators/garantia.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';

/**
 * @swagger
 * /api/v1/garantias:
 *   get:
 *     summary: Listar garantías de neumáticos
 *     description: Retorna todas las garantías de la empresa, con filtros opcionales
 *     tags: [Garantías]
 *     parameters:
 *       - name: estado
 *         in: query
 *         description: Filtrar por estado (VIGENTE, VENCIDA, RECLAMADA, APROBADA, RECHAZADA)
 *         schema:
 *           type: string
 *       - name: neumatico_id
 *         in: query
 *         description: Filtrar por ID de neumático
 *         schema:
 *           type: string
 *           format: uuid
 *       - name: proveedor_id
 *         in: query
 *         description: Filtrar por ID de proveedor
 *         schema:
 *           type: string
 *           format: uuid
 *     responses:
 *       200:
 *         description: Lista de garantías obtenida exitosamente
 */
export const GET = apiHandler(
    async (req, session) => {
        const { searchParams } = new URL(req.url);

        const filters = {
            estado: searchParams.get('estado') || undefined,
            neumatico_id: searchParams.get('neumatico_id') || undefined,
            proveedor_id: searchParams.get('proveedor_id') || undefined,
        };

        const result = await garantiaService.getAll(session.user.empresa_id, filters);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data);
    },
    { permission: PERMISSIONS.NEUMATICOS_READ }
);

/**
 * @swagger
 * /api/v1/garantias:
 *   post:
 *     summary: Crear una nueva garantía para un neumático
 *     description: Registra una garantía asociada a un neumático, con fechas de vigencia y condiciones
 *     tags: [Garantías]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [neumatico_id, fecha_inicio, fecha_fin]
 *             properties:
 *               neumatico_id:
 *                 type: string
 *                 format: uuid
 *               proveedor_id:
 *                 type: string
 *                 format: uuid
 *               numero_garantia:
 *                 type: string
 *                 maxLength: 50
 *               fecha_inicio:
 *                 type: string
 *                 format: date
 *               fecha_fin:
 *                 type: string
 *                 format: date
 *               kilometraje_max:
 *                 type: number
 *               profundidad_min:
 *                 type: number
 *               condiciones:
 *                 type: string
 *                 maxLength: 5000
 *     responses:
 *       201:
 *         description: Garantía creada exitosamente
 */
export const POST = apiHandler(
    async (req, session, _, body) => {
        const result = await garantiaService.create(
            session.user.empresa_id,
            session.user.id,
            body
        );
        if (!result.success) throw result.error;

        return ApiResponseHelper.created(result.data, 'Garantía creada exitosamente');
    },
    {
        permission: PERMISSIONS.NEUMATICOS_CREATE,
        schema: CreateGarantiaSchema,
    }
);
