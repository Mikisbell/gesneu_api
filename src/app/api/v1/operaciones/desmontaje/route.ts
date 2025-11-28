import { NextRequest } from 'next/server';
import { OperacionesNeumaticosService } from '@/lib/services/operaciones-neumaticos.service';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { DesmontajeNeumaticoDTO } from '@/types/domain/operaciones.types';
import { DesmontajeNeumaticoSchema } from '@/lib/validators/operaciones';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/authorization';

const service = new OperacionesNeumaticosService();

/**
 * @swagger
 * /api/v1/operaciones/desmontaje:
 *   post:
 *     summary: Desmontar neumático
 *     description: Registra el desmontaje de un neumático de un vehículo.
 *     tags: [Operaciones]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/DesmontajeNeumaticoDTO'
 *     responses:
 *       200:
 *         description: Neumático desmontado exitosamente
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
 *         description: Permisos insuficientes (Requiere NEUMATICOS_EVENTO_DESMONTAJE)
 *       500:
 *         description: Error de negocio (ej. Neumático no encontrado)
 */
export async function POST(request: NextRequest) {
    try {
        // 1. Autenticación
        const session = await requireAuth();

        // 2. Autorización
        requirePermission(session, PERMISSIONS.NEUMATICOS_EVENTO_DESMONTAJE);

        // 3. Validación de datos
        const body = await request.json();

        // Validación con Zod schema
        const validatedData = DesmontajeNeumaticoSchema.parse(body);

        const data: DesmontajeNeumaticoDTO = {
            neumatico_id: validatedData.neumatico_id,
            destino: validatedData.destino,
            kilometraje_vehiculo: validatedData.kilometraje_vehiculo,
            almacen_destino_id: validatedData.almacen_destino_id,
            motivo_id: validatedData.motivo_id,
            profundidad_remanente_mm: validatedData.profundidad_remanente_mm,
            presion_psi: validatedData.presion_psi,
            observaciones: validatedData.observaciones,
            fecha_evento: validatedData.fecha_evento
        };

        const resultado = await service.desmontarNeumatico(data);

        return ApiResponseHelper.success(resultado, 'Neumático desmontado exitosamente');
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
