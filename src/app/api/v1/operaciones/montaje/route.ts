import { NextRequest } from 'next/server';
import { OperacionesNeumaticosService } from '@/lib/services/operaciones-neumaticos.service';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { MontajeNeumaticoDTO } from '@/types/domain/operaciones.types';
import { MontajeNeumaticoSchema } from '@/lib/validators/operaciones';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';

const service = new OperacionesNeumaticosService();

/**
 * @swagger
 * /api/v1/operaciones/montaje:
 *   post:
 *     summary: Montar neumático
 *     description: Registra el montaje de un neumático en un vehículo.
 *     tags: [Operaciones]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/MontajeNeumaticoDTO'
 *     responses:
 *       200:
 *         description: Neumático montado exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 data:
 *                   type: object
 *                 message:
 *                   type: string
 *       400:
 *         description: Datos inválidos
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere NEUMATICOS_EVENTO_INSTALACION)
 *       500:
 *         description: Error de negocio (ej. Neumático no encontrado)
 */
export async function POST(request: NextRequest) {
    try {
        // 1. Autenticación
        const session = await requireAuth();

        // 2. Autorización
        requirePermission(session, PERMISSIONS.NEUMATICOS_EVENTO_INSTALACION);

        // 3. Validación de datos
        const body = await request.json();

        // Validación con Zod schema
        const validatedData = MontajeNeumaticoSchema.parse(body);

        const data: MontajeNeumaticoDTO = {
            neumatico_id: validatedData.neumatico_id,
            vehiculo_id: validatedData.vehiculo_id,
            posicion_id: validatedData.posicion_id,
            kilometraje_vehiculo: validatedData.kilometraje_vehiculo,
            presion_psi: validatedData.presion_psi,
            observaciones: validatedData.observaciones,
            fecha_evento: validatedData.fecha_evento
        };

        const resultado = await service.montarNeumatico(data);

        return ApiResponseHelper.success(resultado, 'Neumático montado exitosamente');
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
