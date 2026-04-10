import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { bitacoraMantenimientoService } from '@/lib/services/bitacora-mantenimiento.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ApiResponseHelper } from '@/lib/utils/api-response';

/**
 * @swagger
 * /api/v1/bitacora-mantenimiento/vehiculo/{vehiculoId}:
 *   get:
 *     summary: Obtener registros de mantenimiento por vehiculo
 *     description: Retorna todos los registros de mantenimiento asociados a un vehiculo especifico
 *     tags: [Bitacora Mantenimiento]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - name: vehiculoId
 *         in: path
 *         required: true
 *         description: ID del vehiculo
 *         schema:
 *           type: string
 *           format: uuid
 *     responses:
 *       200:
 *         description: Lista de registros de mantenimiento del vehiculo
 *       404:
 *         description: Vehiculo no encontrado
 *       401:
 *         description: No autorizado
 */
export const GET = apiHandler(
    async (req, session, context) => {
        const params = await context.params;
        const vehiculoId = params.vehiculoId;

        const result = await bitacoraMantenimientoService.getByVehiculo(vehiculoId, session.user.empresa_id);
        if (!result.success) throw result.error;

        return ApiResponseHelper.success(result.data);
    },
    { permission: PERMISSIONS.VEHICULOS_READ }
);
