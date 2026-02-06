import { NextRequest } from 'next/server';
import { NeumaticoService } from '@/lib/services/neumatico.service';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { EventoNeumaticoCreateSchema } from '@/lib/validators/evento-neumatico';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';

const service = new NeumaticoService();

/**
 * @swagger
 * /api/v1/operaciones/rotacion:
 *   post:
 *     summary: Rotar neumático
 *     description: Registra la rotación de un neumático en un vehículo.
 *     tags: [Operaciones]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/EventoNeumaticoCreate'
 *     responses:
 *       200:
 *         description: Neumático rotado exitosamente
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

        // Ensure tipo_evento is set to ROTACION
        const eventData = {
            ...body,
            tipo_evento: 'ROTACION'
        };

        // Validación con Zod schema
        const validatedData = EventoNeumaticoCreateSchema.parse(eventData);

        const resultado = await service.registrarEvento(validatedData, session.user.id, session.user.empresa_id!);

        return ApiResponseHelper.success(resultado, 'Neumático rotado exitosamente');
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
