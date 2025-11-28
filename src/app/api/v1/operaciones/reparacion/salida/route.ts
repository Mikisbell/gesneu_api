import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { ApiResponseHelper } from '@/lib/utils/api-response';
import { requirePermission } from '@/lib/auth/permissions';
import { ReparacionSalidaSchema } from '@/lib/validators/operaciones';

/**
 * @swagger
 * /api/v1/operaciones/reparacion/salida:
 *   post:
 *     summary: Retornar neumático de reparación
 *     description: Registra el retorno de un neumático desde el taller de reparación al almacén.
 *     tags: [Operaciones]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/ReparacionSalidaDTO'
 *     responses:
 *       200:
 *         description: Neumático retornado de reparación exitosamente
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
        const session = await requirePermission(req, 'OPERACIONES_CREATE');
        if (session instanceof NextResponse) return session;

        const body = await req.json();
        const validation = ReparacionSalidaSchema.safeParse(body);

        if (!validation.success) {
            return ApiResponseHelper.validationError(validation.error);
        }

        const {
            neumatico_id,
            almacen_destino_id,
            costo_real,
            profundidad_nueva_mm,
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
                    tipo_evento: 'REPARACION_SALIDA',
                    neumatico_id,
                    fecha_evento: fecha_evento || new Date(),
                    almacen_destino_id,
                    costo_evento: costo_real,
                    profundidad_remanente: profundidad_nueva_mm,
                    notas: observaciones,
                    creado_por: session.user.id,
                },
            });

            await tx.neumatico.update({
                where: { id: neumatico_id },
                data: {
                    estado_actual: 'EN_STOCK',
                    ubicacion_almacen_id: almacen_destino_id,
                    ...(profundidad_nueva_mm && {
                        profundidad_actual_mm: profundidad_nueva_mm,
                    }),
                    actualizado_en: new Date(),
                },
            });
        });

        return ApiResponseHelper.success({ message: 'Neumático retornado de reparación exitosamente' });
    } catch (error) {
        return ApiResponseHelper.handleError(error);
    }
}
