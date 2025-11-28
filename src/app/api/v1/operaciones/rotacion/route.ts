import { NextRequest } from 'next/server';
import { OperacionesNeumaticosService } from '@/lib/services/operaciones-neumaticos.service';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { RotacionNeumaticoDTO } from '@/types/domain/operaciones.types';
import { RotacionNeumaticoSchema } from '@/lib/validators/operaciones';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';

const service = new OperacionesNeumaticosService();

/**
 * @swagger
 * /api/v1/operaciones/rotacion:
 *   post:
 *     summary: Rotar neumáticos
 *     description: Registra la rotación de neumáticos en un vehículo.
 *     tags: [Operaciones]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/RotacionNeumaticoDTO'
 *     responses:
 *       200:
 *         description: Neumáticos rotados exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   type: array
 *                   items:
 *                     type: object
 *                 message:
 *                   type: string
 *       400:
 *         description: Datos inválidos
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere NEUMATICOS_EVENTO_ROTACION)
 *       500:
 *         description: Error de negocio
 */
export async function POST(request: NextRequest) {
    try {
        // 1. Autenticación
        const session = await requireAuth();

        // 2. Autorización
        requirePermission(session, PERMISSIONS.NEUMATICOS_EVENTO_ROTACION);

        // 3. Validación de datos
        const body = await request.json();

        // Validación con Zod schema
        const validatedData = RotacionNeumaticoSchema.parse(body);

        const data: RotacionNeumaticoDTO = {
            vehiculo_id: validatedData.vehiculo_id,
            kilometraje_vehiculo: validatedData.kilometraje_vehiculo,
            movimientos: validatedData.movimientos,
            observaciones: validatedData.observaciones
        };

        const resultado = await service.rotarNeumaticos(data);

        return ApiResponseHelper.success(resultado, `${resultado.length} neumáticos rotados exitosamente`);
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
