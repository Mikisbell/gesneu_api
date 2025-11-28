import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { DesechoNeumaticoSchema } from '@/lib/validators/operaciones';

/**
 * @swagger
 * /api/v1/operaciones/desecho:
 *   post:
 *     summary: Desechar neumático
 *     description: Marca un neumático como desechado permanentemente.
 *     tags: [Operaciones]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/DesechoNeumaticoDTO'
 *     responses:
 *       200:
 *         description: Neumático desechado exitosamente
 *       400:
 *         description: Datos inválidos
 *       404:
 *         description: Neumático no encontrado
 *       401:
 *         description: No autenticado
 *       403:
 *         description: Permisos insuficientes (Requiere OPERACIONES_CREATE)
 */
export async function POST(req: NextRequest) {
    try {
        const session = await requireAuth();
        requirePermission(session, PERMISSIONS.NEUMATICOS_EVENTO_DESECHO);

        const body = await req.json();
        const validation = DesechoNeumaticoSchema.safeParse(body);

        if (!validation.success) {
            return ApiResponseHelper.validationError(validation.error);
        }

        const {
            neumatico_id,
            motivo_id,
            kilometraje_vehiculo,
            observaciones,
            fecha_evento
        } = validation.data;

        const neumatico = await prisma.neumatico.findUnique({
            where: { id: neumatico_id },
        });

        if (!neumatico) {
            return ApiResponseHelper.notFound('Neumático no encontrado');
        }

        await prisma.$transaction(async (tx) => {
            await tx.eventoNeumatico.create({
                data: {
                    tipo_evento: 'DESECHO',
                    neumatico_id,
                    fecha_evento: fecha_evento || new Date(),
                    kilometraje_vehiculo,
                    motivo_desecho_id: motivo_id,
                    notas: observaciones,
                    creado_por: session.user.id,
                },
            });

            await tx.neumatico.update({
                where: { id: neumatico_id },
                data: {
                    estado_actual: 'DESECHADO',
                    ubicacion_vehiculo_id: null,
                    ubicacion_posicion_id: null,
                    ubicacion_almacen_id: null,
                    fecha_desecho: fecha_evento || new Date(),
                    activo: false,
                    actualizado_en: new Date(),
                },
            });
        });

        return ApiResponseHelper.success({ message: 'Neumático desechado exitosamente' });
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
