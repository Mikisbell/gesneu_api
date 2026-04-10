import { NextRequest, NextResponse } from 'next/server';
import { apiHandler } from '@/lib/utils/api-wrapper';
import { rutaService } from '@/lib/services/ruta.service';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { AssignRutaSchema } from '@/lib/validators/ruta.validator';
import { ApiResponseHelper } from '@/lib/utils/api-response';

/**
 * @swagger
 * /api/v1/rutas/{id}/asignar:
 *   post:
 *     summary: Asignar vehículo a una ruta
 *     description: Asocia un vehículo existente a la ruta especificada
 *     tags: [Rutas]
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         description: ID de la ruta
 *         schema:
 *           type: string
 *           format: uuid
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [vehiculo_id]
 *             properties:
 *               vehiculo_id:
 *                 type: string
 *                 format: uuid
 *     responses:
 *       201:
 *         description: Vehículo asignado a la ruta exitosamente
 *       404:
 *         description: Ruta o vehículo no encontrado
 */
export const POST = apiHandler(
    async (req, session, context, body) => {
        const params = await context.params;
        const id = params.id;

        const result = await rutaService.assignToVehiculo(
            session.user.empresa_id,
            session.user.id,
            id,
            body
        );
        if (!result.success) throw result.error;

        return ApiResponseHelper.created(result.data, 'Vehículo asignado a la ruta exitosamente');
    },
    {
        permission: PERMISSIONS.VEHICULOS_UPDATE,
        schema: AssignRutaSchema,
    }
);
