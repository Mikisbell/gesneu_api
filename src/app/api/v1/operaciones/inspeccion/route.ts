import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { InspeccionNeumaticoSchema } from '@/lib/validators/operaciones';

/**
 * @swagger
 * /api/v1/operaciones/inspeccion:
 *   post:
 *     summary: Registrar inspección de neumático
 *     description: Registra mediciones de profundidad y presión sin mover el neumático.
 *     tags: [Operaciones]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/InspeccionNeumaticoDTO'
 *     responses:
 *       200:
 *         description: Inspección registrada exitosamente
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
        requirePermission(session, PERMISSIONS.NEUMATICOS_EVENTO_INSPECCION);

        const body = await req.json();
        const validation = InspeccionNeumaticoSchema.safeParse(body);

        if (!validation.success) {
            return ApiResponseHelper.validationError(validation.error);
        }

        const {
            neumatico_id,
            profundidad_izquierda_mm,
            profundidad_centro_mm,
            profundidad_derecha_mm,
            presion_psi,
            kilometraje_vehiculo,
            observaciones,
            fecha_evento
        } = validation.data;

        const neumatico = await prisma.neumatico.findUnique({
            where: { id: neumatico_id },
            include: { ubicacion_vehiculo: true }
        });

        if (!neumatico) {
            return ApiResponseHelper.notFound();
        }

        await prisma.$transaction(async (tx) => {
            // Create inspection event
            await tx.eventoNeumatico.create({
                data: {
                    tipo_evento: 'INSPECCION',
                    neumatico_id,
                    fecha_evento: fecha_evento || new Date(),
                    kilometraje_vehiculo,
                    profundidad_remanente: profundidad_centro_mm,
                    presion_psi,
                    vehiculo_id: neumatico.ubicacion_vehiculo_id,
                    notas: observaciones,
                    creado_por: session.user.id,
                },
            });

            // Update tire measurements (average profundidad)
            const profundidad_promedio = (
                (profundidad_izquierda_mm || 0) +
                (profundidad_centro_mm || 0) +
                (profundidad_derecha_mm || 0)
            ) / 3;

            await tx.neumatico.update({
                where: { id: neumatico_id },
                data: {
                    profundidad_actual_mm: profundidad_promedio,
                    presion_actual_psi: presion_psi,
                    actualizado_en: new Date(),
                },
            });
        });

        return ApiResponseHelper.success({ message: 'Inspección registrada exitosamente' });
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
