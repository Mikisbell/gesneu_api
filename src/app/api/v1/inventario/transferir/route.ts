import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { inventarioService } from '@/lib/services/inventario.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { TransferenciaStockSchema } from '@/lib/validators/inventario.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';

/**
 * @swagger
 * /api/v1/inventario/transferir:
 *   post:
 *     summary: Transferir neumático entre almacenes
 *     description: Transfiere un neumático de un almacén a otro, registrando el evento de movimiento
 *     tags: [Inventario]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [neumatico_id, almacen_origen_id, almacen_destino_id]
 *             properties:
 *               neumatico_id:
 *                 type: string
 *                 format: uuid
 *               almacen_origen_id:
 *                 type: string
 *                 format: uuid
 *               almacen_destino_id:
 *                 type: string
 *                 format: uuid
 *               observaciones:
 *                 type: string
 *                 maxLength: 1000
 *               fecha_evento:
 *                 type: string
 *                 format: date-time
 *     responses:
 *       201:
 *         description: Transferencia realizada exitosamente
 *       400:
 *         description: El neumático no está en el almacén origen especificado
 *       404:
 *         description: Neumático o almacén destino no encontrado
 */
export const POST = apiHandler(
    async (req, session, _, body) => {
        const result = await inventarioService.transferirStock(
            session.user.empresa_id,
            session.user.id,
            body
        );
        if (!result.success) throw result.error;

        return ApiResponseHelper.created(result.data, 'Transferencia realizada exitosamente');
    },
    {
        permission: PERMISSIONS.INVENTARIO_MOVIMIENTOS,
        schema: TransferenciaStockSchema,
    }
);
