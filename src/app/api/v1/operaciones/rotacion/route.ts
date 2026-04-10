import { NextRequest } from 'next/server';
import { NeumaticoService } from '@/lib/services/neumatico.service';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { RotacionNeumaticoSchema } from '@/lib/validators/operaciones';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';

const service = new NeumaticoService();

/**
 * @swagger
 * /api/v1/operaciones/rotacion:
 *   post:
 *     summary: Rotar neumáticos en vehículo
 *     description: >
 *       Registra la rotación de múltiples neumáticos en un vehículo.
 *       Cada movimiento especifica un neumático y su posición destino.
 *       El sistema realiza swap automático si hay neumático en la posición destino.
 *     tags: [Operaciones]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [vehiculo_id, contador_vehiculo, movimientos]
 *             properties:
 *               vehiculo_id:
 *                 type: string
 *                 format: uuid
 *               contador_vehiculo:
 *                 type: integer
 *                 minimum: 0
 *               movimientos:
 *                 type: array
 *                 minItems: 2
 *                 maxItems: 20
 *                 items:
 *                   type: object
 *                   required: [neumatico_id, posicion_destino_id]
 *                   properties:
 *                     neumatico_id:
 *                       type: string
 *                       format: uuid
 *                     posicion_destino_id:
 *                       type: string
 *                       format: uuid
 *               observaciones:
 *                 type: string
 *                 maxLength: 1000
 *     responses:
 *       200:
 *         description: Rotación completada exitosamente
 *       400:
 *         description: Datos inválidos
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes
 *       404:
 *         description: Neumático o posición no encontrada
 *       409:
 *         description: Conflicto de negocio (reencauchado en direccional, etc.)
 *       500:
 *         description: Error interno del servidor
 */
export async function POST(request: NextRequest) {
    try {
        // 1. Autenticación
        const session = await requireAuth();

        // 2. Autorización
        requirePermission(session, PERMISSIONS.NEUMATICOS_EVENTO_ROTACION);

        // 3. Validación de datos con el schema correcto de rotación
        const body = await request.json();
        const validatedData = RotacionNeumaticoSchema.parse(body);

        // 4. Ejecutar rotación como operación atómica multi-movimiento
        const resultado = await service.ejecutarRotacion(
            validatedData,
            session.user.id,
            session.user.empresa_id!
        );

        return ApiResponseHelper.success(resultado, 'Rotación completada exitosamente');
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
