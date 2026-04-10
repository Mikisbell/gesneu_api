import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { inventarioService } from '@/lib/services/inventario.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ReorderPointSchema } from '@/lib/validators/inventario.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';

/**
 * @swagger
 * /api/v1/inventario/reorder:
 *   post:
 *     summary: Configurar puntos de reorden de inventario
 *     description: Establece o actualiza los puntos de reorden (stock mínimo, máximo, cantidad de reorden) para un almacén y/o modelo
 *     tags: [Inventario]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
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
 *         description: Punto de reorden configurado exitosamente
 *       400:
 *         description: Debe especificar al menos almacen_id o modelo_id
 */
export const POST = apiHandler(
    async (req, session, _, body) => {
        const result = await inventarioService.setReorderPoint(
            session.user.empresa_id,
            session.user.id,
            body
        );
        if (!result.success) throw result.error;

        return ApiResponseHelper.created(result.data, 'Punto de reorden configurado exitosamente');
    },
    {
        permission: PERMISSIONS.INVENTARIO_AJUSTES,
        schema: ReorderPointSchema,
    }
);
