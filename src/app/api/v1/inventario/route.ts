import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { inventarioService } from '@/lib/services/inventario.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { CreateInventarioParamSchema } from '@/lib/validators/inventario.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';

/**
 * @swagger
 * /api/v1/inventario:
 *   get:
 *     summary: Obtener resumen de stock por almacén
 *     description: Retorna el stock agrupado por almacén, con desglose por estado y modelo
 *     tags: [Inventario]
 *     parameters:
 *       - name: almacen_id
 *         in: query
 *         description: Filtrar por un almacén específico
 *         schema:
 *           type: string
 *           format: uuid
 *     responses:
 *       200:
 *         description: Stock por almacén obtenido exitosamente
 */
export const GET = apiHandler(
    async (req, session) => {
        const { searchParams } = new URL(req.url);
        const almacenId = searchParams.get('almacen_id') || undefined;

        const result = await inventarioService.getStockByAlmacen(session.user.empresa_id, almacenId);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data);
    },
    { permission: PERMISSIONS.INVENTARIO_READ }
);

/**
 * @swagger
 * /api/v1/inventario:
 *   post:
 *     summary: Crear parámetro de inventario (stock mínimo/máximo)
 *     description: Configura los parámetros de stock para un almacén y/o modelo
 *     tags: [Inventario]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [almacen_id, stock_minimo]
 *             properties:
 *               almacen_id:
 *                 type: string
 *                 format: uuid
 *               modelo_id:
 *                 type: string
 *                 format: uuid
 *               stock_minimo:
 *                 type: integer
 *               stock_maximo:
 *                 type: integer
 *               punto_reorden:
 *                 type: integer
 *               cantidad_reorden:
 *                 type: integer
 *               lead_time_dias:
 *                 type: integer
 *     responses:
 *       201:
 *         description: Parámetro de inventario creado exitosamente
 */
export const POST = apiHandler(
    async (req, session, _, body) => {
        const result = await inventarioService.setReorderPoint(
            session.user.empresa_id,
            session.user.id,
            body
        );
        if (!result.success) throw result.error;

        return ApiResponseHelper.created(result.data, 'Parámetro de inventario creado exitosamente');
    },
    {
        permission: PERMISSIONS.INVENTARIO_AJUSTES,
        schema: CreateInventarioParamSchema,
    }
);
