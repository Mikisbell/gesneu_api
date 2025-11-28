import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requireAuth, requirePermission } from '@/lib/auth/authorization';
import { PERMISSIONS } from '@/lib/auth/permissions';
import { ReencaucheEntradaSchema } from '@/lib/validators/operaciones';

/**
 * @swagger
 * /api/v1/operaciones/reencauche/entrada:
 *   post:
 *     summary: Enviar neumático a reencauche
 *     description: Registra el envío de un neumático a la reencauchadora.
 *     tags: [Operaciones]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/ReencaucheEntradaDTO'
 *     responses:
 *       200:
 *         description: Neumático enviado a reencauche exitosamente
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
        requirePermission(session, PERMISSIONS.NEUMATICOS_EVENTO_REENCAUCHE);

        const body = await req.json();
        const validation = ReencaucheEntradaSchema.safeParse(body);

        if (!validation.success) {
            return ApiResponseHelper.validationError(validation.error);
        }

        const {
            neumatico_id,
            proveedor_id,
            kilometraje_vehiculo,
            costo_estimado,
            observaciones,
            fecha_evento
        } = validation.data;

        const neumatico = await prisma.neumatico.findUnique({
            where: { id: neumatico_id },
        });

        if (!neumatico) {
            return ApiResponseHelper.notFound();
        }

        await prisma.$transaction(async (tx) => {
            await tx.eventoNeumatico.create({
                data: {
                    tipo_evento: 'REENCAUCHE_ENTRADA',
                    neumatico_id,
                    fecha_evento: fecha_evento || new Date(),
                    kilometraje_vehiculo,
                    proveedor_id,
                    costo_evento: costo_estimado,
                    notas: observaciones,
                    creado_por: session.user.id,
                },
            });

            await tx.neumatico.update({
                where: { id: neumatico_id },
                data: {
                    estado_actual: 'EN_REENCAUCHE',
                    ubicacion_vehiculo_id: null,
                    ubicacion_posicion_id: null,
                    actualizado_en: new Date(),
                },
            });
        });

        return ApiResponseHelper.success({ message: 'Neumático enviado a reencauche exitosamente' });
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
